from datetime import date, time
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


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    availability: list[UserAvailability]


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class Booking(BaseModel):
    id: int
    day: date
    start: time
    end: time


class BookingCreate(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    day: date
    slot: TimeRange


class BookingPublic(BaseModel):
    message: str
    booking: Booking


class AvailableSlotsResponse(BaseModel):
    slots: list[TimeRange]