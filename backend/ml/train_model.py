import sqlite3
import pandas as pd
import joblib
import os
import sys

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

DB_PATH = "backend/instance/travel.db"
MODEL_PATH = "backend/ml/travel_model.pkl"

print("🔄 Starting model retraining...")

# =====================================================
# CHECK DB FILE
# =====================================================
if not os.path.exists(DB_PATH):
    print("⚠️ Database file not found. Skipping retraining.")
    sys.exit(0)

try:
    conn = sqlite3.connect(DB_PATH)

    query = """
    SELECT
        f.rating,
        t.budget,
        t.days,
        t.travel_type,
        COALESCE(AVG(f2.liked), 0.5) AS destination_like_rate,
        0 AS comment_sentiment,
        f.liked
    FROM feedback f
    JOIN trip t ON f.trip_id = t.id
    LEFT JOIN feedback f2 ON f2.trip_id = t.id
    WHERE f.rating IS NOT NULL
    AND f.liked IS NOT NULL
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

except Exception as e:
    print("⚠️ Error reading training data. Skipping retraining.")
    print("Reason:", e)
    sys.exit(0)

# =====================================================
# CHECK DATA SIZE
# =====================================================
if df.empty or len(df) < 5:
    print("⚠️ Not enough feedback data to retrain. Skipping.")
    sys.exit(0)

print(f"✅ Training on {len(df)} records")

# =====================================================
# PREPARE DATA
# =====================================================
X = df.drop("liked", axis=1)
y = df["liked"]

num_features = [
    "rating",
    "budget",
    "days",
    "destination_like_rate",
    "comment_sentiment"
]
cat_features = ["travel_type"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_features)
    ]
)

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=8,
    random_state=42
)

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", model)
])

# =====================================================
# TRAIN
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

pipeline.fit(X_train, y_train)

y_pred = pipeline.predict(X_test)

print("📊 Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# =====================================================
# SAVE MODEL
# =====================================================
joblib.dump(pipeline, MODEL_PATH)
print("💾 Model retrained and saved successfully")
