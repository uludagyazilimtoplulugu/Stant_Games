"""UYT Stant Oyunu 2 - Havada Çiz, Şekil Yap, Nesneleri Taşı.

Jestler:
  - İşaret parmağı (diğerleri kapalı) : ekranda serbestçe çiz / yaz.
  - Kapalı kutu/şekil çizersen       : şekil bir nesneye dönüşür (+5 puan).
  - Başparmak + işaret + orta parmak : nesneyi (şekil/yazı/resmi) tutup taşı.
  - Yumruk                           : ekranı kilitler (çizim kapalı).
  - Kapalıyken tekrar yumruk          : ekran yeniden serbest.

Bağımlılıklar: opencv-python, mediapipe (el takip modeli ilk açılışta
otomatik indirilir ve klasöre kaydedilir).
"""
import os
import time
import urllib.request

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

UYT_MAVI = (237, 100, 38)      # BGR -> #2563EB
CYAN = (0, 255, 255)
KIRMIZI = (68, 68, 239)
SARI = (0, 213, 245)

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
             "hand_landmarker/float16/1/hand_landmarker.task")
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "hand_landmarker.task")


def model_hazirla():
    """El takip modeli yoksa internetten indirir (bir kez)."""
    if os.path.exists(MODEL_PATH):
        return MODEL_PATH
    print("El takip modeli indiriliyor...")
    tmp = MODEL_PATH + ".tmp"
    urllib.request.urlretrieve(MODEL_URL, tmp)
    os.replace(tmp, MODEL_PATH)
    print("Model indirildi.")
    return MODEL_PATH


def landmarker_olustur():
    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=model_hazirla()),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_hand_presence_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    return vision.HandLandmarker.create_from_options(options)


def fingers_state(landmarks, label):
    """4 parmak için dik/çökük durumu ve başparmak durumunu döndürür."""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    up = [landmarks[t].y < landmarks[p].y for t, p in zip(tips, pips)]
    if label == "Right":
        thumb_up = landmarks[4].x < landmarks[2].x
    else:
        thumb_up = landmarks[4].x > landmarks[2].x
    return up, thumb_up


def kapali_mi(points):
    """İlk ve son nokta yakınsa ve yeterli nokta varsa şekil kapalıdır."""
    if len(points) < 12:
        return False
    x0, y0 = points[0]
    x1, y1 = points[-1]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    boy = max(max(xs) - min(xs), max(ys) - min(ys))
    if boy < 35:
        return False
    return ((x0 - x1) ** 2 + (y0 - y1) ** 2) ** 0.5 < boy * 0.45


def run_camera():
    try:
        landmarker = landmarker_olustur()
    except Exception as e:
        print("Model yüklenemedi (internet gerekli, bir kez indirilir):", e)
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Kamera açılamadı (index 0).")
        return

    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

    nesneler = []          # bitmis cizimler/sekiller
    aktif = None           # su an cizilen cizgi
    tasima_id = None       # tutulan nesnenin indeksi
    onceki_tasima = None   # bir onceki tasima parmak ucu
    kilitli = False
    yumruk_onceki = False
    isaret_onceki = False
    puan = 0
    t0 = time.monotonic()

    def put_text(img, text, pos, scale=0.9, color=(255, 255, 255), thick=2):
        cv2.putText(img, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color,
                    thick, cv2.LINE_AA)

    def nesne_ciz(img, n):
        pts = np.array(n["nokta"], np.int32)
        if n.get("sekil") and len(pts) >= 3:
            cv2.polylines(img, [pts], True, n["renk"], 3, cv2.LINE_AA)
        else:
            cv2.polylines(img, [pts], False, n["renk"], 4, cv2.LINE_AA)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)  # ayna görüntüsü

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ts = int((time.monotonic() - t0) * 1000)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = landmarker.detect_for_video(mp_image, ts)

        ciziyor = False
        tasıyor = False
        yumruk = False
        parmak_ucu = None

        if results.hand_landmarks:
            hand = results.hand_landmarks[0]
            label = results.handedness[0][0].category_name
            up, thumb_up = fingers_state(hand, label)

            isaret = up[0]
            orta = up[1]
            yuzuk = up[2]
            serce = up[3]
            digerleri_kapali = (not orta) and (not yuzuk) and (not serce)
            yumruk = (not any(up)) and (not thumb_up)

            # Başparmak + işaret + orta birlikte -> nesne taşı
            if thumb_up and isaret and orta and (not yuzuk) and (not serce):
                tasıyor = True
            elif isaret and digerleri_kapali:
                ciziyor = True

            parmak_ucu = (int(hand[8].x * W), int(hand[8].y * H))

        # --- Yumruk: kilidi aç/kapa (kenar tetikli) ---
        if yumruk and not yumruk_onceki:
            kilitli = not kilitli
            aktif = None
            tasima_id = None
            onceki_tasima = None
        yumruk_onceki = yumruk

        # --- Çizim / taşıma (kilitli değilse) ---
        if not kilitli and parmak_ucu is not None:
            if tasıyor:
                x, y = parmak_ucu
                if tasima_id is None:
                    # en yakın nesneyi tut
                    en_yakin, uzaklik = None, 60
                    for i, n in enumerate(nesneler):
                        cx = sum(p[0] for p in n["nokta"]) / len(n["nokta"])
                        cy = sum(p[1] for p in n["nokta"]) / len(n["nokta"])
                        d = ((cx - x) ** 2 + (cy - y) ** 2) ** 0.5
                        if d < uzaklik:
                            en_yakin, uzaklik = i, d
                    tasima_id = en_yakin
                if tasima_id is not None and onceki_tasima is not None:
                    dx = x - onceki_tasima[0]
                    dy = y - onceki_tasima[1]
                    nesneler[tasima_id]["nokta"] = [
                        (p[0] + dx, p[1] + dy) for p in nesneler[tasima_id]["nokta"]
                    ]
                onceki_tasima = (x, y)
                aktif = None
            elif ciziyor:
                onceki_tasima = None
                x, y = parmak_ucu
                if aktif is None or not isaret_onceki:
                    aktif = {"nokta": [(x, y)], "renk": CYAN, "sekil": False}
                else:
                    aktif["nokta"].append((x, y))
                # Kapalı çizim -> şekil nesnesi
                if len(aktif["nokta"]) >= 12 and kapali_mi(aktif["nokta"]):
                    aktif["sekil"] = True
                    nesneler.append(aktif)
                    aktif = None
                    puan += 5
            else:
                # parmak modu değişti: çizgiyi nesneye çevir
                onceki_tasima = None
                if aktif is not None and len(aktif["nokta"]) >= 3:
                    nesneler.append(aktif)
                aktif = None
        else:
            if aktif is not None and len(aktif["nokta"]) >= 3:
                nesneler.append(aktif)
            aktif = None
            onceki_tasima = None
            tasima_id = None

        isaret_onceki = ciziyor and not tasıyor

        # --- GÖRÜNTÜ ---
        display = frame.copy()
        for n in nesneler:
            nesne_ciz(display, n)
        if aktif is not None:
            nesne_ciz(display, aktif)

        # işaret parmağı imleci
        if parmak_ucu is not None and not kilitli:
            renk = SARI if tasıyor else CYAN
            cv2.circle(display, parmak_ucu, 10, renk, 2, cv2.LINE_AA)

        # HUD
        put_text(display, f"Puan: {puan}", (10, 30), 0.8, UYT_MAVI, 2)
        if kilitli:
            cv2.rectangle(display, (0, H - 70), (W, H), (40, 40, 60), -1)
            put_text(display, "EKRAN KİLİTLİ - tekrar yumruk yapın",
                     (10, H - 35), 0.75, KIRMIZI, 2)
            put_text(display, "Çıkış: q / ESC   |   Temizle: c",
                     (10, H - 10), 0.5, (170, 170, 170), 1)
        else:
            mod = "[TAŞIYOR]" if tasıyor else "[ÇİZİYOR]" if ciziyor else ""
            if mod:
                renk = SARI if tasıyor else CYAN
                put_text(display, mod, (W - 190, 30), 0.75, renk, 2)
            put_text(display,
                     "İşaret: çiz/yaz  |  Kapalı şekil: nesne  |  "
                     "Baş+İşaret+Orta: taşı  |  Yumruk: kilitle",
                     (10, H - 12), 0.55, (180, 180, 180), 1)

        cv2.imshow("UYT - CamDraw", display)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        elif key == ord("c"):
            nesneler.clear()
            aktif = None
            puan = 0

    cap.release()
    cv2.destroyAllWindows()
    landmarker.close()


def main():
    run_camera()


if __name__ == "__main__":
    main()
