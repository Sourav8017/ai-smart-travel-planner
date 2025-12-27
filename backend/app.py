from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os
import random

# -------------------- APP SETUP --------------------

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(app.instance_path, "travel.db")
os.makedirs(app.instance_path, exist_ok=True)

# -------------------- DATABASE --------------------

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        destination TEXT,
        days INTEGER,
        budget TEXT,
        interests TEXT,
        source TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS trip_days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        day INTEGER,
        morning TEXT,
        afternoon TEXT,
        evening TEXT
    );

    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trip_id INTEGER,
        rating INTEGER,
        liked INTEGER,
        comment TEXT,
        created_at TEXT
    );

    CREATE TABLE IF NOT EXISTS user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        interest TEXT,
        weight INTEGER DEFAULT 1
    );
    """)

    conn.commit()
    conn.close()


init_db()

# -------------------- ACTIVITY POOL --------------------

ACTIVITY_POOL = {
    "beach": ["Relax at the beach", "Sunset walk", "Beachside café"],
    "food": ["Street food tour", "Local restaurant", "Food market"],
    "nature": ["Park visit", "Scenic viewpoint", "Nature trail"],
    "history": ["Museum visit", "Historic monument", "Heritage walk"],
    "shopping": ["Local market", "Souvenir shopping", "Mall visit"]
}

# -------------------- PREFERENCE LOGIC --------------------

def get_sorted_interests(user_id, fallback_interests):
    """
    Returns interests sorted by user preference weight
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT interest, weight
        FROM user_preferences
        WHERE user_id = ?
        ORDER BY weight DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return fallback_interests

    preferred = [row["interest"] for row in rows]

    # Add missing interests at the end
    for i in fallback_interests:
        if i not in preferred:
            preferred.append(i)

    return preferred

# -------------------- ITINERARY GENERATION --------------------

def generate_personalized_itinerary(days, interests):
    itinerary = []
    top_interest = interests[0]
    second_interest = interests[1] if len(interests) > 1 else interests[0]

    for day in range(1, days + 1):
        itinerary.append({
            "day": day,
            "morning": random.choice(ACTIVITY_POOL.get(top_interest, ["City tour"])),
            "afternoon": random.choice(ACTIVITY_POOL.get(second_interest, ["Local exploration"])),
            "evening": "Dinner and rest"
        })

    return itinerary

# -------------------- GENERATE ITINERARY --------------------

@app.route("/generate-itinerary", methods=["POST"])
def generate_itinerary():
    data = request.get_json()

    user_id = data.get("user_id", 1)
    destination = data.get("destination")
    days = int(data.get("days", 3))
    interests = data.get("interests", [])

    if not destination or not interests:
        return jsonify({"error": "Invalid input"}), 400

    # 🔥 APPLY LEARNING HERE
    sorted_interests = get_sorted_interests(user_id, interests)

    itinerary = generate_personalized_itinerary(days, sorted_interests)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO trips (user_id, destination, days, interests, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        destination,
        days,
        ",".join(sorted_interests),
        "learning-engine",
        datetime.utcnow().isoformat()
    ))

    trip_id = cursor.lastrowid

    for d in itinerary:
        cursor.execute("""
            INSERT INTO trip_days (trip_id, day, morning, afternoon, evening)
            VALUES (?, ?, ?, ?, ?)
        """, (
            trip_id,
            d["day"],
            d["morning"],
            d["afternoon"],
            d["evening"]
        ))

    conn.commit()
    conn.close()

    return jsonify({
        "trip_id": trip_id,
        "destination": destination,
        "days": days,
        "prioritized_interests": sorted_interests,
        "itinerary": itinerary
    }), 200

# -------------------- FEEDBACK --------------------

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()

    trip_id = data.get("trip_id")
    user_id = data.get("user_id", 1)
    rating = int(data.get("rating", 0))

    if not trip_id or rating < 1 or rating > 5:
        return jsonify({"error": "Invalid feedback"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT interests FROM trips WHERE id = ?", (trip_id,))
    trip = cursor.fetchone()

    if trip:
        interests = trip["interests"].split(",")

        for interest in interests:
            cursor.execute("""
                SELECT id, weight FROM user_preferences
                WHERE user_id = ? AND interest = ?
            """, (user_id, interest))

            row = cursor.fetchone()

            if row:
                cursor.execute("""
                    UPDATE user_preferences
                    SET weight = weight + ?
                    WHERE id = ?
                """, (rating, row["id"]))
            else:
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, interest, weight)
                    VALUES (?, ?, ?)
                """, (user_id, interest, rating))

    cursor.execute("""
        INSERT INTO feedback (trip_id, rating, liked, comment, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        trip_id,
        rating,
        1 if rating >= 4 else 0,
        "",
        datetime.utcnow().isoformat()
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Preferences updated successfully"}), 200

# -------------------- RUN --------------------

if __name__ == "__main__":
    app.run(debug=True)
