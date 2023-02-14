import datetime
import uvicorn

from config import HOST_ADD, HOST_PORT
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from db import crud, schemas
from db.database import SessionLocal, engine
from samples.json import SAMPLE_JSON
from copy import deepcopy
from datetime import datetime
from pytz import timezone as tzone

tz = tzone('Europe/Moscow')
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


# response_model=schemas.UserDelete)
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
            output_json["pills"] = crud.get_pills(db, user)
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
async def get_schedule(context: dict, db: Session = Depends(get_db)):
    """
    Get list pills and schedules from DB\n
    context: {'tg_id': str|int}
    """
    tg_id = str(context["tg_id"])
    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            output_json["pills"] = crud.get_schedule(db, user)

    return output_json


@app.post("/schedule")
async def post_schedule(context: dict, db: Session = Depends(get_db)):
    """
    Add schedule to pill in DB\n
    context: {'tg_id': str|int, 'pill_id': str|int, 'timer':str} \n
    timer must be a multiple of 30 like '0:30' / '8:00' / 13:30 / 21:00
    """
    tg_id = str(context["tg_id"])
    pill_id = int(context["pill_id"])
    timer = str(context["timer"])
    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            pill = crud.get_pill(db, pill_id=pill_id)
            if user.id != pill.user_id:
                output_json["text"] = "Это не ваше лекарство"
                return output_json

            list_schedule = crud.get_schedule(db, user)

            for pill_elem in list_schedule:
                if pill_elem["id"] == pill_id:
                    timers = [timer["timer"] for timer in pill_elem['timers']]
                    if timer in timers:
                        output_json["text"] = "У вас уже выбрано это время"
                        return output_json

            crud.add_sch_timer(db, schemas.SchCreate(
                user_id=user.id,
                pill_id=pill.id,
                timer=timer,
            ))
            output_json["text"] = f"Я буду напоминать вам о приёме {pill.pill_name} ежедневно в {timer}"

    return output_json


@app.delete("/schedule/{id}")
async def del_schedule(context: dict, db: Session = Depends(get_db)):
    """
    Del pill's schedule from DB\n
    context: {'tg_id': str|int, timer_id: str|int, pill_id: str|int}
    """
    tg_id = str(context["tg_id"])
    timer_id = int(context["timer_id"])
    pill_id = int(context["pill_id"])

    output_json = await get_user(context, db)

    with engine.connect():
        if output_json["in_database"] and output_json["user"]["is_active"]:
            user = crud.get_user_by_tg(db, tg_id=tg_id)
            sch = crud.get_schedule_element(db, sch_id=timer_id)
            pill = crud.get_pill(db, pill_id=pill_id)
            if sch is None:
                output_json["text"] = "Указанного времени не существует"
                return output_json
            if user.id != sch.user_id:
                output_json["text"] = "Вы не можете это сделать"
                return output_json
            output_json["text"] = f"Время {sch.timer} удалено из списка напоминаний для '{pill.pill_name}'"
            crud.del_sch_timer(db, sch)

    return output_json


@app.get("/reminder")
async def get_reminds(db: Session = Depends(get_db)):
    """
    Get list pills and schedules from DB\n
    This operation is scheduled and called by the bot
    return json containing information about reminders at the time of the request
    """
    now = datetime.now(tz)
    if now.minute not in [0, 30]:
        return {"text": "Ты шо тут забыл?"}

    with engine.connect():
        output_list = []
        users = crud.get_users(db)
        minute = now.minute
        for user in users:
            hour = ((now.hour+int(user.timezone))+24) % 24
            timer = f"{hour}:{minute:02}"
            list_pills = crud.get_pills_by_time(db, user, timer)
            if not list_pills:
                continue
            user_info = await get_user({"tg_id": user.tg_id}, db)
            user_info["pills"] = list_pills
            output_list.append(user_info)

    return output_list


if __name__ == '__main__':
    uvicorn.run("__main__:app",
                host=HOST_ADD,
                port=int(HOST_PORT),
                reload=True
                )
