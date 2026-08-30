"""UYT Stant Oyunu 1 - İnteraktif Bilgi Yarışması.
Özellikler:
  - Canlı sorular (OpenTDB) ve her oyuncuya farklı sorular.
  - 10 soru, 4 seçenek, her oyuncuya 2 dakika.
  - Yanlışta süre 15 sn kısalır, doğruda +10 puan.
  - SQLite ile skor/isim kaydı, sıralama ve liderlik tablosu.
  - Yeni oyun döngüsü.
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
IMG_CACHE = os.path.join(os.path.dirname(__file__), "img_cache")
os.makedirs(IMG_CACHE, exist_ok=True)

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

# Arka plan rengi teması (UYT kurumsal tonları)
BG = "#0d1b2a"
PANEL = "#1b263b"
ACCENT = "#e63946"
ACCENT2 = "#f4a261"
LIGHT = "#e0e1dd"
WHITE = "#ffffff"


def fetch_pool(n, used_ids):
    """OpenTDB'den n adet benzersiz soru çeker (kullanılan id'ler hariç)."""
    sorular = []
    deneme = 0
    while len(sorular) < n and deneme < 25:
        deneme += 1
        try:
            r = requests.get(API, params={"amount": 50, "type": "multiple"}, timeout=10)
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

        self.players = []
        self.scores = {}
        self.questions = {}          # isim -> [soru...]
        self.used_ids = set()
        self.cur_player = 0
        self.cur_q = 0
        self.remaining = 120
        self.timer_job = None
        self.img_job = None
        self._build_styles()

        db_mod.init_db()
        self.show_start()

    # ---------- stil ----------
    def _build_styles(self):
        try:
            self.root.tk.call("source", "azure.tcl")
        except Exception:
            pass

    # ---------- çerçeve yardımcıları ----------
    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None

    # ---------- BAŞLANGIÇ EKRANI ----------
    def show_start(self):
        self._clear()
        self.players = []
        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True, fill="both", padx=40, pady=30)

        tk.Label(f, text="UYT BİLGİ YARIŞMASI", font=("Segoe UI", 30, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(10, 5))
        tk.Label(f, text="Oyuncu isimlerini ekleyin ve yarışmayı başlatın",
                 font=("Segoe UI", 13), fg=LIGHT, bg=BG).pack(pady=(0, 20))

        entry = tk.Entry(f, font=("Segoe UI", 14), bg=PANEL, fg=WHITE,
                         insertbackground=WHITE, relief="flat", justify="center")
        entry.pack(ipady=8, pady=6, fill="x", padx=120)
        entry.focus()

        listbox = tk.Listbox(f, font=("Segoe UI", 13), bg=PANEL, fg=WHITE,
                             relief="flat", height=8, highlightthickness=0)
        listbox.pack(fill="both", expand=True, pady=10, padx=120)

        def add():
            name = entry.get().strip()
            if not name:
                return
            if name in self.players:
                messagebox.showwarning("Tekrar", "Bu isim zaten eklendi.")
                return
            if len(self.players) >= 8:
                messagebox.showwarning("Limit", "En fazla 8 oyuncu.")
                return
            self.players.append(name)
            listbox.insert("end", f"{len(self.players)}. {name}")
            entry.delete(0, "end")

        def remove():
            sel = listbox.curselection()
            if not sel:
                return
            i = sel[0]
            listbox.delete(i)
            self.players.pop(i)
            for idx, nm in enumerate(self.players, 1):
                listbox.insert("end", f"{idx}. {nm}")
            # listbox sıfırlandığı için yeniden doldur
            listbox.delete(0, "end")
            for idx, nm in enumerate(self.players, 1):
                listbox.insert("end", f"{idx}. {nm}")

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(pady=6)
        tk.Button(btn_row, text="➕ Ekle", command=add, bg=ACCENT2, fg=BG,
                  font=("Segoe UI", 12, "bold"), relief="flat", padx=18, pady=6).pack(side="left", padx=6)
        tk.Button(btn_row, text="➖ Çıkar", command=remove, bg=PANEL, fg=LIGHT,
                  font=("Segoe UI", 12), relief="flat", padx=18, pady=6).pack(side="left", padx=6)
        entry.bind("<Return>", lambda e: add())

        def start():
            if len(self.players) < 1:
                messagebox.showwarning("Eksik", "En az 1 oyuncu ekleyin.")
                return
            self.prepare_game()

        bottom = tk.Frame(f, bg=BG)
        bottom.pack(pady=10)
        tk.Button(bottom, text="🎮 OYNA", command=start, bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 16, "bold"), relief="flat", padx=40, pady=10).pack(side="left", padx=8)
        tk.Button(bottom, text="🏆 Liderlik", command=lambda: self.show_leaderboard("quiz"),
                  bg=PANEL, fg=LIGHT, font=("Segoe UI", 13), relief="flat", padx=20, pady=10).pack(side="left", padx=8)

    # ---------- OYUN HAZIRLIĞI ----------
    def prepare_game(self):
        self._clear()
        loading = tk.Label(self.root, text="Sorular internetten çekiliyor...\nLütfen bekleyin",
                           font=("Segoe UI", 18), fg=LIGHT, bg=BG)
        loading.pack(expand=True)

        def work():
            total = len(self.players) * 10
            pool = fetch_pool(total, self.used_ids)
            if not pool:
                self.root.after(0, lambda: messagebox.showerror(
                    "Hata", "İnternetten soru alınamadı. Bağlantıyı kontrol edin."))
                self.root.after(0, self.show_start)
                return
            random.shuffle(pool)
            self.questions = {}
            self.scores = {}
            for i, name in enumerate(self.players):
                self.questions[name] = pool[i * 10:(i + 1) * 10]
                self.scores[name] = 0
            self.root.after(0, self.start_player)

        threading.Thread(target=work, daemon=True).start()

    # ---------- OYUNCU TURU ----------
    def start_player(self):
        self.cur_player = 0
        self.next_player()

    def next_player(self):
        if self.cur_player >= len(self.players):
            self.show_results()
            return
        self.cur_q = 0
        self.remaining = 120
        self.show_question()

    def show_question(self):
        self._clear()
        name = self.players[self.cur_player]
        q = self.questions[name][self.cur_q]

        # ÜST BAR
        top = tk.Frame(self.root, bg=PANEL)
        top.pack(fill="x", padx=0, pady=0)
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)

        self.timer_lbl = tk.Label(top, text=f"⏱ {self.remaining:02d}:00",
                                  font=("Segoe UI", 20, "bold"), fg=ACCENT2, bg=PANEL)
        self.timer_lbl.grid(row=0, column=0, sticky="w", padx=20, pady=12)

        prog = tk.Label(top, text=f"Soru {self.cur_q + 1}/10",
                        font=("Segoe UI", 14), fg=LIGHT, bg=PANEL)
        prog.grid(row=0, column=1)

        self.name_lbl = tk.Label(top, text=f"👤 {name}  |  Puan: {self.scores[name]}",
                                 font=("Segoe UI", 16, "bold"), fg=WHITE, bg=PANEL)
        self.name_lbl.grid(row=0, column=2, sticky="e", padx=20, pady=12)

        # ORTA: RESİM + SORU
        mid = tk.Frame(self.root, bg=BG)
        mid.pack(expand=True, fill="both", padx=30, pady=10)

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
            self.finish_player()
            return
        m, s = divmod(self.remaining, 60)
        self.timer_lbl.configure(text=f"⏱ {m:02d}:{s:02d}")
        if self.remaining <= 15:
            self.timer_lbl.configure(fg=ACCENT)
        self.remaining -= 1
        self.timer_job = self.root.after(1000, self._tick)

    def answer(self, chosen, correct):
        name = self.players[self.cur_player]
        if html.unescape(chosen) == html.unescape(correct):
            self.scores[name] += 10
        else:
            self.remaining -= 15
            if self.remaining < 0:
                self.remaining = 0
        self.cur_q += 1
        if self.cur_q >= 10 or self.remaining <= 0:
            self.finish_player()
        else:
            self.show_question()

    def finish_player(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
        name = self.players[self.cur_player]
        db_mod.kaydet("quiz", name, self.scores[name])
        self.cur_player += 1
        self.next_player()

    # ---------- SONUÇ / SIRALAMA ----------
    def show_results(self):
        self._clear()
        # Bu oyunun sıralaması
        ranking = sorted(self.players, key=lambda n: self.scores[n], reverse=True)
        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True, fill="both", padx=40, pady=30)

        tk.Label(f, text="🏁 OYUN SONU - SIRALAMA", font=("Segoe UI", 26, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(0, 20))

        medals = ["🥇", "🥈", "🥉"]
        for i, name in enumerate(ranking):
            color = ACCENT if i == 0 else PANEL
            fg = WHITE if i == 0 else LIGHT
            row = tk.Frame(f, bg=color, relief="flat")
            row.pack(fill="x", pady=5, padx=80)
            place = medals[i] if i < 3 else f"{i + 1}."
            tk.Label(row, text=f"{place}  {name}", font=("Segoe UI", 16, "bold"),
                     fg=fg, bg=color, anchor="w", padx=15, pady=10).pack(side="left")
            tk.Label(row, text=f"{self.scores[name]} puan", font=("Segoe UI", 16),
                     fg=fg, bg=color, anchor="e", padx=15, pady=10).pack(side="right")

        bottom = tk.Frame(f, bg=BG)
        bottom.pack(pady=25)
        tk.Button(bottom, text="🔄 YENİ OYUN", command=self.show_start,
                  bg=ACCENT, fg=WHITE, font=("Segoe UI", 15, "bold"),
                  relief="flat", padx=30, pady=10).pack(side="left", padx=8)
        tk.Button(bottom, text="🏆 Liderlik", command=lambda: self.show_leaderboard("quiz"),
                  bg=PANEL, fg=LIGHT, font=("Segoe UI", 13), relief="flat",
                  padx=20, pady=10).pack(side="left", padx=8)

    # ---------- LİDERLİK TABLOSU ----------
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
