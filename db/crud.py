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


def get_pill_info(db: Session, pill_id: int):
    """
    return:
    pill (object models.Pill)
    """
    pill = db.query(models.Pill).filter(models.Pill.id == pill_id).first()
    return pill if pill else None


def get_pills(db: Session, user_id: int):
    pills = db.query(models.Pill).filter(models.Pill.user_id == user_id).order_by(models.Pill.pill_name.asc()).all()
    output_dict = {pill.id: {"name": pill.pill_name} for pill in pills}
    return output_dict


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


def get_schedule(db: Session, user_id: int):
    output_dict = get_pills(db, user_id=user_id)
    schedules = db.query(models.SchedulePills).filter(models.Pill.user_id == user_id).order_by(models.SchedulePills.timer.desc()).all()
    for pill_id, _ in output_dict.items():
        timers = [schedule.timer for schedule in schedules if schedule.pill_id == pill_id]
        sort_timers = sorted(timers, key=lambda time: int(time.split(":")[0]))
        output_dict[pill_id]["schedules"] = sort_timers

    return output_dict


# def bool_schedule_timer(db: Session, sch_time: str):
#     timer = db.query(models.SchedulePills).filter(models.SchedulePills.timer == sch_time).all()
#     return True if timer else False

