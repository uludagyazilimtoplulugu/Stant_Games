# UYT Stant Oyunu 1 — Bilgi Yarışması (Tek Oyuncu, Türkçe)

## Oyun Açıklaması
Uludağ Yazılım Topluluğu'nun interaktif stant oyunu — **Tek Oyuncu Modu**:

Kim Milyoner Olmak İster tarzında, **eğlenceli ve şaşırtıcı** teknoloji sorularıyla dolu bir bilgi yarışması. Kodlama bilmenize gerek yok; amaç eğlenceli teknoloji kültürü sorularına doğru cevap vermek.

- **Sadece 1 oyuncu**: Başlangıçta tek bir isim girilir, sonra oyun başlar.
- **200 soruluk havuz**: Her oyunda havuzdan **rastgele 15 soru** seçilir; aynı oyun içinde soru tekrarı olmaz, her oyuncu farklı sorular görür.
- **4 seçenekli, 2×2 grid**: Seçenekler ekranda 2 satır × 2 sütun düzeninde gösterilir.
- **2 dakika süre**: Toplam 120 saniye. Doğru cevap +10 puan, yanlış cevap **-15 saniye**.
- **Her cevaptan sonra bilgi**: Doğru ya da yanlış fark etmeksizin, soruyla ilgili ilginç bir gerçek **sarı renkte** ekranda gösterilir.
- **Yerel görseller**: Her soru için internet olmadan anında üretilen benzersiz gradyan görseller kullanılır.
- **Skor kaydı**: Skorlar SQLite (`skorlar.db`) içine kaydedilir; ilk 10'luk liderlik tablosu ana menüden görüntülenir.

## Soru Türleri
Sorular "Kim Milyoner Olmak İster" havasında, tekdüze kalıplardan uzak, çeşitli formatlardadır:

- **İcat & mucit**: "İlk fare hangi malzemeden yapıldı?"
- **İlk kez / tarih**: "İlk e-posta ne zaman gönderildi?"
- **İsim kökeni**: "Bluetooth adı nereden geliyor?"
- **Neden / nasıl**: "İlk webcam neden icat edildi?"
- **Ne anlama gelir**: "EXE uzantısı ne demek?"
- **Kaç / rakamlar**: "1 TB kaç GB eder?"
- **Enteresan bilgi**: Oyun tarihi, şirket hikâyeleri, Easter egg'ler, güvenlik ve yapay zeka merakları

Konular: internet tarihi, programlama Easter egg'leri, oyun tarihi, icatlar, isim kökenleri, tuhaf teknoloji gerçekleri, yapay zekâ, uzay teknolojisi, donanım, yazılım/OS, siber güvenlik ve teknoloji-pop kültürü kesişimleri.

## Tasarım
- **UYT resmî renk paleti** (ana siteden araştırıldı):
  - Arka plan: `#0a0a0a` (siyah), paneller `#111827` / `#1a1a2e`
  - Vurgu: **mavi `#2563EB`**
  - Durum renkleri: yeşil `#22c55e` (doğru), kırmızı `#ef4444` (yanlış), sarı `#f59e0b` (bilgi/süre uyarısı)
- Üst bar: süre (renkli sayaç), soru numarası, oyuncu adı ve puan.
- Ortada görsel + soru, altta 2×2 seçenek butonları; butonlar üzerine gelince renk değiştirir.
- Süre azaldıkça sayaç sarıya, sonra kırmızıya döner (gerilim efekti).

## Akış
1. Oyuncu adını girer ve **OYUNA BAŞLA**'ya basar.
2. Havuzdan rastgele **15 soru** seçilir ve görseller önceden üretilir.
3. 2 dakikalık sayaç başlar.
4. Her doğru cevap **+10 puan**, yanlış cevap **-15 saniye**.
5. Cevaptan sonra ilginç bilgi sarı renkte gösterilir, ~2 sn beklenip sonraki soruya geçilir.
6. 15 soru bitince ya da süre dolunca **OYUN BİTTİ** ekranı açılır; skor kaydedilir.
7. **TEKRAR OYNA** ile yeni (farklı) 15 soru, **ANA MENU** ile isim ekranına dönüş yapılabilir.
8. Ana menüden **LİDERLİK TABLOSU** görüntülenebilir.

## Nasıl Çalıştırılır
```bash
cd game1_quiz
python quiz.py
```
Ya da klasördeki **`run.bat`** dosyasına çift tıklayarak başlatılabilir.

## Dosyalar
| Dosya | Görevi |
|---|---|
| `quiz.py` | Ana oyun (arayüz, süre, puan, görseller) |
| `sorular.py` | 200 soruluk soru havuzu |
| `run.bat` | Çift tıkla çalıştırıcı |
| `skorlar.db` | Skor veritabanı (otomatik oluşur, git'e girmez) |
| `img_cache/` | Görsel önbelleği (git'e girmez) |

## Gerekli Paketler
```bash
pip install -r requirements.txt
```
> `Pillow` yeterlidir (görseller yerel üretilir, internet gerekmez).

## Özellikler
- ✅ Tek oyuncu modu, tek isim girişi
- ✅ 200 eğlenceli teknoloji sorusu, her oyunda rastgele 15 soru
- ✅ Aynı oyun içinde soru tekrarı yok
- ✅ 2×2 seçenek gridi
- ✅ Her cevap sonrası sarı renkte ilginç bilgi
- ✅ 2 dakika süre, doğru +10 puan, yanlış -15 sn
- ✅ Yerel üretilen benzersiz görseller (internetsiz çalışır)
- ✅ SQLite skor kaydı + liderlik tablosu
- ✅ UYT resmî renk paleti (koyu tema, mavi vurgu)
