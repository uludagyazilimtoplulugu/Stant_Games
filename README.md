# UYT Stant Oyunları

Uludağ Yazılım Topluluğu (UYT) için hazırlanan **3 interaktif stant oyunu**.
Her oyun kendi klasöründe, bağımsız çalışacak şekilde yer alır.

## Klasörler
| Klasör | Oyun | Açıklama |
|--------|------|----------|
| `game1_quiz/` | Bilgi Yarışması | İnternetten canlı çekilen sorular, her oyuncuya farklı; 10 soru, süre/pon sistemi, SQLite sıralama. |
| `game2_camdraw/` | CamDraw | Kamera + el takibi; işaret parmağıyla çiz, yumrukla 3 sn sonra fotoğraf çek ve e-postaya gönder. |
| `game3_arcade/` | Sembol Avı | Kendi tasarladığımız tkinter tabanlı refleks oyunu; liderlik tablosu. |

## Oyun 1 — Bilgi Yarışması
- Oyuncular isimlerini girer (1-8 kişi).
- Sorular OpenTDB'den **canlı** çekilir ve her oyuncuya **farklı** 10 soru verilir.
- Her oyuncuya **2 dakika**; yanlışta süre **15 sn** kısalır, doğruda **+10 puan**.
- Tasarım: sol üstte süre, sağ üstte isim + puan, ortada soruyla ilgili resim,
  altında 4 seçenek.
- Skorlar `stant_oyun.db` (SQLite) içinde saklanır; gün sonu sıralaması ve
  "Yeni Oyun" döngüsü mevcuttur.
```bash
cd game1_quiz
pip install -r requirements.txt
python quiz.py
```

## Oyun 2 — CamDraw
- Gönderen Gmail (uygulama şifresi) `config.json` içinde saklanır.
- Oyuncu e-posta adresini girer; kamera açılır.
- İşaret parmağıyla havada çizim, **yumruk** ile 3 sn geri sayım → fotoğraf çekilir
  ve oyuncunun e-postasına gönderilir.
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
