# UYT Stant Oyunu 2 — Havada Çiz, Şekil Yap, Nesneleri Taşı

## Oyun Açıklaması
Kamera açılır, ekranda **el hareketlerinizle** çizim ve şekiller yaparsınız. Tamamen yerel çalışır; **fotoğraf çekilmez, mail gönderilmez, hiçbir hesap/şifre istenmez.**

### Jestler
| Jest | Ne yapar |
|---|---|
| **İşaret parmağı** (diğer parmaklar kapalı) | Ekranda serbestçe **çizir ve yazı yazarsınız** |
| **Kapalı kutu/şekil çizmek** (işaret parmağıyla) | Çizdiğiniz kapalı şekil bir **nesneye** dönüşür (puan +5) |
| **Başparmak + işaret + orta parmak** (birlikte) | Yakındaki nesneyi (şekil/yazı/çizim) **tutup ekranda taşırsınız** |
| **Yumruk** | Ekran **kilitlenir** — çizim ve taşıma kapalı |
| **Kapalıyken tekrar yumruk** | Ekran yeniden **serbest** hale gelir |

## Akış
1. `run.bat` ile oyunu başlatın (kamera açılır).
2. İşaret parmağıyla havada yazın/çizin.
3. Kutu ya da kapalı bir şekil çizerseniz o şekil nesneye dönüşür, taşıyabilirsiniz.
4. Baş + işaret + orta parmağı birleştirip bir nesnenin üstüne gelin ve sürükleyerek taşıyın.
5. Yumrukla ekranı kilitleyin, tekrar yumrukla açın.
6. Bitirince **q** veya **ESC** ile çıkın.

## Kontroller (klavye)
- **c**: ekranı ve puanı temizler
- **q / ESC**: çıkış

## Tasarım
UYT renk paleti: koyu arka plan, mavi vurgu `#2563EB`, sarı taşıma imleci, kırmızı kilit uyarısı.

## Nasıl Çalıştırılır
```bash
cd game2_camdraw
python camdraw.py
```
Ya da `run.bat` dosyasına çift tıklayın.

## Gerekli Paketler
```bash
pip install -r requirements.txt
```
> `opencv-python` ve `mediapipe` büyük paketlerdir; internet bağlantısı yeterli bir makinede kurun.

## Dosyalar
- `camdraw.py` : kamera + MediaPipe el takibi + çizim/şekil/taşıma/kilit
- `run.bat` : çift tıkla çalıştırıcı
- `README.md` : bu dosya
