from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import joblib
import pandas as pd

# =====================================================
# APP SETUP
# =====================================================
app = Flask(__name__)
CORS(app)

DB_PATH = "instance/travel.db"
MODEL_PATH = "ml/travel_model.pkl"

model = joblib.load(MODEL_PATH)

# =====================================================
# ROOT
# =====================================================
@app.route("/", methods=["GET"])
def root():
    return jsonify({"status": "Backend running"}), 200


# =====================================================
# DESTINATION POPULARITY
# =====================================================
def get_destination_popularity(destination):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT AVG(f.liked)
        FROM feedback f
        JOIN trip t ON f.trip_id = t.id
        WHERE t.destination = ?
        """,
        (destination,)
    )

    result = cursor.fetchone()[0]
    conn.close()

    return result if result is not None else 0.5


# =====================================================
# FETCH TRIPS WITH FALLBACK LOGIC
# =====================================================
def fetch_candidate_trips(travel_type, budget, days):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1️⃣ STRICT MATCH
    cursor.execute(
        """
        SELECT id, destination, budget, days, travel_type
        FROM trip
        WHERE travel_type = ?
        AND budget <= ?
        AND days <= ?
        """,
        (travel_type, budget, days)
    )
    trips = cursor.fetchall()
    if trips:
        conn.close()
        return trips, "exact"

    # 2️⃣ RELAX BUDGET (20%)
    cursor.execute(
        """
        SELECT id, destination, budget, days, travel_type
        FROM trip
        WHERE travel_type = ?
        AND budget <= ?
        AND days <= ?
        """,
        (travel_type, int(budget * 1.2), days)
    )
    trips = cursor.fetchall()
    if trips:
        conn.close()
        return trips, "budget_relaxed"

    # 3️⃣ RELAX DAYS (+2)
    cursor.execute(
        """
        SELECT id, destination, budget, days, travel_type
        FROM trip
        WHERE travel_type = ?
        AND budget <= ?
        AND days <= ?
        """,
        (travel_type, int(budget * 1.2), days + 2)
    )
    trips = cursor.fetchall()
    if trips:
        conn.close()
        return trips, "days_relaxed"

    # 4️⃣ FINAL FALLBACK — POPULAR TRIPS
    cursor.execute(
        """
        SELECT t.id, t.destination, t.budget, t.days, t.travel_type
        FROM trip t
        LEFT JOIN feedback f ON f.trip_id = t.id
        WHERE t.travel_type = ?
        GROUP BY t.id
        ORDER BY AVG(f.liked) DESC
        LIMIT 5
        """,
        (travel_type,)
    )

    trips = cursor.fetchall()
    conn.close()
    return trips, "popular_fallback"


# =====================================================
# GENERATE PLAN
# =====================================================
@app.route("/generate-plan", methods=["POST"])
def generate_plan():
    data = request.get_json()

    budget = data.get("budget")
    days = data.get("days")
    travel_type = data.get("travel_type")

    if not all([budget, days, travel_type]):
        return jsonify({"error": "Missing input fields"}), 400

    trips, mode = fetch_candidate_trips(travel_type, budget, days)

    if not trips:
        return jsonify({"message": "No trips available"}), 404

    recommendations = []

    for trip in trips:
        trip_id, destination, budget, days, travel_type = trip

        popularity = get_destination_popularity(destination)

        X_input = pd.DataFrame([{
            "rating": 3,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "destination_like_rate": popularity,
            "comment_sentiment": 0
        }])

        prob = model.predict_proba(X_input)[0][1]

        recommendations.append({
            "trip_id": trip_id,
            "destination": destination,
            "budget": budget,
            "days": days,
            "travel_type": travel_type,
            "like_probability": round(float(prob), 3)
        })

    recommendations.sort(key=lambda x: x["like_probability"], reverse=True)

    return jsonify({
        "mode": mode,
        "recommendations": recommendations
    }), 200


# =====================================================
# FEEDBACK ENDPOINT
# =====================================================
@app.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()

    trip_id = data.get("trip_id")
    rating = data.get("rating")
    liked = data.get("liked")
    comment = data.get("comment", "")

    if trip_id is None or rating is None or liked is None:
        return jsonify({"error": "Missing feedback fields"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO feedback (trip_id, rating, liked, comment)
        VALUES (?, ?, ?, ?)
        """,
        (trip_id, rating, liked, comment)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Feedback stored"}), 201


# =====================================================
# RUN
# =====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
