"""UYT Stant Oyunu 2 - Kamera ile Çiz & Yumrukla Çek & Mail Gönder.

Akış:
  1. Operatör gönderen Gmail'i ayarlar (config.json).
  2. Oyuncu kendi e-posta adresini girer.
  3. Kamera açılır; işaret parmağıyla havada çizim yapılır.
  4. Yumruk yapılınca 3 saniyelik geri sayım başlar, sonunda fotoğraf
     çekilip oyuncunun e-postasına GMAIL ile gönderilir.

Bağımlılıklar: opencv-python, mediapipe
"""
import os
import time
import cv2
import numpy as np
import mediapipe as mp
import tkinter as tk
from tkinter import messagebox

import config as config_mod
import emailer


# ---------- Yardımcılar ----------
def ask_email():
    """Oyuncudan e-posta adresini alır (Tkinter)."""
    root = tk.Tk()
    root.title("UYT - E-posta Gir")
    root.configure(bg="#0d1b2a")
    root.geometry("460x220")
    root.resizable(False, False)
    tk.Label(root, text="Fotoğrafın hangi e-postaya gönderilsin?",
             bg="#0d1b2a", fg="#f4a261", font=("Segoe UI", 13)).pack(pady=20)
    entry = tk.Entry(root, font=("Segoe UI", 15), bg="#1b263b", fg="white",
                     insertbackground="white", relief="flat", justify="center")
    entry.pack(fill="x", padx=40, ipady=8)
    entry.focus()
    result = {}

    def on_ok():
        v = entry.get().strip()
        if "@" not in v or "." not in v.split("@")[-1]:
            messagebox.showwarning("Hatalı", "Geçerli bir e-posta girin.")
            return
        result["email"] = v
        root.destroy()

    def on_cancel():
        result["cancel"] = True
        root.destroy()

    btn = tk.Frame(root, bg="#0d1b2a")
    btn.pack(pady=20)
    tk.Button(btn, text="📷 Başlat", command=on_ok, bg="#e63946", fg="white",
              font=("Segoe UI", 13, "bold"), relief="flat", padx=25, pady=8).pack(side="left", padx=8)
    tk.Button(btn, text="Çıkış", command=on_cancel, bg="#1b263b", fg="#e0e1dd",
              font=("Segoe UI", 12), relief="flat", padx=20, pady=8).pack(side="left", padx=8)
    entry.bind("<Return>", lambda e: on_ok())
    root.mainloop()
    return result


def fingers_state(landmarks, label):
    """4 parmak için dik/çökük durumu ve başparmak durumunu döndürür."""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    up = []
    for t, p in zip(tips, pips):
        up.append(landmarks[t].y < landmarks[p].y)
    # Başparmak: sağ el için ucu MCP'den solda, sol el için sağda
    if label == "Right":
        thumb_up = landmarks[4].x < landmarks[2].x
    else:
        thumb_up = landmarks[4].x > landmarks[2].x
    return up, thumb_up


def run_camera(recipient, sender):
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Kamera", "Kamera açılamadı (index 0).")
        return

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

    paint = np.zeros((H, W, 3), dtype=np.uint8)
    prev = None  # önceki işaret parmağı noktası
    fist_prev = False
    capturing = False
    capture_start = 0.0
    sent = False
    sent_time = 0.0
    DRAW_COLOR = (0, 255, 255)  # cyan

    out_dir = os.path.join(os.path.dirname(__file__), "captures")
    os.makedirs(out_dir, exist_ok=True)

    def put_text(img, text, pos, scale=0.9, color=(255, 255, 255), thick=2):
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # ayna görüntüsü

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        drawing = False
        fist = False
        if results.multi_hand_landmarks and results.multi_handedness:
            hand = results.multi_hand_landmarks[0]
            label = results.multi_handedness[0].classification[0].label
            up, thumb_up = fingers_state(hand.landmark, label)
            index_up = up[0]
            others_down = (not up[1]) and (not up[2]) and (not up[3])
            drawing = index_up and others_down
            fist = (not any(up)) and (not thumb_up)

            # işaret parmağı ucu (landmark 8)
            lm = hand.landmark[8]
            cx, cy = int(lm.x * W), int(lm.y * H)
            if drawing and not (capturing or sent):
                if prev is not None:
                    cv2.line(paint, prev, (cx, cy), DRAW_COLOR, 5, cv2.LINE_AA)
                prev = (cx, cy)
            else:
                prev = None
        else:
            prev = None

        # Yumruk -> çekim tetikleme (false->true geçişi)
        if fist and not fist_prev and not capturing and not sent:
            capturing = True
            capture_start = time.time()
        fist_prev = fist

        # Çekim geri sayımı
        if capturing:
            elapsed = time.time() - capture_start
            if elapsed >= 3.0:
                # Fotoğrafı kaydet
                photo = cv2.add(frame, paint)
                ts = time.strftime("%Y%m%d_%H%M%S")
                path = os.path.join(out_dir, f"uyt_{ts}.png")
                cv2.imwrite(path, photo)
                # Mail gönder
                try:
                    emailer.send_photo(sender["sender_email"],
                                       sender["sender_password"], recipient, path)
                    send_ok = True
                except Exception as e:
                    send_ok = False
                    print("Mail hatası:", e)
                capturing = False
                sent = True
                sent_time = time.time()
                sent_ok_flag = send_ok
            else:
                put_text(frame, f"CEKIM: {3 - int(elapsed)}",
                         (W // 2 - 80, 60), 1.4, (0, 0, 255), 3)
                put_text(frame, "Yumruk acmayin!", (W // 2 - 110, 100), 0.7, (0, 0, 255), 2)

        # Gönderildi bildirimi
        if sent:
            if time.time() - sent_time > 3.0:
                sent = False
                paint = np.zeros((H, W, 3), dtype=np.uint8)  # temizle
                prev = None
            else:
                msg = "GONDERILDI ✔" if sent_ok_flag else "MAIL HATASI"
                put_text(frame, msg, (W // 2 - 120, H // 2), 1.2,
                         (0, 255, 0) if sent_ok_flag else (0, 0, 255), 3)
                put_text(frame, recipient, (W // 2 - 150, H // 2 + 40), 0.7, (255, 255, 255), 2)

        # Çizimi görüntüye ekle
        display = cv2.add(frame, paint)

        # Üst bilgi
        put_text(display, f"-> {recipient}", (10, 25), 0.6, (200, 200, 200), 1)
        put_text(display, "Isaret parmagi: ciz  |  Yumruk: 3sn sonra cek", (10, H - 15), 0.6, (180, 180, 180), 1)
        if drawing:
            put_text(display, "[CIZIYOR]", (W - 160, 25), 0.7, (0, 255, 255), 2)

        cv2.imshow("UYT - CamDraw", display)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):  # q / ESC
            break
        elif key == ord("c"):
            paint = np.zeros((H, W, 3), dtype=np.uint8)
            prev = None
        elif key == ord("n"):  # yeni oyuncu
            break

    cap.release()
    cv2.destroyAllWindows()
    hands.close()


def main():
    sender = config_mod.ensure_sender()
    if not sender.get("sender_email"):
        return
    while True:
        res = ask_email()
        if res.get("cancel") or "email" not in res:
            break
        run_camera(res["email"], sender)
        again = messagebox.askyesno("Devam", "Yeni bir oyuncu ile devam edilsin mi?")
        if not again:
            break


if __name__ == "__main__":
    main()
