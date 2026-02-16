from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# 1. SETUP KONEKSI (Bikin file database lokal)
DATABASE_URL = "sqlite:///./data/sentinel_history.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DESAIN TABEL (SCHEMA)
class LogSensor(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    cpu = Column(Float)
    ram = Column(Float)
    battery = Column(Integer)

# 3. FUNGSI BUILDER (Jalankan ini buat bikin tabelnya)
def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database 'sentinel_history.db' berhasil dibuat!")

# Kalau file ini dijalankan langsung, dia akan bikin database
if __name__ == "__main__":
    init_db()