from sqlalchemy import create_engine
from config import DB_NAME, DB_PASS, DB_PORT, DB_USER, DB_HOST
from sqlalchemy.orm import sessionmaker

db_config = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    db_config,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

