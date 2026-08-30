# UYT Stant Oyunu 1 — Bilgi Yarışması

## Oyun Açıklaması
Uludağ Yazılım Topluluğu'nun interaktif stant oyunu. Kuralları şöyledir:

- **Toplam 10 soru**, her sorunun **4 seçeneği** vardır.
- Oyun başladığında tüm oyuncuların **2 dakikası** (120 saniye) vardır.
- **Yanlış bilirse** süre **15 saniye** kısalır.
- **Doğru bilirse** puan **+10** kazanılır.
- Oyun başlangıcında oynayanların **isimleri** girilir.
- Oyun bittiğinde veya gün sonu içinde **sıralama (1., 2., 3. vb.)** görülebilir.
- **"Yeni Oyun"** dediğimizde döngü sıfırlar ve tekrar oynanabilir.

## Teknik Özellikler
- **Canlı sorular**: İnternet üzerinden OpenTDB API'si anlık çekilir.
- **Her oyuncuya farklı sorular**: Oyuncu sayısına göre soru havuzu oluşturulup distribute edilir, tekrarlama önlenir.
- **SQLite veritabanı**: Oyuncu isimleri ve skorlar `stant_oyun.db` dosyasında saklanır.
- **Grafik Tasarım**: 
  - Sol Üst: ⏱ Süre sayacı
  - Sağ Üst: Oyuncu ismi + mevcut puan
  - Ortada: Soruyla alakalı resim + soru metni
  - Altta: 4 seçenek butonu

## Nasıl Çalıştırılır
```bash
# Klasör içine gidin
cd game1_quiz

# Oyunu başlatın (ya da doble-click run.bat)
python quiz.py
```

## Gerekli Paketler
```bash
pip install -r requirements.txt
```
> `requests` ve `Pillow` kütüphanelerine ihtiyaç vardır. İlk çalıştırmada bunlar otomatik olarak kurulacaktır.

## Özellikler
- ✅ 10 soru, 4 seçenek
- ✅ Her oyuncu 2 dakika
- ✅ Yanlışta -15 sn, doğru +10 puan
- ✅ Oyuncu adı girişi
- ✅ Sıralama / Liderlik tablosu
- ✅ Yeni oyun döngüsü
- ✅ İnternetten anlık soru çekimi
- ✅ Farklı oyunculara farklı sorular