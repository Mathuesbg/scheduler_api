from fastapi import FastAPI

from .routers import bookings, users

app = FastAPI()

app.include_router(users.router)
app.include_router(bookings.router)
