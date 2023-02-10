import uvicorn

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Ну и шо мы тут забыли?"}


@app.get("/user")
async def get_user(data: dict, db: Session = Depends(get_db)):
    """
    Get user from DB\n
    data: {'tg_id': str}
    """
    tg_id = str(data["tg_id"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        if user is not None:
            if user.is_active:
                return {"in_db": "true", "message": "Пользователь уже существует в базе"}
            crud.activate_user(db, user)
            return {"in_db": "true", "message": "Пользователь восстановлен"}

    return {"in_db": "false"}


# response_model=schemas.UserCreate
@app.post("/user")
async def create_user(data: dict, db: Session = Depends(get_db)):
    """
    Add user to DB\n
    data: {'tg_id': str, 'first_name': str, 'last_name': str, 'timezone': str}
    """

    tg_id = str(data["tg_id"])
    first_name = data["first_name"]
    last_name = data["last_name"]
    timezone = str(data["timezone"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        if user is not None:
            if user.is_active:
                crud.activate_user(db, user)
                return {"message": "Пользователь восстановлен"}
            return {"message": "Пользователь уже существует в базе"}
        else:
            crud.create_user(db, schemas.UserCreate(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                timezone=timezone,
            ))

    return {"message": "Пользователь успешно добавлен"}


# , response_model=schemas.UserDelete)
@app.delete("/user")
async def delete_user(data: dict, db: Session = Depends(get_db)):
    """
    Remove user from DB\n
    data: {'tg_id': str}
    """

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=data["tg_id"])
        if not user:
            return {"message": "Пользователь не существует"}
        if user.is_active:
            return {"message": "Пользователь уже удалён"}
        crud.delete_user(db, user)

    return {"message": "Пользователь удалён"}


@app.get("/pills")
async def get_pill(data: dict, db: Session = Depends(get_db)):
    """
    Add pill list from DB\n
    data: {'tg_id': str}
    """
    tg_id = str(data["tg_id"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        if user and user.is_active:
            list_pills = crud.get_pills(db, user_id=user.id)
        else:
            return {"in_db": "false", "message": "Пользователь не зарегистрирован"}

    return {"in_db": "true", "message": list_pills}


@app.post("/pills")
async def add_pill(data: dict, db: Session = Depends(get_db)):
    """
    Add pill to DB\n
    data: {'tg_id': str, 'pill_name': str}
    """

    pill_name = str(data["pill_name"]).capitalize()
    tg_id = str(data["tg_id"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        if user and user.is_active:
            crud.create_pill(db, schemas.PillCreate(
                pill_name=pill_name,
                user_id=user.id,
            ))
        else:
            return {"message": "Пользователь не зарегистрирован"}

    return {"message": f"{pill_name} добавлен"}


@app.patch("/pills/{id}")
async def edit_pill(data: dict, db: Session = Depends(get_db)):
    """
    Edit pill_name in DB\n
    data: {'tg_id': str, 'pill_name': str, 'pill_id': str/int}
    """

    tg_id = str(data["tg_id"])
    pill_id = int(data["pill_id"])
    pill_name = str(data["pill_name"]).capitalize()

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        pill = crud.get_pill_info(db, pill_id=pill_id)

        if not user or not pill:
            return {"message": "Вы не можете это сделать"}
        if user.id != pill.user_id:
            return {"message": "Это не ваше лекарство"}
        crud.edit_pill_name(db, pill, pill_name)

    return {"message": f"{pill_name}: название изменено"}


@app.delete("/pills/{id}")
async def del_pill(data: dict, db: Session = Depends(get_db)):
    """
    Delete pill from DB\n
    data: {'tg_id': str, 'pill_id': str/int}
    """

    tg_id = str(data["tg_id"])
    pill_id = int(data["pill_id"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        pill = crud.get_pill_info(db, pill_id=pill_id)
        pill_name = pill.pill_name
        if not user or not pill:
            return {"message": "Вы не можете это сделать"}
        if user.id != pill.user_id:
            return {"message": "Это не ваше лекарство"}
        crud.del_pill(db, pill)

    return {"message": f"{pill_name} удалён из списка ваших лекарств"}


@app.get("/schedule")
async def get_schedule(data: dict, db: Session = Depends(get_db)):
    tg_id = str(data["tg_id"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        if user and user.is_active:
            list_pills = crud.get_schedule(db, user_id=user.id)
        else:
            return {"in_db": "false", "message": "Пользователь не зарегистрирован"}

    return {"in_db": "true", "message": list_pills}


@app.post("/schedule")
async def post_schedule(data: dict, db: Session = Depends(get_db)):
    tg_id = str(data["tg_id"])
    pill_id = int(data["pill_id"])
    timer = str(data["timer"])

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        pill = crud.get_pill_info(db, pill_id=pill_id)
        if not user or not pill:
            return {"message": "Вы не можете это сделать"}
        if user.id != pill.user_id:
            return {"message": "Это не ваше лекарство"}

        crud.add_sch_timer(db, schemas.SchCreate(
            user_id=user.id,
            pill_id=pill.id,
            timer=timer,
        ))

    return {"message": f"Я буду напоминать вам о приёме {pill.pill_name} ежедневно в {timer}"}


if __name__ == '__main__':
    uvicorn.run("__main__:app", host='localhost', port=8000, reload=True)
