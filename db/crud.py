from sqlalchemy.orm import Session

from . import schemas, models


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        tg_id=user.tg_id,
        first_name=user.first_name,
        last_name=user.last_name,
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


def activate_user(db: Session, user: models.User):
    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_tg(db: Session, tg_id: str):
    user = db.query(models.User).filter(models.User.tg_id == tg_id).first()
    if user:
        return user, user.is_active, user.id
    return None, None, None


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
    pill.user_id(int owner_id)
    pill.pill_name(str pill_name)
    """
    pill = db.query(models.Pill).filter(models.Pill.id == pill_id).first()
    if pill:
        return pill, pill.user_id, pill.pill_name
    return None, None, None

def get_pills(db: Session, user_id: int):
    pills = db.query(models.Pill).filter(models.Pill.user_id == user_id).order_by(models.Pill.pill_name.asc()).all()
    output_dict = {pill.id: pill.pill_name for pill in pills}
    return output_dict


def del_pill(db: Session, pill: models.Pill):
    db.delete(pill)
    db.commit()
    return pill
