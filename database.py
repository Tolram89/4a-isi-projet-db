from pathlib import Path
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import models


DB_PATH = Path(__file__).resolve().parent / "poleatheck.sqlite"
sqlite_url = f"sqlite:///{DB_PATH}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

@event.listens_for(Engine, "connect")
def on_connect(dbapi_connection, _connection_record): # deuxieme parametre obligatoire car SQLAlchemy appelle avec deux arguments
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

def create_db_and_tables() :
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session