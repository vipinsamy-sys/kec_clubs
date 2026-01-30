from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import date, time

class CreateEvent(BaseModel):
    title: str
    description: Optional[str] = None
    club: List[str] = Field(default_factory=list)
    certificates: List[str] = Field(default_factory=list)
    date: date
    time: time
    venue: str
    max_participants: Optional[int] = None
    current_participants: int = 0
    status: Literal["upcoming", "past"] = "upcoming"
    points: Optional[int] = None


