from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import answer_question

router = APIRouter()

class QueryRequest(BaseModel):
    text: str

@router.post("/query/")
async def query(req: QueryRequest):
    answer = answer_question(req.text)
    return {"answer": answer}
