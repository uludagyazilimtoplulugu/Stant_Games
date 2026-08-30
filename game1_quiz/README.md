# UYT Stant Oyunu 1 — Bilgi Yarışması (Tek Oyuncu, Türkçe, Canlı)

## Oyun Açıklaması
Uludağ Yazılım Topluluğu'nun interaktif stant oyunu - **Tek Oyuncu Modu**:

- **Sadece 1 oyuncu**: Başlangıçta sadece bir isim girilir.
- **Sorular Türkçe**: OpenTDB API'si `language=tr` parametresiyle çekilen sorular Türkçe'dir.
- **10 soru, 4 seçenek**: Her sorunun 4 seçeneği vardır.
- **2 dakika süre**: Her soru çözümünüz için 120 saniye (2 dk).
- **Yanlış bilerse**: Süre **15 saniye** kısalır.
- **Doğru bilerse**: **+10 puan** kazanılır.
- **Sürekli oyun**: Oyun bittiğinde yeni bir soru seti otomatik olarak yüklenir, skor biriktilerek toplu puan olur. Sonsuza kadar oynayabilirsiniz (çıkana kadar).
- **SQLite kaydı**: En yüksek skor ve oyuncu adı `stant_oyun.db` içinde saklanır.

## Tasarım
- **UYT renk paleti**: Dark navy arka plan (#0d1b2a), kırmızı ve turuncu vurgular (#e63946, #f4a261).
- Canlı ve modern arayüz: Sol üstte hızlı sayaç, sağ üstte isim+puan, orta soru+resim, altta 4 seçenek butonu.
- Süre dolduğunda timer rengi değişir (gerilim efekti).
- Oyun başlangıcı: Tek isim girişi + "TAMAM BAŞLAT" butonu.

## Akış
1. Oyuncu adını girer ve "TAMAM BAŞLAT"'a basar.
2. 10 Türkçe soru çekilir ve oyun başlar.
3. 2 dakika (120 sn) timer başlar.
4. Her doğru cevap +10 puya, yanlış -15 sn sürücülük verir.
5. 10 soru bittikten sonra: **3 saniye bekleme**, ardından otomatik olarak yeni 10 soru seti yüklenir ve skor birikintilemeye devam eder.
6. Her tur sonunda en yüksek skor liderlik tablosuna kaydedilir.
7. Çıkmak için pencereyi kapatın ya da "Yeni Oyun" menüsünü kullanın.

## Nasıl Çalıştırılır
```bash
cd game1_quiz
python quiz.py
```
Ya da doğrudan `run.bat` dosyasına tıklayarak başlatılabilir.

## Gerekli Paketler
```bash
pip install -r requirements.txt
```
> `requests` ve `Pillow` kütüphanelerine ihtiyaç vardır.

## Özellikler
- ✅ Tek oyuncu modu
- ✅ Türkçe sorular (OpenTDB language=tr)
- ✅ 10 soru, 4 seçenek
- ✅ 2 dakika süre, yanlışta -15 sn
- ✅ Doğru answer +10 puan
- ✅ SQLite skor kaydı
- ✅ Otomatik yeni soru seti (sürekli oyun)
- ✅ UYT canlı renk tasarımı
- ✨ "Yeni Soru Seti" akışı