from fastapi import FastAPI
from app.routes import upload, query

app = FastAPI(title="PDF RAG FastAPI")

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
