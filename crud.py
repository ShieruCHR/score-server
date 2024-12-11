import datetime
import json
from uuid import uuid4

from sqlalchemy import Engine
from sqlmodel import Session, select

from models import Record
from schemas import PartialRecordSchema, RecordType


class CRUD:
    def __init__(self, engine: Engine):
        self.engine = engine

    def get_all(self):
        session = Session(self.engine)
        stmt = select(Record).order_by(Record.score.desc())
        return session.exec(stmt).all()

    def get_by_mode(self, mode: RecordType):
        with Session(self.engine) as session:
            stmt = (
                select(Record).where(Record.type == mode).order_by(Record.score.desc())
            )
            return (
                {"rank": i, "record": row}
                for i, row in enumerate(session.exec(stmt).all())
            )

    def get_by_id(self, id: str):
        with Session(self.engine) as session:
            stmt = select(Record).where(Record.id == id)
            return session.exec(stmt).first()

    def create_new(self, record: PartialRecordSchema) -> Record:
        with Session(self.engine) as session:
            new_record = Record(
                id=str(uuid4()),
                score=record.score,
                name=record.name,
                type=record.type,
                raw_metadata=json.dumps(record.metadata),
                raw_created_at=datetime.datetime.now().isoformat(),
            )
            session.add(new_record)
            session.commit()
            session.refresh(new_record)
        return new_record

    def delete(self, id: str):
        with Session(self.engine) as session:
            stmt = select(Record).where(Record.id == id)
            record = session.exec(stmt).first()
            session.delete(record)
            session.commit()
            return record
