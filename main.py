from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime, timezone, timedelta
limit_otp_minutes = 5

class Notification(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    src: str = Field(index=True)
    msg: str = Field(index=True)
    time: datetime = Field(index=True, default_factory=lambda: datetime.now(timezone.utc))

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
async def read_root():
    return {"message": "Hello NOFTY"}

@app.get('/items/{id}')
async def read_item(id: int):
    return {"item": id }

@app.post('/notify/')
async def create_noti(
    notification: Notification, 
    session: SessionDep
) -> Notification:
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification

@app.get('/messages/')
async def read_otp(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Notification]:
    noti = session.exec(select(Notification).offset(offset).limit(limit)).all()
    return noti

@app.get('/search-otp/')
async def search_ref(
    ref: str = Query(..., min_length=1)
) -> list[Notification]:
    now = datetime.now(timezone.utc)
    limit_time = now - timedelta(minutes=limit_otp_minutes)
    with Session(engine) as session:
        statement = select(Notification).where(Notification.msg.contains(ref)).where(Notification.src == 'SMSNotification').where(Notification.time >= limit_time)
        results = session.exec(statement).all()
        return results
    
@app.get('/search-email-otp/')
async def search_ref(
    ref: str = Query(min_length=1)
) -> list[Notification]:
    now = datetime.now(timezone.utc)
    limit_time = now - timedelta(minutes=limit_otp_minutes)
    with Session(engine) as session:
        statement = select(Notification).where(Notification.msg.contains(ref)).where(Notification.src == 'OutlookNotification').where(Notification.time >= limit_time)
        results = session.exec(statement).all()
        return results