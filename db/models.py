from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, PrimaryKeyConstraint, UniqueConstraint, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), default=" ")
    last_name = Column(String(50), default=" ")
    tg_id = Column(String(20), nullable=False)
    timezone = Column(String, nullable=True, default="0", )
    is_active = Column(Boolean, default=True, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    pill = relationship("Pill", back_populates="user")
    schedule = relationship("SchedulePills", back_populates="user")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_id'),
        UniqueConstraint("tg_id"),
    )


class Pill(Base):
    __tablename__ = "pills"

    id = Column(Integer, primary_key=True)
    pill_name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="pill")
    schedule = relationship("SchedulePills", back_populates="pill")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pill_id'),
    )


class SchedulePills(Base):
    __tablename__ = "schedulepills"

    id = Column(Integer, primary_key=True)
    timer = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    pill_id = Column(Integer, ForeignKey("pills.id"))
    created_on = Column(DateTime(), default=datetime.now)
    updated_on = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="schedule")
    pill = relationship("Pill", back_populates="schedule")

    __table_args__ = (
        PrimaryKeyConstraint('id', name='schedulepill_id'),
    )
