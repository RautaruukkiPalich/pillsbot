import uvicorn

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import crud, models, schemas
from db.database import SessionLocal, engine
from samples.json import SAMPLE_JSON
from copy import deepcopy


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
async def get_user(context: dict, db: Session = Depends(get_db)):
    """
    Get user info from DB\n
    context: {'tg_id': str}
    """

    tg_id = str(context["tg_id"])

    output_json = deepcopy(SAMPLE_JSON)

    with engine.connect():
        user = crud.get_user_by_tg(db, tg_id=tg_id)
        if user is not None:
            output_json["text"] = "Пользователь уже существует в базе"
            if not user.is_active:
                output_json["text"] = "Пользователь удалён. Вы не можете это сделать"
            output_json["in_database"] = True
            output_json["user"]["id"] = user.id
            output_json["user"]["tg"] = user.tg_id
            output_json["user"]["name"] = user.first_name
            output_json["user"]["surname"] = user.last_name
            output_json["user"]["is_active"] = user.is_active
            output_json["user"]["timezone"] = user.timezone
        else:
            output_json["in_database"] = False
            output_json["user"]["is_active"] = False
            output_json["text"] = "Пользователь не существует в базе"

    return output_json


# response_model=schemas.UserCreate
@app.post("/user")
async def create_user(context: dict, db: Session = Depends(get_db)):
    """
    Add user to DB\n
    context: {'tg_id': str|int, 'first_name': str, 'last_name': str, 'timezone': str}
    """

    tg_id = str(context["tg_id"])
    first_name = str(context["first_name"])
    last_name = str(context["last_name"])
    timezone = str(context["timezone"])

    if first_name is None:
        first_name = ""

    if last_name is None:
        last_name = ""

    with engine.connect():
        output_json = await get_user(context, db)
        if output_json["in_database"]:
            if not output_json["user"]["is_active"]:
                user = crud.get_user_by_tg(db, tg_id=tg_id)
                crud.activate_user(db, user, timezone)
                output_json["text"] = "Пользователь восстановлен"
            return output_json
        else:
            await crud.create_user(db, schemas.UserCreate(
                tg_id=tg_id,
                first_name=first_name,
                last_name=last_name,
                timezone=timezone,
            ))
            output_json["text"] = "Пользователь успешно добавлен"

    return output_json


# , response_model=schemas.UserDelete)
@app.delete("/user")
async def delete_user(context: dict, db: Session = Depends(get_db)):
    """
    Remove user from DB\n
    context: {'tg_id': str|int}
    """
    tg_id = str(context["tg_id"])

    with engine.connect():
        output_json = await get_user(context, db)

        if not output_json["in_database"]:
            output_json["text"] = "Пользователь не существует"
            return output_json

        if not output_json["user"]["is_active"]:
            output_json["text"] = "Пользователь уже удалён"
            return output_json

        user = crud.get_user_by_tg(db, tg_id=tg_id)
        crud.delete_user(db, user)
        output_json["text"] = "Пользователь удалён"

    return output_json


@app.get("/pills")
async def get_pill(context: dict, db: Session = Depends(get_db)):
    """
    Get pill list from DB\n
    context: {'tg_id': str|int}
    """
    tg_id = str(context["tg_id"])
    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            output_json["pills"] = crud.get_pills(db, user_id=user.id)
        else:
            output_json["text"] = "Пользователь не зарегистрирован"

    return output_json


@app.post("/pills")
async def add_pill(context: dict, db: Session = Depends(get_db)):
    """
    Add pill to DB\n
    context: {'tg_id': str|int, 'pill_name': str}
    """

    pill_name = str(context["pill_name"]).capitalize()
    tg_id = str(context["tg_id"])
    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            crud.create_pill(db, schemas.PillCreate(
                pill_name=pill_name,
                user_id=user.id,
            ))
            output_json["text"] = f"{pill_name} добавлен"

    return output_json


@app.patch("/pills/{id}")
async def edit_pill(context: dict, db: Session = Depends(get_db)):
    """
    Edit pill_name in DB\n
    context: {'tg_id': str|int, 'pill_name': str, 'pill_id': str|int}
    """

    tg_id = str(context["tg_id"])
    pill_id = int(context["pill_id"])
    pill_name = str(context["pill_name"]).capitalize()

    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            pill = crud.get_pill(db, pill_id=pill_id)
            if not pill:
                output_json["text"] = "Некорректные данные"
                return output_json
            if user.id != pill.user_id:
                output_json["text"] = "Вы не можете это сделать"
                return output_json
            output_json["text"] = f"{pill_name}: название изменено"
            crud.edit_pill_name(db, pill, pill_name)

    return output_json


@app.delete("/pills/{id}")
async def del_pill(context: dict, db: Session = Depends(get_db)):
    """
    Delete pill from DB\n
    context: {'tg_id': str|int, 'pill_id': str/int}
    """

    tg_id = str(context["tg_id"])
    pill_id = int(context["pill_id"])

    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            pill = crud.get_pill(db, pill_id=pill_id)
            if not pill:
                output_json["text"] = "Некорректные данные"
                return output_json
            if user.id != pill.user_id:
                output_json["text"] = "Вы не можете это сделать"
                return output_json
            output_json["text"] = f"{pill.pill_name} удалён из списка ваших лекарств"
            crud.del_pill(db, pill)

    return output_json


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
        pill = crud.get_pill(db, pill_id=pill_id)
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
