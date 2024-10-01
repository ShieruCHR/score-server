import datetime
from schemas import PartialRecordSchema, RecordSchema, RecordType
from uuid import uuid4
import config


class CRUD:
    def __init__(self, data: list[RecordSchema]):
        self.data = data

    def get_all(self):
        return self.data

    def get_by_mode(self, mode: RecordType):
        return tuple(filter(lambda x: x.type == mode, self.data))

    def get_by_id(self, id: str):
        return next(filter(lambda x: x.id == id, self.data))

    def create_new(self, record: PartialRecordSchema) -> RecordSchema:
        new_data = RecordSchema(
            id=str(uuid4()),
            timestamp=datetime.datetime.now(tz=config.TZ),
            **record.model_dump()
        )
        self.data.append(new_data)
        return new_data
