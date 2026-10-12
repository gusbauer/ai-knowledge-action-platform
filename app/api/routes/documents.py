from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from app.services.document_parser import (
    DocumentParsingError,
    extract_text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.repositories.document import DocumentRepository
from app.schemas.document import (
    DocumentContent,
    DocumentCreate,
    DocumentRead,
)
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
@router.get(
    "/{document_id}/content",
    response_model=DocumentContent,
)
async def get_document_content(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    repository = DocumentRepository(session)

    document = await repository.get_by_id(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if document.storage_path is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The document has no uploaded file.",
        )

    try:
        content = await extract_text(
            document.storage_path
        )

    except DocumentParsingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return DocumentContent(
        id=document.id,
        filename=document.filename,
        content=content,
        character_count=len(content),
    )