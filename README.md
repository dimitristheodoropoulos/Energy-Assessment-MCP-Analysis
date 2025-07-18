# Energy-Assessment-MCP-Analysis

**Εργαλείο ανάλυσης Measure-Correlate-Predict (MCP) σε Python για την αξιολόγηση και πρόβλεψη αιολικών πόρων, με δυνατότητες συλλογής δεδομένων σε πραγματικό χρόνο μέσω MQTT.**

Το εργαλείο αυτό έχει σχεδιαστεί για να:
* Ανακτά δεδομένα ταχύτητας ανέμου από InfluxDB.
* Πραγματοποιεί ανάλυση συσχέτισης μεταξύ δεδομένων αναφοράς και δεδομένων της περιοχής ενδιαφέροντος.
* Εκπαιδεύει ένα γραμμικό μοντέλο παλινδρόμησης για την πρόβλεψη αιολικών πόρων.
* Οπτικοποιεί τα αποτελέσματα της ανάλυσης.
* Περιλαμβάνει ένα setup για την προσομοίωση δεδομένων ανέμου και τη μεταφορά τους σε InfluxDB μέσω MQTT.

Αυτό το project αναδεικνύει την ικανότητα χειρισμού, ανάλυσης και μοντελοποίησης δεδομένων αιολικής ενέργειας χρησιμοποιώντας open-source τεχνολογίες όπως Python, Docker, InfluxDB, Grafana και Mosquitto (MQTT broker).

---

## Δομή Φακέλων

* `analyses/`: Κατάλογος για την αποθήκευση πρόσθετων αναλύσεων ή αποτελεσμάτων που δεν είναι μέρος του κύριου workflow.
* `backend/`: Περιέχει τον κώδικα για την επικοινωνία με τη βάση δεδομένων (InfluxDB) και τις κύριες λειτουργίες ανάλυσης (MCP).
    * `backend/influx/`: InfluxDB client για ανάγνωση και εγγραφή δεδομένων.
    * `backend/analysis/`: Λογική της ανάλυσης MCP.
* `data/`: Κατάλογοι για την οργάνωση των δεδομένων.
    * `data/raw/`: Για αρχικά, μη επεξεργασμένα δεδομένα.
    * `data/processed/`: Για επεξεργασμένα δεδομένα.
    * `data/reference/`: Για δεδομένα αναφοράς (π.χ., από κοντινό μετεωρολογικό σταθμό).
* `data_simulator/`: Περιέχει scripts για την προσομοίωση δεδομένων ανέμου.
    * `data_simulator/simulate_wind_data.py`: Script προσομοίωσης και αποστολής δεδομένων μέσω MQTT.
* `docker/`: Περιέχει τα αρχεία Docker Compose για την εγκατάσταση και εκτέλεση των υπηρεσιών.
    * `docker-compose.yml`: Κεντρικό αρχείο ρύθμισης Docker Compose.
    * `docker/grafana/`: Αρχεία ρύθμισης για το Grafana.
    * `docker/influxdb/`: Αρχεία ρύθμισης για το InfluxDB.
    * `docker/mosquitto/`: Αρχεία ρύθμισης για τον Mosquitto MQTT broker.
    * `docker/mqtt-publisher/`: Dockerfile και κώδικας για την εφαρμογή που δημοσιεύει δεδομένα μέσω MQTT.
        * `docker/mqtt-publisher/app/publisher.py`: Κώδικας για τον publisher.
    * `docker/mqtt-to-influx/`: Dockerfile και κώδικας για την εφαρμογή που λαμβάνει δεδομένα MQTT και τα γράφει στο InfluxDB.
        * `docker/mqtt-to-influx/mqtt_to_influx.py`: Κώδικας για τον MQTT-to-InfluxDB bridge.
* `mcp_analysis/`: Περιέχει τις επαναχρησιμοποιήσιμες συναρτήσεις για την ανάλυση MCP.
    * `mcp_analysis/correlation.py`: Συναρτήσεις για ανάλυση συσχέτισης.
    * `mcp_analysis/prediction.py`: Συναρτήσεις για τη δημιουργία μοντέλων πρόβλεψης.
* `reports/`: Κατάλογος για την αποθήκευση αναφορών και παρουσιάσεων.
* `scripts/`: Βοηθητικά scripts για το setup και την εκτέλεση.
    * `scripts/01_download_data.py`: Ένα παράδειγμα script για λήψη δεδομένων.
    * `scripts/setup_env.sh`: Ένα script για την αρχική ρύθμιση του περιβάλλοντος.
* `venv/`: Το virtual environment του Python (αγνοείται από το Git).
* `mcp_scatter_plot.png`: Το παραγόμενο γράφημα της ανάλυσης MCP (θα δημιουργηθεί μετά την εκτέλεση).
* `requirements.txt`: Οι απαιτούμενες βιβλιοθήκες Python για το project.
* `README.md`: Αυτό το αρχείο.

## Setup & Εκτέλεση

### Προαπαιτούμενα

Βεβαιωθείτε ότι έχετε εγκαταστήσει τα παρακάτω στο σύστημά σας:
* **Docker** και **Docker Compose**: Για την εκτέλεση των υπηρεσιών βάσης δεδομένων και των MQTT microservices.
* **Python 3.12+**: Για την εκτέλεση των scripts ανάλυσης.

### Βήματα Εκτέλεσης

1.  **Κλωνοποίηση του Repository:**
    ```bash
    git clone [https://github.com/dimitristheodoropoulos/Energy-Assessment-MCP-Analysis.git](https://github.com/dimitristheodoropoulos/Energy-Assessment-MCP-Analysis.git)
    cd Energy-Assessment-MCP-Analysis
    ```

2.  **Εκκίνηση υπηρεσιών Docker (InfluxDB, Grafana, Mosquitto, MQTT Microservices):**
    Από τον κύριο φάκελο του project, εκτελέστε:
    ```bash
    docker-compose up -d
    ```
    Αυτό θα εκκινήσει:
    * **InfluxDB**: Βάση δεδομένων χρονοσειρών για την αποθήκευση των δεδομένων ανέμου.
    * **Grafana**: Πλατφόρμα οπτικοποίησης (προαιρετικά, προσβάσιμη στο `http://localhost:3000`).
    * **Mosquitto**: MQTT Broker για την επικοινωνία μεταξύ του publisher και του InfluxDB bridge.
    * **mqtt-publisher**: Docker service που προσομοιώνει και δημοσιεύει δεδομένα ανέμου σε ένα MQTT topic.
    * **mqtt-to-influx**: Docker service που λαμβάνει δεδομένα από το MQTT topic και τα γράφει στο InfluxDB.

    _Σημείωση: Περιμένετε λίγα λεπτά ώστε όλες οι υπηρεσίες να ξεκινήσουν πλήρως._

3.  **Εγκατάσταση Python Virtual Environment και Εξαρτήσεων:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Ροή Δεδομένων και Προσομοίωση:**
    Για να γεμίσετε το InfluxDB με δεδομένα για ανάλυση, υπάρχουν δύο κύριοι τρόποι:

    * **Μέσω Προσομοίωσης (MQTT pipeline):**
        Οι Docker υπηρεσίες `mqtt-publisher` και `mqtt-to-influx` θα πρέπει να τρέχουν (από το `docker-compose up -d`).
        Το `mqtt-publisher` στέλνει συνεχώς δεδομένα στον Mosquitto broker, και το `mqtt-to-influx` τα λαμβάνει και τα αποθηκεύει στο InfluxDB.
        Μπορείτε να δείτε τα logs αυτών των υπηρεσιών για να επιβεβαιώσετε τη ροή δεδομένων:
        ```bash
        docker-compose logs -f mqtt-publisher
        docker-compose logs -f mqtt-to-influx
        ```
        Αυτά τα δεδομένα θα αποθηκευτούν στο InfluxDB bucket "wind-data".

    * **Χειροκίνητη εισαγωγή/Χρήση υπαρχόντων δεδομένων:**
        Αν έχετε δικά σας δεδομένα (π.χ. CSV), μπορείτε να τα εισάγετε απευθείας στο InfluxDB χρησιμοποιώντας το InfluxDB UI (`http://localhost:8086`) ή ένα script.
        _Για την ανάλυση MCP, απαιτούνται δεδομένα για 't1' (περιοχή ενδιαφέροντος) και 'T2_ref' (αναφοράς) στο bucket "wind-data" του InfluxDB._

5.  **Εκτέλεση της ανάλυσης MCP:**
    Αφού τα δεδομένα έχουν εισαχθεί στο InfluxDB, μπορείτε να εκτελέσετε την ανάλυση.
    Από τον κύριο φάκελο του project, με το virtual environment ενεργοποιημένο, εκτελέστε:
    ```bash
    python -m backend.run_mcp
    ```

### Αποτελέσματα

* Το script θα εκτυπώσει στην κονσόλα τον συντελεστή συσχέτισης (Pearson), το R² του μοντέλου, τον συντελεστή κλίσης (slope) και τον σταθερό όρο (intercept) της γραμμικής παλινδρόμησης.
* Ένα γράφημα διασποράς (`mcp_scatter_plot.png`) θα αποθηκευτεί στον κύριο φάκελο του project, οπτικοποιώντας την σχέση μεταξύ των δεδομένων αναφοράς και των προβλέψεων.

```bash
# Παράδειγμα εξόδου κονσόλας από την ανάλυση MCP
Εκτέλεση MCP ανάλυσης για t1 έναντι T2_ref...
Ανάκτηση δεδομένων από ... έως ...
... (InfluxDB logs / μηνύματα) ...
INFO: Correlation coefficient (pearson): X.XX
INFO: Linear regression model trained successfully.
✅ Το γράφημα MCP αποθηκεύτηκε ως 'mcp_scatter_plot.png' στον κύριο φάκελο του project.
Συντελεστής συσχέτισης (pearson): X.XX
Μοντέλο γραμμικής παλινδρόμησης εκπαιδεύτηκε (R^2: X.XX)
Συντελεστής (slope): X.XX
Σταθερός όρος (intercept): X.XX
