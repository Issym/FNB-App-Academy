from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "shopping.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)

def init_db():
    from . import models  # ensure models imported
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
