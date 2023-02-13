from sqlalchemy.orm import Session

from . import schemas, models


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        tg_id=user.tg_id,
        first_name=user.first_name,
        last_name=user.last_name,
        timezone=user.timezone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user: models.User):
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


def activate_user(db: Session, user: models.User, timezone):
    user.is_active = True
    user.timezone = timezone
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session):
    return db.query(models.User).filter(models.User.is_active == True).all()


def get_user_by_tg(db: Session, tg_id: str):
    user = db.query(models.User).filter(models.User.tg_id == tg_id).first()
    if user:
        return user
    return None


def create_pill(db: Session, pill: schemas.PillCreate):
    db_pill = models.Pill(
        pill_name=pill.pill_name,
        user_id=pill.user_id,
    )
    db.add(db_pill)
    db.commit()
    db.refresh(db_pill)
    return db_pill


def get_pill(db: Session, pill_id: int):
    """
    return:
    pill (object models.Pill)
    """
    pill = db.query(models.Pill).filter(models.Pill.id == pill_id).first()
    return pill if pill else None


def get_pills(db: Session, user_id: int):
    pills = db.query(models.Pill).filter(models.Pill.user_id == user_id).filter(models.Pill.is_active).order_by(models.Pill.pill_name.asc()).all()
    output_list = [{
        "id": pill.id,
        "name": pill.pill_name,
        "timers": []}
            for pill in pills]
    return output_list


def get_pills_by_time(db: Session, user: models.User, timer: str):
    sch_pills = db.query(models.SchedulePills).filter(models.SchedulePills.user_id == user.id).filter(models.SchedulePills.timer == timer).all()
    list_sch_id = (sch.pill_id for sch in sch_pills)
    pills = db.query(models.Pill).filter(models.Pill.id.in_(list_sch_id)).all()
    print(pills)
    output_list = [{
        "id": pill.id,
        "name": pill.pill_name,
        "timers": []}
            for pill in pills]
    return output_list
    #return pills


def del_pill(db: Session, pill: models.Pill):
    db.delete(pill)
    db.commit()
    return pill


def edit_pill_name(db: Session, pill: models.Pill, pill_name: str):
    pill.pill_name = pill_name
    db.commit()
    db.refresh(pill)
    return pill


def add_sch_timer(db: Session, sch: schemas.SchCreate):
    db_sch = models.SchedulePills(
        user_id=sch.user_id,
        pill_id=sch.pill_id,
        timer=sch.timer,
    )
    db.add(db_sch)
    db.commit()
    db.refresh(db_sch)
    return db_sch


def del_sch_timer(db: Session, sch: models.SchedulePills):
    db.delete(sch)
    db.commit()
    return sch


def get_schedule_element(db: Session, sch_id: int):
    sch = db.query(models.SchedulePills).filter(models.SchedulePills.id == sch_id).first()
    return sch if sch else None


def get_schedule(db: Session, user_id: int):
    pills_list = get_pills(db, user_id)
    schedules = db.query(models.SchedulePills).filter(models.Pill.user_id == user_id).all()
    for pill in pills_list:
        timers = [
            {
                "id": schedule.id,
                "timer": schedule.timer
            }
            for schedule in schedules if schedule.pill_id == pill["id"]
        ]
        pill["timers"] = timers

    return pills_list


# def bool_schedule_timer(db: Session, sch_time: str):
#     timer = db.query(models.SchedulePills).filter(models.SchedulePills.timer == sch_time).all()
#     return True if timer else False

