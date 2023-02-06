from datetime import datetime, timedelta
from pydantic import BaseModel


class PillBase(BaseModel):
    pass


class PillCreate(PillBase):
    pill_name: str
    user_id: int


class Pill(PillBase):
    id: int
    created_on: datetime
    updated_on: datetime
    is_active = bool

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    tg_id: str
    first_name: str
    last_name: str


class User(UserBase):
    id: int
    is_active: bool
    tz: int
    created_on: datetime
    updated_on: datetime
    pills: list[Pill] = []

    class Config:
        orm_mode = True



