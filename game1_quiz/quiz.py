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
import hashlib

import requests
from PIL import Image, ImageTk, ImageDraw, ImageFont

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
    {"soru": "Dunyada en fazla satir koda sahip yazilim hangisidir?", "secenekler": ["Windows", "Google Arama Motoru", "Facebook", "NASA Uzay Mekigi Yazilimi"], "dogru": 1, "bilgi": "Google'ın tüm kod tabanı yaklaşık 2 milyar satırdır."},
    {"soru": "Dunyada en fazla indirilen mobil uygulama hangisidir?", "secenekler": ["TikTok", "Instagram", "WhatsApp", "Facebook"], "dogru": 2, "bilgi": "WhatsApp 2 milyar+ indirme ile zirvede."},
    {"soru": "Bir iPhone'daki işlemci kaç transistöre sahiptir?", "secenekler": ["15 milyar", "2 milyar", "500 milyon", "1 milyar"], "dogru": 0, "bilgi": "A17 Pro çipi 19 milyar transistöre sahip."},
    {"soru": "Dunyada en pahalı domain adı hangisidir?", "secenekler": ["CarInsurance.com", "Voice.com", "Sex.com", "Insurance.com"], "dogru": 3, "bilgi": "Insurance.com 35.6 milyon dolara satıldı."},
    {"soru": "Google her yıl ortalama kaç kez sloganını değiştirir?", "secenekler": ["4000+", "500", "100", "10000+"], "dogru": 0, "bilgi": "Google Doodle, yılda 4000'den fazla özel logo tasarlar."},
    {"soru": "Bir USB'nin orijinal adı neydi?", "secenekler": ["Universal Serial Bus", "Unified System Bus", "Universal System Bond", "Unified Serial Bond"], "dogru": 0, "bilgi": "USB 1996'da tanıtıldı. 7 şirket bir araya gelerek oluşturdu."},
    {"soru": "Dünyanın en çok kullanılan şifresi hangisidir?", "secenekler": ["123456", "password", "qwerty", "admin"], "dogru": 0, "bilgi": "2023'te '123456' hâlâ bir numaralı şifre."},
    {"soru": "Dünyanın ilk cep telefonu hangi markaydı?", "secenekler": ["Nokia", "Motorola", "Samsung", "Ericsson"], "dogru": 1, "bilgi": "Motorola DynaTAC 1983'te çıktı. 30 dakika konuşma süresi vardı."},
    {"soru": "Bir gigabayt (GB) kaç megabayttan oluşur?", "secenekler": ["1000", "1024", "512", "2048"], "dogru": 1, "bilgi": "Bilgisayarlarda 1 GB = 1024 MB olarak hesaplanır."},
    {"soru": "Dünyanın en çok ziyaret edilen web sitesi hangisidir?", "secenekler": ["YouTube", "Google", "Facebook", "Wikipedia"], "dogru": 1, "bilgi": "Google ayda 80+ milyar ziyaretçi alır."},
    {"soru": "İlk bilgisayar faresi hangi malzemeden yapılmıştı?", "secenekler": ["Tahta", "Metal", "Plastik", "Cam"], "dogru": 0, "bilgi": "Doug Engelbart 1964'te ilk fareyi tahtadan yaptı."},
    {"soru": "Dünyanın en çok oynanan oyunu hangisidir?", "secenekler": ["Minecraft", "GTA V", "Tetris", "Fortnite"], "dogru": 0, "bilgi": "Minecraft 300 milyon+ satis ile dunya rekoru kirdi."},
    {"soru": "İlk webcam ne için icat edildi?", "secenekler": ["Kahve makinesini izlemek", "Güvenlik", "Video konferans", "Canlı yayın"], "dogru": 0, "bilgi": "Cambridge Üniversitesi'nde kahve molalarını takip etmek için yapıldı."},
    {"soru": "Dünyada en çok kullanılan programlama dili hangisidir?", "secenekler": ["Python", "Java", "C", "JavaScript"], "dogru": 3, "bilgi": "JavaScript, web'in dili olduğu için en çok kullanılan dildir."},
    {"soru": "Bir Wi-Fi sinyalinin menzili ortalama ne kadardır?", "secenekler": ["10 metre", "30-50 metre", "100 metre", "200 metre"], "dogru": 1, "bilgi": "Duvarlar ve engeller menzili önemli ölçüde azaltır."},
    {"soru": "Dünyanın en çok kazanan YouTuber'ı kimdir?", "secenekler": ["MrBeast", "PewDiePie", "Dude Perfect", "Markiplier"], "dogru": 0, "bilgi": "MrBeast 2023'te 82 milyon dolar kazandı."},
    {"soru": "İlk e-posta hangi yılda gönderildi?", "secenekler": ["1971", "1980", "1985", "1990"], "dogru": 0, "bilgi": "Ray Tomlinson 1971'de ilk e-postayı kendi kendine gönderdi."},
    {"soru": "Dünyanın en çok kullanılan sosyal medya uygulaması hangisidir?", "secenekler": ["Instagram", "Facebook", "TikTok", "YouTube"], "dogru": 1, "bilgi": "Facebook hâlâ 3 milyar+ aylık aktif kullanıcıya sahip."},
    {"soru": "Bir çöp kutusu simgesi (Recycle Bin) neden icat edildi?", "secenekler": ["Kullanıcı hatalarını düzeltmek için", "Eski dosyaları saklamak için", "Görsel tasarım için", "Yasal zorunluluk"], "dogru": 0, "bilgi": "Windows 95 ile geldi. Silinen dosyaları geri alma kolaylığı sağladı."},
    {"soru": "Dünyanın en pahalı akıllı telefonu hangisidir?", "secenekler": ["Falcon Supernova iPhone 6", "Samsung Galaxy Fold", "Vertu Signature", "Goldvish Le Million"], "dogru": 0, "bilgi": "Falcon Supernova iPhone 6 48.5 milyon dolar değerinde."},
    {"soru": "Bir emoticon yerine ilk emoji hangi ülkede geliştirildi?", "secenekler": ["Japonya", "ABD", "Güney Kore", "Çin"], "dogru": 0, "bilgi": "Shigetaka Kurita 1999'da Japonya'da ilk 17 emojiyi tasarladı."},
    {"soru": "Dünyada en çok satan video oyunu hangisidir?", "secenekler": ["Tetris", "Minecraft", "GTA V", "Wii Sports"], "dogru": 0, "bilgi": "Tetris 520 milyon+ kopya ile zirvede."},
    {"soru": "İlk YouTube videosu ne zaman yüklendi?", "secenekler": ["2004", "2005", "2006", "2007"], "dogru": 1, "bilgi": "'Me at the zoo' 23 Nisan 2005'te yüklendi."},
    {"soru": "Dünyada en çok kullanılan arama motoru hangisidir?", "secenekler": ["Google", "Bing", "Yahoo", "Yandex"], "dogru": 0, "bilgi": "Google %92+ pazar payına sahip."},
    {"soru": "Bir Bluetooth ismi nereden geliyor?", "secenekler": ["Dan Kralı Harald Bluetooth'dan", "Mavi dişli biricinden", "İcaddan", "Rastgele"], "dogru": 0, "bilgi": "10. yüzyıl Danimarka Kralı Harald Bluetooth'dan esinlenildi."},
    {"soru": "Dünyanın en çok kullanılan işletim sistemi hangisidir?", "secenekler": ["Windows", "macOS", "Linux", "Android"], "dogru": 3, "bilgi": "Android mobil pazarda %70+ paya sahip."},
    {"soru": "Dünyanın ilk bilgisayar virüsü hangisiydi?", "secenekler": ["Brain", "ILOVEYOU", "Morris Worm", "CIH"], "dogru": 0, "bilgi": "Brain 1986'da Pakistan'da iki kardeş tarafından yazıldı."},
    {"soru": "Bir hard diskte 1 TB depolama yaklaşık kaç fotoğrafa eşdeğerdir?", "secenekler": ["250.000", "1 milyon", "500.000", "100.000"], "dogru": 0, "bilgi": "Ortalama bir JPEG fotoğraf 4 MB ise 1 TB = ~250.000 fotoğraf."},
    {"soru": "Dünyanın en çok kullanılan mesajlaşma uygulaması hangisidir?", "secenekler": ["WhatsApp", "Telegram", "Signal", "iMessage"], "dogru": 0, "bilgi": "WhatsApp 2 milyar+ aktif kullanıcıya sahip."},
    {"soru": "Dünyanın en büyük teknoloji şirketi (piyasa değeri) hangisidir?", "secenekler": ["Apple", "Microsoft", "Google", "Amazon"], "dogru": 0, "bilgi": "Apple 3 trilyon doları aşan piyasa değeriyle lider."},
    {"soru": "İlk akıllı saat hangi markayla çıktı?", "secenekler": ["Apple", "Samsung", "Pebble", "Sony"], "dogru": 2, "bilgi": "Pebble 2013'te Kickstarter'da rekor kırdı."},
    {"soru": "Dünyanın en çok kullanılan programlama dili (2024) hangisidir?", "secenekler": ["Python", "JavaScript", "Java", "C++"], "dogru": 0, "bilgi": "Python yapay zeka ve veri bilimi patlamasıyla zirveye çıktı."},
    {"soru": "Bir çöp bidonu (Trash) simgesindeki mushroom (mantar) neyi temsil eder?", "secenekler": ["Hiçbir şey, rastgele", "Eski dosyalar", "Bozuk dosyalar", "Güvenlik"], "dogru": 0, "bilgi": "Aslında mantar değil, geri dönüşüm sembolüydü ama zamanla değişti."},
    {"soru": "Dünyanın en çok kazanan e-spor turnuvası hangisidir?", "secenekler": ["The International (Dota 2)", "Fortnite World Cup", "League of Legends Worlds", "PUBG Mobile PMGC"], "dogru": 0, "bilgi": "The International 2021'de 40 milyon dolar ödül havuzuna ulaştı."},
    {"soru": "Bir flash belleğin icadı hangi yıla dayanır?", "secenekler": ["1998", "2000", "1995", "2002"], "dogru": 0, "bilgi": "Toshiba'dan Fujio Masuoka 1980'de flash belleği icat etti."},
    {"soru": "Dünyanın en çok kullanılan bulut depolama hizmeti hangisidir?", "secenekler": ["Google Drive", "Dropbox", "iCloud", "OneDrive"], "dogru": 0, "bilgi": "Google Drive 1 milyar+ kullanıcıya sahip."},
    {"soru": "Dünyanın en uzun isimli programlama dili hangisidir?", "secenekler": ["ANSI Common Lisp", "Brainfuck", "C++", "CoffeeScript"], "dogru": 0, "bilgi": "Resmi olarak en uzun dildi. Kısa versiyonu 'Lisp'."},
    {"soru": "Bir Twitter (X) tweet'i ilk kez ne zaman atıldı?", "secenekler": ["2005", "2006", "2007", "2008"], "dogru": 1, "bilgi": "Jack Dorsey 21 Mart 2006'da 'just setting up my twttr' yazdı."},
    {"soru": "Dünyanın en çok indirilen müzik uygulaması hangisidir?", "secenekler": ["Spotify", "Apple Music", "YouTube Music", "SoundCloud"], "dogru": 0, "bilgi": "Spotify 600 milyon+ kullanıcıya sahip."},
    {"soru": "Bir notebook (dizüstü bilgisayar) ismi nereden geliyor?", "secenekler": ["Defter benzerliğinden", "Marka adından", "Mucidin adından", "Rastgele"], "dogru": 0, "bilgi": "Kapak açıldığında deftere benzediği için 'notebook' adı verildi."},
    {"soru": "Dünyanın en çok ziyaret edilen Wikipedia sayfası hangisidir?", "secenekler": ["Ana Sayfa", "ABD", "COVID-19", "Taylor Swift"], "dogru": 0, "bilgi": "İngilizce Wikipedia ana sayfası yılda 1.5 milyar+ kez ziyaret edilir."},
    {"soru": "Dünyanın en çok satan konsol oyunu hangisidir?", "secenekler": ["Wii Sports", "Tetris", "Minecraft", "GTA V"], "dogru": 0, "bilgi": "Wii Sports 82 milyon kopya ile konsol oyunları şampiyonu."},
    {"soru": "Bir emoji'nin unicode karşılığı nedir?", "secenekler": ["Sayısal bir kod", "Harf dizisi", "Resim dosyası", "HTML tag'ı"], "dogru": 0, "bilgi": "Her emoji Unicode Konsorsiyumu tarafından atanmış benzersiz bir koda sahiptir."},
    {"soru": "Dünyanın en büyük yapay zeka şirketi hangisidir?", "secenekler": ["OpenAI", "Google DeepMind", "Anthropic", "Meta AI"], "dogru": 0, "bilgi": "OpenAI ChatGPT ile 100 milyon+ kullanıcıya ulaştı."},
    {"soru": "Dünyanın en çok kullanılan tarayıcısı hangisidir?", "secenekler": ["Chrome", "Safari", "Firefox", "Edge"], "dogru": 0, "bilgi": "Chrome %65+ pazar payı ile lider."},
    {"soru": "Dünyanın en eski aktif web sitesi hangisidir?", "secenekler": ["info.cern.ch", "yahoo.com", "amazon.com", "ebay.com"], "dogru": 0, "bilgi": "CERN'ün ilk web sitesi 1991'den beri aktif."},
    {"soru": "Dünyanın en çok oynanan mobil oyunu hangisidir?", "secenekler": ["Candy Crush", "Subway Surfers", "PUBG Mobile", "Among Us"], "dogru": 0, "bilgi": "Candy Crush 3 milyar+ indirme ile zirvede."},
    {"soru": "Bir dot-com balonu ne zaman patladı?", "secenekler": ["2000", "2001", "1999", "2002"], "dogru": 0, "bilgi": "Mart 2000'de Nasdaq tarihinin en büyük çöküşü yaşandı."},
    {"soru": "Dünyanın en çok kullanılan e-posta servisi hangisidir?", "secenekler": ["Gmail", "Outlook", "Yahoo Mail", "ProtonMail"], "dogru": 0, "bilgi": "Gmail 1.8 milyar+ kullanıcıya sahip."},
    {"soru": "Bir EXE dosyasının uzantısı ne anlama gelir?", "secenekler": ["Executable (Çalıştırılabilir)", "Extended", "External", "Extra"], "dogru": 0, "bilgi": "EXE, İngilizce 'executable' kelimesinin kısaltmasıdır."},
    {"soru": "Dünyanın en çok kullanılan kod düzenleme aracı (IDE) hangisidir?", "secenekler": ["VS Code", "IntelliJ", "Sublime Text", "Vim"], "dogru": 0, "bilgi": "VS Code 2023'te %70+ geliştirici kullanımı ile lider."},
    {"soru": "Dünyanın en çok kazanan Teknoloji CEO'su hangisidir?", "secenekler": ["Elon Musk", "Tim Cook", "Satya Nadella", "Andy Jassy"], "dogru": 0, "bilgi": "Elon Musk 2023'te 200+ milyar dolarlık servetiyle zirvede."},
    {"soru": "Dünyanın en çok kullanılan yapay zeka sohbet botu hangisidir?", "secenekler": ["ChatGPT", "Google Bard", "Claude", "Perplexity"], "dogru": 0, "bilgi": "ChatGPT 2 ayda 100 milyon kullanıcıya ulaştı."},
    {"soru": "Dünyanın en çok satan tech kitabı hangisidir?", "secenekler": ["Clean Code", "The Pragmatic Programmer", "Design Patterns", "SICP"], "dogru": 0, "bilgi": "Clean Code, milyonlarca kopya sattı veiences zorunlu okuma haline geldi."},
    {"soru": "Dünyanın en pahalı teknoloji markası (marka değeri) hangisidir?", "secenekler": ["Apple", "Google", "Microsoft", "Amazon"], "dogru": 0, "bilgi": "Apple marka değeri 500 milyar doları aşıyor."},
    {"soru": "Dünyanın en çok kullanılan versiyon kontrol sistemi hangisidir?", "secenekler": ["Git", "SVN", "Mercurial", "Perforce"], "dogru": 0, "bilgi": "Git, tüm dünyada %90+ geliştirici tarafından kullanılır."},
    {"soru": "Dünyanın en çok kullanılan uptime check (servis izleme) aracı hangisidir?", "secenekler": ["Pingdom", "UptimeRobot", "StatusCake", "Grafana"], "dogru": 1, "bilgi": "UptimeRobot ücretsiz planı ile en çok tercih edilen."},
    {"soru": "Dünyanın en çok kullanılan şifre yöneticisi hangisidir?", "secenekler": ["LastPass", "1Password", "Bitwarden", "Dashlane"], "dogru": 2, "bilgi": "Bitwarden açık kaynak ve ücretsiz olmasıyla popüler."},
    {"soru": "Bir CAPTCHA'nın açılımı nedir?", "secenekler": ["Completely Automated Public Turing test", "Computer Automated Process", "Code And Password Check", "Cyber Attack Prevention"], "dogru": 0, "bilgi": "CAPTCHA, botları insanlardan ayırmak için kullanılır."},
    {"soru": "Dünyanın en çok kullanılan CI/CD aracı hangisidir?", "secenekler": ["GitHub Actions", "Jenkins", "GitLab CI", "Travis CI"], "dogru": 0, "bilgi": "GitHub Actions, GitHub entegrasyonu sayesinde en hızlı büyüyen."},
    {"soru": "Dünyanın en çok kullanılan container platformu hangisidir?", "secenekler": ["Docker", "Kubernetes", "Podman", "LXC"], "dogru": 0, "bilgi": "Docker, konteyner teknolojisini popüler yaptı."},
    {"soru": "Dünyanın en çok kazanan e-ticaret sitesi hangisidir?", "secenekler": ["Amazon", "eBay", "Alibaba", "Trendyol"], "dogru": 0, "bilgi": "Amazon yılda 500+ milyar dolar gelir elde ediyor."},
    {"soru": "Dünyanın en çok kullanılan sosyal medya platformu (2024) hangisidir?", "secenekler": ["Facebook", "YouTube", "Instagram", "TikTok"], "dogru": 0, "bilgi": "Facebook 3 milyar+ aylık aktif kullanıcı ile lider."},
    {"soru": "Dünyanın en çok kullanılan video düzenleme programı hangisidir?", "secenekler": ["Adobe Premiere", "Final Cut Pro", "DaVinci Resolve", "CapCut"], "dogru": 3, "bilgi": "CapCut ücretsiz olması ve TikTok entegrasyonuyla patlama yaptı."},
    {"soru": "Dünyanın en çok kullanılan grafik tasarım programı hangisidir?", "secenekler": ["Photoshop", "Canva", "Figma", "GIMP"], "dogru": 1, "bilgi": "Canva, 170 milyon+ kullanıcı ile amatörlerin vazgeçilmezi."},
    {"soru": "Dünyanın en çok kullanılan sunum programı hangisidir?", "secenekler": ["PowerPoint", "Google Slides", "Keynote", "Prezi"], "dogru": 0, "bilgi": "PowerPoint 30 yıldır ofis dünyasının standardı."},
    {"soru": "Dünyanın en çok kullanılan harita uygulaması hangisidir?", "secenekler": ["Google Maps", "Apple Maps", "Waze", "Yandex Maps"], "dogru": 0, "bilgi": "Google Maps ayda 1 milyar+ kullanıcı tarafından kullanılır."},
    {"soru": "Dünyanın en çok kullanılan e-kitap platformu hangisidir?", "secenekler": ["Amazon Kindle", "Google Play Books", "Apple Books", "Kobo"], "dogru": 0, "bilgi": "Kindle, e-kitap pazarının %70'ine sahip."},
    {"soru": "Dünyanın en çok kullanılan fotoğraf paylaşma platformu hangisidir?", "secenekler": ["Instagram", "Flickr", "500px", "VSCO"], "dogru": 0, "bilgi": "Instagram 2 milyar+ aktif kullanıcıya sahip."},
    {"soru": "Dünyanın en çok kazanan oyun stüdyosu hangisidir?", "secenekler": ["Tencent", "Sony", "Microsoft Gaming", "Nintendo"], "dogru": 0, "bilgi": "Tencent, League of Legends ve PUBG ile zirvede."},
    {"soru": "Dünyanın en çok kullanılan rescue (kurtarma) disk aracı hangisidir?", "secenekler": ["Hiren's Boot CD", "Ubuntu Live", "Windows Recovery", "Clonezilla"], "dogru": 0, "bilgi": "Hiren's Boot CD, onlarca yıllık geçmişiyle efsane."},
    {"soru": "Dünyanın en çok kullanılan remote desktop (masaüstü erişim) aracı hangisidir?", "secenekler": ["TeamViewer", "AnyDesk", "Chrome Remote Desktop", "Parsec"], "dogru": 0, "bilgi": "TeamViewer 2 milyar+ cihazda kurulu."},
    {"soru": "Dünyanın en çok kullanılan not alma uygulaması hangisidir?", "secenekler": ["Notion", "Evernote", "Obsidian", "OneNote"], "dogru": 0, "bilgi": "Notion, 30 milyon+ kullanıcı ile hızla büyüyor."},
    {"soru": "Dünyanın en çok kullanılan code hosting (kod barındırma) platformu hangisidir?", "secenekler": ["GitHub", "GitLab", "Bitbucket", "SourceForge"], "dogru": 0, "bilgi": "GitHub 100 milyon+ geliştirici ve 400 milyon+ repoya sahip."},
    {"soru": "Dünyanın en çok kullanılan design (tasarım) aracı hangisidir?", "secenekler": ["Figma", "Sketch", "Adobe XD", "InVision"], "dogru": 0, "bilgi": "Figma, tarayıcı tabanlı olmasıyla devrim yaptı."},
    {"soru": "Dünyanın en çok kullanılan project management (proje yönetimi) aracı hangisidir?", "secenekler": ["Jira", "Trello", "Asana", "Monday.com"], "dogru": 0, "bilgi": "Jira, Agile ve Scrum ekibi tarafından en çok tercih edilen."},
    {"soru": "Dünyanın en çok kullanılan email marketing (e-posta pazarlama) aracı hangisidir?", "secenekler": ["Mailchimp", "SendGrid", "ConvertKit", "Brevo"], "dogru": 0, "bilgi": "Mailchimp, 13 milyon+ kullanıcı ile lider."},
    {"soru": "Dünyanın en çok kullanılan analytics (analitik) aracı hangisidir?", "secenekler": ["Google Analytics", "Hotjar", "Mixpanel", "Plausible"], "dogru": 0, "bilgi": "Google Analytics, web analitiğinde %80+ pazar payına sahip."},
    {"soru": "Dünyanın en çok kullanılan CRM (müşteri ilişkileri yönetimi) platformu hangisidir?", "secenekler": ["Salesforce", "HubSpot", "Zoho CRM", "Pipedrive"], "dogru": 0, "bilgi": "Salesforce, CRM pazarının %23'üne sahip."},
    {"soru": "Dünyanın en çok kullanılan hosting (barındırma) şirketi hangisidir?", "secenekler": ["GoDaddy", "Bluehost", "HostGator", "SiteGround"], "dogru": 0, "bilgi": "GoDaddy 20 milyon+ müşteriye sahip."},
    {"soru": "Dünyanın en çok kullanılan CMS (içerik yönetim sistemi) hangisidir?", "secenekler": ["WordPress", "Shopify", "Wix", "Squarespace"], "dogru": 0, "bilgi": "WordPress, tüm web sitelerinin %43'ünü oluşturur."},
    {"soru": "Dünyanın en çok kullanılan e-ticaret platformu hangisidir?", "secenekler": ["Shopify", "WooCommerce", "Magento", "BigCommerce"], "dogru": 0, "bilgi": "Shopify, 4 milyon+ mağaza ile lider."},
    {"soru": "Dünyanın en çok kullanılan VoIP (sesli iletişim) uygulaması hangisidir?", "secenekler": ["Skype", "Zoom", "Discord", "Google Meet"], "dogru": 2, "bilgi": "Discord, 200 milyon+ aktif kullanıcı ile oyun dünyasının vazgeçilmezi."},
    {"soru": "Dünyanın en çok kullanılan VPN uygulaması hangisidir?", "secenekler": ["NordVPN", "ExpressVPN", "Surfshark", "ProtonVPN"], "dogru": 0, "bilgi": "NordVPN 15 milyon+ kullanıcıya sahip."},
    {"soru": "Dünyanın en çok kullanılan password manager (şifre yöneticisi) hangisidir?", "secenekler": ["1Password", "LastPass", "Bitwarden", "Dashlane"], "dogru": 2, "bilgi": "Bitwarden, açık kaynak ve ücretsiz olmasıyla tercih ediliyor."},
    {"soru": "Dünyanın en çok kullanılan video konferans uygulaması hangisidir?", "secenekler": ["Zoom", "Microsoft Teams", "Google Meet", "Webex"], "dogru": 0, "bilgi": "Zoom, pandemi döneminde 300 milyon+ günlük toplantıya ulaştı."},
    {"soru": "Dünyanın en çok kullanılan online code playground'u hangisidir?", "secenekler": ["CodePen", "JSFiddle", "Replit", "StackBlitz"], "dogru": 2, "bilgi": "Replit, 35 milyon+ kullanıcı ile en popüler online IDE."},
    {"soru": "Dünyanın en çok kullanılan low-code platformu hangisidir?", "secenekler": ["Bubble", "OutSystems", "Mendix", "Appian"], "dogru": 0, "bilgi": "Bubble, kod bilmeyenlerin web uygulaması yapmasını sağlar."},
    {"soru": "Dünyanın en çok kullanılan QR kod okuyucusu hangisidir?", "secenekler": ["Kamera uygulaması", "QR & Barcode Scanner", "ScanLife", "NeoReader"], "dogru": 0, "bilgi": "Artık tüm akıllı telefonların kamera uygulaması QR okuyor."},
    {"soru": "Dünyanın en çok kullanılan dijital cüzdan uygulaması hangisidir?", "secenekler": ["Apple Pay", "Google Pay", "Samsung Pay", "PayPal"], "dogru": 0, "bilgi": "Apple Pay, 500 milyon+ kayıtlı kullanıcıya sahip."},
    {"soru": "Dünyanın en çok kullanılan yapay zeka görsel üreticisi hangisidir?", "secenekler": ["Midjourney", "DALL-E", "Stable Diffusion", "Leonardo AI"], "dogru": 0, "bilgi": "Midjourney, 16 milyon+ Discord kullanıcısıyla lider."},
    {"soru": "Dünyanın en çok kullanılan open source (açık kaynak) projesi hangisidir?", "secenekler": ["Linux Kernel", "Chromium", "VS Code", "React"], "dogru": 0, "bilgi": "Linux çekirdeği tüm sunucuların %90+'ında çalışıyor."},
    {"soru": "Dünyanın en çok kullanılan database (veritabanı) hangisidir?", "secenekler": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"], "dogru": 0, "bilgi": "MySQL, Walmart ve GitHub gibi devler tarafından kullanılır."},
    {"soru": "Dünyanın en çok kazanan mobil oyun (tek oyun) hangisidir?", "secenekler": ["PUBG Mobile", "Honor of Kings", "Candy Crush", "Clash of Clans"], "dogru": 1, "bilgi": "Honor of Kings (King of Glory) Çin'de yılda 2.5+ milyar dolar kazanıyor."},
    {"soru": "Dünyanın en çok kullanılan sesli asistanı hangisidir?", "secenekler": ["Alexa", "Siri", "Google Assistant", "Cortana"], "dogru": 0, "bilgi": "Alexa 100 milyon+ cihazda aktif."},
    {"soru": "Dünyanın en çok kullanılan streaming (yayın) platformu hangisidir?", "secenekler": ["Netflix", "YouTube", "Disney+", "Amazon Prime"], "dogru": 0, "bilgi": "Netflix 260 milyon+ abone ile lider."},
    {"soru": "Dünyanın en çok kullanılan e-spor oyunu (turnuva) hangisidir?", "secenekler": ["League of Legends", "Counter-Strike 2", "Dota 2", "Valorant"], "dogru": 0, "bilgi": "LoL, Worlds turnuvasında 5+ milyon eş zamanlı izleyiciye ulaştı."},
    {"soru": "Dünyanın en çok kullanılan open source CMS hangisidir?", "secenekler": ["WordPress", "Joomla", "Drupal", "Ghost"], "dogru": 0, "bilgi": "WordPress, tüm web sitelerinin %43'ünü oluşturur."},
    {"soru": "Dünyanın en çok kullanılan mainframe (ana bilgisayarı) markası hangisidir?", "secenekler": ["IBM", "Unisys", "Fujitsu", "Bull"], "dogru": 0, "bilgi": "IBM mainframe'leri bankacılık ve havayolu sektöründe hakim."},
    {"soru": "Dünyanın en çok kullanılan süper bilgisayarı (2024) hangisidir?", "secenekler": ["Frontier", "Aurora", "Eagle", "LUMI"], "dogru": 0, "bilgi": "Frontier, 1.1 exaflops hızla dünyanın en hızlısı."},
    {"soru": "Dünyanın en çok kullanılan roket üreticisi hangisidir?", "secenekler": ["SpaceX", "Blue Origin", "Rocket Lab", "Arianespace"], "dogru": 0, "bilgi": "SpaceX, Falcon 9 ile yeniden kullanılabilirlik devrimi yaptı."},
    {"soru": "Dünyanın en çok kullanılan elektrikli araba markası hangisidir?", "secenekler": ["Tesla", "BYD", "Volkswagen", "Hyundai"], "dogru": 0, "bilgi": "Tesla, Model Y ile 2023'te dünyanın en çok satan arabası oldu."},
    {"soru": "Dünyanın en çok kullanılan drone markası hangisidir?", "secenekler": ["DJI", "Skydio", "Autel", "Parrot"], "dogru": 0, "bilgi": "DJİ, tüketici drone pazarının %70+'ine sahip."},
    {"soru": "Dünyanın en çok kullanılan 3D baskı markası hangisidir?", "secenekler": ["Creality", "Prusa", "Ultimaker", "Bambu Lab"], "dogru": 0, "bilgi": "Creality, uygun fiyatlarıyla amatörlerin vazgeçilmezi."},
    {"soru": "Dünyanın en çok kullanılan robot süpürge markası hangisidir?", "secenekler": ["iRobot (Roomba)", "Roborock", "Ecovacs", "Shark"], "dogru": 0, "bilgi": "iRobot Roomba, robot süpürge kavramını icat etti."},
    {"soru": "Dünyanın en çok kullanılan akıllı saat markası hangisidir?", "secenekler": ["Apple Watch", "Samsung Galaxy Watch", "Garmin", "Fitbit"], "dogru": 0, "bilgi": "Apple Watch,全球 akıllı saat pazarının %50+'ine sahip."},
    {"soru": "Dünyanın en çok kullanılan kulaklık markası hangisidir?", "secenekler": ["Apple (AirPods)", "Samsung", "Sony", "JBL"], "dogru": 0, "bilgi": "AirPods, 300 milyon+ satis ile kablosuz kulaklıkta lider."},
    {"soru": "Dünyanın en çok kullanılan laptop markası hangisidir?", "secenekler": ["Lenovo", "HP", "Dell", "Apple"], "dogru": 0, "bilgi": "Lenovo, 2023'te 55+ milyon birim satarak lider oldu."},
    {"soru": "Dünyanın en çok kullanılan SSD markası hangisidir?", "secenekler": ["Samsung", "Western Digital", "Crucial", "Kingston"], "dogru": 0, "bilgi": "Samsung, SSD pazarının %30+'una sahip."},
    {"soru": "Dünyanın en çok kullanılan ekran kartı markası hangisidir?", "secenekler": ["NVIDIA", "AMD", "Intel Arc", "Matrox"], "dogru": 0, "bilgi": "NVIDIA, yapay zeka ve gaming'de %80+ pazar payına sahip."},
    {"soru": "Dünyanın en çok kullanılan işlemci markası (masaüstü) hangisidir?", "secenekler": ["Intel", "AMD", "ARM", "RISC-V"], "dogru": 0, "bilgi": "Intel, masaüstü pazarda hâlâ lider ama AMD hızla yaklaşıyor."},
    {"soru": "Dünyanın en çok kullanılan router (yönlendirici) markası hangisidir?", "secenekler": ["TP-Link", "Netgear", "ASUS", "Linksys"], "dogru": 0, "bilgi": "TP-Link, uygun fiyatlarıyla ev ve ofiste en çok tercih edilen."},
    {"soru": "Dünyanın en çok kullanılan NAS (ağ depolama) markası hangisidir?", "secenekler": ["Synology", "QNAP", "Western Digital", "Asustor"], "dogru": 0, "bilgi": "Synology, DSM işletim sistemiyle ev kullanıcılarının favorisi."},
    {"soru": "Dünyanın en çok kullanılan UPS (kesintisiz güç kaynağı) markası hangisidir?", "secenekler": ["APC", "Eaton", "CyberPower", "Tripp Lite"], "dogru": 0, "bilgi": "APC, data center ve ev kullanıcısı için standart."},
    {"soru": "Dünyanın en çok kullanılanmonitör markası hangisidir?", "secenekler": ["Dell", "LG", "Samsung", "BenQ"], "dogru": 0, "bilgi": "Dell, ofis ve profesyonel kullanımda lider."},
    {"soru": "Dünyanın en çok kullanılan yazıcı (printer) markası hangisidir?", "secenekler": ["HP", "Canon", "Epson", "Brother"], "dogru": 0, "bilgi": "HP, lazer ve mürekkep püskürtmeli yazıcı pazarında lider."},
    {"soru": "Dünyanın en çok kullanılan project management (proje yönetimi) uygulaması hangisidir?", "secenekler": ["Trello", "Jira", "Asana", "Monday.com"], "dogru": 0, "bilgi": "Trello, basit Kanban panosu ile 50 milyon+ kullanıcıya ulaştı."},
    {"soru": "Dünyanın en çok kullanılan whiteboard (beyaz tahta) uygulaması hangisidir?", "secenekler": ["Miro", "Mural", "FigJam", "Excalidraw"], "dogru": 0, "bilgi": "Miro, 60 milyon+ kullanıcı ile online beyaz tahtada lider."},
    {"soru": "Dünyanın en çok kullanılan Kanban aracı hangisidir?", "secenekler": ["Trello", "Jira", "ClickUp", "Notion"], "dogru": 0, "bilgi": "Trello, basitliği ile Kanban'ı popüler yaptı."},
    {"soru": "Dünyanın en çok kullanılan code review (kod inceleme) aracı hangisidir?", "secenekler": ["GitHub Pull Requests", "GitLab Merge Requests", "Bitbucket", "Reviewboard"], "dogru": 0, "bilgi": "GitHub PR'ları, code review sürecinin standardı."},
    {"soru": "Dünyanın en çok kullanılan API test aracı hangisidir?", "secenekler": ["Postman", "Insomnia", "Thunder Client", "cURL"], "dogru": 0, "bilgi": "Postman, 30 milyon+ kullanıcı ile API geliştirmede lider."},
    {"soru": "Dünyanın en çok kullanılan database management (veritabanı yönetimi) aracı hangisidir?", "secenekler": ["DBeaver", "Navicat", "HeidiSQL", "pgAdmin"], "dogru": 0, "bilgi": "DBeaver, açık kaynak ve tüm veritabanlarını destekler."},
    {"soru": "Dünyanın en çok kullanılan SSH client (istemcisi) hangisidir?", "secenekler": ["PuTTY", "MobaXterm", "Windows Terminal", "Termius"], "dogru": 0, "bilgi": "PuTTY, 20 yıldır Windows'ta SSH standardı."},
    {"soru": "Dünyanın en çok kullanılan remote desktop (masaüstü erişim) uygulaması hangisidir?", "secenekler": ["AnyDesk", "TeamViewer", "Chrome Remote Desktop", "Parsec"], "dogru": 0, "bilgi": "AnyDesk, 500 milyon+ cihazda kurulu ve ücretsiz."},
    {"soru": "Dünyanın en çok kullanılan file transfer (dosya aktarımı) aracı hangisidir?", "secenekler": ["WeTransfer", "SendAnywhere", "Snapdrop", "LANDrop"], "dogru": 0, "bilgi": "WeTransfer, ayda 100 milyon+ dosya transferi yapılır."},
    {"soru": "Dünyanın en çok kullanılan backup (yedekleme) aracı hangisidir?", "secenekler": ["Veeam", "Acronis", "Macrium Reflect", "Clonezilla"], "dogru": 0, "bilgi": "Veeam, 500.000+ müşteri ile enterprise yedeklemede lider."},
    {"soru": "Dünyanın en çok kullanılan uptime monitoring (servis izleme) aracı hangisidir?", "secenekler": ["UptimeRobot", "Pingdom", "StatusCake", "Better Stack"], "dogru": 0, "bilgi": "UptimeRobot, 2 milyon+ kullanıcı ile ücretsiz izlemede lider."},
    {"soru": "Dünyanın en çok kullanılan form builder (form oluşturucu) hangisidir?", "secenekler": ["Typeform", "Google Forms", "JotForm", "Tally"], "dogru": 0, "bilgi": "Typeform, interaktif form tasarımıyla popüler."},
    {"soru": "Dünyanın en çok kullanılan newsletter (bülten) platformu hangisidir?", "secenekler": ["Substack", "Mailchimp", "ConvertKit", "Beehiiv"], "dogru": 0, "bilgi": "Substack, yazarların para kazanmasını sağlıyor."},
    {"soru": "Dünyanın en çok kullanılan no-code e-ticaret platformu hangisidir?", "secenekler": ["Shopify", "Wix", "Squarespace", "Ecwid"], "dogru": 0, "bilgi": "Shopify, kod bilmeyenlerin mağaza açmasını sağlıyor."},
    {"soru": "Dünyanın en çok kullanılan link shortener (kısaltıcı) hangisidir?", "secenekler": ["Bitly", "TinyURL", "Short.io", "Rebrandly"], "dogru": 0, "bilgi": "Bitly, ayda 1 milyar+ link kısaltılıyor."},
    {"soru": "Dünyanın en çok kullanılan online whiteboard (çevrimiçi beyaz tahta) hangisidir?", "secenekler": ["Miro", "Mural", "FigJam", "Excalidraw"], "dogru": 0, "bilgi": "Miro, 60 milyon+ kullanıcı ile lider."},
    {"soru": "Dünyanın en çok kullanılan code snippet (kod parçacığı) aracı hangisidir?", "secenekler": ["GitHub Gist", "Pastebin", "CodePen", "SnippetsLab"], "dogru": 0, "bilgi": "GitHub Gist, developer'lar arası kod paylaşım standardı."},
    {"soru": "Dünyanın en çok kullanılan Markdown editörü hangisidir?", "secenekler": ["Obsidian", "Typora", "Mark Text", "Zettlr"], "dogru": 0, "bilgi": "Obsidian, 1 milyon+ kullanıcı ile not alma devrimi yaptı."},
    {"soru": "Dünyanın en çok kullanılan static site generator (statik site üreticisi) hangisidir?", "secenekler": ["Next.js", "Hugo", "Gatsby", "Astro"], "dogru": 0, "bilgi": "Next.js, React tabanlı olmasıyla en çok tercih edilen."},
    {"soru": "Dünyanın en çok kullanılan headless CMS hangisidir?", "secenekler": ["Strapi", "Sanity", "Contentful", "Directus"], "dogru": 0, "bilgi": "Strapi, açık kaynak ve self-hosted olmasıyla popüler."},
    {"soru": "Dünyanın en çok kullanılan CSS framework'ü hangisidir?", "secenekler": ["Tailwind CSS", "Bootstrap", "Bulma", "Materialize"], "dogru": 0, "bilgi": "Tailwind CSS, utility-first yaklaşımıyla devrim yaptı."},
    {"soru": "Dünyanın en çok kullanılan JavaScript framework'ü hangisidir?", "secenekler": ["React", "Vue.js", "Angular", "Svelte"], "dogru": 0, "bilgi": "React, 200 milyon+ developer tarafından kullanılır."},
    {"soru": "Dünyanın en çok kullanılan backend framework'ü hangisidir?", "secenekler": ["Express.js", "Django", "FastAPI", "Spring Boot"], "dogru": 0, "bilgi": "Express.js, Node.js ekosisteminin vazgeçilmezi."},
    {"soru": "Dünyanın en çok kullanılan database framework'ü (ORM) hangisidir?", "secenekler": ["Prisma", "Sequelize", "TypeORM", "Mongoose"], "dogru": 0, "bilgi": "Prisma, type-safe approach ile yeni neslin favorisi."},
    {"soru": "Dünyanın en çok kullanılan GraphQL client'ı hangisidir?", "secenekler": ["Apollo Client", "Relay", "urql", "graphql-request"], "dogru": 0, "bilgi": "Apollo Client, GraphQL ekosisteminde standart."},
    {"soru": "Dünyanın en çok kullanılan WebSocket kütüphanesi hangisidir?", "secenekler": ["Socket.IO", "ws", "SockJS", "SocketCluster"], "dogru": 0, "bilgi": "Socket.IO, 6 milyon+ npm indirme ile real-time iletişimde lider."},
    {"soru": "Dünyanın en çok kullanılan testing (test) framework'ü hangisidir?", "secenekler": ["Jest", "Mocha", "Vitest", "Cypress"], "dogru": 0, "bilgi": "Jest, Facebook tarafından geliştirildi ve React ile birlikte geldi."},
    {"soru": "Dünyanın en çok kullanılan E2E testing (uçtan uca test) aracı hangisidir?", "secenekler": ["Cypress", "Playwright", "Selenium", "Puppeteer"], "dogru": 0, "bilgi": "Cypress, modern web uygulamaları için en çok tercih edilen."},
    {"soru": "Dünyanın en çok kullanılan linting (kod kalitesi) aracı hangisidir?", "secenekler": ["ESLint", "Prettier", "Stylelint", "SonarQube"], "dogru": 0, "bilgi": "ESLint, JavaScript ekosisteminde kod kalitesi standardı."},
    {"soru": "Dünyanın en çok kullanılan bundler (paketleyici) hangisidir?", "secenekler": ["Vite", "Webpack", "Rollup", "esbuild"], "dogru": 0, "bilgi": "Vite, ESM tabanlı olmasıyla 2023'ün en hızlı büyüyen aracı."},
    {"soru": "Dünyanın en çok kullanılan package manager (paket yöneticisi) hangisidir?", "secenekler": ["npm", "yarn", "pnpm", "bun"], "dogru": 0, "bilgi": "npm, 2 milyar+ aylık indirme ile en büyüğü."},
    {"soru": "Dünyanın en çok kullanılan runtime (çalışma zamanı) hangisidir?", "secenekler": ["Node.js", "Deno", "Bun", "V8"], "dogru": 0, "bilgi": "Node.js, 15 yıldır server-side JavaScript'in standardı."},
    {"soru": "Dünyanın en çok kullanılan REPL (interaktif konsol) hangisidir?", "secenekler": ["Node.js REPL", "Python REPL", "Browser Console", "IPython"], "dogru": 0, "bilgi": "Tarayıcı konsolu, developer'ların vazgeçilmez aracı."},
    {"soru": "Dünyanın en çok kullanılan debugger (hata ayıklayıcı) hangisidir?", "secenekler": ["Chrome DevTools", "VS Code Debugger", "Firefox Developer Tools", "Safari Web Inspector"], "dogru": 0, "bilgi": "Chrome DevTools, tüm modern tarayıcılarda standart."},
    {"soru": "Dünyanın en çok kullanılan profiler (performans analiz) aracı hangisidir?", "secenekler": ["Chrome Lighthouse", "Webpack Bundle Analyzer", "Sentry", "New Relic"], "dogru": 0, "bilgi": "Lighthouse, web performansı ve erişilebilirlik için Google'dan geldi."},
    {"soru": "Dünyanın en çok kullanılan CI/CD (sürekli entegrasyon) platformu hangisidir?", "secenekler": ["GitHub Actions", "GitLab CI", "Jenkins", "CircleCI"], "dogru": 0, "bilgi": "GitHub Actions, GitHub ekosistemiyle entegrasyon sayesinde patlama yaptı."},
    {"soru": "Dünyanın en çok kullanılan container registry (kayıt defteri) hangisidir?", "secenekler": ["Docker Hub", "GitHub Container Registry", "AWS ECR", "Google Container Registry"], "dogru": 0, "bilgi": "Docker Hub, 10 milyon+ resim ile en büyüğü."},
    {"soru": "Dünyanın en çok kullanılan Kubernetes distribution (dağıtımı) hangisidir?", "secenekler": ["Rancher", "OpenShift", "EKS", "AKS"], "dogru": 0, "bilgi": "Rancher, 40.000+ müşteri ile Kubernetes yönetiminde lider."},
    {"soru": "Dünyanın en çok kullanılan IaçU (altyapı kodlama) aracı hangisidir?", "secenekler": ["Terraform", "Pulumi", "CloudFormation", "Ansible"], "dogru": 0, "bilgi": "Terraform, HashiCorp tarafından geliştirildi ve bulut altyapı standardı."},
    {"soru": "Dünyanın en çok kullanılan configuration management (yapılandırma yönetimi) aracı hangisidir?", "secenekler": ["Ansible", "Chef", "Puppet", "SaltStack"], "dogru": 0, "bilgi": "Ansible, agentless yapısıyla en basit ve popüler olanı."},
    {"soru": "Dünyanın en çok kullanılan secret management (sır yönetimi) aracı hangisidir?", "secenekler": ["HashiCorp Vault", "AWS Secrets Manager", "Azure Key Vault", "Doppler"], "dogru": 0, "bilgi": "Vault, open source ve enterprise özellikleriyle lider."},
    {"soru": "Dünyanın en çok kullanılan log management (log yönetimi) aracı hangisidir?", "secenekler": ["ELK Stack", "Grafana Loki", "Splunk", "Datadog"], "dogru": 0, "bilgi": "ELK Stack (Elasticsearch, Logstash, Kibana) open source log yönetimi standardı."},
    {"soru": "Dünyanın en çok kullanılan APM (uygulama performans yönetimi) aracı hangisidir?", "secenekler": ["Datadog", "New Relic", "Dynatrace", "AppDynamics"], "dogru": 0, "bilgi": "Datadog, 25.000+ müşteri ile cloud monitoring'de lider."},
    {"soru": "Dünyanın en çok kullanılan error tracking (hata izleme) aracı hangisidir?", "secenekler": ["Sentry", "Bugsnag", "Rollbar", "Airbrake"], "dogru": 0, "bilgi": "Sentry, 100.000+ geliştirici tarafından kullanılır."},
    {"soru": "Dünyanın en çok kullanılan status page (durum sayfası) aracı hangisidir?", "secenekler": ["Statuspage", "Better Stack", "Instatus", "Cachet"], "dogru": 0, "bilgi": "Statuspage (Atlassian), 10.000+ şirket tarafından kullanılır."},
    {"soru": "Dünyanın en çok kullanılan incident management (olay yönetimi) aracı hangisidir?", "secenekler": ["PagerDuty", "Opsgenie", "Incident.io", "Rootly"], "dogru": 0, "bilgi": "PagerDuty, 70.000+ müşteri ile on-call yönetimi standardı."},
    {"soru": "Dünyanın en çok kullanılan feature flag (bayrak yönetimi) aracı hangisidir?", "secenekler": ["LaunchDarkly", "Split", "Flagsmith", "Unleash"], "dogru": 0, "bilgi": "LaunchDarkly, enterprise feature flagging'de lider."},
    {"soru": "Dünyanın en çok kullanılan A/B testing (test) aracı hangisidir?", "secenekler": ["Optimizely", "VWO", "AB Tasty", "Google Optimize"], "dogru": 0, "bilgi": "Optimizely, 1500+ müşteri ile conversion optimization'da lider."},
    {"soru": "Dünyanın en çok kullanılan heatmap (ısı haritası) aracı hangisidir?", "secenekler": ["Hotjar", "Crazy Egg", "FullStory", "Microsoft Clarity"], "dogru": 0, "bilgi": "Hotjar, 1.3 milyon+ site tarafından kullanılır."},
    {"soru": "Dünyanın en çok kullanılan session recording (oturum kaydı) aracı hangisidir?", "secenekler": ["FullStory", "Hotjar", "LogRocket", "Microsoft Clarity"], "dogru": 0, "bilgi": "FullStory, behavior analytics ile developer'ların favorisi."},
    {"soru": "Dünyanın en çok kullanılan accessibility (erişilebilirlik) test aracı hangisidir?", "secenekler": ["axe", "WAVE", "Lighthouse", "Pa11y"], "dogru": 0, "bilgi": "axe, 100.000+ site tarafından accessibility testleri için kullanılır."},
    {"soru": "Dünyanın en çok kullanılan SEO aracı hangisidir?", "secenekler": ["Ahrefs", "SEMrush", "Moz", "Ubersuggest"], "dogru": 0, "bilgi": "Ahrefs, backlink analizi ve keyword research'de lider."},
    {"soru": "Dünyanın en çok kullanılan web scraping (veri çekme) aracı hangisidir?", "secenekler": ["Beautiful Soup", "Scrapy", "Puppeteer", "Cheerio"], "dogru": 0, "bilgi": "Beautiful Soup, Python ile web scraping'e başlangıç aracı."},
    {"soru": "Dünyanın en çok kullanılan RSS reader (okuyucu) hangisidir?", "secenekler": ["Feedly", "Inoreader", "NewsBlur", "Reeder"], "dogru": 0, "bilgi": "Feedly, 15 milyon+ kullanıcı ile RSS okumada lider."},
    {"soru": "Dünyanın en çok kullanılan markdown editor (Markdown düzenleyici) hangisidir?", "secenekler": ["Obsidian", "Notion", "Logseq", "Roam Research"], "dogru": 0, "bilgi": "Obsidian, linked notes konseptiyle knowledge management'da devrim yaptı."},
    {"soru": "Dünyanın en çok kullanılan PDF editor (PDF düzenleyici) hangisidir?", "secenekler": ["Adobe Acrobat", "PDF24", "Smallpdf", "Sejda"], "dogru": 0, "bilgi": "Adobe Acrobat, PDF formatını icat eden şirkettir."},
    {"soru": "Dünyanın en çok kullanılan screenshot (ekran görüntüsü) aracı hangisidir?", "secenekler": ["Snipping Tool", "Greenshot", "Lightshot", "ShareX"], "dogru": 0, "bilgi": "Windows Snipping Tool, tüm Windows'larda yerleşik olarak gelir."},
    {"soru": "Dünyanın en çok kullanılan screen recording (ekran kaydı) aracı hangisidir?", "secenekler": ["OBS Studio", "Camtasia", "Bandicam", "ScreenPal"], "dogru": 0, "bilgi": "OBS Studio, ücretsiz ve open source olmasıyla popüler."},
    {"soru": "Dünyanın en çok kullanılan video editing (video düzenleme) programı hangisidir?", "secenekler": ["DaVinci Resolve", "Adobe Premiere", "Final Cut Pro", "CapCut"], "dogru": 0, "bilgi": "DaVinci Resolve, Hollywood'da profesyonel düzeyde kullanılır."},
    {"soru": "Dünyanın en çok kullanılan image editing (görsel düzenleme) programı hangisidir?", "secenekler": ["Photoshop", "GIMP", "Affinity Photo", "Canva"], "dogru": 0, "bilgi": "Photoshop, 30+ yıldır görsel düzenleme standardı."},
    {"soru": "Dünyanın en çok kullanılan vector graphics (vektör grafik) programı hangisidir?", "secenekler": ["Illustrator", "Inkscape", "Affinity Designer", "Figma"], "dogru": 0, "bilgi": "Adobe Illustrator, vektör tasarımında 30+ yıldır lider."},
    {"soru": "Dünyanın en çok kullanılan 3D modeling (3D modelleme) programı hangisidir?", "secenekler": ["Blender", "Maya", "3ds Max", "Cinema 4D"], "dogru": 0, "bilgi": "Blender, ücretsiz ve open source olmasına rağmen Hollywood'da kullanılıyor."},
    {"soru": "Dünyanın en çok kullanılan game engine (oyun motoru) hangisidir?", "secenekler": ["Unity", "Unreal Engine", "Godot", "GameMaker"], "dogru": 0, "bilgi": "Unity, 1.5 milyon+ developer ile en çok kullanılan motor."},
    {"soru": "Dünyanın en çok kullanılan game development (oyun geliştirme) dili hangisidir?", "secenekler": ["C#", "C++", "Lua", "GDScript"], "dogru": 0, "bilgi": "C#, Unity ile birlikte oyun geliştirme standardı."},
    {"soru": "Dünyanın en çok kullanılan mobile app development (mobil uygulama geliştirme) aracı hangisidir?", "secenekler": ["Flutter", "React Native", "SwiftUI", "Kotlin Multiplatform"], "dogru": 0, "bilgi": "Flutter, Google tarafından geliştirildi ve hızla büyüyor."},
    {"soru": "Dünyanın en çok kullanılan desktop app development (masaüstü uygulama geliştirme) aracı hangisidir?", "secenekler": ["Electron", "Tauri", "Qt", "WPF"], "dogru": 0, "bilgi": "Electron, VS Code ve Discord gibi popüler uygulamaların altyapısı."},
    {"soru": "Dünyanın en çok kullanılan web development (web geliştirme) dili hangisidir?", "secenekler": ["JavaScript", "Python", "PHP", "Ruby"], "dogru": 0, "bilgi": "JavaScript, tarayıcının dili olduğu için en çok kullanılan dil."},
    {"soru": "Dünyanın en çok kullanılan data science (veri bilimi) dili hangisidir?", "secenekler": ["Python", "R", "Julia", "SQL"], "dogru": 0, "bilgi": "Python, pandas, numpy ve scikit-learn ile veri biliminde hakim."},
    {"soru": "Dünyanın en çok kullanılan machine learning (makine öğrenmesi) framework'ü hangisidir?", "secenekler": ["TensorFlow", "PyTorch", "Keras", "scikit-learn"], "dogru": 0, "bilgi": "TensorFlow, Google tarafından geliştirildi ve endüstri standardı."},
    {"soru": "Dünyanın en çok kullanılan deep learning (derin öğrenme) framework'ü hangisidir?", "secenekler": ["PyTorch", "TensorFlow", "JAX", "MXNet"], "dogru": 0, "bilgi": "PyTorch, araştırma dünyasında hızla popülerleşti."},
    {"soru": "Dünyanın en çok kullanılan natural language processing (doğal dil işleme) kütüphanesi hangisidir?", "secenekler": ["spaCy", "NLTK", "Transformers", "Gensim"], "dogru": 0, "bilgi": "spaCy, üretim ortamları için en hızlı ve verimli NLP kütüphanesi."},
    {"soru": "Dünyanın en çok kullanılan computer vision (bilgisayarlı görü) kütüphanesi hangisidir?", "secenekler": ["OpenCV", "Pillow", "scikit-image", "SimpleITK"], "dogru": 0, "bilgi": "OpenCV, 25+ yıldır bilgisayarlı görü standardı."},
    {"soru": "Dünyanın en çok kullanılan data visualization (veri görselleştirme) kütüphanesi hangisidir?", "secenekler": ["Matplotlib", "Seaborn", "Plotly", "D3.js"], "dogru": 0, "bilgi": "Matplotlib, Python veri görselleştirmesinin temeli."},
    {"soru": "Dünyanın en çok kullanılan web scraping framework'ü hangisidir?", "secenekler": ["Scrapy", "Beautiful Soup", "Selenium", "Puppeteer"], "dogru": 0, "bilgi": "Scrapy, büyük ölçekli veri çekme projeleri için standard."},
    {"soru": "Dünyanın en çok kullanılan web framework'ü (Python) hangisidir?", "secenekler": ["Django", "Flask", "FastAPI", "Bottle"], "dogru": 0, "bilgi": "Django, 'batteries included' felsefesiyle Python web geliştirme standardı."},
    {"soru": "Dünyanın en çok kullanılan web framework'ü (Ruby) hangisidir?", "secenekler": ["Ruby on Rails", "Sinatra", "Hanami", "Grape"], "dogru": 0, "bilgi": "Rails, web geliştirme hızını 10x artıran framework."},
    {"soru": "Dünyanın en çok kullanılan web framework'ü (PHP) hangisidir?", "secenekler": ["Laravel", "Symfony", "CodeIgniter", "CakePHP"], "dogru": 0, "bilgi": "Laravel, elegan syntax ve developer experience ile PHP'nin favorisi."},
    {"soru": "Dünyanın en çok kullanılan web framework'ü (Java) hangisidir?", "secenekler": ["Spring Boot", "Jakarta EE", "Micronaut", "Quarkus"], "dogru": 0, "bilgi": "Spring Boot, enterprise Java geliştirme standardı."},
    {"soru": "Dünyanın en çok kullanılan web framework'ü (Go) hangisidir?", "secenekler": ["Gin", "Echo", "Fiber", "Chi"], "dogru": 0, "bilgi": "Gin, yüksek performanslı Go web API'leri için en popüler."},
    {"soru": "Dünyanın en çok kullanılan web framework'ü (Rust) hangisidir?", "secenekler": ["Actix Web", "Axum", "Rocket", "Warp"], "dogru": 0, "bilgi": "Actix Web, benchmark'larda en hızlı web framework'ü."},
    {"soru": "Dünyanın en çok kullanılan API gateway hangisidir?", "secenekler": ["Kong", "AWS API Gateway", "Tyk", "NGINX"], "dogru": 0, "bilgi": "Kong, 100 milyar+ API isteği işliyor."},
    {"soru": "Dünyanın en çok kullanılan message broker (mesaj aracısı) hangisidir?", "secenekler": ["Apache Kafka", "RabbitMQ", "NATS", "Redis Pub/Sub"], "dogru": 0, "bilgi": "Kafka, 100+ petabayt veri işleyen distributed event streaming platformu."},
    {"soru": "Dünyanın en çok kullanılan in-memory cache (bellek önbelleği) hangisidir?", "secenekler": ["Redis", "Memcached", "Hazelcast", "Aerospike"], "dogru": 0, "bilgi": "Redis, 100.000+ saniyede işleyebilen ultra hızlı veri yapısı."},
    {"soru": "Dünyanın en çok kullanılan search engine (arama motoru) hangisidir?", "secenekler": ["Elasticsearch", "Apache Solr", "MeiliSearch", "Typesense"], "dogru": 0, "bilgi": "Elasticsearch, 100+ petabayt veri üzerinde arama yapabilen dağıtık motor."},
    {"soru": "Dünyanın en çok kullanılan time series database (zaman serisi veritabanı) hangisidir?", "secenekler": ["InfluxDB", "TimescaleDB", "Prometheus", "QuestDB"], "dogru": 0, "bilgi": "InfluxDB, IoT ve monitoring için en popüler zaman serisi veritabanı."},
    {"soru": "Dünyanın en çok kullanılan graph database (grafik veritabanı) hangisidir?", "secenekler": ["Neo4j", "ArangoDB", "Amazon Neptune", "TigerGraph"], "dogru": 0, "bilgi": "Neo4j, sosyal ağlar ve öneri sistemleri için lider graph veritabanı."},
    {"soru": "Dünyanın en çok kullanılan key-value store (anahtar-değer deposu) hangisidir?", "secenekler": ["Redis", "DynamoDB", "etcd", "Riak"], "dogru": 0, "bilgi": "Redis, hem cache hem veritabanı olarak kullanılabilen çok amaçlı araç."},
    {"soru": "Dünyanın en çok kullanılan document store (belge deposu) hangisidir?", "secenekler": ["MongoDB", "CouchDB", "Firebase Firestore", "Amazon DocumentDB"], "dogru": 0, "bilgi": "MongoDB, JSON benzeri BSON formatında veri depolar."},
    {"soru": "Dünyanın en çok kullanılan relational database (ilişkisel veritabanı) hangisidir?", "secenekler": ["PostgreSQL", "MySQL", "MariaDB", "SQLite"], "dogru": 0, "bilgi": "PostgreSQL, JSONB desteği ile hem relational hem NoSQL gibi."},
    {"soru": "Dünyanın en çok kullanılan NewSQL veritabanı hangisidir?", "secenekler": ["CockroachDB", "TiDB", "YugabyteDB", "Vitess"], "dogru": 0, "bilgi": "CockroachDB, distributed SQL ile Google Spanner rakibi."},
    {"soru": "Dünyanın en çok kullanılan vector database (vektör veritabanı) hangisidir?", "secenekler": ["Pinecone", "Weaviate", "Milvus", "Qdrant"], "dogru": 0, "bilgi": "Pinecone, AI embedding'leri için özel olarak tasarlandı."},
    {"soru": "Dünyanın en çok kullanılan data lake (veri gölü) platformu hangisidir?", "secenekler": ["Databricks", "Snowflake", "Apache Hadoop", "Amazon S3"], "dogru": 0, "bilgi": "Databricks, lakehouse konseptiyle veri ve AI'ı birleştiriyor."},
    {"soru": "Dünyanın en çok kullanılan data warehouse (veri ambarı) platformu hangisidir?", "secenekler": ["Snowflake", "BigQuery", "Redshift", "Databricks"], "dogru": 0, "bilgi": "Snowflake, cloud-native yapısıyla veri ambarı pazarında lider."},
    {"soru": "Dünyanın en çok kullanılan ETL (dönüşüm) aracı hangisidir?", "secenekler": ["Apache Airflow", "dbt", "Apache Spark", "Talend"], "dogru": 0, "bilgi": "Airflow, workflow orchestration için open source standart."},
    {"soru": "Dünyanın en çok kullanılan BI (iş zekası) aracı hangisidir?", "secenekler": ["Power BI", "Tableau", "Looker", "Qlik"], "dogru": 0, "bilgi": "Power BI, Microsoft ekosistemiyle entegrasyon sayesinde lider."},
    {"soru": "Dünyanın en çok kullanılan data catalog (veri kataloğu) aracı hangisidir?", "secenekler": ["Alation", "Collibra", "Apache Atlas", "DataHub"], "dogru": 0, "bilgi": "Alation, veri keşfi ve governance'da enterprise lider."},
    {"soru": "Dünyanın en çok kullanılan data quality (veri kalitesi) aracı hangisidir?", "secenekler": ["Great Expectations", "dbt tests", "Monte Carlo", "Anomalo"], "dogru": 0, "bilgi": "Great Expectations, Python tabanlı data validation standardı."},
    {"soru": "Dünyanın en çok kullanılan ML platformu hangisidir?", "secenekler": ["MLflow", "Kubeflow", "Weights & Biases", "Neptune.ai"], "dogru": 0, "bilgi": "MLflow, open source ML lifecycle management için standard."},
    {"soru": "Dünyanın en çok kullanılan feature store (özellik deposu) hangisidir?", "secenekler": ["Feast", "Tecton", "Hopsworks", "OpenMLDB"], "dogru": 0, "bilgi": "Feast, open source feature store ile ML feature'larını yönetiyor."},
    {"soru": "Dünyanın en çok kullanılan model registry (model kayıt defteri) hangisidir?", "secenekler": ["MLflow Model Registry", "Neptune.ai", "Weights & Biases", "Valohai"], "dogru": 0, "bilgi": "MLflow, model versiyonlama ve deployment için open source standard."},
    {"soru": "Dünyanın en çok kullanılan prompt engineering aracı hangisidir?", "secenekler": ["PromptFlow", "LangChain", "LlamaIndex", "Semantic Kernel"], "dogru": 0, "bilgi": "PromptFlow, Azure ile entegre prompt management aracı."},
    {"soru": "Dünyanın en çok kullanılan LLM framework'ü hangisidir?", "secenekler": ["LangChain", "LlamaIndex", "Haystack", "Semantic Kernel"], "dogru": 0, "bilgi": "LangChain, LLM uygulamaları geliştirmek için en popüler framework."},
    {"soru": "Dünyanın en çok kullanılan vector embedding (ktör gömme) modeli hangisidir?", "secenekler": ["OpenAI Embeddings", "Sentence-BERT", "Cohere Embed", "Voyage AI"], "dogru": 0, "bilgi": "OpenAI Embeddings, text-embedding-ada-002 ile endüstri standardı."},
    {"soru": "Dünyanın en çok kullanılan RAG (retrieval augmented generation) aracı hangisidir?", "secenekler": ["LangChain", "LlamaIndex", "Haystack", "Semantic Kernel"], "dogru": 0, "bilgi": "LangChain, RAG pipeline'ları oluşturmak için en popüler."},
    {"soru": "Dünyanın en çok kullanılan AI agent (yapay zeka ajanı) framework'ü hangisidir?", "secenekler": ["AutoGen", "LangGraph", "CrewAI", "OpenAI Assistants API"], "dogru": 0, "bilgi": "AutoGen, Microsoft tarafından multi-agent conversation için geliştirildi."},
    {"soru": "Dünyanın en çok kullanılan fine-tuning (ince ayar) aracı hangisidir?", "secenekler": ["OpenAI Fine-tuning API", "Hugging Face", "Axolotl", "Unsloth"], "dogru": 0, "bilgi": "OpenAI Fine-tuning API, GPT modellerini özel verilerle eğitmek için."},
    {"soru": "Dünyanın en çok kullanılan AI safety (yapay zeka güvenliği) aracı hangisidir?", "secenekler": ["Guardrails AI", "NVIDIA NeMo Guardrails", "LLM Guard", "Rebuff"], "dogru": 0, "bilgi": "Guardrails AI, LLM çıktılarını doğrulamak ve filtrelemek için."},
    {"soru": "Dünyanın en çok kullanılan AI evaluation (değerlendirme) aracı hangisidir?", "secenekler": ["DeepEval", "Ragas", "TruLens", "LangSmith"], "dogru": 0, "bilgi": "DeepEval, LLM uygulamalarını test etmek için open source değerlendirme çerçevesi."},
    {"soru": "Dünyanın en çok kullanılan observability (gözlemlenebilirlik) platformu hangisidir?", "secenekler": ["Datadog", "New Relic", "Grafana", "Splunk"], "dogru": 0, "bilgi": "Datadog, 25.000+ müşteri ile full-stack observability'de lider."},
    {"soru": "Dünyanın en çok kullanılan cost management (maliyet yönetimi) aracı hangisidir?", "secenekler": ["Infracost", "Kubecost", "CloudHealth", "Spot.io"], "dogru": 0, "bilgi": "Infracost, pull request'lerde altyapı maliyet tahminleri yapıyor."},
    {"soru": "Dünyanın en çok kullanılan FinOps aracı hangisidir?", "secenekler": ["CloudZero", "Vantage", "OpenCost", "Kubecost"], "dogru": 0, "bilgi": "CloudZero, cloud maliyetlerini.business context ile ilişkilendiriyor."},
    {"soru": "Dünyanın en çok kullanılan green computing (yeşil bilişim) aracı hangisidir?", "secenekler": ["Cloud Carbon Footprint", "GreenFrame", "Kepler", "Carbonilytics"], "dogru": 0, "bilgi": "Cloud Carbon Footprint, bulut karbon emisyonlarını ölçüyor."},
    {"soru": "Dünyanın en çok kullanılan platform engineering (platform mühendisliği) aracı hangisidir?", "secenekler": ["Backstage", "Humanitec", "Port", "Cortex"], "dogru": 0, "bilgi": "Backstage, Spotify tarafından geliştirilen internal developer portal."},
    {"soru": "Dünyanın en çok kullanılan dev portal (geliştirici portalı) hangisidir?", "secenekler": ["Backstage", "Port", "Cortex", "OpsLevel"], "dogru": 0, "bilgi": "Backstage, 2.500+ şirket tarafından internal developer portal olarak kullanılıyor."},
    {"soru": "Dünyanın en çok kullanılan SRE (site reliability engineering) aracı hangisidir?", "secenekler": ["PagerDuty", "Blameless", "Rootly", "Slothy"], "dogru": 0, "bilgi": "PagerDuty, SRE ekipleri için incident management standardı."},
    {"soru": "Dünyanın en çok kullanılan cost optimization (maliyet optimizasyonu) aracı hangisidir?", "secenekler": ["Spot.io", "Cast AI", "Zesty", "Kubecost"], "dogru": 0, "bilgi": "Spot.io, spot instance'ları %90'a varan oranda ucuzlatıyor."},
    {"soru": "Dünyanın en çok kullanılan governance (yönetişim) aracı hangisidir?", "secenekler": ["Open Policy Agent", "Kyverno", "Conftest", "Sentry"], "dogru": 0, "bilgi": "OPA (Open Policy Agent), policy-as-code için CNCF graduated proje."},
    {"soru": "Dünyanın en çok kullanılan compliance (uyumluluk) aracı hangisidir?", "secenekler": ["Vanta", "Drata", "Secureframe", "Sprinto"], "dogru": 0, "bilgi": "Vanta, SOC 2 ve ISO 27001 uyumluluğunu otomatikleştiriyor."},
    {"soru": "Dünyanın en çok kullanılan threat detection (tehdit algılama) aracı hangisidir?", "secenekler": ["CrowdStrike", "SentinelOne", "Microsoft Defender", "Carbon Black"], "dogru": 0, "bilgi": "CrowdStrike, 23.000+ müşteri ile endpoint security'de lider."},
    {"soru": "Dünyanın en çok kullanılan vulnerability scanner (açıklık tarayıcı) hangisidir?", "secenekler": ["Nessus", "Qualys", "OpenVAS", "Nmap"], "dogru": 0, "bilgi": "Nessus, 30.000+ kuruluş tarafından kullanılıyor."},
    {"soru": "Dünyanın en çok kullanılan SIEM (güvenlik olay ve olay yönetimi) platformu hangisidir?", "secenekler": ["Splunk", "Microsoft Sentinel", "IBM QRadar", "Elastic SIEM"], "dogru": 0, "bilgi": "Splunk, 15.000+ kuruluş tarafından security monitoring için kullanılıyor."},
    {"soru": "Dünyanın en çok kullanılan DDoS protection (koruma) sağlayıcısı hangisidir?", "secenekler": ["Cloudflare", "Akamai", "AWS Shield", "Imperva"], "dogru": 0, "bilgi": "Cloudflare, 20%+ internet trafiğini koruyor."},
    {"soru": "Dünyanın en çok kullanılan WAF (web application firewall) hangisidir?", "secenekler": ["Cloudflare WAF", "AWS WAF", "Imperva", "F5"], "dogru": 0, "bilgi": "Cloudflare WAF, 32+ milyon internet varlığını koruyor."},
    {"soru": "Dünyanın en çok kullanılan CDN (içerik dağıtım ağı) sağlayıcısı hangisidir?", "secenekler": ["Cloudflare", "Akamai", "Fastly", "AWS CloudFront"], "dogru": 0, "bilgi": "Cloudflare, 300+ şehirde PoP ile en geniş ağa sahip."},
    {"soru": "Dünyanın en çok kullanılan DNS sağlayıcısı hangisidir?", "secenekler": ["Cloudflare DNS", "Google DNS", "Quad9", "OpenDNS"], "dogru": 0, "bilgi": "Cloudflare DNS, 1.1.1.1 ile en hızlı public DNS."},
    {"soru": "Dünyanın en çok kullanılan DDoS attack (saldırı) türü hangisidir?", "secenekler": ["Volumetric", "Protocol", "Application Layer", "Amplification"], "dogru": 0, "bilgi": "Volumetric saldırılar, bant genişliğini doldurarak sistemi çökertir."},
    {"soru": "Dünyanın en çok kullanılan phishing (oltalama) tekniği hangisidir?", "secenekler": ["Email phishing", "Spear phishing", "Whaling", "Smishing"], "dogru": 0, "bilgi": "Email phishing, en yaygın ve etkili siber saldırı tekniği."},
    {"soru": "Dünyanın en çok kullanılan password cracking (şifre kırma) tekniği hangisidir?", "secenekler": ["Brute force", "Dictionary attack", "Rainbow table", "Credential stuffing"], "dogru": 0, "bilgi": "Brute force, tüm olasılıkları deneyerek şifreyi kırmaya çalışır."},
    {"soru": "Dünyanın en çok kullanılan encryption (şifreleme) algoritması hangisidir?", "secenekler": ["AES", "RSA", "ChaCha20", "Blowfish"], "dogru": 0, "bilgi": "AES, 256-bit ile dünyanın en güvenli şifreleme algoritması."},
    {"soru": "Dünyanın en çok kullanılan hash algoritması hangisidir?", "secenekler": ["SHA-256", "MD5", "bcrypt", "Argon2"], "dogru": 0, "bilgi": "SHA-256, Bitcoin madenciliği ve dijital imzalarda kullanılır."},
    {"soru": "Dünyanın en çok kullanılan two-factor authentication (iki faktörlü kimlik doğrulama) yöntemi hangisidir?", "secenekler": ["TOTP (Authenticator uygulaması)", "SMS", "Email", "FIDO2/WebAuthn"], "dogru": 0, "bilgi": "TOTP, Google Authenticator ve Authy gibi uygulamalarla popüler."},
    {"soru": "Dünyanın en çok kullanılan SSO (tek oturum açma) sağlayıcısı hangisidir?", "secenekler": ["Okta", "Azure AD", "Auth0", "OneLogin"], "dogru": 0, "bilgi": "Okta, 15.000+ müşteri ile enterprise SSO'da lider."},
    {"soru": "Dünyanın en çok kullanılan identity provider (kimlik sağlayıcı) hangisidir?", "secenekler": ["Okta", "Azure AD", "Auth0", "Ping Identity"], "dogru": 0, "bilgi": "Okta, 11.000+ uygulama entegrasyonu ile lider."},
    {"soru": "Dünyanın en çok kullanılan PAM (privileged access management) aracı hangisidir?", "secenekler": ["CyberArk", "BeyondTrust", "Delinea", "HashiCorp Vault"], "dogru": 0, "bilgi": "CyberArk, privileged account security'de global lider."},
    {"soru": "Dünyanın en çok kullanılan SIEM (güvenlik olay yönetimi) çözümlerinden hangisi open source'dur?", "secenekler": ["Wazuh", "OSSEC", "Snort", "Suricata"], "dogru": 0, "bilgi": "Wazuh, endpoint security ve SIEM için open source çözüm."},
    {"soru": "Dünyanın en çok kullanılan IDS/IPS (saldırı tespit önleme) sistemi hangisidir?", "secenekler": ["Snort", "Suricata", "Zeek", "OSSEC"], "dogru": 0, "bilgi": "Snort, 6 milyon+ indirme ile open source IDS standardı."},
    {"soru": "Dünyanın en çok kullanılan penetration testing (sızma testi) aracı hangisidir?", "secenekler": ["Kali Linux", "Metasploit", "Burp Suite", "Nmap"], "dogru": 0, "bilgi": "Kali Linux, 600+ güvenlik aracıyla pen test distro'su."},
    {"soru": "Dünyanın en çok kullanılan SIEM çözümü (ticari) hangisidir?", "secenekler": ["Splunk", "IBM QRadar", "LogRhythm", "Exabeam"], "dogru": 0, "bilgi": "Splunk, 15.000+ kuruluş tarafından kullanılıyor."},
    {"soru": "Dünyanın en çok kullanılan SOC (security operations center) aracı hangisidir?", "secenekler": ["Splunk SOAR", "Palo Alto XSOAR", "Swimlane", "Tines"], "dogru": 0, "bilgi": "Splunk SOAR, security orchestration ve otomasyon için lider."},
    {"soru": "Dünyanın en çok kullanılan threat intelligence (tehdit istihbaratı) platformu hangisidir?", "secenekler": ["Recorded Future", "Mandiant", "CrowdStrike Intelligence", "Palo Alto Unit 42"], "dogru": 0, "bilgi": "Recorded Future, yapay zeka destekli threat intelligence'da lider."},
    {"soru": "Dünyanın en çok kullanılan vulnerability management (açıklık yönetimi) platformu hangisidir?", "secenekler": ["Tenable", "Qualys", "Rapid7", "OpenVAS"], "dogru": 0, "bilgi": "Tenable, Nessus ile vulnerability management'da 30+ yıldır lider."},
    {"soru": "Dünyanın en çok kullanılan endpoint protection (son nokta koruma) platformu hangisidir?", "secenekler": ["CrowdStrike", "SentinelOne", "Microsoft Defender", "Carbon Black"], "dogru": 0, "bilgi": "CrowdStrike, Falcon platformu ile AI-powered endpoint protection."},
    {"soru": "Dünyanın en çok kullanılan cloud security (bulut güvenlik) platformu hangisidir?", "secenekler": ["Wiz", "Lacework", "Prisma Cloud", "Orca Security"], "dogru": 0, "bilgi": "Wiz, 2 yıl içinde 1 milyar dolar değerlemeye ulaştı."},
    {"soru": "Dünyanın en çok kullanılan data loss prevention (veri kaybı önleme) aracı hangisidir?", "secenekler": ["Symantec DLP", "McAfee DLP", "Digital Guardian", "Forcepoint"], "dogru": 0, "bilgi": "Symantec DLP, Fortune 500 şirketlerinin %70'inde kullanılır."},
    {"soru": "Dünyanın en çok kullanılan email security (e-posta güvenlik) platformu hangisidir?", "secenekler": ["Proofpoint", "Mimecast", "Barracuda", "Microsoft Defender"], "dogru": 0, "bilgi": "Proofpoint, 50.000+ müşteri ile email security'de lider."},
    {"soru": "Dünyanın en çok kullanılan network security (ağ güvenlik) platformu hangisidir?", "secenekler": ["Palo Alto Networks", "Fortinet", "Cisco", "Check Point"], "dogru": 0, "bilgi": "Palo Alto Networks, next-generation firewall pazarında lider."},
    {"soru": "Dünyanın en çok kullanılan application security (uygulama güvenlik) aracı hangisidir?", "secenekler": ["Snyk", "Veracode", "Checkmarx", "SonarQube"], "dogru": 0, "bilgi": "Snyk, developer-first security yaklaşımıyla 2 milyon+ geliştirici."},
    {"soru": "Dünyanın en çok kullanılan API security (API güvenlik) platformu hangisidir?", "secenekler": ["Salt Security", "Noname Security", "Cequence", "Wallarm"], "dogru": 0, "bilgi": "Salt Security, API discovery ve attack detection'da lider."},
    {"soru": "Dünyanın en çok kullanılan container security (konteyner güvenlik) platformu hangisidir?", "secenekler": ["Aqua Security", "Twistlock", "Sysdig", "NeuVector"], "dogru": 0, "bilgi": "Aqua Security, container ve cloud native security'de lider."},
    {"soru": "Dünyanın en çok kullanılan DevSecOps aracı hangisidir?", "secenekler": ["GitLab", "GitHub Advanced Security", "Snyk", "SonarQube"], "dogru": 0, "bilgi": "GitLab, built-in security scanning ile DevSecOps'ta lider."},
    {"soru": "Dünyanın en çok kullanılan supply chain security (tedarik zinciri güvenlik) aracı hangisidir?", "secenekler": ["SLSA", "Sigstore", "in-toto", "Dependency-Track"], "dogru": 0, "bilgi": "SLSA (Supply-chain Levels for Software Artifacts), Google tarafından geliştirildi."},
    {"soru": "Dünyanın en çok kullanılan zero trust (sıfır güven) platformu hangisidir?", "secenekler": ["Zscaler", "Cloudflare Access", "Okta", "BeyondCorp"], "dogru": 0, "bilgi": "Zscaler, 400+ müşteri ile zero trust network access'de lider."},
    {"soru": "Dünyanın en çok kullanılan XDR (extended detection and response) platformu hangisidir?", "secenekler": ["CrowdStrike", "SentinelOne", "Palo Alto Cortex", "Microsoft 365 Defender"], "dogru": 0, "bilgi": "CrowdStrike Falcon XDR, unified platform ile lider."},
    {"soru": "Dünyanın en çok kullanılan MDR (managed detection and response) sağlayıcısı hangisidir?", "secenekler": ["CrowdStrike", "SentinelOne", "Secureworks", "Arctic Wolf"], "dogru": 0, "bilgi": "CrowdStrike, managed threat hunting'da global lider."},
    {"soru": "Dünyanın en çok kullanılan SOAR (security orchestration, automation and response) aracı hangisidir?", "secenekler": ["Splunk SOAR", "Palo Alto XSOAR", "Swimlane", "Tines"], "dogru": 0, "bilgi": "Splunk SOAR, 1.500+ entegrasyon ile security automation'da lider."},
    {"soru": "Dünyanın en çok kullanılan threat hunting (tehdit avı) aracı hangisidir?", "secenekler": ["Velociraptor", "GRR Rapid Response", "OSQuery", "osquery"], "dogru": 0, "bilgi": "Velociraptor, endpoint visibility ve threat hunting için open source."},
    {"soru": "Dünyanın en çok kullanılan digital forensics (dijital adli tıp) aracı hangisidir?", "secenekler": ["Autopsy", "FTK", "EnCase", "X-Ways"], "dogru": 0, "bilgi": "Autopsy, open source digital forensics platformu."},
    {"soru": "Dünyanın en çok kullanılan incident response (olay müdahale) aracı hangisidir?", "secenekler": ["PagerDuty", "VictorOps", "BigPanda", "Resolve Systems"], "dogru": 0, "bilgi": "PagerDuty, 70.000+ müşteri ile incident management'da lider."},
    {"soru": "Dünyanın en çok kullanılan deception technology (aldatma teknolojisi) platformu hangisidir?", "secenekler": ["Attivo Networks", "Illusive Networks", "CounterCraft", "TrapX"], "dogru": 0, "bilgi": "Attivo Networks, Active Directory koruması için lider."},
    {"soru": "Dünyanın en çok kullanılanICS/SCADA security (endüstriyel kontrol sistemleri güvenlik) platformu hangisidir?", "secenekler": ["Claroty", "Nozomi Networks", "Dragos", "Fortinet"], "dogru": 0, "bilgi": "Claroty, OT ve IoT security'de global lider."},
    {"soru": "Dünyanın en çok kullanılanIoT security (nesnelerin interneti güvenlik) platformu hangisidir?", "secenekler": ["Armis", "Claroty", "Nozomi Networks", "Forescout"], "dogru": 0, "bilgi": "Armis, 1 milyar+ cihazı izleyen IoT security platformu."},
    {"soru": "Dünyanın en çok kullanılan automotive security (otomotiv güvenlik) platformu hangisidir?", "secenekler": ["Argus", "Upstream", "Karamba Security", "C2A Security"], "dogru": 0, "bilgi": "Argous Connected Vehicle Security, 300+ milyon aracın bağlantısını koruyor."},
    {"soru": "Dünyanın en çok kullanılan aviation security (havacılık güvenlik) platformu hangisidir?", "secenekler": ["Akamai", "Cloudflare", "Imperva", "Fastly"], "dogru": 0, "bilgi": "Havacılık sektöründe web application firewall ve DDoS koruması kritik."},
    {"soru": "Dünyanın en çok kullanılan healthcare security (sağlık hizmetleri güvenlik) platformu hangisidir?", "secenekler": ["Clearwater", "Medigate", "CyberMDX", "Vicarius"], "dogru": 0, "bilgi": "Clearwater, healthcare cybersecurity risk management'da lider."},
    {"soru": "Dünyanın en çok kullanılan financial security (finansal güvenlik) platformu hangisidir?", "secenekler": ["NICE Actimize", "Featurespace", "Feedzai", "SAS"], "dogru": 0, "bilgi": "NICE Actimize, fraud detection veAML'de global lider."},
    {"soru": "Dünyanın en çok kullanılan retail security (perakende güvenlik) platformu hangisidir?", "secenekler": ["Forter", "Riskified", "Signifyd", "Kount"], "dogru": 0, "bilgi": "Forter, real-time fraud prevention ile perakende güvenliğinde lider."},
    {"soru": "Dünyanın en çok kullanılan education security (eğitim güvenlik) platformu hangisidir?", "secenekler": ["Lightspeed Systems", "Securly", "Gaggle", "GoGuardian"], "dogru": 0, "bilgi": "Lightspeed Systems, 20.000+ okulda student safety çözümleri sunuyor."},
    {"soru": "Dünyanın en çok kullanılan government security (hükümet güvenlik) platformu hangisidir?", "secenekler": ["Palantir", "Recorded Future", "Mandiant", "CrowdStrike"], "dogru": 0, "bilgi": "Palantir, US government ve müttefik ülkeler için data analytics ve security."},
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
