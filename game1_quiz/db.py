"""SQLite yardımcı modülü - oyuncu ve skorları saklar."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "stant_oyun.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sonuclar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            oyun TEXT NOT NULL,
            isim TEXT NOT NULL,
            skor INTEGER NOT NULL,
            tarih TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )
        """
    )
    conn.commit()
    conn.close()


def kaydet(oyun, isim, skor):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sonuclar (oyun, isim, skor) VALUES (?, ?, ?)",
        (oyun, isim, skor),
    )
    conn.commit()
    conn.close()


def liderlik(oyun=None, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if oyun:
        cur.execute(
            "SELECT isim, skor, tarih FROM sonuclar WHERE oyun=? ORDER BY skor DESC LIMIT ?",
            (oyun, limit),
        )
    else:
        cur.execute(
            "SELECT isim, skor, tarih, oyun FROM sonuclar ORDER BY skor DESC LIMIT ?",
            (limit,),
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def en_iyi(oyun, limit=10):
    """Belirli oyun için en yüksek skorlu oyuncuları döndürür."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT isim, MAX(skor) as skor FROM sonuclar WHERE oyun=? GROUP BY isim ORDER BY skor DESC LIMIT ?",
        (oyun, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("Veritabanı hazır:", DB_PATH)
