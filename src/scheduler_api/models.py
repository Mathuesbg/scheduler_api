from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    availabilities = relationship(
        'Availability', back_populates='user', cascade='all, delete-orphan'
    )
    bookings = relationship(
        'Booking', back_populates='user', cascade='all, delete-orphan'
    )


class Availability(Base):
    __tablename__ = 'availabilities'

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'day', 'start', 'end', name='unique_availability'
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    day = Column(String(50), nullable=False)
    start = Column(Time, nullable=False)
    end = Column(Time, nullable=False)
    user = relationship('User', back_populates='availabilities')


class Booking(Base):
    __tablename__ = 'bookings'

    __table_args__ = (
        UniqueConstraint(
            'user_id', 'day', 'start', 'end', name='unique_booking'
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    client_name = Column(String(100), nullable=False)
    client_email = Column(String(100), nullable=False)
    day = Column(Date, nullable=False)
    start = Column(Time, nullable=False)
    end = Column(Time, nullable=False)
    user = relationship('User', back_populates='bookings')
