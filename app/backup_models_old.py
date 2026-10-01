from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base
from app.db import SessionLocal
from app.db import get_db

# ======================================================
# USER MODEL
# ======================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    name = Column(String, nullable=True)

    # HASHLENMİŞ ŞİFRE BURADA TUTULACAK
    hashed_password = Column(String, nullable=False)
        # ----------------------------
    # RELATIONSHIPS
    # ----------------------------
    # Bir kullanıcının birden fazla yorumu olabilir
    reviews = relationship("Review", back_populates="user")
    ratings = relationship("Rating", back_populates="user")
    lists = relationship("ListItem", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    genre = Column(String)
    description = Column(Text)


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("User", back_populates="reviews")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True)
    score = Column(Integer)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("User", back_populates="ratings")


class ListItem(Base):
    __tablename__ = "lists"

    id = Column(Integer, primary_key=True)
    type = Column(String)  # "watchlist" | "watched"
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("User", back_populates="lists")
