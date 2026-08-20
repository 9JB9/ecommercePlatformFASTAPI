from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLITE_ALCHEMY_LINK = "sqlite:///my_database.db"

engine = create_engine(
    SQLITE_ALCHEMY_LINK,
    connect_args={"check_same_thread" : False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db