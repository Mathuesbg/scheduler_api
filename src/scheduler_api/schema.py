from datetime import time
from enum import Enum

from pydantic import BaseModel, EmailStr


class WeekDay(str, Enum):
    monday = 'monday'
    tuesday = 'tuesday'
    wednesday = 'wednesday'
    thursday = 'thursday'
    friday = 'friday'
    saturday = 'saturday'
    sunday = 'sunday'


class TimeRange(BaseModel):
    start: time
    end: time


class UserAvailability(BaseModel):
    day: WeekDay
    slots: list[TimeRange]


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    availability: list[UserAvailability]


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
