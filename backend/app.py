from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import random
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DB_NAME = "travel.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT,
            budget INTEGER,
            days INTEGER,
            travel_type TEXT,
            plan TEXT,
            confidence TEXT,
            feedback TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "AI Smart Travel Planner backend running"}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK"}), 200


@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    data = request.get_json()

    destination = data.get("destination")
    budget = data.get("budget")
    days = data.get("days")
    travel_type = data.get("travel_type")

    plans = [
        f"Explore {destination} with a {travel_type} focused itinerary.",
        f"Enjoy a {days}-day trip to {destination} within a budget of {budget}.",
        f"Discover food, culture, and attractions in {destination}."
    ]

    return jsonify({
        "plan": random.choice(plans),
        "confidence": random.choice(["baseline", "medium", "high"])
    })


@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback 
        (destination, budget, days, travel_type, plan, confidence, feedback, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("destination"),
        data.get("budget"),
        data.get("days"),
        data.get("travel_type"),
        data.get("plan"),
        data.get("confidence"),
        data.get("feedback"),
        datetime.now().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Feedback saved"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
