import sqlite3
from datetime import datetime
import os

DB_FILE = "pdf_catalogue.db"

# Ensure folders if needed
os.makedirs("data", exist_ok=True)

# --- CONNECTION SETUP ---
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

# --- INITIAL SETUP ---
def initialize_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdfs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            category TEXT,
            subcategory TEXT,
            language TEXT,
            file_hash TEXT,
            date_added TEXT,
            message_id INTEGER,
            channel_id INTEGER,
            user_id INTEGER,
            username TEXT
        )
    ''')
    conn.commit()

    # Check if `subcategory` column exists (for older DBs)
    try:
        cursor.execute('ALTER TABLE pdfs ADD COLUMN subcategory TEXT')
        conn.commit()
        print("[DB] Added missing subcategory column.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" not in str(e):
            print("[DB] Warning:", e)

# --- SAFE WRAPPER ---
def commit():
    conn.commit()

def close():
    conn.close()

# Optionally: function to insert PDFs (clean interface)
def insert_pdf(data: dict):
    cursor.execute("""
        INSERT INTO pdfs (
            title, author, category, subcategory, language,
            file_hash, date_added, message_id, channel_id, user_id, username
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["title"], data["author"], data["category"], data["subcategory"], data["language"],
        data["file_hash"], datetime.utcnow().isoformat(), data["message_id"],
        data["channel_id"], data["user_id"], data["username"]
    ))
    conn.commit()

# Run this immediately on import
initialize_tables()
