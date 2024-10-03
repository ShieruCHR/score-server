from contextlib import asynccontextmanager
import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
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
            await self.broadcast(record.json_safely())


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(_):
    global crud
    with open("records.json", encoding="UTF-8") as f:
        records = json.load(f)
        for record in records:
            record["timestamp"] = datetime.datetime.fromtimestamp(
                record["timestamp"], config.TZ
            )
            data.append(RecordSchema(**record))
    crud = CRUD(data)
    yield
    with open("records.json", encoding="UTF-8", mode="w") as f:
        json.dump(tuple(map(lambda d: d.json_safely(), data)), f, ensure_ascii=False)


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


@app.post("/")
async def post_record(record: PartialRecordSchema):
    data = crud.create_new(record)
    await manager.update()
    return data


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            print(await websocket.receive_text())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
