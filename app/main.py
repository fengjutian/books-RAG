from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
from app.routes import upload, query

# 加载环境变量
load_dotenv()

# 检查DeepSeek API密钥配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
    raise ValueError("请配置有效的DeepSeek API密钥。请编辑.env文件并设置DEEPSEEK_API_KEY")

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
