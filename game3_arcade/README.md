# UYT Stant Oyunu 3 — Sembol Avı (Kendi Tasarımımız)

## Oyun Açıklaması
UYT yazılım topluluğu olarak **kendimiz tasarladığımız**, sadece Tkinter ile çalışan bir refleks oyunu.
Ekstra paket gerekmez; her Windows bilgisayarda çalışır.

## Nasıl Oynanır
- Ekranda **30 saniye** boyunca UYT sembolleri (`⭐ 🚀 💡 🎯 🔥 ...`) belirir.
- Sembollere tıklayarak **puan** kazanarsınız.
- **Ardışık isabetlerde "kombo" çarpanı** artar (10 × kombo).
- Boşluğa tıklarsanız kombo yarıya düşer, hedef süresinde kaçırılırsa kombo sıfırlanır.
- Süre bittikten sonra isminizi girin; skor yerel veritabanına kaydedilir ve **Liderlik Tablosu**'nda sıralanırsınız.

## Nasıl Çalıştırılır
```bash
cd game3_arcade
python arcade.py
```
Ya da doğrudan `run.bat` dosyasına tıklayarak oyun başlatılabilir.

## Bağımlılık
- **Yoktur** — Sadece Python'un standart kütüphanesinden (tkinter) yararlanır.
- Python 3.6+'ın yüklü olduğu her bilgisayarda çalışır.

## Dosyalar
- `arcade.py` : oyun mantığı ve arayüz.
- `db.py`     : yerel skor veritabanı (SQLite).
- `run.bat`   : çift tıklayarak oyunları başlatmak için.