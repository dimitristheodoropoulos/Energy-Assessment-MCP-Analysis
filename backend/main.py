import json
import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point

# Ρυθμίσεις InfluxDB 2.x
INFLUXDB_TOKEN = "admintoken"
INFLUXDB_ORG = "energy-org"
INFLUXDB_BUCKET = "wind-data"
INFLUXDB_URL = "http://localhost:8086"

# Σύνδεση στον InfluxDB client
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api()

# Callback για σύνδεση MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code {rc}")
    client.subscribe("wind/measurements")

# Callback για μήνυμα MQTT
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Received MQTT message: {payload}")

        # Δημιουργία σημείου μέτρησης για InfluxDB
        point = (
            Point("wind_power")
            .tag("turbine", payload.get("turbine_id", "t1"))
            .field("wind_speed", float(payload["speed"]))
            .field("power_output", float(payload["power"]))
            .field("direction", int(payload["direction"]))
        )

        # Γράψε στο InfluxDB
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
        print("Data written to InfluxDB.")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

# Δημιουργία MQTT client και εκκίνηση
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect("localhost", 1883, 60)
mqtt_client.loop_forever()
