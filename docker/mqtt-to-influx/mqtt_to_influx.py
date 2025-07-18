# mqtt_to_influx.py

import os
import time
import logging
import json
from influxdb_client import InfluxDBClient, Point, WriteOptions
import paho.mqtt.client as mqtt
import pandas as pd

# Ρυθμίσεις InfluxDB από env vars
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "admintoken")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "energy-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "wind-data")

# MQTT ρυθμίσεις
MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "wind/measurements")

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

client = None
write_api = None

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        logging.info(f"Συνδεθήκαμε στον MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
        logging.info(f"Εγγραφή στο θέμα: {MQTT_TOPIC}")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.error(f"Αποτυχία σύνδεσης με κωδικό: {rc}")

def on_message(client, userdata, msg):
    try:
        # Αποκωδικοποίηση του JSON payload
        payload = json.loads(msg.payload.decode())
        logging.info(f"Λήψη μηνύματος: {payload} από θέμα: {msg.topic}")

        timestamp_value = payload.get("timestamp")
        if timestamp_value is not None:
            # ************** ΔΙΟΡΘΩΣΗ ΕΔΩ **************
            # Remove unit='s' to allow pandas to automatically detect string format
            # If the timestamp is an integer (epoch), pandas will still handle it.
            point_timestamp = pd.to_datetime(timestamp_value, utc=True)
            # **********************************************
        else:
            # Αν δεν υπάρχει timestamp στο payload, χρησιμοποιούμε την τρέχουσα ώρα UTC
            point_timestamp = pd.to_datetime('now', utc=True)
        
        # Δημιουργία InfluxDB Point με τα νέα πεδία και το tag
        point = (
            Point("wind_speed")
            .tag("turbine", payload["turbine"])
            .field("speed", float(payload["speed"]))
            .field("direction", int(payload["direction"]))
            .field("power", float(payload["power"]))
            .time(point_timestamp)
        )
        
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        logging.info(f"Επιτυχής εγγραφή στην InfluxDB για τουρμπίνα {payload['turbine']}")

    except json.JSONDecodeError as e:
        logging.error(f"Σφάλμα JSON decoding: {e} - Payload: {msg.payload.decode()}")
    except KeyError as e:
        logging.error(f"Λείπει κλειδί στο JSON payload: {e} - Payload: {msg.payload.decode()}")
    except Exception as e:
        logging.error(f"Γενικό σφάλμα στην επεξεργασία μηνύματος: {e} - Payload: {msg.payload.decode()}") # Added payload to error for more context

def main():
    global client, write_api
    influx_client = InfluxDBClient(
        url=INFLUXDB_URL,
        token=INFLUXDB_TOKEN,
        org=INFLUXDB_ORG
    )
    write_api = influx_client.write_api(write_options=WriteOptions(batch_size=1))

    client = mqtt.Client(protocol=mqtt.MQTTv311)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = lambda client, userdata, rc: logging.warning(f"Αποσυνδέθηκε από broker με κωδικό: {rc}")

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        logging.error(f"Σφάλμα σύνδεσης με MQTT Broker: {e}")
        return

    client.loop_forever()

if __name__ == "__main__":
    main()