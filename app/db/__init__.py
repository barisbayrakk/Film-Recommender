# SQLAlchemy'nin veritabanı motoru oluşturmak için gerekli fonksiyonunu içe aktarır
from sqlalchemy import create_engine
# ORM oturumlarını (session) ve tablo sınıflarını tanımlamak için gerekli bileşenler
from sqlalchemy.orm import sessionmaker, declarative_base
# Ortam değişkenlerini okumak için os modülü
import os

##############################
# VERİTABANI BAĞLANTI AYARLARI
##############################
# Ortam değişkenlerinden DATABASE_URL okunur.
# Eğer ortam değişkeni tanımlı değilse, geliştirme ortamı için
# SQLite veritabanı varsayılan olarak kullanılı

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/movies.db")


# SQLite veritabanı kullanıldığında gerekli olan bağlantı ayarları
# check_same_thread=False parametresi, FastAPI gibi çok iş parçacıklı
# ortamlarda aynı veritabanı bağlantısının kullanılabilmesini sağlar.

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# --------------------------------------------------
# VERİTABANI MOTORU OLUŞTURMA
# --------------------------------------------------
# SQLAlchemy engine nesnesi oluşturulur.
# Bu nesne, uygulama ile veritabanı arasındaki
# tüm düşük seviyeli bağlantıyı yönetir.

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)

# --------------------------------------------------
# ORM OTURUM (SESSION) YAPILANDIRMASI
# --------------------------------------------------
# Veritabanı ile etkileşim kurmak için kullanılacak
# session nesnelerini üretecek factory tanımlanır.
# autocommit=False: Değişiklikler manuel olarak commit edilir.
# autoflush=False: Otomatik flush işlemi devre dışı bırakılır.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --------------------------------------------------
# ORM BASE SINIFI
# --------------------------------------------------

# Tüm ORM model sınıflarının miras alacağı Base sınıfı oluşturulur.
# Veritabanı tabloları bu Base sınıfı üzerinden tanımlanır.

Base = declarative_base()



# --------------------------------------------------
# VERİTABANI OTURUMU SAĞLAYICI FONKSİYON
# --------------------------------------------------

# Bu fonksiyon FastAPI router'ları tarafından kullanılır.
# Her istek için yeni bir veritabanı oturumu oluşturur
# ve işlem tamamlandığında oturumu güvenli şekilde kapatır.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
