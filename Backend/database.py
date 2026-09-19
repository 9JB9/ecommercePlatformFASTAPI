from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_PATH = Path(__file__).resolve().parent / "my_database.db" # anchored to Backend/ so the db resolves the same regardless of cwd
SQLITE_ALCHEMY_LINK = f"sqlite:///{DB_PATH}"

# connect sqlaclhemy to database
engine = create_engine(
    SQLITE_ALCHEMY_LINK,
    connect_args={"check_same_thread" : False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # NOT ASYNC

class Base(DeclarativeBase):
    pass

def get_db():
    with SessionLocal() as db:
        yield db