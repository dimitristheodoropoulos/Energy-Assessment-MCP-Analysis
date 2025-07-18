# backend/influx/influx_client.py

from influxdb_client import InfluxDBClient
import pandas as pd
import datetime

# Assume these are configured elsewhere or passed
INFLUXDB_URL = "http://localhost:8086"
INFLUXDB_TOKEN = "admintoken"
INFLUXDB_ORG = "energy-org"
INFLUXDB_BUCKET = "wind-data"

class InfluxClient:
    def __init__(self, url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG, bucket=INFLUXDB_BUCKET):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.query_api = self.client.query_api()
        self.bucket = bucket
        self.org = org

    def get_wind_speed_data(self, turbine_id: str, start_time: str, stop_time: str) -> pd.DataFrame:
        """
        Ανακτά δεδομένα ταχύτητας ανέμου ('speed') για μια συγκεκριμένη τουρμπίνα/τοποθεσία
        εντός ενός εύρους χρόνου.
        """
        # ΑΛΛΑΓΗ ΕΔΩ: Αφαίρεση του pivot από το Flux query
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: time(v: "{start_time}"), stop: time(v: "{stop_time}"))
          |> filter(fn: (r) => r._measurement == "wind_speed")
          |> filter(fn: (r) => r.turbine == "{turbine_id}")
          |> filter(fn: (r) => r._field == "speed")
          |> keep(columns: ["_time", "_value", "turbine"])
        '''
        
        print(f"\n--- InfluxClient: Executing query for {turbine_id} ---")
        print(f"Query:\n{query}")

        tables = self.query_api.query(query, org=self.org)
        
        print(f"Raw query results (tables object) for {turbine_id}: {tables}")
        if not tables:
            print(f"InfluxClient: No tables returned for {turbine_id} from the query.")
            return pd.DataFrame()


        data = []
        for table in tables:
            print(f"InfluxClient: Processing table: {table.get_group_key()}")
            for record in table.records:
                # Συλλέγουμε μόνο _time και _value, αφού το turbine_id είναι ήδη γνωστό από το φίλτρο
                data.append({"_time": record.get_time(), "speed": record.get_value()}) # ΑΛΛΑΓΗ ΕΔΩ: Ονομάζουμε τη στήλη 'speed' απευθείας

        if not data:
            print(f"InfluxClient: No data extracted into list for {turbine_id}.")
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df = df.set_index("_time") # ΑΛΛΑΓΗ ΕΔΩ: Ορίζουμε το _time ως index
        df.index = pd.to_datetime(df.index) # Μετατροπή index σε datetime objects
        
        print(f"InfluxClient: Final DataFrame for {turbine_id} before return:\n{df.head()}")
        print(f"InfluxClient: Columns for {turbine_id}: {df.columns.tolist()}")
        
        # Εδώ δεν χρειάζεται πλέον το rename ή ο έλεγχος turbine_id in df.columns
        # επειδή έχουμε ήδη ονομάσει τη στήλη "speed"
        return df[['speed']]


    def write_mcp_prediction(self, timestamp: pd.Timestamp, turbine_id: str, predicted_speed: float):
        write_api = self.client.write_api()
        point = {
            "measurement": "mcp_predictions",
            "tags": {"turbine": turbine_id},
            "fields": {"predicted_wind_speed": predicted_speed},
            "time": timestamp
        }
        write_api.write(bucket=self.bucket, org=self.org, record=point)
        write_api.close()

    def close(self):
        self.client.close()

# Example usage (for testing)
if __name__ == "__main__":
    client = InfluxClient()
    
    end_time_dt = datetime.datetime.now(datetime.UTC)
    start_time_dt = end_time_dt - datetime.timedelta(hours=24) # Test with 24 hours
    end_time = end_time_dt.isoformat().replace('+00:00', 'Z')
    start_time = start_time_dt.isoformat().replace('+00:00', 'Z')

    print(f"\n--- Running InfluxClient.py Test Block ---")
    print(f"Testing get_wind_speed_data for t1 from {start_time} to {end_time}")
    df_t1 = client.get_wind_speed_data("t1", start_time, end_time)
    print(f"Resulting DataFrame for t1:\n{df_t1.head()}")
    print(f"Shape for t1: {df_t1.shape}")
    
    print(f"\nTesting get_wind_speed_data for T2_ref from {start_time} to {end_time}")
    df_t2_ref = client.get_wind_speed_data("T2_ref", start_time, end_time)
    print(f"Resulting DataFrame for T2_ref:\n{df_t2_ref.head()}")
    print(f"Shape for T2_ref: {df_t2_ref.shape}")

    client.close()
    print(f"\n--- InfluxClient.py Test Block Finished ---")