from typing import List
from pydantic import BaseModel, Field
from .custom_types import Duration, StrList


class Song(BaseModel):
    albumName: str
    artistName: str
    discNumber: int
    duration: Duration = Field(alias="durationInMillis")
    genreNames: StrList
    name: str
    releaseDate: str
