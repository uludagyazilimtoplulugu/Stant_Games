"""
UYT Bilgi Yarismasi
Teknoloji, yapay zeka ve yazilim hakkinda genel kultur sorulari.
Sorular her oyuncu icin rastgele secilir (herkes farkli sorular gorur).
Her soru icin fotograf internetten yuklenir.
"""
import os
import random
import sqlite3
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk, ImageDraw, ImageFont

from sorular import SORULAR

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skorlar.db")

Siyah = "#0a0a0a"
Koyu = "#111827"
Panel = "#1a1a2e"
Mavi = "#2563EB"
Yesil = "#22c55e"
Kirmizi = "#ef4444"
Sari = "#f59e0b"
Beyaz = "#ffffff"
Gri = "#9ca3af"
AcikGri = "#d1d5db"



def veritabani_olustur():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skorlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isim TEXT NOT NULL,
            skor INTEGER NOT NULL,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def skor_kaydet(isim, skor):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO skorlar (isim, skor) VALUES (?, ?)", (isim, skor))
    conn.commit()
    conn.close()


def liderlik_tablosu():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT isim, MAX(skor) as en_yuksek FROM skorlar GROUP BY isim ORDER BY en_yuksek DESC LIMIT 10"
    )
    sonuclar = cursor.fetchall()
    conn.close()
    return sonuclar


class UYTQuiz:
    def __init__(self, root):
        self.root = root
        self.root.title("UYT Bilgi Yarismasi")
        self.root.configure(bg=Siyah)
        self.root.geometry("1100x780")
        self.root.resizable(False, False)

        self.oyuncu_adi = ""
        self.puan = 0
        self.soru_index = 0
        self.kalan_sure = 120
        self.sorular = []
        self.sure_aktif = False
        self.timer_id = None
        self.img_label = None
        self.current_img = None
        self.img_id = 0
        self.img_cache = {}

        veritabani_olustur()
        self.ana_ekran()

    def temizle(self):
        for w in self.root.winfo_children():
            w.destroy()
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.sure_aktif = False

    def ana_ekran(self):
        self.temizle()

        frame = tk.Frame(self.root, bg=Siyah)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="UYT", font=("Helvetica", 72, "bold"),
                 fg=Mavi, bg=Siyah).pack(pady=(0, 5))
        tk.Label(frame, text="BILGI YARISMASI", font=("Helvetica", 28, "bold"),
                 fg=Beyaz, bg=Siyah).pack(pady=(0, 5))
        tk.Label(frame, text="Teknoloji, Yapay Zeka ve Yazilim hakkinda genel kultur",
                 font=("Helvetica", 13), fg=Gri, bg=Siyah).pack(pady=(0, 40))

        tk.Label(frame, text="Adinizi girin:", font=("Helvetica", 13),
                 fg=AcikGri, bg=Siyah).pack(anchor="w", padx=180)

        self.ad_entry = tk.Entry(
            frame, font=("Helvetica", 16), bg=Panel, fg=Beyaz,
            insertbackground=Beyaz, relief="flat",
            highlightthickness=2, highlightbackground=Mavi, highlightcolor=Mavi
        )
        self.ad_entry.pack(ipady=10, pady=(5, 20), padx=180, fill="x")
        self.ad_entry.focus()
        self.ad_entry.bind("<Return>", lambda e: self.oyuna_basla())

        tk.Button(
            frame, text="OYUNA BASLA", font=("Helvetica", 15, "bold"),
            bg=Mavi, fg=Beyaz, relief="flat",
            activebackground="#1d4ed8", activeforeground=Beyaz,
            cursor="hand2", command=self.oyuna_basla
        ).pack(ipady=8, padx=180, fill="x")

        tk.Button(
            frame, text="LIDERLIK TABLOSU", font=("Helvetica", 12),
            bg=Panel, fg=Gri, relief="flat",
            activebackground=Mavi, activeforeground=Beyaz,
            cursor="hand2", command=self.liderlik_ekrani
        ).pack(ipady=6, padx=180, fill="x", pady=(10, 0))

    def oyuna_basla(self):
        self.oyuncu_adi = self.ad_entry.get().strip()
        if not self.oyuncu_adi:
            messagebox.showwarning("Uyari", "Lutfen adinizi girin.")
            return
        self.puan = 0
        self.soru_index = 0
        self.kalan_sure = 120
        self.sorular = random.sample(SORULAR, min(15, len(SORULAR)))
        self.img_cache = {}
        self.gorselleri_on_yukle()
        self.sure_aktif = True
        self.soru_goster()

    def ust_bar(self, parent):
        bar = tk.Frame(parent, bg=Koyu, height=60)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        sure_renk = Yesil
        if self.kalan_sure <= 30:
            sure_renk = Kirmizi
        elif self.kalan_sure <= 60:
            sure_renk = Sari

        dakika = self.kalan_sure // 60
        saniye = self.kalan_sure % 60

        tk.Label(bar, text=f"{dakika:02d}:{saniye:02d}",
                 font=("Helvetica", 20, "bold"), fg=sure_renk, bg=Koyu).pack(side="left", padx=20)
        tk.Label(bar, text=f"Soru {self.soru_index + 1}/{len(self.sorular)}",
                 font=("Helvetica", 13), fg=Gri, bg=Koyu).pack(side="left", padx=30)
        tk.Label(bar, text=self.oyuncu_adi,
                 font=("Helvetica", 14, "bold"), fg=Beyaz, bg=Koyu).pack(side="right", padx=20)
        tk.Label(bar, text=f"{self.puan} Puan",
                 font=("Helvetica", 14, "bold"), fg=Mavi, bg=Koyu).pack(side="right", padx=10)
        return bar

    def sure_baslat(self):
        if not self.sure_aktif:
            return
        if self.kalan_sure <= 0:
            self.oyun_bitti()
            return
        self.kalan_sure -= 1
        self.sure_guncelle()
        self.timer_id = self.root.after(1000, self.sure_baslat)

    def sure_guncelle(self):
        for w in self.root.winfo_children():
            if isinstance(w, tk.Frame) and w.winfo_reqheight() == 60:
                for child in w.winfo_children():
                    child.destroy()
                sure_renk = Yesil
                if self.kalan_sure <= 30:
                    sure_renk = Kirmizi
                elif self.kalan_sure <= 60:
                    sure_renk = Sari
                dakika = self.kalan_sure // 60
                saniye = self.kalan_sure % 60
                tk.Label(w, text=f"{dakika:02d}:{saniye:02d}",
                         font=("Helvetica", 20, "bold"), fg=sure_renk, bg=Koyu).pack(side="left", padx=20)
                tk.Label(w, text=f"Soru {self.soru_index + 1}/{len(self.sorular)}",
                         font=("Helvetica", 13), fg=Gri, bg=Koyu).pack(side="left", padx=30)
                tk.Label(w, text=self.oyuncu_adi,
                         font=("Helvetica", 14, "bold"), fg=Beyaz, bg=Koyu).pack(side="right", padx=20)
                tk.Label(w, text=f"{self.puan} Puan",
                         font=("Helvetica", 14, "bold"), fg=Mavi, bg=Koyu).pack(side="right", padx=10)
                break

    def soru_goster(self):
        self.temizle()

        if self.soru_index >= len(self.sorular):
            self.oyun_bitti()
            return

        soru = self.sorular[self.soru_index]
        self.ust_bar(self.root)

        orta = tk.Frame(self.root, bg=Siyah)
        orta.pack(expand=True, fill="both", padx=40, pady=10)

        self.img_id += 1
        my_id = self.img_id
        self.img_label = tk.Label(orta, bg=Panel, text="Yukleniyor...",
                                   fg=Gri, font=("Helvetica", 12))
        self.img_label.pack(pady=(0, 10), ipadx=10, ipady=10)

        self.fotograf_yukle(self.soru_index)

        tk.Label(orta, text=soru["soru"], font=("Helvetica", 16, "bold"),
                 fg=Beyaz, bg=Siyah, wraplength=900, justify="center").pack(pady=(5, 15))

        secenek_frame = tk.Frame(orta, bg=Siyah)
        secenek_frame.pack(fill="x")
        secenek_frame.columnconfigure(0, weight=1)
        secenek_frame.columnconfigure(1, weight=1)

        renkler = [Panel, Panel, Panel, Panel]
        hover = [Mavi, Yesil, Kirmizi, Sari]

        butonlar = []
        for i, secenek in enumerate(soru["secenekler"]):
            btn = tk.Button(
                secenek_frame, text=secenek, font=("Helvetica", 13),
                fg=Beyaz, bg=renkler[i], relief="flat", activeforeground=Beyaz,
                cursor="hand2", wraplength=420, height=2,
                command=lambda s=i: self.cevap_ver(s)
            )
            satir = i // 2
            sutun = i % 2
            btn.grid(row=satir, column=sutun, sticky="nsew", padx=5, pady=5, ipady=8)
            butonlar.append((btn, hover[i], renkler[i]))

        for btn, h, o in butonlar:
            btn.bind("<Enter>", lambda e, b=btn, hc=h: b.configure(bg=hc))
            btn.bind("<Leave>", lambda e, b=btn, oc=o: b.configure(bg=oc))

        if not self.sure_aktif:
            self.sure_aktif = True
            self.sure_baslat()

    def gorselleri_on_yukle(self):
        for i, soru in enumerate(self.sorular):
            photo = self._yerel_gorsel_olustur(i, soru)
            self.img_cache[i] = photo

    def _yerel_gorsel_olustur(self, index, soru):
        colors = [
            ("#1a1a2e", "#16213e", "#0f3460"),
            ("#0d1117", "#161b22", "#21262d"),
            ("#1b1b2f", "#162447", "#1f4068"),
            ("#2d132c", "#3e1f47", "#4a2c5e"),
            ("#0a192f", "#112240", "#1d3557"),
            ("#1a1a2e", "#e94560", "#533483"),
            ("#0f0e17", "#232946", "#b8c1ec"),
            ("#16161a", "#242629", "#7f5af0"),
        ]
        c = colors[index % len(colors)]
        img = Image.new("RGB", (640, 360), c[0])
        draw = ImageDraw.Draw(img)
        for y in range(360):
            ratio = y / 360
            r1 = int(c[0][1:3], 16)
            g1 = int(c[0][3:5], 16)
            b1 = int(c[0][5:7], 16)
            r2 = int(c[2][1:3], 16)
            g2 = int(c[2][3:5], 16)
            b2 = int(c[2][5:7], 16)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (640, y)], fill=(r, g, b))
        icons = ["{ }", "< />", "[ ]", "# _", "/ >", "( )", "< >", "=>"]
        icon = icons[index % len(icons)]
        try:
            font_big = ImageFont.truetype("arial.ttf", 80)
            font_med = ImageFont.truetype("arial.ttf", 24)
            font_sm = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font_big = ImageFont.load_default()
            font_med = ImageFont.load_default()
            font_sm = ImageFont.load_default()
        draw.text((320, 120), icon, fill="#ffffff", font=font_big, anchor="mm")
        draw.text((320, 220), f"Soru {index + 1}", fill="#ffffff", font=font_med, anchor="mm")
        draw.text((320, 260), "UYT Bilgi Yarismasi", fill="#888888", font=font_sm, anchor="mm")
        return ImageTk.PhotoImage(img)

    def fotograf_yukle(self, index):
        if index in self.img_cache:
            self.current_img = self.img_cache[index]
            self.img_label.configure(image=self.current_img, text="")

    def cevap_ver(self, secim):
        self.sure_aktif = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        soru = self.sorular[self.soru_index]
        dogru_mu = (secim == soru["dogru"])

        if dogru_mu:
            self.puan += 10
        else:
            self.kalan_sure = max(0, self.kalan_sure - 15)

        for w in self.root.winfo_children():
            if isinstance(w, tk.Frame) and w.winfo_reqheight() != 60:
                w.destroy()

        sonuc = tk.Frame(self.root, bg=Siyah)
        sonuc.pack(expand=True)

        if dogru_mu:
            tk.Label(sonuc, text="+10 Puan!", font=("Helvetica", 40, "bold"),
                     fg=Yesil, bg=Siyah).pack()
        else:
            dogru_cevap = soru["secenekler"][soru["dogru"]]
            tk.Label(sonuc, text="-15 Saniye", font=("Helvetica", 40, "bold"),
                     fg=Kirmizi, bg=Siyah).pack()
            tk.Label(sonuc, text=f"Dogru cevap: {dogru_cevap}",
                     font=("Helvetica", 16), fg=Beyaz, bg=Siyah).pack(pady=(10, 5))

        bilgi = soru.get("bilgi", "")
        if bilgi:
            tk.Label(sonuc, text=bilgi, font=("Helvetica", 12),
                     fg=Sari, bg=Siyah, wraplength=800, justify="center").pack(padx=60, pady=(5, 0))

        self.soru_index += 1

        if self.soru_index >= len(self.sorular) or self.kalan_sure <= 0:
            self.root.after(1800, self.oyun_bitti)
        else:
            self.root.after(1800, lambda: self.soru_goster())

    def oyun_bitti(self):
        self.sure_aktif = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        skor_kaydet(self.oyuncu_adi, self.puan)
        self.temizle()

        frame = tk.Frame(self.root, bg=Siyah)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="OYUN BITTI", font=("Helvetica", 36, "bold"),
                 fg=Beyaz, bg=Siyah).pack(pady=(0, 10))
        tk.Label(frame, text=self.oyuncu_adi, font=("Helvetica", 22),
                 fg=Gri, bg=Siyah).pack(pady=(0, 5))
        tk.Label(frame, text=f"{self.puan} Puan", font=("Helvetica", 48, "bold"),
                 fg=Mavi, bg=Siyah).pack(pady=(0, 30))

        bf = tk.Frame(frame, bg=Siyah)
        bf.pack()
        tk.Button(bf, text="TEKRAR OYNA", font=("Helvetica", 14, "bold"),
                  bg=Mavi, fg=Beyaz, relief="flat", cursor="hand2",
                  activebackground="#1d4ed8", activeforeground=Beyaz,
                  command=self.tekrar_oyna).pack(side="left", padx=10, ipady=8)
        tk.Button(bf, text="ANA MENU", font=("Helvetica", 14),
                  bg=Panel, fg=Gri, relief="flat", cursor="hand2",
                  activebackground=Mavi, activeforeground=Beyaz,
                  command=self.ana_ekran).pack(side="left", padx=10, ipady=8)

    def tekrar_oyna(self):
        self.puan = 0
        self.soru_index = 0
        self.kalan_sure = 120
        self.sure_aktif = False
        self.sorular = random.sample(SORULAR, min(15, len(SORULAR)))
        self.sure_aktif = True
        self.soru_goster()

    def liderlik_ekrani(self):
        self.temizle()
        frame = tk.Frame(self.root, bg=Siyah)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="LIDERLIK TABLOSU", font=("Helvetica", 28, "bold"),
                 fg=Mavi, bg=Siyah).pack(pady=(0, 30))

        sonuclar = liderlik_tablosu()
        if not sonuclar:
            tk.Label(frame, text="Henuz skor kaydi yok.", font=("Helvetica", 14),
                     fg=Gri, bg=Siyah).pack()
        else:
            for i, (isim, skor) in enumerate(sonuclar):
                sira_renk = Sari if i == 0 else Gri if i == 1 else "#cd7f32" if i == 2 else "#6b7280"
                satir = tk.Frame(frame, bg=Panel)
                satir.pack(fill="x", pady=3, padx=40)
                tk.Label(satir, text=f"  {i+1}.  {isim}", font=("Helvetica", 13),
                         fg=Beyaz, bg=Panel, anchor="w").pack(side="left", padx=10, pady=8)
                tk.Label(satir, text=f"{skor}  ", font=("Helvetica", 13, "bold"),
                         fg=sira_renk, bg=Panel, anchor="e").pack(side="right", padx=10, pady=8)

        tk.Button(frame, text="GERI DON", font=("Helvetica", 13),
                  bg=Mavi, fg=Beyaz, relief="flat", cursor="hand2",
                  activebackground="#1d4ed8", activeforeground=Beyaz,
                  command=self.ana_ekran).pack(pady=30, ipady=6, padx=80, fill="x")


def main():
    root = tk.Tk()
    root.state("zoomed")
    UYTQuiz(root)
    root.mainloop()


if __name__ == "__main__":
    main()
