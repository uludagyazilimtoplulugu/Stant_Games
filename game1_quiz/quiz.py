"""
UYT Bilgi Yarismasi
Teknoloji, yapay zeka ve yazilim hakkinda genel kultur sorulari.
Sorular her oyuncu icin rastgele secilir (herkes farkli sorular gorur).
Her soru icin fotograf internetten yuklenir.
"""
import os
import random
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox
from io import BytesIO

import requests
from PIL import Image, ImageTk

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

SORULAR = [
    {"soru": "Internet'in babasi olarak bilinen bilim insani kimdir?", "secenekler": ["Tim Berners-Lee", "Vint Cerf", "Steve Jobs", "Bill Gates"], "dogru": 0, "kat": "internet"},
    {"soru": "Ilk bilgisayarin adi neydi?", "secenekler": ["ENIAC", "UNIVAC", "Colossus", "Altair"], "dogru": 0, "kat": "bilgisayar"},
    {"soru": "Yapay zeka terimi ilk kez hangi yilda kullanildi?", "secenekler": ["1956", "1970", "1985", "2000"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Twitter'in kurucusu kimdir?", "secenekler": ["Jack Dorsey", "Mark Zuckerberg", "Larry Page", "Jeff Bezos"], "dogru": 0, "kat": "sirket"},
    {"soru": "Dunyada en cok kullanilan programlama dili hangisidir?", "secenekler": ["Python", "Java", "C", "JavaScript"], "dogru": 3, "kat": "programlama"},
    {"soru": "Google hangi yil kuruldu?", "secenekler": ["1998", "2000", "2004", "1995"], "dogru": 0, "kat": "sirket"},
    {"soru": "Bluetooth teknolojisi hangi ulkenin kralinin adini tasir?", "secenekler": ["Danimarka", "Norvec", "Isvec", "Finlandiya"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Ilk iPhone hangi yil piyasaya suruldu?", "secenekler": ["2007", "2005", "2009", "2010"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Python programlama dili neden 'Python' olarak adlandirilmistir?", "secenekler": ["Monty Python'dan", "Yilan turunden", "Kurucunun hayvanindan", "Rastgele secilmis"], "dogru": 0, "kat": "programlama"},
    {"soru": "Dunyada ilk kez e-posta hangi yilda gonderildi?", "secenekler": ["1971", "1980", "1990", "1965"], "dogru": 0, "kat": "internet"},
    {"soru": "ChatGPT hangi sirket tarafindan gelistirildi?", "secenekler": ["OpenAI", "Google", "Meta", "Microsoft"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Amazon'un kurucusu kimdir?", "secenekler": ["Jeff Bezos", "Elon Musk", "Bill Gates", "Mark Zuckerberg"], "dogru": 0, "kat": "sirket"},
    {"soru": "Dunyada en cok indirilen mobil uygulama hangisidir?", "secenekler": ["TikTok", "Instagram", "WhatsApp", "Facebook"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka ile insan beyni arasindaki en buyuk fark nedir?", "secenekler": ["Duygu ve yaraticilik", "Hiz", "Bellek", "Islem gucu"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Mars'a ilk insansiz araci hangi ulke gonderdi?", "secenekler": ["ABD", "Rusya", "Cin", "Avrupa"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Dunyada en cok kullanilan sosyal medya platformu hangisidir?", "secenekler": ["Facebook", "YouTube", "Instagram", "TikTok"], "dogru": 0, "kat": "sosyal-medya"},
    {"soru": "Blockchain teknolojisi aslinda ne icin gelistirildi?", "secenekler": ["Bitcoin icin", "Oyun icin", "Egitim icin", "Saglik icin"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka'da 'machine learning' ne anlama gelir?", "secenekler": ["Makine ogrenmesi", "Veri depolama", "Ag baglantisi", "Dosya donusumu"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Ilk web tarayicisinin adi neydi?", "secenekler": ["WorldWideWeb", "Netscape", "Internet Explorer", "Mosaic"], "dogru": 0, "kat": "internet"},
    {"soru": "Elon Musk hangi sirketin kurucusudur?", "secenekler": ["Tesla ve SpaceX", "Apple", "Google", "Amazon"], "dogru": 0, "kat": "sirket"},
    {"soru": "Dunyada ilk kez 3D baski ile yapilan ev hangi ulkede basildi?", "secenekler": ["Cin", "Hollanda", "ABD", "Japonya"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka'nin en cok kullanildigi alan hangisidir?", "secenekler": ["Tanim ve oneri", "Oyun", "Muzik", "Yemek"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan isletim sistemi hangisidir?", "secenekler": ["Windows", "macOS", "Linux", "Android"], "dogru": 0, "kat": "bilgisayar"},
    {"soru": "Netflix aslinda hangi hizmeti sunuyordu?", "secenekler": ["DVD kiralama", "Muzik streaming", "Oyun", "Alisveris"], "dogru": 0, "kat": "sirket"},
    {"soru": "Yapay zeka ile yapilan ilk sanat eseri hangi yilda satildi?", "secenekler": ["2018", "2015", "2020", "2010"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada ilk kez yapay zeka ile yazilan bir kitap hangi yilda yayinlandi?", "secenekler": ["2016", "2010", "2020", "2005"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Tesla'nin elektrikli arabalari hangi ozelligiyle taninir?", "secenekler": ["Otonom surus", "Hiz", "Tasarim", "Fiyat"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Dunyada en cok kullanilan arama motoru hangisidir?", "secenekler": ["Google", "Bing", "Yahoo", "Yandex"], "dogru": 0, "kat": "internet"},
    {"soru": "Yapay zeka'da 'deep learning' ne anlama gelir?", "secenekler": ["Derin ogrenme", "Hizli islem", "Bellek yonetimi", "Ag baglantisi"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Instagram'i kim olusturmustu?", "secenekler": ["Kevin Systrom", "Mark Zuckerberg", "Jack Dorsey", "Evan Spiegel"], "dogru": 0, "kat": "sirket"},
    {"soru": "Dunyada ilk kez drone ile teslimat hangi sirket tarafindan yapildi?", "secenekler": ["Amazon", "Google", "DHL", "FedEx"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka'nin en buyuk riski nedir?", "secenekler": ["Is kaybi", "Hiz", "Maliyet", "Depolama"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan bulut hizmeti hangisidir?", "secenekler": ["Amazon AWS", "Google Cloud", "Microsoft Azure", "Dropbox"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Spotify hangi ulkede kuruldu?", "secenekler": ["Isvec", "Norvec", "Finlandiya", "Danimarka"], "dogru": 0, "kat": "sirket"},
    {"soru": "Yapay zeka ile yapilan ilk muzik hangi yilda bestelendi?", "secenekler": ["2016", "2010", "2020", "2005"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan mesajlasma uygulamasi hangisidir?", "secenekler": ["WhatsApp", "Telegram", "Signal", "iMessage"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka ile yapilan ilk film sahnesi hangi filmde kullanildi?", "secenekler": ["Star Wars", "Matrix", "Avatar", "Iron Man"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada ilk kez 5G teknolojisi hangi yilda kullanima girdi?", "secenekler": ["2019", "2015", "2020", "2022"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka'nin en cok kullanildigi saglik alani hangisidir?", "secenekler": ["Tani ve goruntuleme", "Ameliyat", "Ilac uretimi", "Hemsirelik"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan e-ticaret sitesi hangisidir?", "secenekler": ["Amazon", "eBay", "Alibaba", "Trendyol"], "dogru": 0, "kat": "sirket"},
    {"soru": "Yapay zeka ile yapilan ilk selfie hangi yilda cekildi?", "secenekler": ["2015", "2010", "2018", "2020"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan video platformu hangisidir?", "secenekler": ["YouTube", "TikTok", "Twitch", "Vimeo"], "dogru": 0, "kat": "sosyal-medya"},
    {"soru": "Yapay zeka ile yapilan ilk yarisma hangi platformda duzenlendi?", "secenekler": ["Kaggle", "GitHub", "Stack Overflow", "Reddit"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka asistani hangisidir?", "secenekler": ["Siri", "Alexa", "Google Assistant", "Cortana"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk yemek tarifi hangi yilda paylasildi?", "secenekler": ["2017", "2015", "2020", "2010"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan bulut depolama hizmeti hangisidir?", "secenekler": ["Google Drive", "Dropbox", "OneDrive", "iCloud"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka ile yapilan ilk tani sistemi hangi hastalik icin kullanildi?", "secenekler": ["Kanser", "Diabet", "Kalp hastaligi", "Grip"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan kod editoru hangisidir?", "secenekler": ["VS Code", "Sublime Text", "Atom", "Notepad++"], "dogru": 0, "kat": "programlama"},
    {"soru": "Yapay zeka ile yapilan ilk cevrimici egitim platformu hangisidir?", "secenekler": ["Khan Academy", "Coursera", "Udemy", "edX"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan mobil isletim sistemi hangisidir?", "secenekler": ["Android", "iOS", "HarmonyOS", "KaiOS"], "dogru": 0, "kat": "bilgisayar"},
    {"soru": "Yapay zeka ile yapilan ilk guvenlik sistemi hangi alanda kullanildi?", "secenekler": ["Yuz tanima", "Parmak izi", "Ses tanima", "Goz tanima"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan veritabani yonetim sistemi hangisidir?", "secenekler": ["MySQL", "PostgreSQL", "MongoDB", "Oracle"], "dogru": 0, "kat": "bilgisayar"},
    {"soru": "Yapay zeka ile yapilan ilk otomobil hangi sirket tarafindan uretildi?", "secenekler": ["Tesla", "Google", "Apple", "BMW"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan oyun motoru hangisidir?", "secenekler": ["Unity", "Unreal Engine", "Godot", "CryEngine"], "dogru": 0, "kat": "programlama"},
    {"soru": "Yapay zeka ile yapilan ilk tarih kitabi hangi yilda yayinlandi?", "secenekler": ["2018", "2015", "2020", "2010"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan web framework'u hangisidir?", "secenekler": ["React", "Angular", "Vue.js", "Django"], "dogru": 0, "kat": "programlama"},
    {"soru": "Yapay zeka ile yapilan ilk muzik albumu hangi yilda cikti?", "secenekler": ["2016", "2010", "2020", "2005"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan versiyon kontrol sistemi hangisidir?", "secenekler": ["Git", "SVN", "Mercurial", "Perforce"], "dogru": 0, "kat": "programlama"},
    {"soru": "Yapay zeka ile yapilan ilk guzel sanatlar sergisi hangi yilda acildi?", "secenekler": ["2016", "2010", "2020", "2015"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan iletisim araci hangisidir?", "secenekler": ["E-posta", "Telefon", "Mektup", "Telegram"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka ile yapilan ilk edebi eser hangi turdeydi?", "secenekler": ["Siir", "Roman", "Hikaye", "Oyun"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka kutuphanesi hangisidir?", "secenekler": ["TensorFlow", "PyTorch", "Keras", "Scikit-learn"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk hava durumu tahmini hangi yilda yapildi?", "secenekler": ["2015", "2010", "2020", "2005"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan veri analiz araci hangisidir?", "secenekler": ["Excel", "Tableau", "Power BI", "Google Sheets"], "dogru": 0, "kat": "bilgisayar"},
    {"soru": "Yapay zeka ile yapilan ilk akilli sehir projesi hangi ulkede baslatildi?", "secenekler": ["Cin", "ABD", "Japonya", "G. Kore"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan web tarayicisi hangisidir?", "secenekler": ["Chrome", "Safari", "Firefox", "Edge"], "dogru": 0, "kat": "bilgisayar"},
    {"soru": "Yapay zeka ile yapilan ilk ticari robot hangi sirket tarafindan uretildi?", "secenekler": ["Boston Dynamics", "Tesla", "Honda", "SoftBank"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan bulut bilisim platformu hangisidir?", "secenekler": ["AWS", "Azure", "Google Cloud", "IBM Cloud"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka ile yapilan ilk tani dogruluk orani hangi hastalikta en yuksekti?", "secenekler": ["Deri kanseri", "Goz hastaligi", "Kalp hastaligi", "Diyabet"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan mobil uygulama gelistirme dili hangisidir?", "secenekler": ["Swift", "Kotlin", "Flutter", "React Native"], "dogru": 0, "kat": "programlama"},
    {"soru": "Yapay zeka ile yapilan ilk cevrimici yarisma odulu ne kadardi?", "secenekler": ["1 milyon dolar", "100 bin dolar", "10 bin dolar", "1 milyar dolar"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan siber guvenlik araci hangisidir?", "secenekler": ["Firewall", "Antivirus", "VPN", "Shredder"], "dogru": 0, "kat": "teknoloji"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik ceviri sistemi hangi diller arasinda calisiyordu?", "secenekler": ["Ingilizce-Fransizca", "Turkce-Ingilizce", "Cince-Ingilizce", "Japonca-Ingilizce"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka gorsel olusturucu hangisidir?", "secenekler": ["DALL-E", "Midjourney", "Stable Diffusion", "Firefly"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk tani sistemi hangi hastaneyde kullanildi?", "secenekler": ["Mayo Clinic", "Harvard", "Stanford", "Oxford"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan api yonetim araci hangisidir?", "secenekler": ["Postman", "Swagger", "Insomnia", "cURL"], "dogru": 0, "kat": "programlama"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik soforluk sistemi hangi marka arabada kullanildi?", "secenekler": ["Tesla", "BMW", "Mercedes", "Audi"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka sesli asistani hangisidir?", "secenekler": ["Alexa", "Siri", "Google Assistant", "Cortana"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik kod inceleme araci hangi yilda yayinlandi?", "secenekler": ["2017", "2015", "2020", "2010"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka video olusturucu hangisidir?", "secenekler": ["Sora", "Runway", "Pika", "HeyGen"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik muzik bestecisi hangi turde eserler olusturuyordu?", "secenekler": ["Klasik muzik", "Pop", "Rock", "Jazz"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka metin duzenleyicisi hangisidir?", "secenekler": ["Grammarly", "Hemingway", "ProWritingAid", "QuillBot"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik e-posta yanitlama sistemi hangi yilda kullanildi?", "secenekler": ["2015", "2010", "2020", "2005"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka fotografcilik uygulamasi hangisidir?", "secenekler": ["Lensa", "Remini", "FaceApp", "Prisma"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik veri girisi sistemi hangi alanda kullanildi?", "secenekler": ["Bankacilik", "Saglik", "Egitim", "Uretim"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka chatbot platformu hangisidir?", "secenekler": ["ChatGPT", "Bard", "Claude", "Perplexity"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik hukuki analiz sistemi hangi ulkede kullanildi?", "secenekler": ["ABD", "Ingiltere", "Almanya", "Japonya"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka egitim platformu hangisidir?", "secenekler": ["Coursera", "Udacity", "DataCamp", "Kaggle Learn"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik ceviri cihazi hangi ulkede uretildi?", "secenekler": ["Japonya", "Cin", "ABD", "G. Kore"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka tani araci hangi hastalik icin kullaniliyor?", "secenekler": ["Kanser", "Kalp hastaligi", "Diyabet", "Grip"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik mali analiz sistemi hangi yilda baslatildi?", "secenekler": ["2016", "2010", "2020", "2005"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka guvenlik sistemi hangi alanda calisiyor?", "secenekler": ["Yuz tanima", "Ses tanima", "Parmak izi", "Goz tanima"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik stok yonetim sistemi hangi sektorde kullanildi?", "secenekler": ["Perakende", "Uretim", "Lojistik", "Tarim"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka enerji yonetim sistemi hangi ulkede aktif?", "secenekler": ["Almanya", "ABD", "Cin", "Japonya"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik trafik yonetim sistemi hangi sehirde calisiyor?", "secenekler": ["Singapur", "Tokyo", "New York", "Londra"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Dunyada en cok kullanilan yapay zeka cevrimici alisveris sistemi hangi platformda?", "secenekler": ["Amazon", "eBay", "Alibaba", "Trendyol"], "dogru": 0, "kat": "yapay-zeka"},
    {"soru": "Yapay zeka ile yapilan ilk otomatik egitim sistemi hangi derste kullanildi?", "secenekler": ["Matematik", "Tarih", "Biyoloji", "Fizik"], "dogru": 0, "kat": "yapay-zeka"},
]


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
        self.sorular = random.sample(SORULAR, min(10, len(SORULAR)))
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

        self.img_label = tk.Label(orta, bg=Panel, width=70, height=14)
        self.img_label.pack(pady=(0, 10))
        self.img_label.configure(text="Yukleniyor...", fg=Gri, font=("Helvetica", 12))

        self.fotograf_yukle(soru.get("kat", "teknoloji"))

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

    def fotograf_yukle(self, kategori):
        keyword = kategori.lower().replace(" ", "+")
        url = f"https://loremflickr.com/500/300/{keyword}"

        def isle():
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200:
                    img = Image.open(BytesIO(r.content))
                    img = img.resize((500, 300), Image.LANCZOS)
                    self.current_img = ImageTk.PhotoImage(img)
                    self.root.after(0, lambda: self.img_label.configure(
                        image=self.current_img, text=""))
            except Exception:
                self.root.after(0, lambda: self.img_label.configure(
                    text="Gorsel yuklenemedi", fg=Gri))

        threading.Thread(target=isle, daemon=True).start()

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
                     font=("Helvetica", 16), fg=Gri, bg=Siyah).pack(pady=10)

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
        self.sorular = random.sample(SORULAR, min(10, len(SORULAR)))
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
