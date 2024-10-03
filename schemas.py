from datetime import datetime
from enum import Enum
from typing import Any, Dict
from pydantic import BaseModel, Field


class RecordType(str, Enum):
    TYPING = "TYPING"
    SHOOTING = "SHOOTING"


class RecordFilter(BaseModel):
    type: RecordType | None = None


class PartialRecordSchema(BaseModel):
    score: int
    name: str
    type: RecordType
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RecordSchema(PartialRecordSchema):
    id: str
    timestamp: datetime

    def json_safely(self):
        data = self.model_dump()
        data["timestamp"] = data["timestamp"].timestamp()
        return data


class RankedRecord(BaseModel):
    rank: int
    record: RecordSchema

    def json_safely(self):
        return {"rank": self.rank, "record": self.record.json_safely()}
