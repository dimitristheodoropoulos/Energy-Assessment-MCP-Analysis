# Energy-Assessment-MCP-Analysis

Εργαλείο ανάλυσης Measure-Correlate-Predict (MCP) σε Python για την αξιολόγηση και πρόβλεψη αιολικών πόρων.
Το εργαλείο ανακτά δεδομένα ταχύτητας ανέμου από InfluxDB, πραγματοποιεί ανάλυση συσχέτισης, εκπαιδεύει ένα γραμμικό μοντέλο παλινδρόμησης και οπτικοποιεί τα αποτελέσματα.
Αυτό το project αποδεικνύει την ικανότητα χειρισμού, ανάλυσης και μοντελοποίησης δεδομένων αιολικής ενέργειας χρησιμοποιώντας open-source τεχνολογίες.

---

**Περιγραφή Project (Αρχική δομή)**
Workflow για πλήρη αξιολόγηση αιολικού δυναμικού.

**Δομή Φακέλων**
- `backend/`: Περιέχει τον κώδικα για την επικοινωνία με τη βάση δεδομένων (InfluxDB) και τις κύριες λειτουργίες ανάλυσης (MCP).
    - `backend/influx/`: InfluxDB client.
    - `backend/analysis/`: Λογική ανάλυσης.
- `mcp_analysis/`: Περιέχει τις επαναχρησιμοποιήσιμες συναρτήσεις για την ανάλυση MCP (correlation, prediction).
- `docker/`: Περιέχει τα αρχεία Docker Compose για την εγκατάσταση και εκτέλεση του InfluxDB και του Grafana.
- `venv/`: Το virtual environment του Python.
- `mcp_scatter_plot.png`: Το παραγόμενο γράφημα της ανάλυσης MCP.
- `requirements.txt`: Οι απαιτούμενες βιβλιοθήκες Python.
- `README.md`: Αυτό το αρχείο.

**Setup & Εκτέλεση**

1.  **Εγκατάσταση Docker και Docker Compose:** Βεβαιωθείτε ότι έχετε εγκαταστήσει το Docker και το Docker Compose στο σύστημά σας.

2.  **Εκκίνηση υπηρεσιών βάσης δεδομένων (InfluxDB & Grafana):**
    Από τον κύριο φάκελο του project, εκτελέστε:
    ```bash
    docker-compose up -d
    ```
    Αυτό θα εκκινήσει το InfluxDB (για την αποθήκευση δεδομένων) και το Grafana (για οπτικοποίηση, προαιρετικά).

3.  **Εγκατάσταση Python Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4.  **Εισαγωγή Δεδομένων (Δείγμα):**
    Θα χρειαστεί να εισάγετε κάποια δείγματα δεδομένων στο InfluxDB. Μπορείτε να χρησιμοποιήσετε ένα script εισαγωγής δεδομένων ή να το κάνετε χειροκίνητα μέσω του InfluxDB UI.
    _Σημείωση: Στο project αυτό, υποθέτουμε ότι τα δεδομένα για 't1' και 'T2_ref' υπάρχουν ήδη στο bucket "wind-data" του InfluxDB._

5.  **Εκτέλεση της ανάλυσης MCP:**
    Από τον κύριο φάκελο του project, με το virtual environment ενεργοποιημένο, εκτελέστε:
    ```bash
    python -m backend.run_mcp
    ```

**Αποτελέσματα:**

* Το script θα εκτυπώσει στην κονσόλα τον συντελεστή συσχέτισης, το R^2 του μοντέλου, τον συντελεστή κλίσης (slope) και τον σταθερό όρο (intercept) της γραμμικής παλινδρόμησης.
* Ένα γράφημα διασποράς (`mcp_scatter_plot.png`) θα αποθηκευτεί στον κύριο φάκελο του project, οπτικοποιώντας την σχέση μεταξύ των δεδομένων αναφοράς και των προβλέψεων.

```bash
# Παράδειγμα εξόδου
Εκτέλεση MCP ανάλυσης για t1 έναντι T2_ref...
Ανάκτηση δεδομένων από ... έως ...
... (InfluxDB logs) ...
INFO: Correlation coefficient (pearson): X.XX
INFO: Linear regression model trained successfully.
✅ Το γράφημα MCP αποθηκεύτηκε ως 'mcp_scatter_plot.png' στον κύριο φάκελο του project.
Συντελεστής συσχέτισης (pearson): X.XX
Μοντέλο γραμμικής παλινδρόμησης εκπαιδεύτηκε (R^2: X.XX)
Συντελεστής (slope): X.XX
Σταθερός όρος (intercept): X.XX