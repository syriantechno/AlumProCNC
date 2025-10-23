# frontend/window/profiles_db.py
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/profiles.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    company TEXT,
    width REAL,
    height REAL,
    sku TEXT,
    dxf_path TEXT,
    image_path TEXT,
    created_at TEXT
);
"""

class ProfilesDB:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as con:
            con.execute(SCHEMA)

    def add_profile(self, name, company, width, height, sku, dxf_path, image_path):
        with sqlite3.connect(self.db_path) as con:
            con.execute("""
                INSERT INTO profiles (name, company, width, height, sku, dxf_path, image_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, company, width, height, sku, dxf_path, image_path, datetime.now().isoformat()))
            con.commit()

    def list_profiles(self):
        with sqlite3.connect(self.db_path) as con:
            cur = con.cursor()
            cur.execute("SELECT id, name, company, width, height, sku, dxf_path, image_path FROM profiles ORDER BY id DESC")
            return cur.fetchall()

    def delete_profile(self, pid):
        with sqlite3.connect(self.db_path) as con:
            con.execute("DELETE FROM profiles WHERE id=?", (pid,))
            con.commit()
