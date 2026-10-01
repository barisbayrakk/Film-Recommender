import os
import sys
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------
# PYTHONPATH FIX
# ---------------------------
# Test dosyaları genelde /tests altında olur
# Bu yüzden proje kök dizinini (ROOT_DIR) manuel olarak sys.path'e ekliyoruz
# Böylece "app.*" importları testlerde sorunsuz çalışır
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
# FastAPI uygulaması
from app.main import app
# SQLAlchemy Base ve dependency
from app.database import Base, get_db


# ---------------------------
# TEST DATABASE
# ---------------------------
# Testler için ayrı bir SQLite veritabanı kullanılır
#  Asla production DB kullanılmaz
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------
# HER TEST ÖNCESİ TABLOLARI SIFIRLA
# ---------------------------
# autouse=True → Bu fixture HER testten önce otomatik çalışır
# Amaç: testlerin birbirini etkilemesini önlemek
@pytest.fixture(autouse=True)
def reset_tables():
    # Var olan tüm tabloları sil
    Base.metadata.drop_all(bind=engine)
     # Tabloları yeniden oluştur
    Base.metadata.create_all(bind=engine)


# ---------------------------
# get_db DEPENDENCY OVERRIDE
# ---------------------------
# FastAPI normalde production DB kullanır
# Test sırasında bunu test DB ile override ederiz
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Asıl kritik nokta:
# get_db dependency'si test DB ile override ediliyor
# Böylece tüm endpoint testleri test.db üzerinden çalışır
app.dependency_overrides[get_db] = override_get_db
