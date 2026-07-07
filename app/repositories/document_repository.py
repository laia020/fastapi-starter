from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_model import Document


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_owner(
        self,
        owner_id: str,
        limit: int,
        offset: int,
    ) -> list[Document]:
        statement = (
            select(Document)
            .where(Document.owner_id == owner_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(statement))

    def get_by_id_and_owner(
        self,
        document_id: str,
        owner_id: str,
    ) -> Document | None:
        statement = select(Document).where(
            Document.id == document_id,
            Document.owner_id == owner_id,
        )
        return self.db.scalar(statement)

    def create(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self.db.delete(document)
        self.db.commit()
