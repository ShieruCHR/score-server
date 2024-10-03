import datetime
from schemas import PartialRecordSchema, RankedRecord, RecordSchema, RecordType
from uuid import uuid4
import config


class CRUD:
    def __init__(self, data: list[RecordSchema]):
        self.data = data

    def get_all(self):
        return tuple(map(self.with_rank, self.data))

    def get_by_mode(self, mode: RecordType):
        return tuple(map(self.with_rank, filter(lambda x: x.type == mode, self.data)))

    def get_by_id(self, id: str):
        return next(map(self.with_rank, filter(lambda x: x.id == id, self.data)))

    def with_rank(self, record: RecordSchema) -> RankedRecord:
        sorted_data = sorted(
            tuple(filter(lambda x: x.type == record.type, self.data)),
            key=lambda x: x.score,
            reverse=True,
        )
        rank = next(
            (i for i, r in enumerate(sorted_data, 1) if r.id == record.id), None
        )
        return RankedRecord(rank=rank, record=record)

    def create_new(self, record: PartialRecordSchema) -> RecordSchema:
        new_data = RecordSchema(
            id=str(uuid4()),
            timestamp=datetime.datetime.now(tz=config.TZ),
            **record.model_dump()
        )
        self.data.append(new_data)
        return self.with_rank(new_data)
