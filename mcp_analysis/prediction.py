# mcp_analysis/prediction.py
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def train_predictor(df: pd.DataFrame, feature_column: str, target_column: str):
    """
    Εκπαιδεύει ένα γραμμικό μοντέλο για πρόβλεψη ανέμου.
    :param df: DataFrame με τα δεδομένα
    :param feature_column: στήλη εισόδου (π.χ. wind_speed_10m)
    :param target_column: στήλη στόχος (π.χ. wind_speed_80m)
    :return: εκπαιδευμένο μοντέλο, ακρίβεια (R^2)
    """
    X = df[[feature_column]]
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)

    return model, score
