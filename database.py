import sqlite3
from datetime import datetime
from typing import Optional

DB = "fichee.db"

def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id INTEGER PRIMARY KEY,
            username TEXT,
            language TEXT DEFAULT 'en',
            subscribed INTEGER DEFAULT 0,
            joined_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            action TEXT,
            ts TEXT
        )
    """)
    con.commit()
    con.close()

def upsert_user(chat_id: int, username: str = ""):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT chat_id FROM users WHERE chat_id=?", (chat_id,))
    if cur.fetchone():
        cur.execute("UPDATE users SET username=? WHERE chat_id=?", (username, chat_id))
    else:
        cur.execute(
            "INSERT INTO users (chat_id, username, joined_at) VALUES (?,?,?)",
            (chat_id, username, datetime.now().isoformat())
        )
    con.commit()
    con.close()

def set_language(chat_id: int, lang: str):
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("UPDATE users SET language=? WHERE chat_id=?", (lang, chat_id))
    con.commit()
    con.close()

def get_language(chat_id: int) -> str:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT language FROM users WHERE chat_id=?", (chat_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row else 'en'

def toggle_subscription(chat_id: int) -> bool:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT subscribed FROM users WHERE chat_id=?", (chat_id,))
    row = cur.fetchone()
    new = 0 if (row and row[0]) else 1
    cur.execute("UPDATE users SET subscribed=? WHERE chat_id=?", (new, chat_id))
    con.commit()
    con.close()
    return bool(new)

def get_subscribers() -> list:
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("SELECT chat_id FROM users WHERE subscribed=1")
    rows = [r[0] for r in cur.fetchall()]
    con.close()
    return rows
