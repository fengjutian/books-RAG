from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv
from app.routes import upload, query
import logging
from app.logger.logging_config import get_logging_config

logging.config.dictConfig(get_logging_config())
logger = logging.getLogger("myapp")

# 加载环境变量
load_dotenv()
logger.info("环境变量加载完成")

# 检查DeepSeek API密钥配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
    raise ValueError("请配置有效的DeepSeek API密钥。请编辑.env文件并设置DEEPSEEK_API_KEY")

logger.info("DeepSeek API密钥验证通过")

app = FastAPI(title="PDF RAG FastAPI")
logger = logging.getLogger("myapp")
logger.info("FastAPI应用初始化完成，标题: PDF RAG FastAPI")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
logger.info("静态文件目录挂载完成，路径: /static")

app.include_router(upload.router, prefix="/api")
app.include_router(query.router, prefix="/api")
logger.info("API路由注册完成，前缀: /api")

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """主页面 - 显示上传界面"""
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

if __name__ == "__main__":
    import uvicorn
    logger.info("应用启动中...")
    logger.info("服务将运行在 http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_config=get_logging_config())
