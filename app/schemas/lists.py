# app/schemas/lists.py
from pydantic import BaseModel


class ListCreate(BaseModel):
    movie_id: int
    type: str  # Örn: "Favorilerim", "İzleyeceklerim"
