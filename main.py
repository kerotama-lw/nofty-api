# https://www.youtube.com/watch?v=G4vH5IqLvDI
# /UDjSSq,WW32a36

from fastapi import FastAPI
from pydantic import BaseModel

class Notification(BaseModel):
    src: str
    msg: str

app = FastAPI()

@app.get('/')
def read_root():
    return {"message": "KERORO"}

@app.get('/items/{id}')
def read_item(id: int):
    return {"item": id }

@app.post('/notify/')
def create_noti(notification: Notification):
    return notification