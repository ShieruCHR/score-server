from contextlib import asynccontextmanager
import datetime
from fastapi import FastAPI
import json
import config

from crud import CRUD
from schemas import PartialRecordSchema, RecordSchema, RecordType

crud = None
data: list[RecordSchema] = []


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

    def serialize(record: RecordSchema):
        data = record.model_dump()
        data["timestamp"] = data["timestamp"].timestamp()
        return data

    with open("records.json", encoding="UTF-8", mode="w") as f:
        json.dump(tuple(map(serialize, data)), f, ensure_ascii=False)


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
def post_record(record: PartialRecordSchema):
    return crud.create_new(record)
