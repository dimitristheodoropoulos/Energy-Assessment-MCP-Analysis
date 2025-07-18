# mqtt-to-influx/Dockerfile

FROM python:3.12-slim

WORKDIR /app

# ΑΛΛΑΓΗ ΕΔΩ: Αντιγράφουμε το requirements.txt από τον ριζικό φάκελο του project
COPY requirements.txt .

# Εγκαθιστούμε όλες τις εξαρτήσεις από αυτό το αρχείο
RUN pip install -r requirements.txt

# ΑΛΛΑΓΗ ΕΔΩ: Αντιγράφουμε το mqtt_to_influx.py από τη σωστή του διαδρομή
COPY docker/mqtt-to-influx/mqtt_to_influx.py .

CMD ["python", "mqtt_to_influx.py"]