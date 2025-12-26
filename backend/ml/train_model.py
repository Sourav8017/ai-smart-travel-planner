import sqlite3
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report

# =====================================================
# CONFIG
# =====================================================
DB_PATH = "instance/travel.db"
MODEL_PATH = "ml/travel_model.pkl"

# =====================================================
# 1. SIMPLE SENTIMENT FUNCTION
# =====================================================
POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "nice",
    "love", "loved", "awesome", "perfect", "wonderful"
}

NEGATIVE_WORDS = {
    "bad", "poor", "worst", "terrible", "awful",
    "hate", "hated", "boring", "disappointed"
}


def get_sentiment(comment):
    if not comment:
        return 0

    text = comment.lower()
    pos = sum(word in text for word in POSITIVE_WORDS)
    neg = sum(word in text for word in NEGATIVE_WORDS)

    if pos > neg:
        return 1
    elif neg > pos:
        return -1
    else:
        return 0


# =====================================================
# 2. CONNECT TO DATABASE
# =====================================================
conn = sqlite3.connect(DB_PATH)

tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)
print("📦 Tables in DB:", tables["name"].tolist())

# =====================================================
# 3. DESTINATION POPULARITY
# =====================================================
popularity_query = """
SELECT
    t.destination,
    AVG(f.liked) AS destination_like_rate
FROM feedback f
JOIN trip t ON f.trip_id = t.id
WHERE f.liked IS NOT NULL
GROUP BY t.destination
"""

destination_popularity = pd.read_sql_query(popularity_query, conn)

# =====================================================
# 4. MAIN TRAINING DATA
# =====================================================
training_query = """
SELECT
    f.rating,
    f.comment,
    t.budget,
    t.days,
    t.travel_type,
    t.destination,
    f.liked
FROM feedback f
JOIN trip t ON f.trip_id = t.id
WHERE
    f.rating IS NOT NULL
    AND t.budget IS NOT NULL
    AND t.days IS NOT NULL
    AND t.travel_type IS NOT NULL
    AND t.destination IS NOT NULL
    AND f.liked IS NOT NULL
"""

df = pd.read_sql_query(training_query, conn)
conn.close()

print("✅ Raw training data:", df.shape)

if df.empty:
    raise ValueError("❌ No training data found. Add feedback before training.")

# =====================================================
# 5. SENTIMENT FEATURE
# =====================================================
df["comment_sentiment"] = df["comment"].apply(get_sentiment)

# =====================================================
# 6. MERGE DESTINATION POPULARITY
# =====================================================
df = df.merge(
    destination_popularity,
    on="destination",
    how="left"
)

df["destination_like_rate"].fillna(
    df["destination_like_rate"].mean(),
    inplace=True
)

print("✅ Training data after feature engineering:", df.shape)

# =====================================================
# 7. FEATURES & LABEL
# =====================================================
X = df[
    [
        "rating",
        "budget",
        "days",
        "travel_type",
        "destination_like_rate",
        "comment_sentiment"
    ]
]

y = df["liked"]

# =====================================================
# 8. PREPROCESSING
# (No scaling needed for RandomForest)
# =====================================================
categorical_features = ["travel_type"]
numeric_features = [
    "rating",
    "budget",
    "days",
    "destination_like_rate",
    "comment_sentiment"
]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", "passthrough", numeric_features),
    ]
)

# =====================================================
# 9. RANDOM FOREST MODEL
# =====================================================
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    min_samples_split=5,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", model)
    ]
)

# =====================================================
# 10. TRAIN / TEST SPLIT
# =====================================================
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# =====================================================
# 11. TRAIN MODEL
# =====================================================
pipeline.fit(X_train, y_train)

# =====================================================
# 12. EVALUATION
# =====================================================
y_pred = pipeline.predict(X_test)

print("\n🎯 Accuracy:", accuracy_score(y_test, y_pred))
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))

# =====================================================
# 13. SAVE MODEL
# =====================================================
joblib.dump(pipeline, MODEL_PATH)
print(f"\n💾 RandomForest model saved to {MODEL_PATH}")
