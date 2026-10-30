from app.services.query_embedding_cache import (
    generate_cached_query_embeddings,
)
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)


from app.schemas.document import (
    DocumentChunkProcessResult,
    DocumentChunkRead,
    DocumentContent,
    DocumentCreate,
    DocumentEmbeddingProcessResult,
    DocumentRead,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
)

from app.services.embedding_service import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    EmbeddingGenerationError,
    generate_document_embeddings,
    generate_embeddings,
)
from app.services.document_parser import (
    DocumentParsingError,
    extract_text,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.dependencies import get_db
from app.repositories.document import DocumentRepository
from app.schemas.document import (
    DocumentChunkProcessResult,
    DocumentChunkRead,
    DocumentContent,
    DocumentCreate,
    DocumentEmbeddingProcessResult,
    DocumentRead,
)
from app.repositories.document_chunk import DocumentChunkRepository
from app.services.text_chunker import (
    ChunkingError,
    split_text,
)
from app.services.document_storage import (
    InvalidDocumentFileError,
    save_upload,
    
)
from app.repositories.document_chunk import DocumentChunkRepository

from app.services.text_chunker import (
    ChunkingError,
    split_text,
)
from app.schemas.document import (
    DocumentChunkProcessResult,
    DocumentChunkRead,
    DocumentContent,
    DocumentCreate,
    DocumentRead,
)
from app.services.text_chunker import (
    ChunkingError,
    split_text,
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
@router.post(
    "/{document_id}/chunks",
    response_model=DocumentChunkProcessResult,
)
async def process_document_chunks(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(session)

    document = await document_repository.get_by_id(
        document_id
    )

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

        chunks = split_text(content)

    except (DocumentParsingError, ChunkingError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    chunk_repository = DocumentChunkRepository(
        session
    )

    stored_chunks = (
        await chunk_repository.replace_for_document(
            document.id,
            chunks,
        )
    )

    return DocumentChunkProcessResult(
        document_id=document.id,
        chunk_count=len(stored_chunks),
        chunks=stored_chunks,
    )
    
@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkRead],
)
async def list_document_chunks(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(session)

    document = await document_repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    chunk_repository = DocumentChunkRepository(
        session
    )

    return await chunk_repository.list_for_document(
        document_id
    )
@router.post(
    "/{document_id}/chunks",
    response_model=DocumentChunkProcessResult,
)
async def process_document_chunks(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(session)

    document = await document_repository.get_by_id(
        document_id
    )

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

        chunks = split_text(content)

    except (DocumentParsingError, ChunkingError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    chunk_repository = DocumentChunkRepository(
        session
    )

    stored_chunks = (
        await chunk_repository.replace_for_document(
            document.id,
            chunks,
        )
    )

    return DocumentChunkProcessResult(
        document_id=document.id,
        chunk_count=len(stored_chunks),
        chunks=stored_chunks,
    )
@router.get(
    "/{document_id}/chunks",
    response_model=list[DocumentChunkRead],
)
async def list_document_chunks(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(session)

    document = await document_repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    chunk_repository = DocumentChunkRepository(
        session
    )

    return await chunk_repository.list_for_document(
        document_id
    )
@router.post(
    "/{document_id}/embeddings",
    response_model=DocumentEmbeddingProcessResult,
)
async def process_document_embeddings(
    document_id: int,
    session: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(
        session
    )

    document = await document_repository.get_by_id(
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    chunk_repository = DocumentChunkRepository(
        session
    )

    chunks = await chunk_repository.list_for_document(
        document_id
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The document has no chunks. "
                "Process the document chunks first."
            ),
        )

    try:
        embeddings = await generate_document_embeddings(
    [
        chunk.content
        for chunk in chunks
    ]
)

    except EmbeddingGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    await chunk_repository.save_embeddings(
        document_id,
        embeddings,
    )

    return DocumentEmbeddingProcessResult(
        document_id=document_id,
        chunk_count=len(chunks),
        embedding_dimension=EMBEDDING_DIMENSION,
        model=EMBEDDING_MODEL_NAME,
    )

@router.post(
    "/search",
    response_model=SemanticSearchResponse,
)
async def semantic_search_documents(
    payload: SemanticSearchRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        query_embedding = (
            await generate_cached_query_embeddings(
            [payload.query]
)
        )[0]

    except EmbeddingGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    repository = DocumentChunkRepository(
        session
    )

    matches = await repository.semantic_search(
        query_embedding=query_embedding,
        limit=payload.limit,
    )

    results = [
        SemanticSearchResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            position=chunk.position,
            content=chunk.content,
            similarity=round(
                1.0 - distance,
                4,
            ),
        )
        for chunk, distance in matches
    ]

    return SemanticSearchResponse(
        query=payload.query,
        results=results,
    )