import time
import random
import paho.mqtt.client as mqtt
import os
import logging
import json # Προσθήκη για JSON payload
import math # Προσθήκη για ημιτονοειδές κύμα
from datetime import datetime # Προσθήκη για ISO timestamp (αν και θα χρησιμοποιήσουμε epoch int)

# Ρύθμιση logging με timestamp
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO
)

broker = os.getenv("MQTT_BROKER", "mosquitto")
port = int(os.getenv("MQTT_PORT", 1883))
# !!! ΣΗΜΑΝΤΙΚΟ: Το topic θα είναι wind/measurements όπως συμφωνήσαμε
topic = os.getenv("MQTT_TOPIC", "wind/measurements")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info(f"Συνδεθήκαμε επιτυχώς στον broker {broker}:{port}")
    else:
        logging.error(f"Αποτυχία σύνδεσης με broker, κωδικός {rc}")

def on_disconnect(client, userdata, rc):
    logging.warning("Αποσυνδέθηκε από broker")

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_disconnect = on_disconnect

try:
    client.connect(broker, port, 60)
except Exception as e:
    logging.error(f"Σφάλμα σύνδεσης: {e}")
    exit(1)

client.loop_start()

# Αναγνωριστικό τουρμπίνας (σημαντικό για το Grafana)
turbine_id = "t1" # Μπορείς να προσθέσεις και άλλες τουρμπίνες αν θες

# Παράμετροι για ένα απλό trend/cycle (24-ωρος κύκλος)
start_time = time.time()
cycle_duration = 3600 * 24 # Ένας κύκλος 24 ωρών σε δευτερόλεπτα

try:
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Προσθήκη εποχιακής διακύμανσης (π.χ. ημέρας/νύχτας) στην ταχύτητα ανέμου
        daily_cycle_factor = math.sin((elapsed_time / cycle_duration) * 2 * math.pi)

        # Βασική ταχύτητα ανέμου με προσθήκη κύκλου και τυχαίας διακύμανσης
        # Η ταχύτητα θα κυμαίνεται περίπου 5 m/s (όταν daily_cycle_factor είναι -1) έως 11 m/s (όταν daily_cycle_factor είναι 1)
        base_wind_speed = 8 + daily_cycle_factor * 3 + random.uniform(-2.0, 2.0) # m/s
        
        # Εξασφάλιση ότι η ταχύτητα δεν είναι αρνητική
        wind_speed = max(0, round(base_wind_speed, 2))

        # Υπολογισμός ισχύος με βάση το απλό μοντέλο P=0.5ρv³ (όπου ρ=1.2 kg/m³)
        power_output = round(0.5 * 1.2 * (wind_speed**3), 2) # kW

        # Κατεύθυνση ανέμου (παραμένει τυχαία)
        wind_direction = random.randint(0, 359) # Degrees

        # Δημιουργία JSON payload
        data = {
            "turbine": turbine_id,
            "speed": wind_speed,
            "direction": wind_direction,
            "power": power_output,
            "timestamp": int(time.time()) # Timestamp σε epoch δευτερόλεπτα
        }

        # Δημοσίευση του JSON payload
        result = client.publish(topic, json.dumps(data))
        status = result[0]
        if status == 0:
            logging.info(f"Απεστάλη: {data} στο θέμα {topic}")
        else:
            logging.error(f"Αποτυχία αποστολής στο θέμα {topic}")
        
        time.sleep(5) # Στέλνει δεδομένα κάθε 5 δευτερόλεπτα
except KeyboardInterrupt:
    logging.info("Τερματισμός publisher από χρήστη")
finally:
    client.loop_stop()
    client.disconnect()