# app/main.py
# --------------------------------------------------
# FastAPI ana uygulama dosyası
# - Environment ayarları
# - Middleware (CORS)
# - Database init
# - Startup işlemleri
# - Router kayıtları
# --------------------------------------------------

from dotenv import load_dotenv
import os
# FastAPI çekirdek
from fastapi import FastAPI
# CORS ayarları için middleware
from fastapi.middleware.cors import CORSMiddleware
# OpenAPI şemasını özelleştirmek için
from fastapi.openapi.utils import get_openapi

# --------------------------------------------------
# ENV DOSYASI YÜKLEME
# --------------------------------------------------
# Bu dosyanın bulunduğu dizin
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Proje kökündeki .env dosyasının yolu
ENV_PATH = os.path.join(BASE_DIR, "..", ".env")

print("ENV DOSYASI:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

# --------------------------------------------------
# DATABASE & UTILS IMPORT
# --------------------------------------------------
from app.db import Base, engine, SessionLocal
# İlk veri yükleme scriptleri
from app.utils.init_data import import_local_movies, update_movie_posters
# TMDB üzerinden film çekme servisi
from app.services.tmdb_import import add_movies_to_db

# --------------------------------------------------
# ROUTER IMPORTLARI
# --------------------------------------------------
# Uygulamadaki tüm modüler router’lar burada toplanır
from app.routers import (
    auth, users, movies, ratings, reviews, lists, admin, recommend, likes, collections, chatbot, contact, watched, user_actions, dashboard, trivia
)


# --------------------------------------------------
# FASTAPI APP OLUŞTURMA
# --------------------------------------------------
app = FastAPI(title="Film Recommender API", version="1.0.0")
# --------------------------------------------------
# CORS AYARLARI
# --------------------------------------------------
# Frontend (React) erişimi için izin verilen origin listesi
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

cors_env = os.getenv("CORS_ORIGINS")
if cors_env:
    for origin in cors_env.split(","):
        origin = origin.strip()
        if origin and origin not in allowed_origins:
            allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# DATABASE TABLOLARINI OLUŞTUR
# --------------------------------------------------
# SQLAlchemy modellerine göre tabloları yaratır
Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# OPENAPI (SWAGGER) ÖZELLEŞTİRME
# --------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Film Recommender API",
        version="1.0.0",
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi

# --------------------------------------------------
# STARTUP EVENT
# --------------------------------------------------
@app.on_event("startup")
def startup_event():
    print("🔥 STARTUP BAŞLADI...")

    # 1) 1500 yerel film
    import_local_movies()

    # 2) TMDB popüler + upcoming
    db = SessionLocal()
    from app.models.movie import Movie
    add_movies_to_db(db, Movie)
    db.close()

    # 3) Poster update
    update_movie_posters()

    print("🔥 STARTUP TAMAMLANDI (1500 + TMDB)")

# ROUTERS
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(movies.router)
app.include_router(ratings.router)
app.include_router(reviews.router)
app.include_router(lists.router)
app.include_router(likes.router)
app.include_router(admin.router)
app.include_router(recommend.router)
app.include_router(collections.router)
app.include_router(chatbot.router)
app.include_router(contact.router)
app.include_router(watched.router)
app.include_router(user_actions.router)
app.include_router(dashboard.router)
app.include_router(trivia.router)
# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------
@app.get("/")
def home():
    return {"message": "Film Recommender Backend Running!"}
