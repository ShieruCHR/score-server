from datetime import datetime
from enum import Enum, auto
from pydantic import BaseModel


class RecordType(str, Enum):
    TYPING = "TYPING"
    SHOOTING = "SHOOTING"


class RecordFilter(BaseModel):
    type: RecordType | None = None


class PartialRecordSchema(BaseModel):
    score: int
    name: str
    type: RecordType


class RecordSchema(PartialRecordSchema):
    id: str
    timestamp: datetime
