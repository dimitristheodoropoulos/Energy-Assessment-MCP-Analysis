import paho.mqtt.client as mqtt
import time
import json
import random
import math
from datetime import datetime, timezone # Προσθήκη timezone για ISO timestamp

# Ρυθμίσεις MQTT
broker = "localhost"
port = 1883
topic = "wind/measurements"

client = mqtt.Client()
client.connect(broker, port)
client.loop_start()  # Ξεκινά το network loop σε background

# Παράμετροι για ένα απλό trend/cycle (24-ωρος κύκλος)
start_time = time.time()
cycle_duration = 3600 * 24 # Ένας κύκλος 24 ωρών σε δευτερόλεπτα

print("Ξεκινά ο προσομοιωτής δεδομένων ανέμου για 't1' και 'T2_ref'. Πατήστε Ctrl+C για έξοδο.")

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time
    timestamp_iso = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    
    # Προσθήκη εποχιακής διακύμανσης (π.χ. ημέρας/νύχτας) στην ταχύτητα ανέμου
    daily_cycle_factor = math.sin((elapsed_time / cycle_duration) * 2 * math.pi)

    # --- Δεδομένα για την τουρμπίνα 't1' ---
    turbine_id_t1 = "t1"
    base_wind_speed_t1 = 8 + daily_cycle_factor * 3 + random.uniform(-2.0, 2.0) # m/s
    wind_speed_t1 = max(0, round(base_wind_speed_t1, 2))
    power_output_t1 = round(0.5 * 1.2 * (wind_speed_t1**3), 2) # kW
    wind_direction_t1 = random.randint(0, 359) # Degrees

    data_t1 = {
        "turbine": turbine_id_t1,
        "speed": wind_speed_t1,
        "direction": wind_direction_t1,
        "power": power_output_t1,
        "timestamp": timestamp_iso # Χρησιμοποιούμε ISO timestamp
    }
    client.publish(topic, json.dumps(data_t1))
    print(f"Published (t1): {data_t1}")

    # --- Δεδομένα για την τουρμπίνα 'T2_ref' ---
    # Για την T2_ref, μπορούμε να χρησιμοποιήσουμε μια ελαφρώς διαφορετική βασική ταχύτητα
    # ή λιγότερη τυχαιότητα για να την προσομοιώσουμε ως "αναφορά".
    turbine_id_t2ref = "T2_ref"
    base_wind_speed_t2ref = 9 + daily_cycle_factor * 2 + random.uniform(-1.0, 1.0) # Ελαφρώς υψηλότερη μέση ταχύτητα, λιγότερη διακύμανση
    wind_speed_t2ref = max(0, round(base_wind_speed_t2ref, 2))
    power_output_t2ref = round(0.5 * 1.2 * (wind_speed_t2ref**3), 2) # kW
    wind_direction_t2ref = random.randint(0, 359) # Επίσης τυχαία κατεύθυνση

    data_t2ref = {
        "turbine": turbine_id_t2ref,
        "speed": wind_speed_t2ref,
        "direction": wind_direction_t2ref,
        "power": power_output_t2ref,
        "timestamp": timestamp_iso # Χρησιμοποιούμε ISO timestamp
    }
    client.publish(topic, json.dumps(data_t2ref))
    print(f"Published (T2_ref): {data_t2ref}")

    time.sleep(5) # Στέλνει δεδομένα κάθε 5 δευτερόλεπτα για κάθε τουρμπίνα