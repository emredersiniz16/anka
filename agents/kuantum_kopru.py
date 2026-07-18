# agents/kuantum_kopru.py - ANKA OS KUANTUM C KÖPRÜSÜ
#
# libanka_quantum.so için Python ctypes sarmalayıcı.
#
# Çift modlu çalışır:
#   • GERCEK_C  — Android/ARM64'te .so yüklenirse gerçek C katmanını kullanır.
#   • PYTHON_SIM — .so yüklenemezse (x86 geliştirme ortamı, .so eksik) tamamen
#                  Python ile aynı arayüzü simüle eder. Hiçbir hata fırlatmaz.
#
# Dışa açık API (her iki modda aynı imzalar):
#   kopru = KuantumKopru()
#   kopru.qd_init("device_fp", "kovan_secret")   → 0 / QD_OK
#   kopru.qd_seal(veri_bytes, tip)                → blok_id (int)
#   kopru.qd_collapse(blok_id)                   → bytes | None
#   kopru.qd_evolve(blok_id, yeni_veri_bytes)    → 0 / QD_OK
#   kopru.qd_total_noise_bytes()                 → int
#   kopru.qd_count_by_type(tip)                  → int
#   kopru.collapse_fire(tetikleyici)             → int
#   kopru.fsm_handle_event(olay)                 → 0 / hata
#   kopru.fsm_get_state()                        → SinekDurum (int)
#   kopru.fsm_state_name()                       → str

import os
import ctypes
import hashlib
import json
import struct
import threading
import time
from enum import IntEnum

# --- KUANTUM SABİTLERİ (quantum_dust.h / sinek_fsm.h / collapse_engine.h) ---

QD_OK             =  0
QD_ERR_NOT_INIT   = -1
QD_ERR_STORE_FULL = -2
QD_ERR_NOT_FOUND  = -3
QD_ERR_TAG_MISMATCH = -4

class QdTip(IntEnum):
    SENSOR_DATA    = 1
    KOVAN_STATE    = 2
    USER_INTERACT  = 3
    AMBIENT_OBS    = 4
    COMMAND_QUEUE  = 5

class SinekDurum(IntEnum):
    DORMANT   = 0
    AWAKE     = 1
    OBSERVING = 2
    COLLAPSED = 3
    ACTING    = 4
    SYNCING   = 5

class SinekOlay(IntEnum):
    SENSOR_DATA    =  1
    USER_COMMAND   =  2
    KOVAN_MSG      =  3
    TIMER          =  4
    AMBIENT_CHANGE =  5
    ACTION_DONE    =  6
    SYNC_DONE      =  7
    OFFLINE        =  8
    ONLINE         =  9
    SLEEP          = 10
    WAKE           = 11

class CollapseTetik(IntEnum):
    SENSOR  = 1
    USER    = 2
    KOVAN   = 3
    TIMER   = 4
    AMBIENT = 5

_DURUM_ISIMLERI = {
    SinekDurum.DORMANT:   "DORMANT (Uyku)",
    SinekDurum.AWAKE:     "AWAKE (Uyanık)",
    SinekDurum.OBSERVING: "OBSERVING (Gözlem)",
    SinekDurum.COLLAPSED: "COLLAPSED (Çöküş)",
    SinekDurum.ACTING:    "ACTING (Aksiyon)",
    SinekDurum.SYNCING:   "SYNCING (Senkron)",
}

# Struct boyutları (ARM64, quantum_dust.h'dan hesaplanmış)
_QD_BLOCK_SIZE   = 4096
_QD_BLOCK_T_SIZE = 4 + 4 + 8 + 12 + 16 + _QD_BLOCK_SIZE  # ≈ 4140 bytes
_QD_MAX_BLOCKS   = 256
_QD_STORE_T_SIZE = (_QD_MAX_BLOCKS * _QD_BLOCK_T_SIZE) + 4 + 4 + 32 + 32 + 128  # ~1.06 MB
_SINEK_FSM_T_SIZE = 512  # güvenli üst sınır


# ============================================================================
# Python Simülasyon Katmanı (fallback)
# ============================================================================

class _PythonSimStore:
    """
    qd_store_t'nin saf Python kopyası.
    Gerçek şifreleme yerine SHA-256 hash kullanır — mantıksal olarak aynı API.
    """
    def __init__(self):
        self._blocks: dict[int, dict] = {}  # id → {tip, veri, nonce}
        self._next_id = 1
        self._master_key = b""
        self._initialized = False
        self._lock = threading.Lock()

    def init(self, device_fp: str, kovan_secret: str) -> int:
        with self._lock:
            self._master_key = hashlib.sha256(
                f"{device_fp}:{kovan_secret}".encode()
            ).digest()
            self._initialized = True
        return QD_OK

    def seal(self, veri: bytes, tip: int) -> int:
        with self._lock:
            if not self._initialized:
                return QD_ERR_NOT_INIT
            nonce = os.urandom(12)
            blok_id = self._next_id
            self._next_id += 1
            # XOR-benzeri basit "şifreleme" (simülasyon — üretimde C katmanı kullanılır)
            anahtar = hashlib.sha256(self._master_key + nonce).digest()
            sifreli = bytes(b ^ anahtar[i % 32] for i, b in enumerate(veri))
            self._blocks[blok_id] = {"tip": tip, "sifreli": sifreli, "nonce": nonce}
            return blok_id

    def collapse(self, blok_id: int) -> bytes | None:
        with self._lock:
            blok = self._blocks.get(blok_id)
            if blok is None:
                return None
            nonce = blok["nonce"]
            anahtar = hashlib.sha256(self._master_key + nonce).digest()
            duzmetin = bytes(b ^ anahtar[i % 32] for i, b in enumerate(blok["sifreli"]))
            return duzmetin

    def evolve(self, blok_id: int, yeni_veri: bytes) -> int:
        with self._lock:
            if blok_id not in self._blocks:
                return QD_ERR_NOT_FOUND
            nonce = os.urandom(12)
            anahtar = hashlib.sha256(self._master_key + nonce).digest()
            sifreli = bytes(b ^ anahtar[i % 32] for i, b in enumerate(yeni_veri))
            self._blocks[blok_id]["sifreli"] = sifreli
            self._blocks[blok_id]["nonce"] = nonce
            return QD_OK

    def total_noise_bytes(self) -> int:
        with self._lock:
            return sum(len(b["sifreli"]) for b in self._blocks.values())

    def count_by_type(self, tip: int) -> int:
        with self._lock:
            return sum(1 for b in self._blocks.values() if b["tip"] == tip)

    def purge(self, blok_id: int):
        with self._lock:
            self._blocks.pop(blok_id, None)

    def destroy(self):
        with self._lock:
            self._blocks.clear()
            self._master_key = b""
            self._initialized = False


class _PythonSimFSM:
    """sinek_fsm_t Python kopyası."""
    _GECISLER = {
        # (durum, olay) → yeni_durum
        (SinekDurum.DORMANT,   SinekOlay.WAKE):          SinekDurum.AWAKE,
        (SinekDurum.AWAKE,     SinekOlay.SENSOR_DATA):   SinekDurum.OBSERVING,
        (SinekDurum.AWAKE,     SinekOlay.SLEEP):          SinekDurum.DORMANT,
        (SinekDurum.OBSERVING, SinekOlay.TIMER):          SinekDurum.COLLAPSED,
        (SinekDurum.OBSERVING, SinekOlay.USER_COMMAND):   SinekDurum.COLLAPSED,
        (SinekDurum.OBSERVING, SinekOlay.KOVAN_MSG):      SinekDurum.COLLAPSED,
        (SinekDurum.COLLAPSED, SinekOlay.ACTION_DONE):    SinekDurum.ACTING,
        (SinekDurum.ACTING,    SinekOlay.SYNC_DONE):      SinekDurum.SYNCING,
        (SinekDurum.ACTING,    SinekOlay.ACTION_DONE):    SinekDurum.AWAKE,
        (SinekDurum.SYNCING,   SinekOlay.SYNC_DONE):      SinekDurum.AWAKE,
        (SinekDurum.AWAKE,     SinekOlay.OFFLINE):        SinekDurum.AWAKE,
        (SinekDurum.AWAKE,     SinekOlay.ONLINE):         SinekDurum.AWAKE,
    }

    def __init__(self):
        self.durum = SinekDurum.DORMANT
        self.collapse_sayisi = 0
        self._lock = threading.Lock()
        self.baslangic = time.time()

    def handle_event(self, olay: int) -> int:
        with self._lock:
            key = (self.durum, SinekOlay(olay))
            if key in self._GECISLER:
                eski = self.durum
                self.durum = self._GECISLER[key]
                if self.durum == SinekDurum.COLLAPSED:
                    self.collapse_sayisi += 1
                return 0
            return -1

    def get_state(self) -> SinekDurum:
        with self._lock:
            return self.durum

    def uptime_ms(self) -> int:
        return int((time.time() - self.baslangic) * 1000)


# ============================================================================
# KuantumKopru — Birleşik Arayüz
# ============================================================================

class KuantumKopru:
    """
    Anka OS için birleşik kuantum köprüsü.
    Android/ARM64'te libanka_quantum.so kullanır,
    diğer ortamlarda Python simülasyonuyla devam eder.
    """

    def __init__(self, so_yolu: str | None = None):
        if so_yolu is None:
            so_yolu = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../core/quantum/libanka_quantum.so",
            )
        self._lib          = None
        self._store_buf    = None
        self._fsm_buf      = None
        self._sim_store    = _PythonSimStore()
        self._sim_fsm      = _PythonSimFSM()
        self.mod           = "PYTHON_SIM"
        self._initialized  = False
        self._so_yolu      = os.path.normpath(so_yolu)

        self._so_yukle()
        print(f"⚛️  [KUANTUM KÖPRÜ]: Mod → {self.mod}")

    # -----------------------------------------------------------------------
    # .so yükleme
    # -----------------------------------------------------------------------

    def _so_yukle(self):
        try:
            lib = ctypes.CDLL(self._so_yolu)
            # İmzaları doğrula
            lib.qd_init.argtypes  = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
            lib.qd_init.restype   = ctypes.c_int
            lib.qd_seal.argtypes  = [ctypes.c_void_p, ctypes.c_int,
                                      ctypes.c_char_p, ctypes.c_size_t,
                                      ctypes.POINTER(ctypes.c_uint32)]
            lib.qd_seal.restype   = ctypes.c_int
            lib.qd_collapse.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                         ctypes.c_char_p, ctypes.c_size_t,
                                         ctypes.POINTER(ctypes.c_size_t)]
            lib.qd_collapse.restype  = ctypes.c_int
            lib.qd_evolve.argtypes   = [ctypes.c_void_p, ctypes.c_uint32,
                                         ctypes.c_char_p, ctypes.c_size_t]
            lib.qd_evolve.restype    = ctypes.c_int
            lib.qd_total_noise_bytes.argtypes = [ctypes.c_void_p]
            lib.qd_total_noise_bytes.restype  = ctypes.c_size_t
            lib.qd_count_by_type.argtypes     = [ctypes.c_void_p, ctypes.c_int]
            lib.qd_count_by_type.restype      = ctypes.c_int
            lib.qd_destroy.argtypes           = [ctypes.c_void_p]
            lib.qd_destroy.restype            = None
            lib.collapse_init.argtypes        = [ctypes.c_void_p, ctypes.c_void_p]
            lib.collapse_init.restype         = ctypes.c_int
            lib.collapse_fire.argtypes        = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
            lib.collapse_fire.restype         = ctypes.c_int
            lib.sinek_fsm_init.argtypes       = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
            lib.sinek_fsm_init.restype        = ctypes.c_int
            lib.sinek_fsm_handle_event.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                                    ctypes.c_void_p, ctypes.c_size_t]
            lib.sinek_fsm_handle_event.restype  = ctypes.c_int
            lib.sinek_fsm_get_state.argtypes  = [ctypes.c_void_p]
            lib.sinek_fsm_get_state.restype   = ctypes.c_int
            lib.sinek_state_name.argtypes     = [ctypes.c_int]
            lib.sinek_state_name.restype      = ctypes.c_char_p

            self._lib       = lib
            self._store_buf = ctypes.create_string_buffer(_QD_STORE_T_SIZE)
            self._fsm_buf   = ctypes.create_string_buffer(_SINEK_FSM_T_SIZE)
            self.mod        = "GERCEK_C"
        except OSError as e:
            print(f"⚛️  [KUANTUM KÖPRÜ]: .so yüklenemedi ({e}) — Python simülasyonu aktif.")

    # -----------------------------------------------------------------------
    # Başlatma
    # -----------------------------------------------------------------------

    def baslat(self, device_fingerprint: str = "AnkaDevice", kovan_secret: str = "KovanGizli") -> int:
        """Kuantum deposunu ve FSM'yi başlatır."""
        if self.mod == "GERCEK_C":
            rc = self._lib.qd_init(
                self._store_buf,
                device_fingerprint.encode(),
                kovan_secret.encode(),
            )
            if rc == QD_OK:
                self._lib.collapse_init(self._store_buf, None)
                self._lib.sinek_fsm_init(self._fsm_buf, self._store_buf, None)
            self._initialized = (rc == QD_OK)
            return rc
        else:
            rc = self._sim_store.init(device_fingerprint, kovan_secret)
            self._initialized = True
            return rc

    # -----------------------------------------------------------------------
    # qd_seal — Deneyimi toza mühürle
    # -----------------------------------------------------------------------

    def qd_seal(self, veri: bytes, tip: int = QdTip.SENSOR_DATA) -> int:
        """
        Veriyi şifreleyerek kuantum tozu bloğuna mühürler.

        Returns:
            blok_id (>0) başarıda, negatif hata kodunda.
        """
        if not self._initialized:
            return QD_ERR_NOT_INIT

        if self.mod == "GERCEK_C":
            out_id = ctypes.c_uint32(0)
            rc = self._lib.qd_seal(
                self._store_buf, tip,
                veri, len(veri),
                ctypes.byref(out_id),
            )
            return int(out_id.value) if rc == QD_OK else rc
        else:
            return self._sim_store.seal(veri, tip)

    # -----------------------------------------------------------------------
    # qd_collapse — Toz bloğunu çöz
    # -----------------------------------------------------------------------

    def qd_collapse(self, blok_id: int) -> bytes | None:
        """
        Kuantum toz bloğunu çözer (şifreyi çözer).
        Gözlemci anahtara sahip değilse None döner.
        """
        if not self._initialized:
            return None

        if self.mod == "GERCEK_C":
            out_buf = ctypes.create_string_buffer(_QD_BLOCK_SIZE)
            out_len = ctypes.c_size_t(0)
            rc = self._lib.qd_collapse(
                self._store_buf, blok_id,
                out_buf, _QD_BLOCK_SIZE,
                ctypes.byref(out_len),
            )
            if rc == QD_OK:
                return bytes(out_buf.raw[:out_len.value])
            return None
        else:
            return self._sim_store.collapse(blok_id)

    # -----------------------------------------------------------------------
    # qd_evolve — Bloğu yeni veriyle evrilt
    # -----------------------------------------------------------------------

    def qd_evolve(self, blok_id: int, yeni_veri: bytes) -> int:
        if not self._initialized:
            return QD_ERR_NOT_INIT

        if self.mod == "GERCEK_C":
            return self._lib.qd_evolve(self._store_buf, blok_id, yeni_veri, len(yeni_veri))
        else:
            return self._sim_store.evolve(blok_id, yeni_veri)

    # -----------------------------------------------------------------------
    # Metrikler
    # -----------------------------------------------------------------------

    def qd_total_noise_bytes(self) -> int:
        """Depodaki toplam gürültü byte'ı — 'Sinek şu an kaç byte kuantum tozu taşıyor?'"""
        if not self._initialized:
            return 0
        if self.mod == "GERCEK_C":
            return int(self._lib.qd_total_noise_bytes(self._store_buf))
        return self._sim_store.total_noise_bytes()

    def qd_count_by_type(self, tip: int) -> int:
        if not self._initialized:
            return 0
        if self.mod == "GERCEK_C":
            return int(self._lib.qd_count_by_type(self._store_buf, tip))
        return self._sim_store.count_by_type(tip)

    # -----------------------------------------------------------------------
    # Collapse Engine
    # -----------------------------------------------------------------------

    def collapse_fire(self, tetikleyici: int = CollapseTetik.TIMER,
                      kullanici_girdisi: str | None = None) -> int:
        """
        Kuantum çöküşünü ateşler — kuralları tetikler, aksiyonları çalıştırır.

        Returns:
            Tetiklenen kural sayısı (>= 0).
        """
        if self.mod == "GERCEK_C":
            girdi_bytes = kullanici_girdisi.encode() if kullanici_girdisi else None
            girdi_len   = len(kullanici_girdisi) if kullanici_girdisi else 0
            return self._lib.collapse_fire(tetikleyici, girdi_bytes, girdi_len)
        else:
            # Simülasyon: her zamanlayıcı tetiklemesinde FSM'ye TIMER olayı gönder
            self._sim_fsm.handle_event(SinekOlay.TIMER)
            return 1

    # -----------------------------------------------------------------------
    # Sinek FSM
    # -----------------------------------------------------------------------

    def fsm_handle_event(self, olay: int, veri: bytes | None = None) -> int:
        if self.mod == "GERCEK_C":
            veri_ptr = (ctypes.c_char * len(veri))(*veri) if veri else None
            veri_len = len(veri) if veri else 0
            return self._lib.sinek_fsm_handle_event(self._fsm_buf, olay, veri_ptr, veri_len)
        else:
            return self._sim_fsm.handle_event(olay)

    def fsm_get_state(self) -> int:
        if self.mod == "GERCEK_C":
            return self._lib.sinek_fsm_get_state(self._fsm_buf)
        return int(self._sim_fsm.get_state())

    def fsm_state_name(self) -> str:
        durum = self.fsm_get_state()
        if self.mod == "GERCEK_C":
            raw = self._lib.sinek_state_name(durum)
            return raw.decode("utf-8", errors="replace") if raw else "BILINMEYEN"
        return _DURUM_ISIMLERI.get(SinekDurum(durum), "BILINMEYEN")

    # -----------------------------------------------------------------------
    # Temizlik
    # -----------------------------------------------------------------------

    def destroy(self):
        if self.mod == "GERCEK_C" and self._initialized:
            self._lib.qd_destroy(self._store_buf)
        else:
            self._sim_store.destroy()
        self._initialized = False


# -----------------------------------------------------------------------
# Bağımsız test
# -----------------------------------------------------------------------

if __name__ == "__main__":
    kopru = KuantumKopru()
    kopru.baslat("TestCihaz", "TestSirri")

    print("\n--- Toz Mühürleme ---")
    bid1 = kopru.qd_seal(b"Jammer sinyali tespit edildi.", QdTip.SENSOR_DATA)
    bid2 = kopru.qd_seal(b"Kullanici: Anka uyan!", QdTip.USER_INTERACT)
    print(f"Blok ID'leri: {bid1}, {bid2}")
    print(f"Toplam gürültü: {kopru.qd_total_noise_bytes()} bayt")

    print("\n--- Çöküş (Collapse) ---")
    duzmetin = kopru.qd_collapse(bid1)
    print(f"Çözülen: {duzmetin}")

    print("\n--- FSM Geçişleri ---")
    kopru.fsm_handle_event(SinekOlay.WAKE)
    print(f"Durum: {kopru.fsm_state_name()}")
    kopru.fsm_handle_event(SinekOlay.SENSOR_DATA)
    print(f"Durum: {kopru.fsm_state_name()}")
    kopru.collapse_fire(CollapseTetik.TIMER)
    print(f"Durum: {kopru.fsm_state_name()}")

    kopru.destroy()
