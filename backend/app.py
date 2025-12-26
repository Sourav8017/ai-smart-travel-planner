from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import random
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

DB_PATH = "instance/travel.db"
MODEL_PATH = "ml/model.pkl"

model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
    print("✅ ML model loaded")
else:
    print("⚠️ ML model not found, using baseline confidence")


def get_conn():
    os.makedirs("instance", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trip (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT,
            budget INTEGER,
            days INTEGER,
            travel_type TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER,
            rating INTEGER,
            liked INTEGER,
            comment TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "message": "Backend running"})


@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    data = request.get_json()

    destination = data["destination"]
    budget = int(data["budget"])
    days = int(data["days"])
    travel_type = data["travel_type"]

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO trip (destination, budget, days, travel_type)
        VALUES (?, ?, ?, ?)
    """, (destination, budget, days, travel_type))

    trip_id = cur.lastrowid
    conn.commit()
    conn.close()

    confidence = "baseline"

    if model:
        sample_df = pd.DataFrame([{
            "rating": 3,
            "budget": budget,
            "days": days,
            "travel_type": travel_type
        }])

        prob = model.predict_proba(sample_df)[0][1]

        if prob > 0.7:
            confidence = "high"
        elif prob > 0.4:
            confidence = "medium"

    plans = [
        f"Explore {destination} with a {travel_type} plan",
        f"{days}-day {travel_type} trip to {destination} under budget {budget}",
        f"Discover food and culture in {destination}"
    ]

    return jsonify({
        "trip_id": trip_id,
        "plan": random.choice(plans),
        "confidence": confidence
    })


@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.get_json()

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO feedback (trip_id, rating, liked, comment)
        VALUES (?, ?, ?, ?)
    """, (
        data["trip_id"],
        data["rating"],
        data["liked"],
        data.get("comment", "")
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Feedback saved"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
