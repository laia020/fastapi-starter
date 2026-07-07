import logging

from fastapi import HTTPException, status

from app.models.document_model import Document
from app.models.user_model import User
from app.repositories.document_repository import DocumentRepository
from app.schemas.document_schema import DocumentCreate


logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, repository: DocumentRepository) -> None:
        self.repository = repository

    def create_document(
        self,
        payload: DocumentCreate,
        current_user: User,
    ) -> Document:
        document = Document(
            title=payload.title,
            content=payload.content,
            owner_id=current_user.id,
        )

        created_document = self.repository.create(document)
        logger.info(
            "document_created",
            extra={
                "document_id": created_document.id,
                "owner_id": current_user.id,
            },
        )
        return created_document

    def list_documents(
        self,
        current_user: User,
        limit: int,
        offset: int,
    ) -> list[Document]:
        return self.repository.list_by_owner(current_user.id, limit, offset)

    def get_document(self, document_id: str, current_user: User) -> Document:
        document = self.repository.get_by_id_and_owner(
            document_id,
            current_user.id,
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        return document

    def delete_document(self, document_id: str, current_user: User) -> None:
        document = self.get_document(document_id, current_user)
        self.repository.delete(document)
        logger.info(
            "document_deleted",
            extra={
                "document_id": document_id,
                "owner_id": current_user.id,
            },
        )
