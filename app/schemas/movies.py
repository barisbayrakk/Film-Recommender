# app/schemas/movies.py
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any


class MovieBase(BaseModel):
    title: str
    overview: Optional[str] = None
    overview_tr: Optional[str] = None   

    poster_path: Optional[str] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    backdrop_path: Optional[str] = None
    release_date: Optional[str] = None
    original_language: Optional[str] = None 

    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    popularity: Optional[float] = None

    # TMDB’den gelen dict listeler
    genres: Optional[List[Dict[str, Any]]] = None
    cast: Optional[List[Dict[str, Any]]] = None
    directors: Optional[List[Dict[str, Any]]] = None


class MovieOut(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
