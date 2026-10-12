from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentRead


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    payload: DocumentCreate,
    session: AsyncSession = Depends(get_db),
):
    repository = DocumentRepository(session)

    return await repository.create(payload.filename)


@router.get(
    "",
    response_model=list[DocumentRead],
)
async def list_documents(
    session: AsyncSession = Depends(get_db),
):
    repository = DocumentRepository(session)

    return await repository.list_all()