# kovan/models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class Sinekler(Base):
    """Kovan'a bağlı olan tüm Sineklerin (cihazların) kimlik ve durum kayıtları."""
    __tablename__ = "sinekler"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    sinek_id = Column(String, unique=True, index=True)
    status = Column(String, default="OFFLINE") # ONLINE, OFFLINE, KARANTINA

class KaraKutuLog(Base):
    """Sineklerden Kovan'a akan tüm operasyonel verilerin (foto, ses, log) tutulduğu devasa arşiv."""
    __tablename__ = "kara_kutu_log"
    
    id = Column(Integer, primary_key=True, index=True)
    sinek_id = Column(String, index=True)
    islem_tipi = Column(String) # Örn: KAMERA_CEKIMI, SES_CIKISI
    veri_yolu = Column(String)  # Dosyanın kaydedildiği yol
    zaman = Column(DateTime, default=func.now())
