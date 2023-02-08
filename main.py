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


# response_model=schemas.UserCreate
@app.post("/user")
async def create_user(data: dict, db: Session = Depends(get_db)):
    """
    Add user to DB\n
    data: {'tg_id': str, 'first_name': str, 'last_name': str}
    """

    with engine.connect():
        user, is_active, _ = crud.get_user_by_tg(db, tg_id=data["tg_id"])
        if is_active:
            return {"message": "Пользователь уже существует в базе"}
        if user:
            crud.activate_user(db, user)
            return {"message": "Пользователь восстановлен"}
        else:
            crud.create_user(db, schemas.UserCreate(
                tg_id=data["tg_id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
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
        user, is_active, _ = crud.get_user_by_tg(db, tg_id=data["tg_id"])
        if user and is_active:
            return {"message": "Пользователь уже существует в базе"}
        if user:
            crud.activate_user(db, user)
            return {"message": "Пользователь восстановлен"}
        else:
            crud.create_user(db, schemas.UserCreate(
                tg_id=data["tg_id"],
                first_name=data["first_name"],
                last_name=data["last_name"],
            ))

    return {"message": "Пользователя не существует в базе"}


@app.get("/pills")
async def get_pill(data: dict, db: Session = Depends(get_db)):
    """
    Add pill list from DB\n
    data: {'tg_id': str}
    """
    tg_id = str(data["tg_id"])

    with engine.connect():
        user, is_active, user_id = crud.get_user_by_tg(db, tg_id=tg_id)
        if user and is_active:
            list_pills = crud.get_pills(db, user_id=user_id)
        else:
            return {"message": "Пользователь не зарегистрирован"}

    return {"message": list_pills}


@app.post("/pills")
async def add_pill(data: dict, db: Session = Depends(get_db)):
    """
    Add pill to DB\n
    data: {'tg_id': str, 'pill_name': str}
    """

    pill_name = data["pill_name"].capitalize()
    tg_id = data["tg_id"]

    with engine.connect():
        user, is_active, user_id = crud.get_user_by_tg(db, tg_id=tg_id)
        if user and is_active:
            crud.create_pill(db, schemas.PillCreate(
                pill_name=pill_name,
                user_id=user_id,
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
        user, _, user_id = crud.get_user_by_tg(db, tg_id=tg_id)
        pill, pill_user_id, _ = crud.get_pill_info(db, pill_id=pill_id)

        if not user or not pill:
            return {"message": "Вы не можете это сделать"}
        if user_id != pill_user_id:
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
        user, is_active, user_id = crud.get_user_by_tg(db, tg_id=tg_id)
        pill, pill_user_id, pill_name = crud.get_pill_info(db, pill_id=pill_id)
        if not user or not pill:
            return {"message": "Вы не можете это сделать"}
        if user_id != pill_user_id:
            return {"message": "Это не ваше лекарство"}
        crud.del_pill(db, pill)

    return {"message": f"{pill_name} удалён из списка ваших лекарств"}


@app.get("/schedule")
async def get_schedule():
    return {"message": "schedule"}


if __name__ == '__main__':
    uvicorn.run("__main__:app", host='localhost', port=8000, reload=True)
