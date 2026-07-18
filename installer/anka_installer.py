"""
ANKA OS Installer — Windows GUI Kurulum Aracı
=============================================
USB'ye takılan Android cihazı otomatik tanır,
modeline özel ROM indirir ve ADB/fastboot ile flash'lar.

Gereksinimler (EXE build için):
    pip install pyinstaller
    build_exe.bat

Çalışma gereksinimleri (kaynak olarak):
    Python 3.8+  (tkinter dahil)
    ADB + Fastboot (PATH'te veya installer/ altında)
"""

import os
import sys
import json
import time
import hashlib
import threading
import subprocess
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# ─────────────────────────────────────────────
# Sabitler
# ─────────────────────────────────────────────
ANKA_REPO       = "emredersiniz16/anka"
ANKA_REPO_URL   = f"https://github.com/{ANKA_REPO}"
GH_API_RELEASES = f"https://api.github.com/repos/{ANKA_REPO}/releases/latest"
GH_API_DISPATCH = f"https://api.github.com/repos/{ANKA_REPO}/actions/workflows/rom_build.yml/dispatches"

APP_TITLE   = "🪰 ANKA OS Installer"
APP_VERSION = "v1.0.0"
WIN_W, WIN_H = 780, 560

# ADB komutunu bul: önce installer yanında, sonra PATH'te
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _find_tool(name: str) -> str:
    """ADB veya fastboot binary'sini bul."""
    local = os.path.join(_BASE_DIR, name + (".exe" if sys.platform == "win32" else ""))
    if os.path.isfile(local):
        return local
    return name  # PATH'teki sürüm

ADB      = _find_tool("adb")
FASTBOOT = _find_tool("fastboot")

# ─────────────────────────────────────────────
# ADB yardımcı fonksiyonlar
# ─────────────────────────────────────────────

def _run(cmd: list, timeout: int = 15) -> tuple[int, str, str]:
    """Komut çalıştır, (returncode, stdout, stderr) döndür."""
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return -1, "", f"{cmd[0]} bulunamadı. ADB/Fastboot yüklü mü?"
    except subprocess.TimeoutExpired:
        return -2, "", f"Zaman aşımı: {' '.join(cmd)}"


def adb_devices() -> list[dict]:
    """
    Bağlı ADB cihazlarını listele.
    [{"serial": "...", "state": "device|unauthorized|offline"}]
    """
    rc, out, _ = _run([ADB, "devices"])
    cihazlar = []
    for satir in out.splitlines()[1:]:
        parcalar = satir.split("\t")
        if len(parcalar) == 2:
            cihazlar.append({"serial": parcalar[0].strip(),
                              "state": parcalar[1].strip()})
    return cihazlar


def adb_getprop(serial: str, prop: str) -> str:
    """Cihazdan Android property oku."""
    rc, out, _ = _run([ADB, "-s", serial, "shell", "getprop", prop])
    return out.strip()


def cihaz_bilgisi_al(serial: str) -> dict:
    """Bir cihazın tüm tanımlayıcı bilgilerini topla."""
    return {
        "serial":       serial,
        "model":        adb_getprop(serial, "ro.product.model"),
        "codename":     adb_getprop(serial, "ro.product.device"),
        "brand":        adb_getprop(serial, "ro.product.brand"),
        "manufacturer": adb_getprop(serial, "ro.product.manufacturer"),
        "android":      adb_getprop(serial, "ro.build.version.release"),
        "sdk":          adb_getprop(serial, "ro.build.version.sdk"),
        "arch":         adb_getprop(serial, "ro.product.cpu.abi"),
        "board":        adb_getprop(serial, "ro.product.board"),
    }


def fastboot_devices() -> list[str]:
    """Fastboot modundaki cihazları listele."""
    rc, out, _ = _run([FASTBOOT, "devices"])
    return [s.split()[0] for s in out.splitlines() if s.strip()]


# ─────────────────────────────────────────────
# GitHub Releases
# ─────────────────────────────────────────────

def _gh_request(url: str, token: str = "") -> dict | None:
    """GitHub API isteği gönder."""
    try:
        headers = {"User-Agent": "AnkaOS-Installer/1.0",
                   "Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"******"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        return None


def en_son_release_al() -> dict | None:
    return _gh_request(GH_API_RELEASES)


def rom_url_bul(release: dict, codename: str) -> tuple[str, str]:
    """
    Release asset'leri arasında codename'e uygun ROM zip ve sha256 bul.
    Bulamazsa genel merlin zip'i döndür.
    """
    assets = release.get("assets", [])
    rom_url = sha_url = ""
    for a in assets:
        n = a["name"].lower()
        if codename.lower() in n and n.endswith(".zip"):
            rom_url = a["browser_download_url"]
        if codename.lower() in n and n.endswith(".sha256"):
            sha_url = a["browser_download_url"]
    # Codename bulunamazsa ilk zip'i al
    if not rom_url:
        for a in assets:
            if a["name"].endswith(".zip"):
                rom_url = a["browser_download_url"]
                break
    return rom_url, sha_url


def sha256_dogrula(dosya: str, beklenen: str) -> bool:
    h = hashlib.sha256()
    with open(dosya, "rb") as f:
        for blok in iter(lambda: f.read(65536), b""):
            h.update(blok)
    return h.hexdigest() == beklenen


# ─────────────────────────────────────────────
# İndirme (ilerleme callback'li)
# ─────────────────────────────────────────────

def rom_indir(url: str, hedef: str, ilerleme_cb=None) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            toplam = int(r.headers.get("Content-Length", 0))
            indirilen = 0
            with open(hedef, "wb") as f:
                while True:
                    blok = r.read(65536)
                    if not blok:
                        break
                    f.write(blok)
                    indirilen += len(blok)
                    if ilerleme_cb and toplam:
                        ilerleme_cb(indirilen / toplam * 100)
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────
# Flash işlemleri
# ─────────────────────────────────────────────

def adb_sideload(serial: str, zip_yolu: str, log_cb=None) -> bool:
    """ADB sideload ile ROM yükle (cihaz recovery modunda olmalı)."""
    if log_cb:
        log_cb(f"ADB sideload başlıyor: {zip_yolu}")
    rc, out, err = _run([ADB, "-s", serial, "sideload", zip_yolu], timeout=300)
    if log_cb:
        if out:
            log_cb(out)
        if err:
            log_cb(err)
    return rc == 0


def cihazi_recovery_a_al(serial: str, log_cb=None) -> bool:
    """Cihazı recovery moduna geçir."""
    if log_cb:
        log_cb("Cihaz recovery moduna geçiriliyor...")
    rc, _, _ = _run([ADB, "-s", serial, "reboot", "recovery"])
    if log_cb:
        log_cb("Recovery bekleniyor (20 sn)...")
    time.sleep(20)
    return rc == 0


# ─────────────────────────────────────────────
# GUI
# ─────────────────────────────────────────────

class AnkaInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} {APP_VERSION}")
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.resizable(False, False)
        self.configure(bg="#0a0a12")

        # Durum
        self.secili_cihaz: dict | None = None
        self.secili_release: dict | None = None
        self._kurulum_thread: threading.Thread | None = None

        self._stiller_yukle()
        self._arayuz_olustur()
        self._log("🪰 ANKA OS Installer hazır. Cihazınızı USB ile bağlayın.")
        self._log("USB Hata Ayıklama açık olmalı: Ayarlar → Geliştirici Seçenekleri")
        self.after(500, self._cihazlari_tara)

    # ── Stiller ──────────────────────────────

    def _stiller_yukle(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("TFrame",       background="#0a0a12")
        s.configure("TLabel",       background="#0a0a12", foreground="#e0e0ff",
                    font=("Segoe UI", 10))
        s.configure("Title.TLabel", background="#0a0a12", foreground="#00e5ff",
                    font=("Segoe UI", 14, "bold"))
        s.configure("Sub.TLabel",   background="#0a0a12", foreground="#888aaa",
                    font=("Segoe UI", 9))
        s.configure("TButton",      background="#1a1a2e", foreground="#00e5ff",
                    font=("Segoe UI", 10, "bold"), borderwidth=1,
                    focusthickness=3, focuscolor="#00e5ff")
        s.map("TButton",
              background=[("active", "#00e5ff"), ("disabled", "#111122")],
              foreground=[("active", "#0a0a12"), ("disabled", "#444466")])
        s.configure("Green.TButton", background="#0d3b1f", foreground="#00ff88",
                    font=("Segoe UI", 11, "bold"))
        s.map("Green.TButton",
              background=[("active", "#00ff88"), ("disabled", "#0a1a10")],
              foreground=[("active", "#0a0a12"), ("disabled", "#335544")])
        s.configure("TProgressbar", troughcolor="#1a1a2e",
                    background="#00e5ff", thickness=8)
        s.configure("Treeview",     background="#0f0f1e", foreground="#c0c0e0",
                    fieldbackground="#0f0f1e", rowheight=28,
                    font=("Segoe UI", 10))
        s.configure("Treeview.Heading", background="#1a1a2e",
                    foreground="#00e5ff", font=("Segoe UI", 10, "bold"))
        s.map("Treeview", background=[("selected", "#00e5ff")],
              foreground=[("selected", "#0a0a12")])

    # ── Arayüz ───────────────────────────────

    def _arayuz_olustur(self):
        # ── Başlık
        baslik_frame = ttk.Frame(self)
        baslik_frame.pack(fill="x", padx=20, pady=(16, 4))
        ttk.Label(baslik_frame, text="🪰 ANKA OS Installer",
                  style="Title.TLabel").pack(side="left")
        ttk.Label(baslik_frame, text=APP_VERSION,
                  style="Sub.TLabel").pack(side="left", padx=8)
        self.durum_label = ttk.Label(baslik_frame, text="● Bekleniyor",
                                     foreground="#888aaa",
                                     background="#0a0a12",
                                     font=("Segoe UI", 9))
        self.durum_label.pack(side="right")

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # ── Sol panel: cihaz listesi + bilgi
        ana_frame = ttk.Frame(self)
        ana_frame.pack(fill="both", expand=True, padx=20, pady=4)

        sol = ttk.Frame(ana_frame)
        sol.pack(side="left", fill="both", expand=False, padx=(0, 12))

        ttk.Label(sol, text="📱 Bağlı Cihazlar",
                  font=("Segoe UI", 10, "bold"),
                  foreground="#00e5ff",
                  background="#0a0a12").pack(anchor="w")

        self.cihaz_tree = ttk.Treeview(sol, columns=("marka", "model", "android"),
                                        show="headings", height=5,
                                        selectmode="browse")
        self.cihaz_tree.heading("marka",   text="Marka")
        self.cihaz_tree.heading("model",   text="Model")
        self.cihaz_tree.heading("android", text="Android")
        self.cihaz_tree.column("marka",   width=90)
        self.cihaz_tree.column("model",   width=140)
        self.cihaz_tree.column("android", width=70)
        self.cihaz_tree.pack(fill="x")
        self.cihaz_tree.bind("<<TreeviewSelect>>", self._cihaz_secildi)

        # Tara butonu
        tara_frame = ttk.Frame(sol)
        tara_frame.pack(fill="x", pady=(6, 0))
        ttk.Button(tara_frame, text="🔄 Yenile",
                   command=self._cihazlari_tara).pack(side="left")
        self.tarama_label = ttk.Label(tara_frame, text="",
                                       style="Sub.TLabel")
        self.tarama_label.pack(side="left", padx=8)

        # Cihaz detay
        ttk.Label(sol, text="Cihaz Bilgileri",
                  font=("Segoe UI", 9, "bold"),
                  foreground="#888aaa",
                  background="#0a0a12").pack(anchor="w", pady=(10, 2))
        self.bilgi_text = tk.Text(sol, height=7, width=38,
                                   bg="#0f0f1e", fg="#c0c0e0",
                                   font=("Consolas", 9),
                                   relief="flat", state="disabled",
                                   insertbackground="#00e5ff")
        self.bilgi_text.pack(fill="x")

        # ── Sağ panel: log + ilerleme + kurulum
        sag = ttk.Frame(ana_frame)
        sag.pack(side="left", fill="both", expand=True)

        ttk.Label(sag, text="📋 Kurulum Kaydı",
                  font=("Segoe UI", 10, "bold"),
                  foreground="#00e5ff",
                  background="#0a0a12").pack(anchor="w")

        self.log_alan = scrolledtext.ScrolledText(
            sag, height=14, bg="#060610", fg="#a0ffa0",
            font=("Consolas", 9), relief="flat",
            insertbackground="#00e5ff", state="disabled")
        self.log_alan.pack(fill="both", expand=True)

        # İlerleme
        ilerleme_frame = ttk.Frame(sag)
        ilerleme_frame.pack(fill="x", pady=(6, 0))
        self.ilerleme_var = tk.DoubleVar()
        self.ilerleme_bar = ttk.Progressbar(ilerleme_frame,
                                             variable=self.ilerleme_var,
                                             maximum=100)
        self.ilerleme_bar.pack(fill="x")
        self.ilerleme_label = ttk.Label(ilerleme_frame, text="",
                                         style="Sub.TLabel")
        self.ilerleme_label.pack(anchor="e")

        # Kurulum butonu
        self.kur_btn = ttk.Button(sag, text="⚡ ANKA OS'u Kur",
                                   style="Green.TButton",
                                   command=self._kurulumu_baslat,
                                   state="disabled")
        self.kur_btn.pack(fill="x", pady=(8, 0))

        # ── Alt durum çubuğu
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=20, pady=4)
        alt_frame = ttk.Frame(self)
        alt_frame.pack(fill="x", padx=20, pady=(0, 8))
        ttk.Label(alt_frame,
                  text=f"GitHub: {ANKA_REPO_URL}",
                  style="Sub.TLabel").pack(side="left")
        self.release_label = ttk.Label(alt_frame, text="Release: —",
                                        style="Sub.TLabel")
        self.release_label.pack(side="right")

        # Arka planda release bilgisini çek
        threading.Thread(target=self._release_yukle, daemon=True).start()

    # ── Cihaz tarama ─────────────────────────

    def _cihazlari_tara(self):
        self.tarama_label.config(text="Taranıyor...")
        self.cihaz_tree.delete(*self.cihaz_tree.get_children())
        self.secili_cihaz = None
        self.kur_btn.config(state="disabled")
        threading.Thread(target=self._tara_thread, daemon=True).start()

    def _tara_thread(self):
        cihazlar = adb_devices()
        self.after(0, lambda: self.tarama_label.config(
            text=f"{len(cihazlar)} cihaz"))
        for c in cihazlar:
            if c["state"] == "unauthorized":
                self.after(0, lambda s=c["serial"]: self.cihaz_tree.insert(
                    "", "end", iid=s,
                    values=("⚠️ İzin Yok", s, "—")))
                self.after(0, lambda: self._log(
                    "⚠️ Cihaz izin bekliyor — telefonda 'Bu bilgisayara güven' onayını ver."))
                continue
            if c["state"] != "device":
                continue
            b = cihaz_bilgisi_al(c["serial"])
            self.after(0, lambda b=b: self.cihaz_tree.insert(
                "", "end", iid=b["serial"],
                values=(b["brand"], b["model"], b["android"])))
            self.after(0, lambda b=b: self._log(
                f"✅ Cihaz bulundu: {b['brand']} {b['model']} "
                f"(Android {b['android']}, {b['codename']})"))

    def _cihaz_secildi(self, event=None):
        sel = self.cihaz_tree.selection()
        if not sel:
            return
        serial = sel[0]
        cihazlar = adb_devices()
        for c in cihazlar:
            if c["serial"] == serial and c["state"] == "device":
                self.secili_cihaz = cihaz_bilgisi_al(serial)
                self._cihaz_bilgisi_goster(self.secili_cihaz)
                self._kur_butonu_guncelle()
                return

    def _cihaz_bilgisi_goster(self, b: dict):
        satir = (
            f"Marka     : {b['brand']} {b['manufacturer']}\n"
            f"Model     : {b['model']}\n"
            f"Codename  : {b['codename']}\n"
            f"Android   : {b['android']} (SDK {b['sdk']})\n"
            f"Mimari    : {b['arch']}\n"
            f"Board     : {b['board']}\n"
            f"Seri No   : {b['serial']}\n"
        )
        self.bilgi_text.config(state="normal")
        self.bilgi_text.delete("1.0", "end")
        self.bilgi_text.insert("end", satir)
        self.bilgi_text.config(state="disabled")

    # ── Release ──────────────────────────────

    def _release_yukle(self):
        r = en_son_release_al()
        if r:
            self.secili_release = r
            tag = r.get("tag_name", "?")
            self.after(0, lambda: self.release_label.config(
                text=f"Release: {tag}"))
            self.after(0, lambda: self._log(f"📦 GitHub Release bulundu: {tag}"))
            self.after(0, self._kur_butonu_guncelle)
        else:
            self.after(0, lambda: self._log(
                "⚠️ GitHub Release alınamadı — internet bağlantısını kontrol et."))

    def _kur_butonu_guncelle(self):
        if self.secili_cihaz and self.secili_release:
            self.kur_btn.config(state="normal")
        else:
            self.kur_btn.config(state="disabled")

    # ── Kurulum ──────────────────────────────

    def _kurulumu_baslat(self):
        if not self.secili_cihaz:
            messagebox.showwarning("Cihaz Seç", "Lütfen önce bir cihaz seçin.")
            return
        if not self.secili_release:
            messagebox.showwarning("Release Yok",
                                   "GitHub Release bilgisi alınamadı.\n"
                                   "İnternet bağlantısını kontrol et.")
            return

        onay = messagebox.askyesno(
            "Kurulumu Onayla",
            f"Cihaz: {self.secili_cihaz['brand']} {self.secili_cihaz['model']}\n"
            f"Sürüm: {self.secili_release.get('tag_name', '?')}\n\n"
            "ANKA OS kurulumu başlatılsın mı?\n"
            "⚠️ Cihaz TWRP recovery moduna geçirilecek.",
            icon="question"
        )
        if not onay:
            return

        self.kur_btn.config(state="disabled")
        self._kurulum_thread = threading.Thread(
            target=self._kurulum_thread_fn, daemon=True)
        self._kurulum_thread.start()

    def _kurulum_thread_fn(self):
        cihaz  = self.secili_cihaz
        release = self.secili_release

        self._durum("⏳ Kurulum hazırlanıyor...")
        self._log("=" * 50)
        self._log(f"🚀 Kurulum başlıyor: {cihaz['brand']} {cihaz['model']}")

        # 1. ROM URL bul
        rom_url, sha_url = rom_url_bul(release, cihaz["codename"])
        if not rom_url:
            self._log("❌ Bu cihaz için uygun ROM bulunamadı.")
            self._log(f"   Codename: {cihaz['codename']}")
            self._log("   GitHub Actions'da önce bir build çalıştırılmalı.")
            self._durum("❌ ROM bulunamadı")
            self.after(0, lambda: self.kur_btn.config(state="normal"))
            return

        self._log(f"📦 ROM URL: {rom_url}")

        # 2. İndir
        hedef = os.path.join(os.path.expanduser("~"), "Downloads",
                             "anka_os_rom.zip")
        self._log(f"⬇️  İndiriliyor → {hedef}")
        self._durum("⬇️  ROM indiriliyor...")

        def _ilerleme(pct):
            self.after(0, lambda p=pct: self.ilerleme_var.set(p))
            self.after(0, lambda p=pct: self.ilerleme_label.config(
                text=f"%{p:.0f}"))

        basari = rom_indir(rom_url, hedef, _ilerleme)
        if not basari:
            self._log("❌ İndirme başarısız. İnternet bağlantısını kontrol et.")
            self._durum("❌ İndirme hatası")
            self.after(0, lambda: self.kur_btn.config(state="normal"))
            return

        self._log("✅ İndirme tamamlandı.")

        # 3. SHA256 doğrula
        if sha_url:
            self._log("🔐 SHA256 doğrulanıyor...")
            try:
                with urllib.request.urlopen(sha_url, timeout=10) as r:
                    beklenen = r.read().decode().strip().split()[0]
                if sha256_dogrula(hedef, beklenen):
                    self._log(f"✅ SHA256 doğrulandı: {beklenen[:16]}...")
                else:
                    self._log("❌ SHA256 uyuşmazlığı! Dosya bozuk olabilir.")
                    self._durum("❌ Doğrulama hatası")
                    self.after(0, lambda: self.kur_btn.config(state="normal"))
                    return
            except Exception as e:
                self._log(f"⚠️  SHA256 doğrulama atlandı: {e}")
        else:
            self._log("⚠️  SHA256 dosyası bulunamadı, doğrulama atlandı.")

        # 4. Recovery'e geç
        self._log("📲 Cihaz TWRP recovery moduna alınıyor...")
        self._durum("📲 Recovery modu...")
        cihazi_recovery_a_al(cihaz["serial"], self._log)

        # 5. ADB sideload
        self._log("⚡ ADB sideload başlatılıyor...")
        self._durum("⚡ Flash ediliyor...")
        basari = adb_sideload(cihaz["serial"], hedef, self._log)

        if basari:
            self._log("🎉 KURULUM TAMAMLANDI! Cihazı yeniden başlatın.")
            self._durum("✅ Kurulum tamamlandı!")
            self.after(0, lambda: messagebox.showinfo(
                "Kurulum Tamamlandı",
                "🎉 ANKA OS başarıyla yüklendi!\n\n"
                "Cihazı yeniden başlatın:\n"
                "TWRP → Reboot → System"))
        else:
            self._log("⚠️  Sideload tamamlanamadı.")
            self._log("   Manuel kurulum için TWRP'de şunu dene:")
            self._log(f"   Install → {hedef}")
            self._durum("⚠️  Manuel kurulum gerekli")

        self.after(0, lambda: self.kur_btn.config(state="normal"))
        self.after(0, lambda: self.ilerleme_var.set(100))

    # ── Yardımcı ─────────────────────────────

    def _log(self, mesaj: str):
        def _yaz():
            self.log_alan.config(state="normal")
            self.log_alan.insert("end", mesaj + "\n")
            self.log_alan.see("end")
            self.log_alan.config(state="disabled")
        self.after(0, _yaz)

    def _durum(self, mesaj: str):
        renk = "#00ff88" if "✅" in mesaj or "🎉" in mesaj else \
               "#ff4444" if "❌" in mesaj else \
               "#ffaa00" if "⚠️" in mesaj else "#00e5ff"
        self.after(0, lambda: self.durum_label.config(
            text=f"● {mesaj}", foreground=renk))


# ─────────────────────────────────────────────
# Giriş noktası
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = AnkaInstallerApp()
    app.mainloop()
