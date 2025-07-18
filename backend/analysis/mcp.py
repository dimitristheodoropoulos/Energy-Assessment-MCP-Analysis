# backend/analysis/mcp.py

import pandas as pd
from backend.influx.influx_client import InfluxClient
from mcp_analysis.correlation import compute_correlations
from mcp_analysis.prediction import train_predictor # Αυτή η συνάρτηση διορθώνεται η κλήση της
from typing import Union
import logging

logger = logging.getLogger(__name__)

def run_mcp(short_term_turbine_id: str, long_term_ref_id: str,
            start_time: str, end_time: str,
            correlation_method: str = "pearson") -> Union[tuple, None]:
    """
    Performs MCP (Measure-Correlate-Predict) analysis.
    """
    logger.info(f"Starting MCP analysis for {short_term_turbine_id} vs {long_term_ref_id} from {start_time} to {end_time}")

    client = InfluxClient()
    try:
        short_term_data = client.get_wind_speed_data(short_term_turbine_id, start_time, end_time)
        long_term_data = client.get_wind_speed_data(long_term_ref_id, start_time, end_time)

        if short_term_data.empty or long_term_data.empty:
            logger.warning("One or both DataFrames are empty. Cannot perform MCP analysis.")
            return None

        short_term_data = short_term_data.rename(columns={'speed': f'speed_{short_term_turbine_id}'})
        long_term_data = long_term_data.rename(columns={'speed': f'speed_{long_term_ref_id}'})

        df_merged = pd.merge(short_term_data, long_term_data, left_index=True, right_index=True, how='inner')

        if df_merged.empty:
            logger.warning("No common data points found after merging. Cannot perform MCP analysis.")
            return None

        # Υπολογισμός συσχέτισης
        correlation_coefficient = compute_correlations(
            df=df_merged,
            column1=f'speed_{short_term_turbine_id}',
            column2=f'speed_{long_term_ref_id}',
            method=correlation_method
        )
        logger.info(f"Correlation coefficient ({correlation_method}): {correlation_coefficient:.2f}")

        # Για την εκπαίδευση του μοντέλου
        # Η train_predictor αναμένει το πλήρες DataFrame και τα ονόματα των στηλών ως strings.
        # Επίσης, η train_predictor επιστρέφει (model, score), αλλά το score το υπολογίζει
        # ξανά το run_mcp.py, οπότε μπορούμε να το αγνοήσουμε εδώ με _.
        
        # ΔΙΟΡΘΩΣΗ: Καλούμε την train_predictor με το df_merged και τα ονόματα των στηλών
        model, _ = train_predictor(
            df=df_merged,
            feature_column=f'speed_{short_term_turbine_id}',
            target_column=f'speed_{long_term_ref_id}'
        )
        logger.info("Linear regression model trained successfully.")

        # Ελέγχουμε ξανά αν έχουμε αρκετά δεδομένα για τη γραμμική παλινδρόμηση
        # (αυτός ο έλεγχος γίνεται και στην train_predictor εσωτερικά, αλλά είναι καλό να υπάρχει και εδώ)
        if len(df_merged) < 2:
            logger.warning(f"Not enough data points ({len(df_merged)}) for training the linear regression model.")
            return None

        return model, df_merged

    except Exception as e:
        logger.error(f"An error occurred during MCP analysis: {e}")
        return None
    finally:
        client.close()