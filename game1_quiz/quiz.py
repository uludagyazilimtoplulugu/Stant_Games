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
    {"soru": "Linux çekirdeğinin ilk sürümü kaç satır koddan oluşuyordu?", "secenekler": ["~10.000", "~240.000", "~1.000.000", "~500.000"], "dogru": 0, "bilgi": "Linus Torvalds 1991'de yazdı. İlk sürüm sadece 10.239 satırdı."},
    {"soru": "Google'ın arama motoru ilk hangi dilde yazıldı?", "secenekler": ["Python", "Java", "C++", "Lisp"], "dogru": 2, "bilgi": "Larry Page ve Sergey Brin C++ ile yazdı. İlk adı 'BackRub' idi."},
    {"soru": "Bir milyar satır kod hangi projede bulunur?", "secenekler": ["Windows 10", "Google Arama", "Facebook", "NASA Uzay Mekiği"], "dogru": 1, "bilgi": "Google'ın tüm kod tabanı yaklaşık 2 milyar satırdır."},
    {"soru": "En çok satır koda sahip oyun hangisidir?", "secenekler": ["GTA V", "Cyberpunk 2077", "Red Dead Redemption 2", "Star Citizen"], "dogru": 3, "bilgi": "Star Citizen 50+ milyon satır kod ile rekor kırdı."},
    {"soru": "Programlama dillerinde 'bug' terimi nereden geliyor?", "secenekler": ["Böcek hatası", "Hata raporu", "Eski Almanca", "Kod satırı"], "dogru": 0, "bilgi": "1947'de Grace Hopper bilgisayara yapışan bir böcek buldu."},
    {"soru": "Python'da 'self' anahtar kelimesi ne anlama gelir?", "secenekler": ["Sınıf自身的 referans", "Değişken adı", "Fonksiyon çağrısı", "Modül adı"], "dogru": 0, "bilgi": "self, sınıf içindeki instance'ı temsil eder. Zorunlu değildir ama convention'dır."},
    {"soru": "Bir API'ın 'REST' olmasının şartı nedir?", "secenekler": ["HTTP kullanması", "JSON döndürmesi", "6 mimari kurala uyması", "OAuth kullanması"], "dogru": 2, "bilgi": "REST, 6 mimari kısıta sahiptir. JSON veya XML dönüşü zorunlu değildir."},
    {"soru": "Git'te 'rebase' ile 'merge' arasındaki fark nedir?", "secenekler": ["Rebase geçmişi temizler", "Merge daha hızlı", "İkisi aynı", "Rebase sadece Linux'ta çalışır"], "dogru": 0, "bilgi": "Rebase, commit geçmişini düzleştirir. Merge ise Dal oluşturmaya devam eder."},
    {"soru": "Docker'ın temel mantığı nedir?", "secenekler": ["VM oluşturmak", "Uygulamayı izole container'a koymak", "Veritabanını klonlamak", "Kod derlemek"], "dogru": 1, "bilgi": "Docker, uygulamaları ve bağımlılıklarını izole eder. VM'lere göre çok daha hafiftir."},
    {"soru": "Bir saniyede kaç tane JavaScript event loop'u çalışır?", "secenekler": ["Tek bir tane", "Çoklu", "Hiç", "Tarayıcıya göre değişir"], "dogru": 0, "bilgi": "JS tek thread'dir. Event loop, callback queue'dan sırayla işleri alır."},
    {"soru": "En çok CVE açığı bulunan yazılım hangisidir?", "secenekler": ["Windows", "Linux Kernel", "Apache", "WordPress"], "dogru": 0, "bilgi": "Windows, tarihte en fazla güvenlik açığı bulunan yazılımdır."},
    {"soru": "Stack Overflow'un kurucuları hangi siteden ilham aldı?", "secenekler": ["Wikipedia", "Expert Exchange", "Reddit", "Quora"], "dogru": 1, "bilgi": "Expert Exchange'in sinir bozucu ödeme duvarından bıkarak kuruldu."},
    {"soru": "En çok pull request'e sahip GitHub repoları hangileri?", "secenekler": ["React, Vue", "VS Code, Flutter", "Python, Django", "Linux, Kubernetes"], "dogru": 1, "bilgi": "VS Code ve Flutter topluluk tarafından sürekli geliştirilir."},
    {"soru": "MongoDB hangi veri yapısını kullanır?", "secenekler": ["Tablo", "JSON/BSON", "Ağaç", "Liste"], "dogru": 1, "bilgi": "MongoDB, BSON formatında document depolar. SQL tablosu yoktur."},
    {"soru": "Kubernetes hangi şirkette geliştirildi?", "secenekler": ["Google", "Microsoft", "Amazon", "Red Hat"], "dogru": 0, "bilgi": "Google'da Borg projesinin devamı olarak geliştirildi. 2014'te açık kaynak oldu."},
    {"soru": "React'te 'Virtual DOM' ne işe yarar?", "secenekler": ["Veritabanını önbelleğe almak", "Gerçek DOM'u hızlı güncellemek", "CSS'i yönetmek", "Router yapmak"], "dogru": 1, "bilgi": "Sanal DOM, değişiklikleri önce bellekte hesaplar, sonra minimum güncelleme yapar."},
    {"soru": "Yapay zeka modeli 'GPT-4'ün tahmini parametre sayısı nedir?", "secenekler": ["100 milyar", "1 trilyon+", "500 milyar", "10 milyar"], "dogru": 1, "bilgi": "OpenAI resmi olarak açıklamadı. Tahminler 1 trilyon civarında."},
    {"soru": "Rust dilinde 'ownership' sistemi neyi engeller?", "secenekler": ["Memory leak ve race condition", "Syntax hatası", "Compile hatası", "Runtime crash"], "dogru": 0, "bilgi": "Rust, compile-time'da memory safety sağlar. Garbage collector'a ihtiyaç duymaz."},
    {"soru": "Redis'in hız sırrı nedir?", "secenekler": ["Veritabanı_optimizasyonu", "RAM'de çalışması", "SSD kullanımı", "Özel donanım"], "dogru": 1, "bilgi": "Redis tamamen RAM'de çalışır. 100.000+ sorguyu saniyede işleyebilir."},
    {"soru": "Bir WordPress sitesi ortalama kaç KB ağırlığındadır?", "secenekler": ["~100 KB", "~500 KB", "~2 MB", "~10 MB"], "dogru": 3, "bilgi": "Ortalama WordPress sitesi 3MB+ yüklenir. Çoğu eklenti ve tema yüzünden."},
    {"soru": "En uzun kod adı hangi üründe kullanıldı?", "secenekler": ["Windows Vista", "Mac OS X Tiger", "Android Pie", "iOS 6"], "dogru": 0, "bilgi": "Windows Vista'nın kod adı 'Longhorn' idi ve 5 yıl gecikti."},
    {"soru": "Bir ‘Hello World’ programı kaç bayttan oluşabilir?", "secenekler": ["29 byte (x86 Linux)", "1 KB", "100 byte", "10 byte"], "dogru": 0, "bilgi": "x86 Linux'ta en küçük hello world 29 byte. Assembly ile yazılır."},
    {"soru": "CERN'deki ilk web sitesi hangi adresteydi?", "secenekler": ["info.cern.ch", "www.cern.ch", "web.cern.ch", "cern.org"], "dogru": 0, "bilgi": "Tim Berners-Lee 1991'de info.cern.ch adresini oluşturdu."},
    {"soru": "TensorFlow ve PyTorch arasında temel fark nedir?", "secenekler": ["TF statik, PyTorch dinamik graph", "İkisi aynı", "PyTorch daha yavaş", "TF açık kaynak değil"], "dogru": 0, "bilgi": "TensorFlow 1.x statik graph kullandı. PyTorch ise dinamik graph ile esneklik sağlar."},
    {"soru": "En çok indirilen npm paketi hangisidir?", "secenekler": ["lodash", "react", "left-pad", "express"], "dogru": 0, "bilgi": "Lodash, React'i geçerek en çok indirilen paket oldu."},
    {"soru": "Kuantum bilgisayar 'qubit' yerine hangi yapıyı kullanır?", "secenekler": ["Süperpozisyon", "Bit", "Byte", "Register"], "dogru": 0, "bilgi": "Qubit, 0 ve 1'in süperpozisyonunda olabilir. Geleneksel bit sadece birini tutar."},
    {"soru": "Siber güvenlikte 'SQL injection' nasıl engellenir?", "secenekler": ["Parametreli sorgu", "Antivirüs", "Firewall", "Şifreleme"], "dogru": 0, "bilgi": "Parametreli Prepared Statements kullanmak SQL injection'ı %100 engeller."},
    {"soru": "Fiber optik kablolar hangi prensiple çalışır?", "secenekler": ["Işık yansıması", "Elektrik akımı", "Manyetik alan", "Radyo dalgası"], "dogru": 0, "bilgi": "Total internal reflection ile ışık sinyali kilometrelerce kaybolmadan iletilir."},
    {"soru": "Hangisi real-time operational system değildir?", "secenekler": ["Windows 10", "RTLinux", "VxWorks", "FreeRTOS"], "dogru": 0, "bilgi": "Windows 10 real-time değildir. RTLinux, VxWorks real-time OS'tür."},
    {"soru": "Bir CPU'da 'cache miss' ne anlama gelir?", "secenekler": ["Veri L1/L2 cache'te yok", "CPU aşırı ısındı", "RAM dolu", "Fazla process çalışıyor"], "dogru": 0, "bilgi": "Cache miss, istenen veri önbellekte bulunamaz ve yavaş RAM'den okunur."},
    {"soru": "Linux'ta 'chmod 777' ne yapar?", "secenekler": ["Herkese tam yetki verir", "Dosyayı siler", "Yedek alır", "İzinleri kaldırır"], "dogru": 0, "bilgi": "777 = read+write+execute for owner/group/other. Güvenlik açığıdır, kullanılmamalı."},
    {"soru": "WebSocket ve HTTP arasındaki fark nedir?", "secenekler": ["WebSocket çift yönlü, HTTP tek yönlü", "İkisi aynı", "HTTP daha hızlı", "WebSocket eski"], "dogru": 0, "bilgi": "WebSocket sürekli açık bağlantı kurar. HTTP her istekte yeni bağlantı açar."},
    {"soru": "En uzun programlama dili ismi hangisidir?", "secenekler": ["Brainfuck", "COBOL", "ANSI Common Lisp", "Haskell"], "dogru": 2, "bilgi": "ANSI Common Lisp resmi olarak en uzun resmi dile sahiptir."},
    {"soru": "Bir SSD ile HDD arasındaki en belirgin fark nedir?", "secenekler": ["SSD mekanik parça içermez", "HDD daha hızlı", "SSD daha ucuz", "HDD daha dayanıklı"], "dogru": 0, "bilgi": "SSD'de hareketli parça yoktur. 10x daha hızlı, sessiz ve dayanıklıdır."},
    {"soru": "DevOps'un temel amacı nedir?", "secenekler": ["Geliştirme ve operasyonları birleştirmek", "Yeni programlama dili oluşturmak", "Veritabanı yönetmek", "Tasarım yapmak"], "dogru": 0, "bilgi": "DevOps, CI/CD pipeline ile yazılım teslimatını hızlandırır."},
    {"soru": "Linux'ta 'grep' komutu ne yapar?", "secenekler": ["Metin içinde arama yapar", "Dosya siler", "Dizin oluşturur", "İzin değiştirir"], "dogru": 0, "bilgi": "grep, regular expression ile dosya içeriklerinde arama yapar."},
    {"soru": "Git'te 'cherry-pick' ne işe yarar?", "secenekler": ["Belirli bir commit'i diğer dala taşımak", "Branch silmek", "Push yapmak", "Log görmek"], "dogru": 0, "bilgi": "Cherry-pick, belirli bir commit'i current branch'e ekler."},
    {"soru": "CDN'in açılımı ve görevi nedir?", "secenekler": ["Content Delivery Network - İçerik dağıtımı", "Code Development Node", "Central Database Network", "Cloud Deploy Network"], "dogru": 0, "bilgi": "CDN, statik dosyaları kullanıcılara en yakın sunucudan sunarak hız kazandırır."},
    {"soru": "Bir web sitesinin 'Core Web Vitals' metrikleri nelerdir?", "secenekler": ["LCP, FID, CLS", "FPS, DPI, PPI", "CPU, RAM, GPU", "GET, POST, PUT"], "dogru": 0, "bilgi": "LCP (yüklenme), FID (etkileşim), CLS (görsel kararlılık) Google sıralama faktörü."},
    {"soru": "NoSQL veritabanı neden tercih edilir?", "secenekler": ["Esnek şema ve yatay ölçekleme", "Daha güvenli", "Daha hızlı JOIN", "ACID garantisi"], "dogru": 0, "bilgi": "NoSQL, büyük veri ve esnek yapılar için idealdir. ACID yerine BASE modeli kullanır."},
    {"soru": "En çok bilinen sızıntı (data breach) hangisidir?", "secenekler": ["Equifax", "Heartland", "Yahoo", "Adobe"], "dogru": 2, "bilgi": "Yahoo 3 milyar hesabın sızdırıldığı en büyük sızıntı oldu."},
    {"soru": "Python'da 'list comprehension' nedir?", "secenekler": ["Tek satırda liste oluşturma", "Döngü yapısı", "Fonksiyon türü", "Sınıf tanımı"], "dogru": 0, "bilgi": "[x**2 for x in range(10)] şeklindedir. For döngüsüne göre 2x daha hızlıdır."},
    {"soru": "Hangi programlama dili 'en yavaş' olarak bilinir?", "secenekler": ["Python", "Perl", "Ruby", "Fortran"], "dogru": 0, "bilgi": "Python yavaştır ama C kütüphaneleriyle hız kazanır. Hızdan çok okunabilirlik önemlidir."},
    {"soru": "Bir SSH bağlantısının portu nedir?", "secenekler": ["22", "80", "443", "3306"], "dogru": 0, "bilgi": "SSH varsayılan olarak 22 portunu kullanır. HTTP 80, HTTPS 443, MySQL 3306."},
    {"soru": "Bulut bilişimde 'serverless' ne anlama gelir?", "secenekler": ["Sunucu yönetimi gerektirmez", "Sunucu yoktur", "Sadece frontend", "Yerel sunucu"], "dogru": 0, "bilgi": "Serverless'ta sunucu vardır ama siz yönetmezsiniz. AWS Lambda buna örnektir."},
    {"soru": "Bir SQL Injection saldırısında ' UNION ' neden kullanılır?", "secenekler": ["Birden fazla tabloyu birleştirmek için", "Verileri silmek için", "Şifre kırmak için", "Giriş yapmak için"], "dogru": 0, "bilgi": "UNION, saldırganın farklı tablolardan veri çekmesini sağlar."},
    {"soru": "En popüler statik site üreticisi (SSG) hangisidir?", "secenekler": ["Next.js", "Hugo", "Jekyll", "Gatsby"], "dogru": 1, "bilgi": "Hugo, Go ile yazılmıştır ve 1000'den fazla sayfayı saniyeler içinde derler."},
    {"soru": "Redis'in 'TTL' özelliği ne işe yarar?", "secenekler": ["Anahtarın ömrünü belirler", "Veritabanını yedekler", "Şifreleri çözer", "Bağlantı açar"], "dogru": 0, "bilgi": "TTL (Time To Live) ile anahtar belirli süre sonra otomatik silinir."},
    {"soru": "En hızlı JavaScript motoru hangisidir?", "secenekler": ["V8", "SpiderMonkey", "JavaScriptCore", "Chakra"], "dogru": 0, "bilgi": "V8, Google Chrome ve Node.js tarafından kullanılır. JIT compilation yapar."},
    {"soru": "Bir Docker container ile VM arasındaki fark nedir?", "secenekler": ["Container daha hafif, kernel paylaşır", "VM daha hızlı", "İkisi aynı", "Container GUI'ye sahip"], "dogru": 0, "bilgi": "Container OS seviyesinde sanallaştırır. VM donanım seviyesinde sanallaştırır."},
    {"soru": "En çok kullanılan CI/CD aracı hangisidir?", "secenekler": ["GitHub Actions", "Jenkins", "GitLab CI", "Travis CI"], "dogru": 0, "bilgi": "GitHub Actions, GitHub entegrasyonu sayesinde en hızlı büyüyen CI/CD aracı."},
    {"soru": "Bir web uygulamasında 'CORS' hatası ne anlama gelir?", "secenekler": ["Cross-Origin kaynak erişimi engellendi", "CSS hatası", "SQL hatası", "JS hatası"], "dogru": 0, "bilgi": "CORS, tarayıcının farklı origin'den gelen istekleri güvenlik nedeniyle engellemesidir."},
    {"soru": "Kuantum computing'de 'quantum supremacy' ne demektir?", "secenekler": ["Kuantum bilgisayarın klasik bilgisayarı geçmesi", "Yeni işlemci türü", "Şifreleme yöntemi", "Yazılım dili"], "dogru": 0, "bilgi": "Google 2019'da Sycamore işlemcisi ile 200 saniyede 10.000 yıl süren işlemi yaptı."},
    {"soru": "En çok star alan GitHub reposu hangisidir?", "secenekler": ["FreeCodeCamp", "VS Code", "React", "TensorFlow"], "dogru": 0, "bilgi": "FreeCodeCamp 350K+ ile en çok yıldız alan açık kaynak projesidir."},
    {"soru": "Bir frontend framework'ü olan Svelte'in farkı nedir?", "secenekler": ["Compile-time'da çalışır, runtime gerekmez", "Daha yavaş", "Sadece mobil için", "React tabanlı"], "dogru": 0, "bilgi": "Svelte, bileşenleri compile eder. Virtual DOM kullanmaz, doğrudan DOM'u değiştirir."},
    {"soru": "SQL'de 'JOIN' işlemi ne yapar?", "secenekler": ["Birden fazla tabloyu birleştirir", "Tabloyu siler", "Veri ekler", "İndeks oluşturur"], "dogru": 0, "bilgi": "JOIN, ortak alanlara göre tabloları birleştirir. INNER, LEFT, RIGHT, FULL türleri vardır."},
    {"soru": "Bir yapay zeka modelinin 'overfitting' olması ne demektir?", "secenekler": ["Eğitim verisine çok iyi uyuyor ama genelleme yapamıyor", "Çok yavaş", "Veri eksik", "Donanım yetersiz"], "dogru": 0, "bilgi": "Overfitting, modelin eğitim verisini ezberlemesi ama yeni verilerde başarısız olmasıdır."},
    {"soru": "Hangi dil 'Hello World' için en az kod satırı gerektirir?", "secenekler": ["Brainfuck", "Python", "C", "Java"], "dogru": 0, "bilgi": "Brainfuck'ta Hello World 8 karakterden oluşur ama okunması imkansızdır."},
    {"soru": "En çok kullanılan versiyon kontrol sistemi hangisidir?", "secenekler": ["Git", "SVN", "Mercurial", "Perforce"], "dogru": 0, "bilgi": "Git, Linus Torvalds tarafından Linux çekirdeği için geliştirildi."},
    {"soru": "Bir Redis verisi 'hash' olarak depolandığında avantajı nedir?", "secenekler": ["Alan bazlı erişim ve bellek tasarrufu", "Daha hızlı silme", "Şifreleme", "Yedekleme"], "dogru": 0, "bilgi": "Redis hash, küçük veriler için string'ten %60 daha az bellek kullanır."},
    {"soru": "Dünyanın en eski aktif programlama dili hangisidir?", "secenekler": ["Fortran", "COBOL", "Lisp", "BASIC"], "dogru": 0, "bilgi": "Fortran 1957'de yazıldı. Hala bilimsel hesaplamalarda kullanılır."},
    {"soru": "Bir API rate limiting'i neden uygulanır?", "secenekler": ["Sunucuyu aşırı yüklenmeden korumak", "Kullanıcı gizliliği", "Hız artırmak", "Veri şifrelemek"], "dogru": 0, "bilgi": "Rate limiting, istek sayısını sınırlandırarak DDoS saldırılarını ve aşırı kullanımı engeller."},
    {"soru": "Bir 'microservice' mimarisinin avantajı nedir?", "secenekler": ["Her servis bağımsız dağıtılabilir", "Daha az server", "Daha az kod", "Daha basit"], "dogru": 0, "bilgi": "Microservice'ler bağımsız geliştirilir, dağıtılır ve ölçeklendirilir."},
    {"soru": "En çok kullanılan veritabanı yönetim sistemi hangisidir?", "secenekler": ["MySQL", "PostgreSQL", "MongoDB", "SQLite"], "dogru": 0, "bilgi": "MySQL, Walmart, GitHub, Netflix gibi devler tarafından kullanılır."},
    {"soru": "Bir web sitesinin 'DOMContentLoaded' olayı ne zaman tetiklenir?", "secenekler": ["HTML parse edildiğinde", "Tüm resimler yüklendiğinde", "CSS yüklendiğinde", "Sayfa tamamen kapandığında"], "dogru": 0, "bilgi": "DOMContentLoaded, DOM ağacı hazır olduğunda tetiklenir. CSS/resim beklemez."},
    {"soru": "Bulut bilişimin 'IaaS' açılımı nedir?", "secenekler": ["Infrastructure as a Service", "Internet as a Service", "Integration as a Service", "Information as a Service"], "dogru": 0, "bilgi": "IaaS, sanal sunucu ve depolama hizmetidir. AWS EC2 buna örnektir."},
    {"soru": "Python'da 'decorator' ne işe yarar?", "secenekler": ["Fonksiyona ek işlevsellik katar", "Değişken tanımlar", "Sınıf oluşturur", "Hata yakalar"], "dogru": 0, "bilgi": "@timer gibi decorator'lar fonksiyonların çalışma süresini ölçebilir."},
    {"soru": "Linux'ta 'pipeline' (|) operatörü ne yapar?", "secenekler": ["Bir komutun çıktısını diğerine iletir", "Dosya siler", "Process öldürür", "Ağ bağlantısı kurar"], "dogru": 0, "bilgi": "ls | grep .py ile Python dosyalarını filtreleyebilirsin."},
    {"soru": "Bir Agile sprint'i genellikle ne kadar sürer?", "secenekler": ["1-4 hafta", "1 gün", "3 ay", "6 ay"], "dogru": 0, "bilgi": "Sprintler genellikle 2 hafta sürer. Ama 1-4 hafta arası değişebilir."},
    {"soru": "En çok kullanılan container registry hangisidir?", "secenekler": ["Docker Hub", "GitHub Packages", "AWS ECR", "Google Container Registry"], "dogru": 0, "bilgi": "Docker Hub, 10M+ resim ile en büyük container registry'dir."},
    {"soru": "Bir 'WebSocket' bağlantısı kaç TCP bağlantısı kullanır?", "secenekler": ["1", "2", "4", "Hiç"], "dogru": 0, "bilgi": "WebSocket, HTTP upgrade ile tek TCP bağlantısına dönüşür."},
    {"soru": "En hızlı büyüyen programlama dili hangisidir (2024)?", "secenekler": ["Rust", "Python", "TypeScript", "Go"], "dogru": 0, "bilgi": "Rust, 8 yıldır Stack Overflow'da 'en çok beğenilen dil' unvanını koruyor."},
    {"soru": "Bir 'load balancer' ne işe yarar?", "secenekler": ["Trafikleri sunuculara dağıtır", "Veritabanını yönetir", "Kod derler", "Dosya depolar"], "dogru": 0, "bilgi": "Load balancer, gelen istekleri sunuculara eşit dağıtarak performans sağlar."},
    {"soru": "Bir CSS 'grid' ile 'flexbox' arasındaki temel fark nedir?", "secenekler": ["Grid 2B, Flexbox 1B layout", "İkisi aynı", "Flexbox daha yeni", "Grid sadece mobilde çalışır"], "dogru": 0, "bilgi": "Flexbox tek eksende hizalama, Grid ise 2 boyutlu layout için kullanılır."},
    {"soru": "En çok bilinen DDoS saldırısı hangi yıl ve hangi siteye yapıldı?", "secenekler": ["2016 - Dyn DNS", "2020 - AWS", "2018 - Cloudflare", "2014 - Google"], "dogru": 0, "bilgi": "Mirai botnet 2016'da Dyn DNS'e saldırı düzenledi. Twitter, Netflix erişilemez oldu."},
    {"soru": "Bir 'CRON job' ne işe yarar?", "secenekler": ["Zamanlanmış görevleri çalıştırır", "Dosya siler", "Ağ bağlantısı kurar", "E-posta gönderir"], "dogru": 0, "bilgi": "Cron, Linux'ta belirli zaman aralıklarında otomatik görev çalıştırır."},
    {"soru": "TypeScript'in JavaScript'e göre avantajı nedir?", "secenekler": ["Statik tip kontrolü", "Daha hızlı çalışma", "Daha az kod", "Tarayıcı desteği"], "dogru": 0, "bilgi": "TypeScript, compile-time'da hata yakalar. JS'e göre %15 daha az bug oluşur."},
    {"soru": "Bir 'message queue' (RabbitMQ, Kafka) neden kullanılır?", "secenekler": ["Servisler arası asenkron iletişim", "Veritabanı yönetimi", "Frontend geliştirme", "Dosya depolama"], "dogru": 0, "bilgi": "Message queue, servisler arasındaki iletişimi多达队化 ederek dayanıklılık sağlar."},
    {"soru": "En uzun aktif olan web sitesi hangisidir?", "secenekler": ["CERN (1991)", "Yahoo (1994)", "Amazon (1994)", "eBay (1995)"], "dogru": 0, "bilgi": "CERN'ün ilk web sitesi 1991'den beri aktif: info.cern.ch"},
    {"soru": "Bir PostgreSQL veritabanının en büyük avantajı nedir?", "secenekler": ["ACID uyumluluğu ve JSON desteği", "En hızlı olması", "En az bellek kullanması", "Bedava olması"], "dogru": 0, "bilgi": "PostgreSQL, standart SQL'e JSONB desteği ile hem relational hem NoSQL gibidir."},
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
        self.sorular = random.sample(SORULAR, min(10, len(SORULAR)))
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
