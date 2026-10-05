# UYT Stant Oyunları

Uludağ Yazılım Topluluğu (UYT) için hazırlanan **3 interaktif stant oyunu**.
Her oyun kendi klasöründe, bağımsız çalışacak şekilde yer alır.

## Klasörler
| Klasör | Oyun | Açıklama |
|--------|------|----------|
| `game1_quiz/` | Bilgi Yarışması | 200 eğlenceli teknoloji sorusu; her oyunda rastgele 15 soru, süre/puan sistemi, SQLite liderlik tablosu. |
| `game2_camdraw/` | CamDraw | Kamera + el takibi; işaret parmağıyla çiz, kapalı şekil yap, parmak üçlüsüyle taşı, yumrukla kilitle. |
| `game3_arcade/` | Sembol Avı | Kendi tasarladığımız tkinter tabanlı refleks oyunu; liderlik tablosu. |

## Oyun 1 — Bilgi Yarışması
- Tek oyuncu; isim girilir ve oyun başlar.
- `sorular.py` içindeki **200 soruluk havuzdan** her oyunda **rastgele 15 soru** seçilir (tekrar yok).
- Kim Milyoner tarzı eğlenceli/şaşırtıcı teknoloji soruları; her cevaptan sonra sarı renkte **ilginç bilgi** gösterilir.
- **2 dakika** süre; yanlışta **15 sn** kısalır, doğruda **+10 puan**.
- Yerel üretilen görseller (internetsiz çalışır), 2×2 seçenek gridi, UYT renk paleti.
- Skorlar `skorlar.db` (SQLite) içinde saklanır; liderlik tablosu ana menüde.
```bash
cd game1_quiz
pip install -r requirements.txt
python quiz.py
```

## Oyun 2 — CamDraw
- Kamera açılır; **hiçbir mail/adres/şifre istenmez**, fotoğraf çekilmez.
- **İşaret parmağı** (diğerleri kapalı): havada çizim ve yazı.
- **Kapalı kutu/şekil** çizerseniz şekil nesneye dönüşür (+5 puan).
- **Başparmak + işaret + orta parmak**: nesneyi tutup ekranda taşırsınız.
- **Yumruk**: ekranı kilitler; kapalıyken tekrar **yumruk** serbest bırakır.
- Klavye: **c** temizle, **q/ESC** çıkış.
```bash
cd game2_camdraw
pip install -r requirements.txt
python camdraw.py
```
> `opencv` ve `mediapipe` büyük paketlerdir; iyi internet bağlantısı olan makinede kurun.

## Oyun 3 — Sembol Avı
- Ekstra bağımlılık yok; doğrudan çalışır.
```bash
cd game3_arcade
python arcade.py
```

## Çalıştırma
Her klasördeki `run.bat` dosyasına çift tıklayarak ilgili oyunu başlatabilirsiniz.
