"""UYT Stant Oyunu 3 - "SEMbol AVI" (kendi tasarımımız arcade oyunu).

Kendi tasarladığımız, sadece Tkinter ile çalışan hızlı bir refleks oyunu.
30 saniye içinde ekranda beliren UYT sembollerine tıklayarak puan topla.
Ardışık isabetlerde kombo çarpanı artar. En yüksek skorlar yerel veritabanında
saklanır ve bir liderlik tablosu gösterilir.

Bağımlılık: sadece Python standart kütüphanesi (tkinter).
"""
import random
import tkinter as tk
from tkinter import ttk, messagebox

import db as db_mod

BG = "#0d1b2a"
PANEL = "#1b263b"
ACCENT = "#e63946"
ACCENT2 = "#f4a261"
LIGHT = "#e0e1dd"
WHITE = "#ffffff"

SEMOLLER = ["⭐", "🚀", "💡", "🎯", "🔥", "🐍", "💻", "🏆", "🧠", "⚡"]
RENKLER = ["#e63946", "#f4a261", "#2a9d8f", "#e9c46a", "#457b9d", "#a8dadc"]

SURE = 30  # saniye


class SembolAvi:
    def __init__(self, root):
        self.root = root
        self.root.title("UYT - Sembol Avı")
        self.root.configure(bg=BG)
        self.root.geometry("900x680")
        self.root.minsize(700, 560)
        self.root.resizable(True, True)

        self.skor = 0
        self.combo = 0
        self.kalan = SURE
        self.hedefler = []  # (id_oval, id_text, expiry)
        self.oyun_aktif = False
        self.spawn_job = None
        self.timer_job = None
        self.canvas = None

        db_mod.init_db()
        self.menu()

    # ---------- MENÜ ----------
    def menu(self):
        self._temizle()
        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True, fill="both", padx=40, pady=30)

        tk.Label(f, text="🎯 SEMBOL AVI", font=("Segoe UI", 34, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(10, 4))
        tk.Label(f, text="UYT'nin kendi tasarladığı refleks oyunu",
                 font=("Segoe UI", 14), fg=LIGHT, bg=BG).pack(pady=(0, 6))
        tk.Label(f, text=f"{SURE} saniyede beliren sembollere tıkla, kombonu artır, zirveye çık!",
                 font=("Segoe UI", 12), fg=LIGHT, bg=BG, wraplength=600,
                 justify="center").pack(pady=(0, 24))

        btn = tk.Frame(f, bg=BG)
        btn.pack(pady=10)
        tk.Button(btn, text="🎮 BAŞLA", command=self.basla, bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 16, "bold"), relief="flat", padx=40, pady=12).pack(side="left", padx=8)
        tk.Button(btn, text="🏆 Liderlik", command=self.liderlik_ekrani,
                  bg=PANEL, fg=LIGHT, font=("Segoe UI", 13), relief="flat",
                  padx=20, pady=12).pack(side="left", padx=8)

    # ---------- OYUN ----------
    def basla(self):
        self._temizle()
        self.skor = 0
        self.combo = 0
        self.kalan = SURE
        self.hedefler = []
        self.oyun_aktif = True

        ust = tk.Frame(self.root, bg=PANEL)
        ust.pack(fill="x")
        self.skor_lbl = tk.Label(ust, text="Skor: 0", font=("Segoe UI", 16, "bold"),
                                 fg=WHITE, bg=PANEL)
        self.skor_lbl.pack(side="right", padx=20, pady=8)
        self.combo_lbl = tk.Label(ust, text="Kombo: x1", font=("Segoe UI", 14),
                                  fg=ACCENT2, bg=PANEL)
        self.combo_lbl.pack(side="right", padx=10, pady=8)
        self.sure_lbl = tk.Label(ust, text=f"⏱ {SURE}", font=("Segoe UI", 18, "bold"),
                                 fg=ACCENT2, bg=PANEL)
        self.sure_lbl.pack(side="left", padx=20, pady=8)

        self.canvas = tk.Canvas(self.root, bg="#081019", cursor="crosshair",
                                highlightthickness=0)
        self.canvas.pack(expand=True, fill="both")
        self.canvas.bind("<Button-1>", self.tikla)

        self._spawn()
        self._tick()

    def _spawn(self):
        if not self.oyun_aktif:
            return
        w = self.canvas.winfo_width() or 800
        h = self.canvas.winfo_height() or 560
        r = random.randint(26, 46)
        x = random.randint(r + 10, max(r + 20, w - r - 10))
        y = random.randint(r + 10, max(r + 20, h - r - 10))
        renk = random.choice(RENKLER)
        sembol = random.choice(SEMOLLER)
        oval = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                       fill=renk, outline=WHITE, width=2)
        txt = self.canvas.create_text(x, y, text=sembol, font=("Segoe UI", r, "bold"),
                                      fill=WHITE)
        self.hedefler.append((oval, txt, self.root.after(1300, lambda: self._sil(oval, txt))))

        # zorluk: süre azaldıkça hedefler sıklaşır
        gecikme = max(380, 800 - (SURE - self.kalan) * 14)
        self.spawn_job = self.root.after(int(gecikme), self._spawn)

    def _sil(self, oval, txt):
        for item in (oval, txt):
            try:
                self.canvas.delete(item)
            except Exception:
                pass
        self.hedefler = [(o, t, e) for (o, t, e) in self.hedefler if o != oval]
        # kaçırılan hedef kombonu sıfırlar
        self.combo = 0
        self.combo_lbl.configure(text="Kombo: x1")

    def tikla(self, event):
        if not self.oyun_aktif:
            return
        for (oval, txt, _) in list(self.hedefler):
            bbox = self.canvas.bbox(oval)
            if bbox and bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
                # isabet
                self.combo += 1
                kazan = 10 * max(1, self.combo)
                self.skor += kazan
                self.skor_lbl.configure(text=f"Skor: {self.skor}")
                self.combo_lbl.configure(text=f"Kombo: x{self.combo}")
                # patlama efekti
                self._patlama(event.x, event.y)
                self.canvas.delete(oval)
                self.canvas.delete(txt)
                self.hedefler = [(o, t, e) for (o, t, e) in self.hedefler if o != oval]
                return
        # boşluğa tıklama kombonun yarısını düşürür
        if self.combo > 0:
            self.combo = max(0, self.combo // 2)
            self.combo_lbl.configure(text=f"Kombo: x{max(1, self.combo)}")

    def _patlama(self, x, y):
        for i, dr in enumerate([6, 14, 22]):
            cir = self.canvas.create_oval(x - dr, y - dr, x + dr, y + dr,
                                         outline=ACCENT2, width=2)
            self.root.after(120 + i * 60, lambda c=cir: self.canvas.delete(c))

    def _tick(self):
        if not self.oyun_aktif:
            return
        self.kalan -= 1
        self.sure_lbl.configure(text=f"⏱ {max(0, self.kalan)}")
        if self.kalan <= 0:
            self.bitir()
            return
        self.timer_job = self.root.after(1000, self._tick)

    def bitir(self):
        self.oyun_aktif = False
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        for (o, t, e) in self.hedefler:
            try:
                self.canvas.delete(o)
                self.canvas.delete(t)
            except Exception:
                pass
        self.hedefler = []

        # isim girişi
        pencere = tk.Toplevel(self.root)
        pencere.title("Skorunu Kaydet")
        pencere.configure(bg=BG)
        pencere.geometry("380x220")
        pencere.resizable(False, False)
        pencere.grab_set()
        tk.Label(pencere, text=f"Skorun: {self.skor}", font=("Segoe UI", 20, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=15)
        tk.Label(pencere, text="İsmin:", bg=BG, fg=LIGHT, font=("Segoe UI", 12)).pack()
        entry = tk.Entry(pencere, font=("Segoe UI", 14), bg=PANEL, fg=WHITE,
                         insertbackground=WHITE, justify="center")
        entry.pack(pady=8, padx=40, ipady=6)
        entry.focus()

        def kaydet_ve_kapat():
            isim = entry.get().strip() or "Anonim"
            db_mod.kaydet(isim, self.skor)
            pencere.destroy()
            self.liderlik_ekrani(son=self.skor, isim=isim)

        tk.Button(pencere, text="💾 Kaydet", command=kaydet_ve_kapat, bg=ACCENT,
                  fg=WHITE, font=("Segoe UI", 13, "bold"), relief="flat",
                  padx=25, pady=8).pack(pady=15)
        entry.bind("<Return>", lambda e: kaydet_ve_kapat())

    # ---------- LİDERLİK ----------
    def liderlik_ekrani(self, son=None, isim=None):
        self._temizle()
        f = tk.Frame(self.root, bg=BG)
        f.pack(expand=True, fill="both", padx=40, pady=30)
        tk.Label(f, text="🏆 LİDERLİK TABLOSU", font=("Segoe UI", 24, "bold"),
                 fg=ACCENT2, bg=BG).pack(pady=(0, 15))

        rows = db_mod.liderlik(15)
        if not rows:
            tk.Label(f, text="Henüz kayıt yok.", font=("Segoe UI", 14), fg=LIGHT,
                     bg=BG).pack(pady=20)
        else:
            medals = ["🥇", "🥈", "🥉"]
            for i, (nm, sk) in enumerate(rows, 1):
                renk = ACCENT if (son is not None and nm == isim and sk == son and i == 1) else PANEL
                row = tk.Frame(f, bg=renk)
                row.pack(fill="x", pady=3, padx=100)
                place = medals[i - 1] if i <= 3 else f"{i}."
                tk.Label(row, text=f"{place}  {nm}", font=("Segoe UI", 14), fg=WHITE,
                         bg=renk, anchor="w", padx=15, pady=6).pack(side="left")
                tk.Label(row, text=f"{sk} puan", font=("Segoe UI", 14, "bold"),
                         fg=ACCENT2, bg=renk, anchor="e", padx=15, pady=6).pack(side="right")

        bottom = tk.Frame(f, bg=BG)
        bottom.pack(pady=20)
        tk.Button(bottom, text="🔄 Yeni Oyun", command=self.basla, bg=ACCENT, fg=WHITE,
                  font=("Segoe UI", 14, "bold"), relief="flat", padx=25, pady=10).pack(side="left", padx=8)
        tk.Button(bottom, text="🏠 Menü", command=self.menu, bg=PANEL, fg=LIGHT,
                  font=("Segoe UI", 13), relief="flat", padx=20, pady=10).pack(side="left", padx=8)

    # ---------- yardımcı ----------
    def _temizle(self):
        for w in self.root.winfo_children():
            w.destroy()
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)
            self.spawn_job = None
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None


def main():
    root = tk.Tk()
    try:
        root.state("zoomed")
    except Exception:
        pass
    SembolAvi(root)
    root.mainloop()


if __name__ == "__main__":
    main()
