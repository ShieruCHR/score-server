import json
from datetime import datetime

from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class Record(SQLModel):
    id: int = Field(primary_key=True)
    score: int
    name: str
    type: str
    _metadata: str = Field(default="", sa_column=Column("metadata"))
    _created_at: str = Field(default="", sa_column=Column("created_at"))

    @property
    def metadata(self):
        return json.loads(self._metadata)

    @property
    def created_at(self):
        return datetime.fromisoformat(self._created_at)
