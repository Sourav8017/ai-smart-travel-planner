import sqlite3

DB_PATH = "backend/instance/travel.db"

print("🌱 Seeding database with realistic trip data...")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------------------------------
# CLEAN EXISTING DATA (SAFE)
# -----------------------------------------------------
cursor.execute("DELETE FROM feedback;")
cursor.execute("DELETE FROM trip;")

# -----------------------------------------------------
# REALISTIC SEED TRIP DATA
# -----------------------------------------------------
trips = [
    # Leisure Trips
    ("Manali", 25000, 7, "leisure"),
    ("Shimla", 20000, 5, "leisure"),
    ("Goa", 30000, 6, "leisure"),
    ("Udaipur", 22000, 4, "leisure"),
    ("Jaipur", 18000, 3, "leisure"),
    ("Coorg", 24000, 5, "leisure"),
    ("Darjeeling", 26000, 6, "leisure"),

    # Adventure Trips
    ("Rishikesh", 18000, 4, "adventure"),
    ("Bir Billing", 20000, 4, "adventure"),
    ("Spiti Valley", 42000, 9, "adventure"),
    ("Ladakh", 48000, 10, "adventure"),
    ("Meghalaya", 35000, 8, "adventure"),
    ("Andaman", 55000, 7, "adventure")
]

cursor.executemany(
    """
    INSERT INTO trip (destination, budget, days, travel_type)
    VALUES (?, ?, ?, ?)
    """,
    trips
)

conn.commit()
conn.close()

print(f"✅ Seeded {len(trips)} trips successfully!")
print("🚀 Database is now clean, realistic, and demo-ready.")
