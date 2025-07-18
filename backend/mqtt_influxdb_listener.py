# backend/mqtt_influxdb_listener.py

import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import os

# Ρυθμίσεις InfluxDB (πρέπει να ταιριάζουν με αυτές στο influx_client.py)
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "admintoken") # Βεβαιώσου ότι είναι το σωστό token
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "energy-org") # Βεβαιώσου ότι είναι το σωστό organization
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "wind-data") # Βεβαιώσου ότι είναι το σωστό bucket

# Ρυθμίσεις MQTT
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "wind/measurements") # Το ίδιο topic με τον προσομοιωτή

influx_client = None
write_api = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Συνδέθηκε επιτυχώς στον MQTT Broker")
        client.subscribe(MQTT_TOPIC)
        print(f"Εγγεγραμμένος στο θέμα: {MQTT_TOPIC}")
    else:
        print(f"Αποτυχία σύνδεσης στον MQTT Broker, κωδικός: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"Λήφθηκε μήνυμα MQTT: {payload}")

        # Δημιουργία InfluxDB Point από το payload
        point = Point("wind_speed") \
            .tag("turbine", payload.get("turbine")) \
            .field("speed", float(payload.get("speed"))) \
            .field("direction", int(payload.get("direction"))) \
            .field("power", float(payload.get("power"))) \
            .time(payload.get("timestamp")) # Χρησιμοποιούμε το timestamp από το μήνυμα

        if write_api:
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
            print(f"Επιτυχής εγγραφή δεδομένων στην InfluxDB για την τουρμπίνα: {payload.get('turbine')}")
        else:
            print("InfluxDB write_api δεν είναι διαθέσιμο.")

    except json.JSONDecodeError:
        print(f"Λάθος JSON Payload: {msg.payload}")
    except Exception as e:
        print(f"Σφάλμα επεξεργασίας μηνύματος ή εγγραφής στην InfluxDB: {e}")

if __name__ == "__main__":
    try:
        # Αρχικοποίηση InfluxDB Client
        influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        write_api = influx_client.write_api(write_options=SYNCHRONOUS)

        # Αρχικοποίηση MQTT Client
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60) # Keepalive interval 60 seconds
        mqtt_client.loop_forever() # Ξεκινά τον MQTT loop και μπλοκάρει

    except KeyboardInterrupt:
        print("\nΟ Listener τερματίστηκε.")
    except Exception as e:
        print(f"Προέκυψε σφάλμα στον Listener: {e}")
    finally:
        if influx_client:
            influx_client.close()
            print("InfluxDB Client έκλεισε.")