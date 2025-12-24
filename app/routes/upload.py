from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import process_pdf
from app.services.vector_service import add_documents_to_index

router = APIRouter()

@router.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        # 检查文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="只支持PDF文件")
        
        docs, chunk_count = await process_pdf(file)
        add_documents_to_index(docs)
        return {"message": "PDF uploaded and indexed", "chunks": chunk_count}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {str(e)}")
