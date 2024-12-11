import json
from datetime import datetime

from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class Record(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    score: int
    name: str
    type: str
    raw_metadata: str = Field(default="")
    raw_created_at: str = Field(default="")

    @property
    def score_metadata(self):
        return json.loads(self.raw_metadata)

    @property
    def created_at(self):
        return datetime.fromisoformat(self.raw_created_at)
