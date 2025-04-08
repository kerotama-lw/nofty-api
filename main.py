# https://www.youtube.com/watch?v=G4vH5IqLvDI
# /UDjSSq,WW32a36
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    src: str = Field(index=True)
    msg: str = Field(index=True)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(on_startup=[create_db_and_tables])

@app.get('/')
def read_root():
    return {"message": "KERORO"}

@app.get('/items/{id}')
def read_item(id: int):
    return {"item": id }

@app.post('/notify/')
def create_noti(notification: Notification, session: SessionDep) -> Notification:
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

@app.get('/messages/')
def read_otp(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Notification] :
    noti = session.exec(select(Notification).offset(offset).limit(limit)).all()
    return noti