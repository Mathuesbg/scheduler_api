from fastapi import FastAPI

from .routers import availability, bookings, users

app = FastAPI()

app.include_router(users.router)
app.include_router(bookings.router)
app.include_router(availability.router)
