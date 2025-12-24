from fastapi import APIRouter, UploadFile, File
from app.services.pdf_service import process_pdf
from app.services.vector_service import add_documents_to_index

router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    docs, chunk_count = await process_pdf(file)
    add_documents_to_index(docs)
    return {"message": "PDF uploaded and indexed", "chunks": chunk_count}
