from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.routes import upload, query

app = FastAPI(title="PDF RAG FastAPI")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页面 - 显示上传界面"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
