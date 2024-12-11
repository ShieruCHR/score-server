import datetime
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlmodel import Session, SQLModel, create_engine

import config
from crud import CRUD
from schemas import PartialRecordSchema, RecordSchema, RecordType

crud = None
data: list[RecordSchema] = []


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        await self.update()

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def update(self):
        for record in crud.get_all():
            await self.broadcast(record)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(_):
    global crud
    engine = create_engine("sqlite:///database.db")
    SQLModel.metadata.create_all(engine)

    crud = CRUD(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def get_records(record_type: RecordType | None = None):
    if record_type is None:
        return crud.get_all()
    else:
        return crud.get_by_mode(record_type)


@app.get("/{record_id}")
def get_single_record(record_id: str):
    return crud.get_by_id(record_id)


@app.post("/", response_model=RecordSchema)
async def post_record(record: PartialRecordSchema):
    data = crud.create_new(record)
    await manager.update()
    return RecordSchema(
        id=data.id,
        score=data.score,
        name=data.name,
        type=data.type,
        metadata=data.score_metadata,
        timestamp=data.created_at,
    )


@app.delete("/{record_id}")
async def delete_record(record_id: str):
    crud.delete(record_id)
    await manager.update()
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            print(await websocket.receive_text())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
