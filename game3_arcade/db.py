"""Game 3 için yerel SQLite skor tabanı."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "arcade.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS skorlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            skor INTEGER NOT NULL,
            tarih TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
        """
    )
    conn.commit()
    conn.close()


def kaydet(isim, skor):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO skorlar (isim, skor) VALUES (?, ?)", (isim, skor))
    conn.commit()
    conn.close()


def liderlik(limit=15):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT isim, MAX(skor) as skor FROM skorlar GROUP BY isim ORDER BY skor DESC LIMIT ?",
                (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("Arcade db hazir")
