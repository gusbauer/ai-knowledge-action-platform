from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentCreate, DocumentRead
from app.services.document_storage import (
    InvalidDocumentFileError,
    save_upload,
)


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


@router.post(
    "/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
):
    try:
        storage_path, size_bytes = await save_upload(file)

    except InvalidDocumentFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    repository = DocumentRepository(session)

    return await repository.create(
        filename=file.filename or "unknown",
        storage_path=storage_path,
        content_type=file.content_type,
        size_bytes=size_bytes,
    )