"""E-posta gönderme yardımcı modülü (saf standart kütüphane).
Gmail SMTP üzerinden fotoğraf ekli mail gönderir.
"""
import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


def build_message(sender, to_addr, image_path, subject="UYT Stant - Fotoğrafın",
                  body="Merhaba! UYT standımızdaki deneyiminin fotoğrafı ektedir. Teşekkürler!"):
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with open(image_path, "rb") as f:
        img_data = f.read()
    image = MIMEImage(img_data, name=os.path.basename(image_path))
    image.add_header("Content-Disposition", "attachment",
                     filename=os.path.basename(image_path))
    msg.attach(image)
    return msg


def send_photo(sender, password, to_addr, image_path,
               smtp_host="smtp.gmail.com", smtp_port=465):
    msg = build_message(sender, to_addr, image_path)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(sender, password)
        server.send_message(msg)
    return True


if __name__ == "__main__":
    # Yerel bir hata ayıklama SMTP sunucusu ile MIMe yapısını test eder.
    import tempfile
    tmp = os.path.join(tempfile.gettempdir(), "test.png")
    with open(tmp, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")  # geçersiz ama test için yeterli
    m = build_message("a@b.com", "c@d.com", tmp)
    print("MIME tipi:", m.get_content_type())
    print("Ek sayısı:", len(m.get_payload()))
    print("E-posta yapısı başarıyla oluşturuldu.")
