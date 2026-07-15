from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base

class Sinekler(Base):
    __tablename__ = "sinekler"
    id = Column(Integer, primary_key=True)
    token = Column(String, unique=True, index=True)
    sinek_id = Column(String, unique=True, index=True)
    status = Column(String, default="OFFLINE")

class KaraKutuLog(Base):
    __tablename__ = "kara_kutu_log"
    id = Column(Integer, primary_key=True)
    sinek_id = Column(String, index=True)
    islem_tipi = Column(String)
    veri_yolu = Column(String)
    zaman = Column(DateTime, default=func.now())
