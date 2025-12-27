import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.join("instance", "travel.db")
os.makedirs("instance", exist_ok=True)

conn = sqlite3.connect(DB_PATH)
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
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS trip_days (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER,
    day INTEGER,
    morning TEXT,
    afternoon TEXT,
    evening TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER,
    rating INTEGER,
    liked INTEGER,
    comment TEXT,
    created_at TEXT,
    FOREIGN KEY (trip_id) REFERENCES trips(id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    interest TEXT,
    weight INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully")
