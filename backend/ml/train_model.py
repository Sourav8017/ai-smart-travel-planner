import pandas as pd
from sklearn.linear_model import LogisticRegression
import joblib
import sqlite3

# Connect to SQLite DB
conn = sqlite3.connect("instance/travel.db")

# Read feedback + trips
query = """
SELECT t.budget, t.interests, f.rating, f.liked
FROM trip t
JOIN feedback f ON t.id = f.trip_id
"""
df = pd.read_sql(query, conn)

conn.close()

if df.empty:
    print("❌ Not enough data to train")
    exit()

# Simple feature encoding
df["liked"] = df["liked"].astype(int)
df["rating"] = df["rating"].astype(int)

X = df[["rating"]]
y = df["liked"]

model = LogisticRegression()
model.fit(X, y)

joblib.dump(model, "ml/travel_model.pkl")
print("✅ Model trained and saved")
