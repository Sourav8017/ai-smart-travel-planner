import sqlite3
import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

DB_PATH = "instance/travel.db"
MODEL_PATH = "ml/model.pkl"


def load_data():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT 
            f.rating,
            t.budget,
            t.days,
            t.travel_type,
            f.liked
        FROM feedback f
        JOIN trip t ON f.trip_id = t.id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def train_model(df):
    X = df[["rating", "budget", "days", "travel_type"]]
    y = df["liked"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), ["travel_type"]),
            ("num", "passthrough", ["rating", "budget", "days"]),
        ]
    )

    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"✅ Model accuracy: {acc:.2f}")

    return model


if __name__ == "__main__":
    print("🔹 Loading data...")
    df = load_data()

    if len(df) < 10:
        print("❌ Not enough data to train model (need ~10 feedback rows)")
        exit()

    print("🔹 Training ML model...")
    model = train_model(df)

    os.makedirs("ml", exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("🎉 Model trained and saved as ml/model.pkl")
