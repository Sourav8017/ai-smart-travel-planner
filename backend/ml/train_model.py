import os
import sqlite3
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# -----------------------------------------------------
# PATHS (ROBUST — WORKS EVERYWHERE)
# -----------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "instance", "travel.db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "travel_model.pkl")

print("🔄 Starting model retraining...")

# -----------------------------------------------------
# CHECK DATABASE
# -----------------------------------------------------
if not os.path.exists(DB_PATH):
    print("⚠️ Database file not found. Skipping retraining.")
    exit(0)

conn = sqlite3.connect(DB_PATH)

# -----------------------------------------------------
# LOAD TRAINING DATA (JOIN trip + feedback)
# -----------------------------------------------------
query = """
SELECT
    f.rating,
    t.budget,
    t.days,
    t.travel_type,
    f.liked
FROM feedback f
JOIN trip t ON f.trip_id = t.id
WHERE
    f.rating IS NOT NULL
    AND t.budget IS NOT NULL
    AND t.days IS NOT NULL
    AND t.travel_type IS NOT NULL
    AND f.liked IS NOT NULL
"""

df = pd.read_sql_query(query, conn)
conn.close()

if df.empty or len(df) < 5:
    print("⚠️ Not enough feedback data to retrain. Skipping.")
    exit(0)

print(f"📊 Training on {len(df)} feedback records")

# -----------------------------------------------------
# FEATURES / LABEL
# -----------------------------------------------------
X = df[["rating", "budget", "days", "travel_type"]]
y = df["liked"]

# -----------------------------------------------------
# PREPROCESSING
# -----------------------------------------------------
numeric_features = ["rating", "budget", "days"]
categorical_features = ["travel_type"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)

# -----------------------------------------------------
# MODEL
# -----------------------------------------------------
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42,
    class_weight="balanced"
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model),
    ]
)

# -----------------------------------------------------
# TRAIN
# -----------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipeline.fit(X_train, y_train)

# -----------------------------------------------------
# SAVE MODEL
# -----------------------------------------------------
joblib.dump(pipeline, MODEL_PATH)

print("✅ Model retrained and saved successfully")
print(f"📦 Model path: {MODEL_PATH}")
