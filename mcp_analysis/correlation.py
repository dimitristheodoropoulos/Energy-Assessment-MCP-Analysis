# mcp_analysis/correlation.py
import pandas as pd

def compute_correlations(df: pd.DataFrame, column1: str, column2: str, method: str = "pearson") -> float:
    """
    Υπολογίζει συντελεστή συσχέτισης μεταξύ δύο στηλών.
    :param df: DataFrame με τις τιμές
    :param column1: Πρώτη στήλη (π.χ. wind_speed_10m)
    :param column2: Δεύτερη στήλη (π.χ. wind_speed_80m)
    :param method: 'pearson' ή 'spearman'
    """
    return df[[column1, column2]].corr(method=method).iloc[0, 1]