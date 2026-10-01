from pydantic import BaseModel


class ReviewCreate(BaseModel):
    text: str
    movie_id: int
