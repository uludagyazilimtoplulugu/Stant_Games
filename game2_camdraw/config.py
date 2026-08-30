"""Operatör ayarları (gönderen Gmail hesabı) config.json içinde saklanır."""
import os
import json

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def ensure_sender():
    """Gönderen bilgisi yoksa operatöre sorar ve kaydeder."""
    import tkinter as tk
    from tkinter import ttk, messagebox

    cfg = load_config()
    if cfg.get("sender_email") and cfg.get("sender_password"):
        return cfg

    root = tk.Tk()
    root.title("UYT - Operatör Ayarları")
    root.configure(bg="#0d1b2a")
    root.geometry("460x300")
    root.resizable(False, False)

    info = ("Bu oyun, çekilen fotoğrafları GMAIL üzerinden gönderir.\n"
            "Lütfen gönderen (booth) Gmail adresini ve\n"
            "UYGULAMA ŞİFRESİNİ (app password) girin.\n"
            "(Normal şifre çalışmaz; 2 adımlı doğrulama + uygulama şifresi gerekir.)")
    tk.Label(root, text=info, bg="#0d1b2a", fg="#e0e1dd",
             font=("Segoe UI", 11), wraplength=420, justify="left").pack(pady=15, padx=20)

    frm = tk.Frame(root, bg="#0d1b2a")
    frm.pack(padx=30, pady=5, fill="x")
    tk.Label(frm, text="Gönderen Gmail:", bg="#0d1b2a", fg="#f4a261",
             font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w", pady=4)
    e_mail = tk.Entry(frm, font=("Segoe UI", 12), bg="#1b263b", fg="white",
                      insertbackground="white", relief="flat")
    e_mail.grid(row=0, column=1, pady=4, sticky="ew")
    tk.Label(frm, text="Uygulama Şifresi:", bg="#0d1b2a", fg="#f4a261",
             font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", pady=4)
    e_pass = tk.Entry(frm, font=("Segoe UI", 12), bg="#1b263b", fg="white",
                      insertbackground="white", show="*", relief="flat")
    e_pass.grid(row=1, column=1, pady=4, sticky="ew")
    frm.columnconfigure(1, weight=1)

    result = {}

    def kaydet():
        m = e_mail.get().strip()
        p = e_pass.get().strip()
        if "@" not in m or not p:
            messagebox.showwarning("Eksik", "Geçerli bir Gmail ve şifre girin.")
            return
        result["sender_email"] = m
        result["sender_password"] = p
        save_config(result)
        root.destroy()

    tk.Button(root, text="💾 Kaydet ve Devam", command=kaydet, bg="#e63946",
              fg="white", font=("Segoe UI", 13, "bold"), relief="flat",
              padx=20, pady=8).pack(pady=20)
    root.mainloop()
    return result or load_config()
