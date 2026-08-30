"""
UYT Bilgi Yarismasi - Teknoloji, Yazilim ve Yapay Zeka
Uludag Yazilim Toplulugu stant oyunu
"""
import os
import random
import sqlite3
import threading
import tkinter as tk
from tkinter import messagebox

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skorlar.db")

SORULAR = [
    {
        "soru": "Yapay zeka terimini ilk kez kim kullanmistir?",
        "secenekler": ["Alan Turing", "John McCarthy", "Marvin Minsky", "Herbert Simon"],
        "dogru": 1
    },
    {
        "soru": "Python programlama dilinin yaraticisi kimdir?",
        "secenekler": ["James Gosling", "Guido van Rossum", "Bjarne Stroustrup", "Dennis Ritchie"],
        "dogru": 1
    },
    {
        "soru": "Derin ogrenme (deep learning) hangi yapiyi kullanir?",
        "secenekler": ["Dogrusal regresyon", "Yapay sinir aglari", "Karar agaclari", "K-means"],
        "dogru": 1
    },
    {
        "soru": "Git versiyon kontrol sistemi kim tarafindan gelistirilmistir?",
        "secenekler": ["Bill Gates", "Linus Torvalds", "Mark Zuckerberg", "Steve Jobs"],
        "dogru": 1
    },
    {
        "soru": "API ne anlama gelir?",
        "secenekler": ["Advanced Program Interface", "Application Programming Interface", "Automated Protocol Integration", "Advanced Processing Index"],
        "dogru": 1
    },
    {
        "soru": "HTML'in tam acilimi nedir?",
        "secenekler": ["Hyper Text Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyper Transfer Markup Language"],
        "dogru": 0
    },
    {
        "soru": "Bulut bilisim (cloud computing) orneklerinden hangisi dogrudur?",
        "secenekler": ["AWS, Azure, Google Cloud", "CPU, GPU, RAM", "LAN, WAN, MAN", "USB, HDMI, VGA"],
        "dogru": 0
    },
    {
        "soru": "ChatGPT hangi sirket tarafindan gelistirilmistir?",
        "secenekler": ["Google", "Meta", "OpenAI", "Microsoft"],
        "dogru": 2
    },
    {
        "soru": "JavaScript hangi yil icat edilmistir?",
        "secenekler": ["1995", "2000", "1985", "2010"],
        "dogru": 0
    },
    {
        "soru": "Yapay sinir aglarinda 'backpropagation' ne ise yarar?",
        "secenekler": ["Veri toplar", "Hata oranini geriye yayarak ogrenmeyi saglar", "Modeli egitir", "Sonucu gosterir"],
        "dogru": 1
    },
    {
        "soru": "Linux isletim sistemi hangi yil olusturulmustur?",
        "secenekler": ["1989", "1991", "1995", "2000"],
        "dogru": 1
    },
    {
        "soru": "SQL ne ise yarar?",
        "secenekler": ["Web sitesi tasarlar", "Veritabanini yonetir", "Grafik isler", "Ses isler"],
        "dogru": 1
    },
    {
        "soru": "Makine ogrenmesinde 'overfitting' ne demektir?",
        "secenekler": ["Modelin cok iyi ogrenmesi", "Modelin egitim verisine cok fazla uyum saglamasi", "Modelin hizi", "Modelin boyutu"],
        "dogru": 1
    },
    {
        "soru": "Docker ne islev gorur?",
        "secenekler": ["Kod yazar", "Konteyner tabanli uygulama calistirir", "Veritabani yonetir", "Dosyalari depolar"],
        "dogru": 1
    },
    {
        "soru": "React JS hangi sirket tarafindan gelistirilmistir?",
        "secenekler": ["Google", "Microsoft", "Meta (Facebook)", "Apple"],
        "dogru": 2
    },
    {
        "soru": "Yapay zeka etigi en cok hangi konuda tartismalara yol acmistir?",
        "secenekler": ["Hiz", "Maliyet", "Onyargi ve adalet", "Depolama"],
        "dogru": 2
    },
    {
        "soru": "REST API'de PUT ne ise yarar?",
        "secenekler": ["Yeni veri olusturur", "Mevcut veriyi gunceller", "Veriyi siler", "Veriyi listeler"],
        "dogru": 1
    },
    {
        "soru": "Blockchain teknolojisi aslinda ne icin gelistirilmistir?",
        "secenekler": ["Oyun oynamak", "Bitcoin kripto para birimi", "Film izlemek", "Muzik dinlemek"],
        "dogru": 1
    },
    {
        "soru": "Python'da bir liste olusturmak icin hangi isaret kullanilir?",
        "secenekler": ["Parantez ()", "Kose parantez []", "Suslu parantez {}", "Angle bracket <>"],
        "dogru": 1
    },
    {
        "soru": "Ozellikle yapay zeka ugulamalarinda kullanilan GPU'nun acilimi nedir?",
        "secenekler": ["General Processing Unit", "Graphics Processing Unit", "Global Program Unit", "General Purpose Unit"],
        "dogru": 1
    },
    {
        "soru": "Version control (versiyon kontrol) sistemi nedir?",
        "secenekler": ["Kod degisikliklerini takip eden sistem", "Sifre yoneten sistem", "Dosya silen sistem", "Internet baglantisi yoneten sistem"],
        "dogru": 0
    },
    {
        "soru": "NLP'nin tam acilimi nedir?",
        "secenekler": ["Natural Language Processing", "Network Layer Protocol", "New Learning Platform", "Node Logic Programming"],
        "dogru": 0
    },
    {
        "soru": "Siber guvenlikte 'phishing' ne demektir?",
        "secenekler": ["Ag hizi testi", "Kisa mesajla dolandiricilik", "Sifre guclendirmesi", "Veri sifreleme"],
        "dogru": 1
    },
    {
        "soru": "Machine Learning'de 'training data' ne anlama gelir?",
        "secenekler": ["Test verisi", "Egitim icin kullanilan veri", "Sonuc verisi", "Dosya verisi"],
        "dogru": 1
    },
    {
        "soru": "Hangisi bir programlama dili degildir?",
        "secenekler": ["Python", "Java", "HTML", "C++"],
        "dogru": 2
    },
    {
        "soru": "Yapay zeka dalinda 'Turing Testi' neyi olcer?",
        "secenekler": ["Hizi", "Bellek kapasitesini", "Makinanin insan gibi dusunup dusunemedigini", "Islem gucunu"],
        "dogru": 2
    },
    {
        "soru": "JavaScript'de 'DOM' ne anlama gelir?",
        "secenekler": ["Data Object Model", "Document Object Model", "Digital Output Module", "Dynamic Order Manager"],
        "dogru": 1
    },
    {
        "soru": "IoT'nin tam acilimi nedir?",
        "secenekler": ["Internet of Things", "Input of Technology", "Integration of Tools", "Interface of Transfer"],
        "dogru": 0
    },
    {
        "soru": "Yazilim gelistirmede 'agile' yontemi neye onem verir?",
        "secenekler": ["Uzun planlama", "Esnek ve iteratif gelistirme", "Tek seferde bitirme", "Dokumantasyon"],
        "dogru": 1
    },
    {
        "soru": "Neural network'te 'epoch' ne demektir?",
        "secenekler": ["Bir sure birimi", "Tum egitim verisinin bir kez islenmesi", "Bir hata degeri", "Bir katman sayisi"],
        "dogru": 1
    },
    {
        "soru": "Kubernetes (K8s) ne ise yarar?",
        "secenekler": ["Kod yazar", "Konteyner uygulamalarini ornekler", "Veritabani olusturur", "Web sitesi tasarlar"],
        "dogru": 1
    },
    {
        "soru": "C++ programlama dili hangi yil olusturulmustur?",
        "secenekler": ["1979", "1985", "1990", "1995"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'reinforcement learning' ne demektir?",
        "secenekler": ["Denetimli ogrenme", "Denetimsiz ogrenme", "Peyderpey ogrenme (odul ceza)", "Derin ogrenme"],
        "dogru": 2
    },
    {
        "soru": "Bir yazilim hatasini bulma islemine ne denir?",
        "secenekler": ["Compiling", "Debugging", "Running", "Testing"],
        "dogru": 1
    },
    {
        "soru": "Cloud storage orneklerinden hangisi dogrudur?",
        "secenekler": ["Google Drive, Dropbox, OneDrive", "CPU, RAM, SSD", "LAN, WAN, Bluetooth", "Python, Java, C++"],
        "dogru": 0
    },
    {
        "soru": "OpenCV kutuphanesi ne icin kullanilir?",
        "secenekler": ["Veri analizi", "Bilgisayarli goru", "Ses isleme", "Ag yonetimi"],
        "dogru": 1
    },
    {
        "soru": "Makine ogrenmesinde 'regresyon' problemi neyi cozer?",
        "secenekler": ["Siniflandirma", "Sayisal deger tahmini", "Gruplama", "Veri temizleme"],
        "dogru": 1
    },
    {
        "soru": "React'te 'component' ne anlama gelir?",
        "secenekler": ["Veri tabani", "Yeniden kullanilabilir UI bileseni", "API", "Dosya turu"],
        "dogru": 1
    },
    {
        "soru": "Siber saldiri turlerinden 'DDoS' ne demektir?",
        "secenekler": ["Dosya silme", "Daginik hizmet reddi", "Sifre kirma", "Veri calma"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'GAN' ne anlama gelir?",
        "secenekler": ["General Artificial Network", "Generative Adversarial Network", "Global Analysis Node", "Gradient Adaptive Network"],
        "dogru": 1
    },
    {
        "soru": "Python'da 'pip' ne ise yarar?",
        "secenekler": ["Kod editoru", "Paket yonetici", "Veritabani", "Tarayici"],
        "dogru": 1
    },
    {
        "soru": "React Native ne icin kullanilir?",
        "secenekler": ["Web sitesi yapmak", "Cep uygulamasi gelistirmek", "Veritabani olusturmak", "Oyun yapmak"],
        "dogru": 1
    },
    {
        "soru": "Makine ogrenmesinde 'feature' ne demektir?",
        "secenekler": ["Ozellik/degisken", "Hata", "Sonuc", "Dongu"],
        "dogru": 0
    },
    {
        "soru": "Ag ustunde veri iletisimi icin hangi protokol kullanilir?",
        "secenekler": ["HTTP", "USB", "HDMI", "VGA"],
        "dogru": 0
    },
    {
        "soru": "DevOps ne demektir?",
        "secenekler": ["Gelistirme ve calistirma isbirligi", "Veri analizi", "Grafik tasarim", "Ses kaydi"],
        "dogru": 0
    },
    {
        "soru": "Yapay zeka'da 'transformer' mimarisi ne icin onemlidir?",
        "secenekler": ["Goru isleme", "Dil modelleme (NLP)", "Ses tanima", "Robot kontrolu"],
        "dogru": 1
    },
    {
        "soru": "Python'da 'for dongusu' ne ise yarar?",
        "secenekler": ["Kosul kontrol eder", "Bir dizi uzerinde tekrarli islem yapar", "Fonksiyon tanimlar", "Hata yakalar"],
        "dogru": 1
    },
    {
        "soru": "Siber guvenlikte 'firewall' ne ise yarar?",
        "secenekler": ["Dosya depolar", "Ag guvenlik duvari olusturur", "Sifre olusturur", "E-posta gonderir"],
        "dogru": 1
    },
    {
        "soru": "Yazilim testinde 'unit test' ne demektir?",
        "secenekler": ["Tum sistemi test etme", "Tek bir bileseni test etme", "Kullanici testi", "Performans testi"],
        "dogru": 1
    },
    {
        "soru": "TensorFlow hangi sirket tarafindan gelistirilmistir?",
        "secenekler": ["Microsoft", "Apple", "Google", "Amazon"],
        "dogru": 2
    },
    {
        "soru": "JSON ne anlama gelir?",
        "secenekler": ["Java Source Object Notation", "JavaScript Object Notation", "Java Standard Output Network", "Joint System Object Notation"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'bias' (onyargi) ne demektir?",
        "secenekler": ["Modelin hizi", "Verilerdeki sistematik onyargi", "Modelin boyutu", "Egitim suresi"],
        "dogru": 1
    },
    {
        "soru": "Node.js ne icin kullanilir?",
        "secenekler": ["Masaustu uygulama", "Sunucu tarafinda JavaScript calistirma", "Mobil uygulama", "Grafik tasarim"],
        "dogru": 1
    },
    {
        "soru": "Bir yazilim projesinde 'code review' ne demektir?",
        "secenekler": ["Kod yazma", "Kodun baskisi tarafindan incelenmesi", "Kod silme", "Kod kopyalama"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'supervised learning' ne demektir?",
        "secenekler": ["Etiketlenmis verilerle ogrenme", "Etiketlenmemis verilerle ogrenme", "Kendi kendine ogrenme", "Peyderpey ogrenme"],
        "dogru": 0
    },
    {
        "soru": "SQL injection saldirisi nedir?",
        "secenekler": ["Ag hizi testi", "Veritabani uzerinden yapilan guvenlik acigi", "Sifre kirma", "E-posta dolandiriciligi"],
        "dogru": 1
    },
    {
        "soru": "Python'da 'class' ne anlama gelir?",
        "secenekler": ["Fonksiyon", "Sinif (nesne oriented programlama)", "Dongu", "Degisken"],
        "dogru": 1
    },
    {
        "soru": "CI/CD'nin acilimi nedir?",
        "secenekler": ["Central Intelligence / Central Data", "Continuous Integration / Continuous Delivery", "Computer Interface / Computer Design", "Code Import / Code Deploy"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'fine-tuning' ne demektir?",
        "secenekler": ["Modeli sifirdan olusturma", "Onceden egitilmis modeli ozel goreve gore ayarlama", "Modeli silme", "Modeli depolama"],
        "dogru": 1
    },
    {
        "soru": "GitHub ne icin kullanilir?",
        "secenekler": ["Sosyal medya", "Kod depolama ve isbirligi", "E-posta", "Alisveris"],
        "dogru": 1
    },
    {
        "soru": "Makine ogrenmesinde 'classification' problemi neyi cozer?",
        "secenekler": ["Sayisal deger tahmini", "Verileri siniflandirma", "Gruplama", "Veri temizleme"],
        "dogru": 1
    },
    {
        "soru": "WebSocket protokolü ne icin kullanilir?",
        "secenekler": ["Tek yonlu iletisim", "Gercek zamanli bidirectional iletisim", "Dosya transferi", "Veritabani baglantisi"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'attention mechanism' ne ise yarar?",
        "secenekler": ["Hizi artirir", "Girdideki onemli kisimlara odaklanmayi saglar", "Bellek tasarrufu saglar", "Hata duzeltir"],
        "dogru": 1
    },
    {
        "soru": "Django hangi programlama diline ait bir web framework'udur?",
        "secenekler": ["JavaScript", "Python", "Java", "C#"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'gradient descent' ne demektir?",
        "secenekler": ["Veri toplama yontemi", "Kayip fonksiyonunu optimize etme yontemi", "Veri gosterme yontemi", "Model depolama yontemi"],
        "dogru": 1
    },
    {
        "soru": "Ag aclari (network) icin hangi cihaz kullanilir?",
        "secenekler": ["Monitor", "Router", "Klavye", "Yazici"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'epoch' sayisi neyi gosterir?",
        "secenekler": ["Modelin boyutunu", "Egitim dongusu sayisini", "Hata oranini", "Veri miktarini"],
        "dogru": 1
    },
    {
        "soru": "TypeScript hangi dilin uzerine insa edilmistir?",
        "secenekler": ["Python", "Java", "JavaScript", "C++"],
        "dogru": 2
    },
    {
        "soru": "Yapay zeka'da 'convolutional neural network' (CNN) ne icin kullanilir?",
        "secenekler": ["Metin analizi", "Goru isleme ve goruntu tanima", "Ses isleme", "Veri depolama"],
        "dogru": 1
    },
    {
        "soru": "Mikro servis mimarisi ne demektir?",
        "secenekler": ["Tek bir dev uygulama", "Kucuk bagimsiz servislerden olusan mimari", "Masaustu uygulama", "Veritabani yapisi"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'LLM' ne anlama gelir?",
        "secenekler": ["Large Language Model", "Low Level Machine", "Linear Learning Method", "Long Lasting Memory"],
        "dogru": 0
    },
    {
        "soru": "Raspberry Pi ne tür bir cihazdir?",
        "secenekler": ["Bilgisayar", "Kart (tek kartli bilgisayar)", "Yazici", "Tarayici"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'hallucination' (halusinasyon) ne demektir?",
        "secenekler": ["Modelin hizli calismasi", "Modelin gercek olmayan bilgi uydurmasi", "Modelin yavas calismasi", "Modelin hafizasinin dolmasi"],
        "dogru": 1
    },
    {
        "soru": "Django REST framework ne icin kullanilir?",
        "secenekler": ["Frontend gelistirme", "API olusturma", "Veritabani yonetimi", "Dosya donusumu"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'data preprocessing' ne demektir?",
        "secenekler": ["Verileri dogrudan kullanma", "Verileri temizleme ve hazirlama", "Verileri silme", "Verileri paylasma"],
        "dogru": 1
    },
    {
        "soru": "NoSQL veritabani orneklerinden hangisi dogrudur?",
        "secenekler": ["MySQL, PostgreSQL", "MongoDB, Redis, Cassandra", "Oracle, SQL Server", "Excel, Word"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'ensemble learning' ne demektir?",
        "secenekler": ["Tek model kullanma", "Birden fazla modeli birlestirme", "Modeli silme", "Veri toplama"],
        "dogru": 1
    },
    {
        "soru": "Python'da 'dictionary' (sozluk) veri yapisi nasil tanimlanir?",
        "secenekler": ["[] ile", "{} ile", "() ile", "<> ile"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'hyperparameter' ne demektir?",
        "secenekler": ["Modelin ogrendigi parametre", "Egitimden once ayarlanan parametre", "Sonuc parametresi", "Veri parametresi"],
        "dogru": 1
    },
    {
        "soru": "Microservices ile monolith mimari arasindaki temel fark nedir?",
        "secenekler": ["Monolith daha hizli", "Microservices daha modular ve bagimsiz", "Monolith daha guvenli", "Microservices daha basit"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'transfer learning' ne demektir?",
        "secenekler": ["Veri transferi", "Onceden ogrenilmis bilgiyi yeni goreve tasima", "Model transferi", "Dosya transferi"],
        "dogru": 1
    },
    {
        "soru": "Scikit-learn kutuphanesi ne icin kullanilir?",
        "secenekler": ["Web gelistirme", "Makine ogrenmesi", "Grafik tasarim", "Ses isleme"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'data augmentation' ne demektir?",
        "secenekler": ["Veri silme", "Veri setini cesitlendirerek genisletme", "Veri toplama", "Veri paylasma"],
        "dogru": 1
    },
    {
        "soru": "Kubernetes'ta 'pod' ne anlama gelir?",
        "secenekler": ["Bir dosya turu", "Konteynerlerin calistigi en kucuk birim", "Bir ag protokolu", "Bir veritabani"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'loss function' ne ise yarar?",
        "secenekler": ["Veri toplar", "Modelin hata oranini olcer", "Sonucu gosterir", "Modeli calistirir"],
        "dogru": 1
    },
    {
        "soru": "Git'te 'merge conflict' ne demektir?",
        "secenekler": ["Kod silme", "Ayni satirda farkli degisiklikler oldugunda olusan catisma", "Dosya olusturma", "Branch silme"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'embedding' ne demektir?",
        "secenekler": ["Veri silme", "Kelimeleri sayisal vektorlere donusturma", "Modeli egitme", "Sonucu gosterme"],
        "dogru": 1
    },
    {
        "soru": "MongoDB hangi veritabani turune ornektir?",
        "secenekler": ["Relational (ilişkisel)", "Document-based (belge tabanli)", "Graph (graf)", "Key-value (anahtar-deger)"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'gradient' ne anlama gelir?",
        "secenekler": ["Hata degeri", "Turev/degisim orani", "Veri tipi", "Model boyutu"],
        "dogru": 1
    },
    {
        "soru": "Agustos 2024 itibariyla en buyuk dil modeli (LLM) hangisidir?",
        "secenekler": ["GPT-4", "Claude 3.5", "Llama 3", "Hepsinin farkli guclu yonleri var"],
        "dogru": 3
    },
    {
        "soru": "Yapay zeka'da 'prompt engineering' ne demektir?",
        "secenekler": ["Kod yazma", "Yapay zekaya etkili komutlar tasarlama", "Model egitme", "Veri toplama"],
        "dogru": 1
    },
    {
        "soru": "Redis ne tur bir veritabanidir?",
        "secenekler": ["Relational", "In-memory (bellek icinde)", "Document", "Graph"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'attention' mekanizmasi ilk olarak hangi makalede tanimlanmistir?",
        "secenekler": ["Attention Is All You Need", "Deep Learning Book", "Python Documentation", "Git Manual"],
        "dogru": 0
    },
    {
        "soru": "Lambda ifadesi (anonim fonksiyon) hangi programlama dillerinde kullanilir?",
        "secenekler": ["Sadece Python", "Python, JavaScript, Java ve digerleri", "Sadece C++", "Sadece HTML"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'MLOps' ne demektir?",
        "secenekler": ["Makine ogrenmesi operasyonlari", "Modelelleme ve islemler", "Veri islemleri", "Dosya yonetimi"],
        "dogru": 0
    },
    {
        "soru": "WebSocket ve HTTP arasindaki temel fark nedir?",
        "secenekler": ["WebSocket daha yavastir", "WebSocket gercek zamanli bidirectional, HTTP tek yonlu", "HTTP daha guvenlidir", "Fark yoktur"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'tokenization' ne demektir?",
        "secenekler": ["Veri silme", "Metni kucuk parcalara (token) bolme", "Sifre olusturma", "Model egitme"],
        "dogru": 1
    },
    {
        "soru": "Agustos 2024 itibariyla hangi sirket en buyuk yapay zeka yatirimlarini yapmaktadir?",
        "secenekler": ["Apple", "Google ve Microsoft", "Amazon", "Tesla"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'context window' ne anlama gelir?",
        "secenekler": ["Pencere boyutu", "Modelin ayni anda isleyebilecegi metin uzunlugu", "Ekran boyutu", "Dosya boyutu"],
        "dogru": 1
    },
    {
        "soru": "Flask hangi programlama diline ait bir web framework'udur?",
        "secenekler": ["JavaScript", "Python", "Java", "Ruby"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'RLHF' ne demektir?",
        "secenekler": ["Random Learning Human Feedback", "Reinforcement Learning from Human Feedback", "Recurrent Layer High Frequency", "Raw Language Handling Framework"],
        "dogru": 1
    },
    {
        "soru": "Version control sisteminde 'branch' ne demektir?",
        "secenekler": ["Ana kod hatti", "Gelistirmeye ozel ayri bir kopya", "Dosya turu", "Veritabani"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'token limit' ne demektir?",
        "secenekler": ["Hizi sinirlama", "Modelin isleyebilecegi maksimum token sayisi", "Bellek siniri", "Aga baglanti siniri"],
        "dogru": 1
    },
    {
        "soru": "PostgreSQL hangi tur veritabanidir?",
        "secenekler": ["NoSQL", "Relational (ilişkisel)", "Document", "Graph"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'benchmark' ne demektir?",
        "secenekler": ["Kod yazma", "Modellerin karsilastirmali degerlendirilmesi", "Veri toplama", "Model silme"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'multimodal' model ne demektir?",
        "secenekler": ["Tek modlu calisan", "Metin, goruntu, ses gibi birden fazla veri turu ile calisan", "Sadece goruntu ile calisan", "Sadece metin ile calisan"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'RAG' ne anlama gelir?",
        "secenekler": ["Random Answer Generation", "Retrieval-Augmented Generation", "Rapid Algorithm Growth", "Real-time Analysis Graph"],
        "dogru": 1
    },
    {
        "soru": "Numpy kutuphanesi ne icin kullanilir?",
        "secenekler": ["Web gelistirme", "Sayisal hesaplamalar ve dizi islemleri", "Grafik tasarim", "Ses isleme"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'hallucination' problemi nasil azaltilabilir?",
        "secenekler": ["Modeli kucultme", "RAG ve dogrulama teknikleri", "Modeli silme", "Veri sayisini azaltma"],
        "dogru": 1
    },
    {
        "soru": "Yazilim gelistirmede 'unit test' ile 'integration test' arasindaki fark nedir?",
        "secenekler": ["Unit test daha yavastir", "Unit test tek bileseni, integration test birden fazla bilesenin etkilesimini test eder", "Fark yoktur", "Integration test daha basittir"],
        "dogru": 1
    },
    {
        "soru": "Yapay zeka'da 'vector database' ne demektir?",
        "secenekler": ["Normal veritabani", "Vektor embeddingleri icin ozellesmis veritabani", "Gorsel veritabani", "Ses veritabani"],
        "dogru": 1
    },
    {
        "soru": "Vercel hangi konuda hizmet verir?",
        "secenekler": ["Veri depolama", "Web uygulamalari icin hosting ve deployment", "Masaustu uygulama", "Mobil uygulama"],
        "dogru": 1
    },
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
        self.root.configure(bg="#0a0a0a")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        self.oyuncu_adi = ""
        self.puan = 0
        self.soru_index = 0
        self.kalan_sure = 120
        self.sorular = []
        self.sure_aktif = False
        self.timer_id = None

        veritabani_olustur()
        self.ana_ekran()

    def temizle(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def ana_ekran(self):
        self.temizle()
        self.sure_aktif = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame, text="UYT", font=("Helvetica", 72, "bold"),
            fg="#2563EB", bg="#0a0a0a"
        ).pack(pady=(0, 5))

        tk.Label(
            frame, text="BILGI YARISMASI", font=("Helvetica", 28, "bold"),
            fg="#ffffff", bg="#0a0a0a"
        ).pack(pady=(0, 5))

        tk.Label(
            frame, text="Teknoloji, Yazilim ve Yapay Zeka", font=("Helvetica", 14),
            fg="#6b7280", bg="#0a0a0a"
        ).pack(pady=(0, 40))

        tk.Label(
            frame, text="Adinizi girin:", font=("Helvetica", 13),
            fg="#d1d5db", bg="#0a0a0a"
        ).pack(anchor="w", padx=180)

        self.ad_entry = tk.Entry(
            frame, font=("Helvetica", 16), bg="#1a1a2e", fg="#ffffff",
            insertbackground="#ffffff", relief="flat",
            highlightthickness=2, highlightbackground="#2563EB",
            highlightcolor="#2563EB"
        )
        self.ad_entry.pack(ipady=10, pady=(5, 20), padx=180, fill="x")
        self.ad_entry.focus()
        self.ad_entry.bind("<Return>", lambda e: self.oyuna_basla())

        basla_btn = tk.Button(
            frame, text="OYUNA BASLA", font=("Helvetica", 15, "bold"),
            bg="#2563EB", fg="#ffffff", relief="flat",
            activebackground="#1d4ed8", activeforeground="#ffffff",
            cursor="hand2", command=self.oyuna_basla
        )
        basla_btn.pack(ipady=8, padx=180, fill="x")

        tk.Button(
            frame, text="LIDERLIK TABLOSU", font=("Helvetica", 12),
            bg="#1a1a2e", fg="#9ca3af", relief="flat",
            activebackground="#2563EB", activeforeground="#ffffff",
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

    def ust_bar(self):
        bar = tk.Frame(self.root, bg="#111827", height=60)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        sure_renk = "#22c55e"
        if self.kalan_sure <= 30:
            sure_renk = "#ef4444"
        elif self.kalan_sure <= 60:
            sure_renk = "#f59e0b"

        dakika = self.kalan_sure // 60
        saniye = self.kalan_sure % 60

        tk.Label(
            bar, text=f"{dakika:02d}:{saniye:02d}",
            font=("Helvetica", 20, "bold"), fg=sure_renk, bg="#111827"
        ).pack(side="left", padx=20)

        tk.Label(
            bar, text=f"Soru {self.soru_index + 1}/10",
            font=("Helvetica", 13), fg="#9ca3af", bg="#111827"
        ).pack(side="left", padx=30)

        tk.Label(
            bar, text=f"{self.oyuncu_adi}", font=("Helvetica", 14, "bold"),
            fg="#ffffff", bg="#111827"
        ).pack(side="right", padx=20)

        tk.Label(
            bar, text=f"{self.puan} Puan", font=("Helvetica", 14, "bold"),
            fg="#2563EB", bg="#111827"
        ).pack(side="right", padx=10)

    def sure_baslat(self):
        if not self.sure_aktif:
            return
        if self.kalan_sure <= 0:
            self.oyun_bitti()
            return
        self.kalan_sure -= 1
        self.ust_bar_guncelle()
        self.timer_id = self.root.after(1000, self.sure_baslat)

    def ust_bar_guncelle(self):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_reqheight() == 60:
                for child in widget.winfo_children():
                    child.destroy()

                sure_renk = "#22c55e"
                if self.kalan_sure <= 30:
                    sure_renk = "#ef4444"
                elif self.kalan_sure <= 60:
                    sure_renk = "#f59e0b"

                dakika = self.kalan_sure // 60
                saniye = self.kalan_sure % 60

                tk.Label(
                    widget, text=f"{dakika:02d}:{saniye:02d}",
                    font=("Helvetica", 20, "bold"), fg=sure_renk, bg="#111827"
                ).pack(side="left", padx=20)

                tk.Label(
                    widget, text=f"Soru {self.soru_index + 1}/10",
                    font=("Helvetica", 13), fg="#9ca3af", bg="#111827"
                ).pack(side="left", padx=30)

                tk.Label(
                    widget, text=f"{self.oyuncu_adi}",
                    font=("Helvetica", 14, "bold"), fg="#ffffff", bg="#111827"
                ).pack(side="right", padx=20)

                tk.Label(
                    widget, text=f"{self.puan} Puan",
                    font=("Helvetica", 14, "bold"), fg="#2563EB", bg="#111827"
                ).pack(side="right", padx=10)
                break

    def soru_goster(self):
        self.temizle()

        if self.soru_index >= len(self.sorular):
            self.oyun_bitti()
            return

        self.ust_bar()

        soru = self.sorular[self.soru_index]

        soru_frame = tk.Frame(self.root, bg="#0a0a0a")
        soru_frame.pack(expand=True, fill="both", padx=60, pady=20)

        soru_kutu = tk.Frame(soru_frame, bg="#1a1a2e", bd=0)
        soru_kutu.pack(fill="x", pady=(0, 30))

        tk.Label(
            soru_kutu, text=soru["soru"],
            font=("Helvetica", 17, "bold"), fg="#ffffff", bg="#1a1a2e",
            wraplength=900, justify="center"
        ).pack(pady=30, padx=40)

        secenek_frame = tk.Frame(soru_frame, bg="#0a0a0a")
        secenek_frame.pack(fill="x")

        renkler = ["#1e3a5f", "#1a3a2a", "#3a1a2a", "#2a2a1a"]
        hover_renkler = ["#2563EB", "#22c55e", "#ef4444", "#f59e0b"]

        for i, secenek in enumerate(soru["secenekler"]):
            btn = tk.Button(
                secenek_frame, text=secenek,
                font=("Helvetica", 14), fg="#ffffff", bg=renkler[i],
                relief="flat", activebackground=hover_renkler[i],
                activeforeground="#ffffff", cursor="hand2",
                command=lambda s=i: self.cevap_ver(s),
                height=2
            )
            btn.pack(fill="x", pady=5)
            btn.bind("<Enter>", lambda e, b=btn, r=hover_renkler[secenek_frame.winfo_children().index(b) % 4]: b.configure(bg=r))
            btn.bind("<Leave>", lambda e, b=btn, r=renkler[secenek_frame.winfo_children().index(b) % 4]: b.configure(bg=r))

        if not self.sure_aktif:
            self.sure_aktif = True
            self.sure_baslat()

    def cevap_ver(self, secim):
        self.sure_aktif = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        soru = self.sorular[self.soru_index]

        if secim == soru["dogru"]:
            self.puan += 10
            self.geri_bildirim_goster(True)
        else:
            self.kalan_sure = max(0, self.kalan_sure - 15)
            self.geri_bildirim_goster(False)

        self.soru_index += 1

        if self.soru_index >= len(self.sorular) or self.kalan_sure <= 0:
            self.root.after(1500, self.oyun_bitti)
        else:
            self.root.after(1500, self.yeni_soru)

    def geri_bildirim_goster(self, dogru):
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.winfo_reqheight() != 60:
                widget.destroy()

        renk = "#22c55e" if dogru else "#ef4444"
        text = "+10 Puan!" if dogru else "-15 Saniye!"

        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.pack(expand=True)

        tk.Label(
            frame, text=text, font=("Helvetica", 36, "bold"),
            fg=renk, bg="#0a0a0a"
        ).pack()

    def yeni_soru(self):
        self.soru_goster()

    def oyun_bitti(self):
        self.sure_aktif = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        skor_kaydet(self.oyuncu_adi, self.puan)

        self.temizle()

        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame, text="OYUN BITTI", font=("Helvetica", 36, "bold"),
            fg="#ffffff", bg="#0a0a0a"
        ).pack(pady=(0, 10))

        tk.Label(
            frame, text=f"{self.oyuncu_adi}", font=("Helvetica", 22),
            fg="#9ca3af", bg="#0a0a0a"
        ).pack(pady=(0, 5))

        tk.Label(
            frame, text=f"{self.puan} Puan", font=("Helvetica", 48, "bold"),
            fg="#2563EB", bg="#0a0a0a"
        ).pack(pady=(0, 30))

        buton_frame = tk.Frame(frame, bg="#0a0a0a")
        buton_frame.pack()

        tk.Button(
            buton_frame, text="TEKRAR OYNA", font=("Helvetica", 14, "bold"),
            bg="#2563EB", fg="#ffffff", relief="flat",
            activebackground="#1d4ed8", activeforeground="#ffffff",
            cursor="hand2", command=self.oyuna_basla2
        ).pack(side="left", ipady=8, padx=20)

        tk.Button(
            buton_frame, text="ANA MENU", font=("Helvetica", 14),
            bg="#1a1a2e", fg="#9ca3af", relief="flat",
            activebackground="#2563EB", activeforeground="#ffffff",
            cursor="hand2", command=self.ana_ekran
        ).pack(side="left", ipady=8, padx=20)

    def oyuna_basla2(self):
        self.puan = 0
        self.soru_index = 0
        self.kalan_sure = 120
        self.sorular = random.sample(SORULAR, min(10, len(SORULAR)))
        self.sure_aktif = True
        self.soru_goster()

    def liderlik_ekrani(self):
        self.temizle()
        self.sure_aktif = False

        frame = tk.Frame(self.root, bg="#0a0a0a")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            frame, text="LIDERLIK TABLOSU", font=("Helvetica", 28, "bold"),
            fg="#2563EB", bg="#0a0a0a"
        ).pack(pady=(0, 30))

        sonuclar = liderlik_tablosu()

        if not sonuclar:
            tk.Label(
                frame, text="Henuz skor kaydi yok.", font=("Helvetica", 14),
                fg="#6b7280", bg="#0a0a0a"
            ).pack()
        else:
            for i, (isim, skor) in enumerate(sonuclar):
                sira_renk = "#f59e0b" if i == 0 else "#9ca3af" if i == 1 else "#cd7f32" if i == 2 else "#6b7280"

                satir = tk.Frame(frame, bg="#1a1a2e")
                satir.pack(fill="x", pady=3, padx=40)

                tk.Label(
                    satir, text=f"  {i+1}.  {isim}",
                    font=("Helvetica", 13), fg="#ffffff", bg="#1a1a2e",
                    anchor="w"
                ).pack(side="left", padx=10, pady=8)

                tk.Label(
                    satir, text=f"{skor}  ",
                    font=("Helvetica", 13, "bold"), fg=sira_renk, bg="#1a1a2e",
                    anchor="e"
                ).pack(side="right", padx=10, pady=8)

        tk.Button(
            frame, text="GERI DON", font=("Helvetica", 13),
            bg="#2563EB", fg="#ffffff", relief="flat",
            activebackground="#1d4ed8", activeforeground="#ffffff",
            cursor="hand2", command=self.ana_ekran
        ).pack(pady=30, ipady=6, padx=80, fill="x")


def main():
    root = tk.Tk()
    root.state("zoomed")
    UYTQuiz(root)
    root.mainloop()


if __name__ == "__main__":
    main()
