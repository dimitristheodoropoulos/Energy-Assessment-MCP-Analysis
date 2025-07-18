# backend/run_mcp.py

import matplotlib
matplotlib.use('Agg') # Ορισμός του backend σε μη-διαδραστικό. ΠΡΕΠΕΙ ΝΑ ΕΙΝΑΙ ΣΤΗΝ ΑΡΧΗ
import matplotlib.pyplot as plt
import datetime
import pandas as pd # Προσθήκη import pandas
import numpy as np # Προσθήκη import numpy
from sklearn.linear_model import LinearRegression # Έχει ήδη γίνει import
from sklearn.metrics import r2_score # Έχει ήδη γίνει import
from backend.analysis.mcp import run_mcp # Σωστός import της run_mcp
import logging
import os
import sys

# Ρύθμιση του logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    short_term_turbine_id = "t1"
    long_term_ref_id = "T2_ref"

    end_time_dt = datetime.datetime.now(datetime.UTC)
    start_time_dt = end_time_dt - datetime.timedelta(hours=1) # Τελευταία 1 ώρα

    end_time = end_time_dt.isoformat().replace('+00:00', 'Z')
    start_time = start_time_dt.isoformat().replace('+00:00', 'Z')

    print(f"Εκτέλεση MCP ανάλυσης για {short_term_turbine_id} έναντι {long_term_ref_id}...")
    print(f"Ανάκτηση δεδομένων από {start_time} έως {end_time}...")
    
    # Η backend.analysis.mcp.run_mcp επιστρέφει μόνο model και df_merged
    output = run_mcp(short_term_turbine_id, long_term_ref_id, start_time, end_time)

    if output is None:
        print("❌ Η ανάλυση MCP απέτυχε. Ελέγξτε τα δεδομένα και το εύρος χρόνου.")
    else:
        # Αποδοχή μόνο 2 τιμών από το output
        model, df_merged = output

        # Ελέγχουμε αν έχουμε αρκετά δεδομένα για να προχωρήσουμε στη γραφική παράσταση και τους υπολογισμούς
        # Χρειαζόμαστε τουλάχιστον 2 σημεία για γραμμική παλινδρόμηση
        if df_merged.empty or len(df_merged) < 2:
            print("Δεν υπάρχουν αρκετά κοινά δεδομένα για την εκτέλεση της ανάλυσης MCP και τη δημιουργία γραφήματος.")
            print(f"Μέγεθος συγχωνευμένου DataFrame: {df_merged.shape}")
        else:
            X = df_merged[[f'speed_{short_term_turbine_id}']]
            y = df_merged[f'speed_{long_term_ref_id}']

            # Υπολογισμός συντελεστή συσχέτισης και R^2 εδώ, αφού έχουμε τα δεδομένα
            correlation_coefficient = df_merged.corr().loc[f'speed_{short_term_turbine_id}', f'speed_{long_term_ref_id}']
            y_pred = model.predict(X)
            r_squared = r2_score(y, y_pred)

            plt.figure(figsize=(8, 6))
            plt.scatter(X, y, label="Πραγματικές Τιμές (αναφορά)", alpha=0.5)
            plt.plot(X, y_pred, color="red", label="Πρόβλεψη (Linear Fit)")
            plt.xlabel(f"Ταχύτητα ανέμου ({short_term_turbine_id})")
            plt.ylabel(f"Ταχύτητα ανέμου ({long_term_ref_id})")
            plt.title("MCP Ανάλυση: Πρόβλεψη vs Πραγματικότητα")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            output_filename = "mcp_scatter_plot.png"
            plt.savefig(output_filename) # <-- Αυτό αποθηκεύει το γράφημα σε αρχείο
            print(f"✅ Το γράφημα MCP αποθηκεύτηκε ως '{output_filename}' στον κύριο φάκελο του project.")
            plt.close() # <-- Αυτό κλείνει το γράφημα και απελευθερώνει τη μνήμη
            # H γραμμή plt.show() ΑΦΑΙΡΕΘΗΚΕ ΕΔΩ

            # Εκτύπωση των αποτελεσμάτων του μοντέλου
            print(f"Συντελεστής συσχέτισης (pearson): {correlation_coefficient:.2f}")
            print(f"Μοντέλο γραμμικής παλινδρόμησης εκπαιδεύτηκε (R^2: {r_squared:.2f})")
            # Προσθήκη εκτύπωσης συντελεστή και σταθερού όρου
            print(f"Συντελεστής (slope): {model.coef_[0]:.2f}")
            print(f"Σταθερός όρος (intercept): {model.intercept_:.2f}")