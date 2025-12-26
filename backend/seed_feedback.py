import sqlite3

DB_PATH = "backend/instance/travel.db"

print("💬 Seeding minimal demo feedback...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------------------------------
# FETCH TRIP IDS (dynamic, safe)
# -----------------------------------------------------
cursor.execute("SELECT id, destination FROM trip;")
trips = cursor.fetchall()

trip_map = {destination: trip_id for trip_id, destination in trips}

# -----------------------------------------------------
# MINIMAL, REALISTIC FEEDBACK
# -----------------------------------------------------
feedback = [
    # Positive leisure feedback
    (trip_map["Manali"], 5, 1, "Amazing views and weather"),
    (trip_map["Goa"], 4, 1, "Great beaches and food"),
    (trip_map["Udaipur"], 4, 1, "Beautiful and peaceful"),
    (trip_map["Coorg"], 5, 1, "Very relaxing experience"),

    # Positive adventure feedback
    (trip_map["Rishikesh"], 5, 1, "Perfect for adventure sports"),
    (trip_map["Bir Billing"], 4, 1, "Paragliding was awesome"),
    (trip_map["Ladakh"], 5, 1, "Once in a lifetime experience"),

    # One realistic negative feedback
    (trip_map["Shimla"], 2, 0, "Too crowded during season")
]

cursor.executemany(
    """
    INSERT INTO feedback (trip_id, rating, liked, comment)
    VALUES (?, ?, ?, ?)
    """,
    feedback
)

conn.commit()
conn.close()

print(f"✅ Seeded {len(feedback)} feedback entries")
print("🧠 ML model now has realistic learning signals")
