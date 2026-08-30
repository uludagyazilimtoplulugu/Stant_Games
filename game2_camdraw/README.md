# UYT Stant Oyunu 2 — Kamera ile Çiz & Yumrukla Çek & Mail Gönder

## Oyun Açıklaması
Kamera açılır ve işaret parmağını hareket ettirerek ekranda yazı yapılır.
Yumruk yapılması ile **3 saniyelik geri sayım** başlar ve sonunda fotoğraf çekilir.
Çekilen fotoğraf, oyuncunun başına girdiği e-posta adresine **Gmail** üzerinden otomatik gönderilir.

## Akış
1. **Operatör Ayarları** (bir kez): `config.json` içinde gönderen Gmail adresi ve uygulama şifresi kaydedilir.
2. **Oyuncu Giriimi**: Oyuncu kendi e-posta adresini girer.
3. **Kamera Açılır**: İşaret parmağı (index parmağı diğerleri ile birlikte yukarı yukarı çıktığında) havada **yazı yapabilirsiniz**.
4. **Yumruk Yapın**: Tüm parmaklar bendirildiği (yumruk) anı 3 saniye geri sayım başlar.
5. **Fotoğraf Çekildikten Sonra**: 3 sanika içinde fotoğraf oyuncunun girdiği e-postaya gönderilir ve "GÖNDERİLDİ" bildirimi gösterilir.

## Gmail "Uygulama Şifresi" Nedir?
Gmail normal şifre ile SMTP login kabul etmez. Adımlar:
1. Google hesabınızda **2 Adımlı Doğrulama**'yı açın.
2. https://myaccount.google.com/apppasswords adresinden **Uygulama Şifresi** oluşturun.
3. Program ilk açıldığında bu şifreyi (ve gönderen Gmail adresini) girin; `config.json` içine kaydedilir.

## Nasıl Çalıştırılır
```bash
cd game2_camdraw
python camdraw.py
```
Ya da doğrudan `run.bat` dosyasına tıklayarak Oyun başlatılabilir.

## Gerekli Paketler
```bash
pip install -r requirements.txt
```
> `opencv-python` ve `mediapipe` büyük paketlerdir. İnternet bağlantısı yeterli bir makinede kurun.

## Kontroller
- **İşaret parmağı** (diğerleri kapalı): Çizim yapar.
- **Yumruk**: 3 sn geri sayım → fotoğraf çekilir ve mail gönderilir.
- **c**: çizimi temizler.
- **n**: yeni oyuncu (yeni e-posta sorar).
- **q / ESC**: çıkış.

## Dosyalar
- `config.py` : gönderen hesap ayarı (config.json).
- `emailer.py` : SMTP ile fotoğraf gönderme (saf stdlib, test edilebilir).
- `camdraw.py` : kamera + MediaPipe el takibi + çizim + çekim.