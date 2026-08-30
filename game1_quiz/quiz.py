"""UYT Stant Oyunu 1 - İnteraktif Bilgi Yarışması (Tek Oyuncu, Türkçe, Canlı Tasarım).
Özellikler:
  - Tek oyuncu mod: tek isim girişi
  - Canlı sorular: OpenTDB'den Türkçe dilinde anlık sorular
  - 10 soru, 4 seçenek, 2 dakika süre
  - Yanlışta süre 15 sn kısalır, doğruda +10 puan
  - SQLite ile skor kaydı ve liderlik tablosu
  - Oyun bittiğinde otomatik olarak yeni soru seti yükler (sürekli çalışma)
"""
import os
import sys
import html
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from io import BytesIO

import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont

import db as db_mod

API = "https://opentdb.com/api.php"
API_PARAMS = {"type": "multiple", "language": "tr"}  # Türkçe sorular için language=tr
IMG_CACHE = os.path.join(os.path.dirname(__file__), "img_cache")
os.makedirs(IMG_CACHE, exist_ok=True)

# UYT renk paleti - canlı ve dikkat çekici
BG = "#0d1b2a"        # Ana arka plan (dark navy)
PANEL = "#1b263b"     # Panel/frame arka planı
ACCENT = "#e63946"    # Kırmızı emphasize (UYT kırmızısı)
ACCENT2 = "#f4a261"   # Turuncu emphasize (canlı/yönelici)
LIGHT = "#e0e1dd"     # Açık yazı arka planı
WHITE = "#ffffff"     # Beyaz tekst

# Soru kategorisi -> resim anahtar kelimesi (loremflickr)
KATEGORI_RESIM = {
    "General Knowledge": "knowledge",
    "Entertainment: Books": "book",
    "Entertainment: Film": "movie",
    "Entertainment: Music": "music",
    "Entertainment: Musicals & Theatres": "theatre",
    "Entertainment: Television": "television",
    "Entertainment: Video Games": "videogame",
    "Entertainment: Board Games": "boardgame",
    "Science & Nature": "science",
    "Science: Computers": "computer",
    "Science: Mathematics": "mathematics",
    "Mythology": "mythology",
    "Sports": "sport",
    "Geography": "geography",
    "History": "history",
    "Politics": "politics",
    "Art": "art",
    "Celebrities": "celebrity",
    "Animals": "animal",
    "Vehicles": "vehicle",
}


def fetch_questions(n, used_ids):
    """OpenTDB'den Türkçe dilinde n adet benzersiz soru çeker."""
    sorular = []
    deneme = 0
    while len(sorular) < n and deneme < 30:
        deneme += 1
        try:
            # language=tr parametresiyle Türkçe sorular iste
            r = requests.get(API, params={"amount": 50, "type": "multiple", "language": "tr"}, timeout=10)
            data = r.json()
        except Exception:
            continue
        if data.get("response_code") != 0:
            continue
        for q in data.get("results", []):
            qid = q.get("question", "")[:60] + q.get("correct_answer", "")[:20]
            if qid in used_ids:
                continue
            used_ids.add(qid)
            sorular.append(q)
            if len(sorular) >= n:
                break
    return sorular


class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UYT - Bilgi Yarışması")
        self.root.configure(bg=BG)
        self.root.geometry("1000x720")
        self.root.minsize(800, 600)
        self.root.resizable(True, True)

        self.player_name = ""          # Tek oyuncu ismi
        self.scores = 0
        self.questions = []            # Tek oyuncu için soru listesi
        self.used_ids = set()
        self.cur_q = 0
        self.remaining = 120
        self.timer_job = None
        self.round_count = 0           # Kaç tur oynandığını takip
        self._build_styles()

        db_mod.init_db()
        self.show_start()

    # ---------- stil ----------
    def _build_styles(self):
        try:
            self.root.tk.call("source", "azure.tcl")
        except Exception:
            pass

    # ---------- ana başlangıç ekranı (tek oyuncu) ----------
    def show_start(self):
        self._clear()
        self.player_name = ""
        self.round_count = 0
        self.scores = 0
        self.questions = []
        self.used_ids = set()
        self.cur_q = 0
        self.remaining = 120

        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True, fill="both", padx=40, pady=30)

        # UYT logo-like dekoratif başlık
        tk.Label(f, text="🏓 UYT BİLGİ YARIŞMASI", font=("Segoe UI", 32, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(10, 5))
        tk.Label(f, text="Tek Oyuncu Mod - İnternetten Türkçe Sorular",
                 font=("Segoe UI", 14), fg=LIGHT, bg=BG).pack(pady=(0, 20))

        # Oyuncu ismi girişi
        tk.Label(f, text="Adınızı giriniz:", font=("Segoe UI", 16), fg=WHITE, bg=BG).pack(anchor="w")
        entry = tk.Entry(f, font=("Segoe UI", 16), bg=PANEL, fg=WHITE,
                         insertbackground=WHITE, relief="flat", justify="center")
        entry.pack(ipady=10, pady=6, fill="x", padx=100)
        entry.focus()

        def start_game():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Uyarı", "Lütfen bir isim girin.")
                return
            self.player_name = name
            self._clear()
            self.prepare_game()

        btn = tk.Button(f, text="✅ TAMAM BAŞLAT", command=start_game, bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 16, "bold"), relief="flat", padx=30, pady=12)
        btn.pack(pady=20)

        # İpucu
        

    # ---------- OYUN HAZIRLIĞI ----------
    def prepare_game(self):
        self._clear()
        loading = tk.Label(self.root, text="Sorular internetten çekiliyor...\nLütfen bekleyin",
                           font=("Segoe UI", 18), fg=LIGHT, bg=BG)
        loading.pack(expand=True)

        def work():
            pool = fetch_questions(10, self.used_ids)  # 10 Türkçe soru
            if not pool:
                self.root.after(0, lambda: messagebox.showerror(
                    "Hata", "İnternetten soru alınamadı. Bağlantıyı kontrol edin."))
                self.root.after(0, self.show_start)
                return
            random.shuffle(pool)
            self.questions = pool
            self.scores = 0
            self.cur_q = 0
            self.remaining = 120
            self.round_count = 1
            self.root.after(0, self.start_round)

        threading.Thread(target=work, daemon=True).start()

    # ---------- TUR BAŞI ----------
    def start_round(self):
        # Tur başlangıcı: timer sıfırla, soruyu göster
        self.show_question()

    def show_question(self):
        self._clear()
        if self.cur_q >= len(self.questions):
            self.finished_round()
            return

        q = self.questions[self.cur_q]

        # ÜST BAR - canlı tasarım
        top = tk.Frame(self.root, bg=PANEL, height=60)
        top.pack(fill="x", padx=0, pady=0)
        top.configure(highlightthickness=0)
        # Renge geçişli efekt simülasyonu için renkler
        top_bg = PANEL

        self.timer_lbl = tk.Label(top, text=f"⏱ {self.remaining:02d}:00",
                                  font=("Segoe UI", 20, "bold"), fg=ACCENT2, bg=top_bg)
        self.timer_lbl.pack(side="left", padx=20, pady=8)

        # Round info
        prog = tk.Label(top, text=f"Tur {self.round_count} - Soru {self.cur_q + 1}/10",
                        font=("Segoe UI", 13), fg=LIGHT, bg=top_bg)
        prog.pack(side="right", padx=20, pady=8)

        # Oyuncu ismi
        name_lbl = tk.Label(top, text=f"👤 {self.player_name}  |  Puan: {self.scores}",
                            font=("Segoe UI", 14, "bold"), fg=WHITE, bg=top_bg)
        name_lbl.pack(side="right", padx=100, pady=8)

        # ORTA: RESİM + SORU
        mid = tk.Frame(self.root, bg=BG, padx=30, pady=10)
        mid.pack(expand=True, fill="both")

        img_frame = tk.Frame(mid, bg=PANEL, relief="ridge", bd=2)
        img_frame.pack(pady=(0, 12))
        self.img_lbl = tk.Label(img_frame, bg=PANEL, width=70, height=18)
        self.img_lbl.pack(padx=4, pady=4)

        qtext = html.unescape(q["question"])
        qlbl = tk.Label(mid, text=qtext, font=("Segoe UI", 17, "bold"), fg=WHITE,
                        bg=BG, wraplength=820, justify="center")
        qlbl.pack(pady=(6, 14), fill="x")

        # SEÇENEKLER
        answers = [html.unescape(q["correct_answer"])] + [html.unescape(a) for a in q["incorrect_answers"]]
        random.shuffle(answers)
        opts = tk.Frame(self.root, bg=BG)
        opts.pack(fill="x", padx=60, pady=(0, 20))
        opts.columnconfigure(0, weight=1)
        opts.columnconfigure(1, weight=1)

        cat = q.get("category", "")
        keyword = KATEGORI_RESIM.get(cat, "quiz")
        qid = q.get("question", "")[:50]
        self._schedule_image(qid, keyword)

        def make_handler(chosen):
            return lambda: self.answer(chosen, q["correct_answer"])

        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for (chosen, pos) in zip(answers, positions):
            b = tk.Button(opts, text=chosen, command=make_handler(chosen),
                          bg=PANEL, fg=WHITE, font=("Segoe UI", 13),
                          relief="flat", wraplength=380, height=2,
                          activebackground=ACCENT2)
            b.grid(row=pos[0], column=pos[1], padx=8, pady=8, sticky="nsew")

        self.start_timer()

    def _schedule_image(self, qid, keyword):
        path = os.path.join(IMG_CACHE, f"{abs(hash(qid)) % 100000}.jpg")
        if os.path.exists(path):
            self._set_image(path)
            return

        def work():
            try:
                r = requests.get(f"https://loremflickr.com/600/400/{keyword}?lock={abs(hash(qid)) % 1000}",
                                 timeout=6)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    self.root.after(0, lambda: self._set_image(path))
                    return
            except Exception:
                pass
            self.root.after(0, lambda: self._set_fallback(keyword))

        threading.Thread(target=work, daemon=True).start()

    def _set_image(self, path):
        try:
            img = Image.open(path).convert("RGB")
            img = img.resize((560, 320), Image.LANCZOS)
            self._imgtk = ImageTk.PhotoImage(img)
            self.img_lbl.configure(image=self._imgtk, text="")
        except Exception:
            pass

    def _set_fallback(self, keyword):
        try:
            img = Image.new("RGB", (560, 320), PANEL[1:] if PANEL.startswith("#") else "1b263b")
            d = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 22)
            except Exception:
                font = ImageFont.load_default()
            d.text((280, 130), keyword.upper(), fill="f4a261", font=font, anchor="mm")
            d.text((280, 175), "gorsel yuklenemedi", fill="e0e1dd", font=font, anchor="mm")
            self._imgtk = ImageTk.PhotoImage(img)
            self.img_lbl.configure(image=self._imgtk, text="")
        except Exception:
            pass

    def start_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self._tick()

    def _tick(self):
        if self.remaining <= 0:
            self.finished_round()
            return
        m, s = divmod(self.remaining, 60)
        self.timer_lbl.configure(text=f"⏱ {m:02d}:{s:02d}")
        # Süre azalırken renk değişimi (gerilim effectively)
        if self.remaining <= 15:
            self.timer_lbl.configure(fg=ACCENT)
        elif self.remaining <= 30:
            self.timer_lbl.configure(fg=ACCENT2)
        self.remaining -= 1
        self.timer_job = self.root.after(1000, self._tick)

    def answer(self, chosen, correct):
        if html.unescape(chosen) == html.unescape(correct):
            self.scores += 10
        else:
            self.remaining -= 15
            if self.remaining < 0:
                self.remaining = 0
        self.cur_q += 1
        if self.cur_q >= 10:
            self.finished_round()
        else:
            self.show_question()

    def finished_round(self):
        """Sorular bittikten sonra: skor kaydet, yeni tur yükle."""
        # Skoru veritabanına kaydet
        db_mod.kaydet("quiz_single", self.player_name, self.scores)

        self.round_count += 1
        self.cur_q = 0
        self.remaining = 120

        # Yeni soru seti otomatik yükle (sürekli oyun simülasyonu)
        # Kullanıcı onayını sorsak da otomatik olarak devam edelim
        def load_next():
            self.prepare_game()  # Yeni 10 soru yığını getir

        # 3 saniye bekletip sonra yeni tur
        self.root.after(2500, load_next)

    # ---------- LİDERLİK ----------
    def show_leaderboard(self, oyun):
        self._clear()
        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True, fill="both", padx=40, pady=30)
        tk.Label(f, text="🏆 LİDERLİK TABLOSU", font=("Segoe UI", 24, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(0, 15))

        rows = db_mod.en_iyi(oyun, 15)
        if not rows:
            tk.Label(f, text="Henüz kayıt yok.", font=("Segoe UI", 14),
                     fg=LIGHT, bg=BG).pack(pady=20)
        else:
            for i, (name, skor) in enumerate(rows, 1):
                row = tk.Frame(f, bg=PANEL)
                row.pack(fill="x", pady=3, padx=100)
                tk.Label(row, text=f"{i}. {name}", font=("Segoe UI", 14),
                         fg=WHITE, bg=PANEL, anchor="w", padx=15, pady=6).pack(side="left")
                tk.Label(row, text=f"{skor} puan", font=("Segoe UI", 14, "bold"),
                         fg=ACCENT2, bg=PANEL, anchor="e", padx=15, pady=6).pack(side="right")

        tk.Button(f, text="⬅ Geri", command=self.show_start, bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 13, "bold"), relief="flat", padx=25, pady=8).pack(pady=20)


def main():
    root = tk.Tk()
    try:
        root.state("zoomed")
    except Exception:
        pass
    QuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()