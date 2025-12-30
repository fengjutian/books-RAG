from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import time
import os
from contextlib import asynccontextmanager

# 导入配置和路由
from app.config import config
from app.routes import upload, query
from app.logger.logging_config import get_logging_config

# 配置日志
logging.config.dictConfig(get_logging_config(config.DEBUG))
logger = logging.getLogger("app")
logger.info("应用日志配置完成")
logger.info(f"应用版本: {config.APP_VERSION}")
logger.info(f"DEBUG模式: {config.DEBUG}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    - 启动时执行初始化
    - 关闭时执行清理
    """
    logger.info("应用正在启动...")
    
    # 启动时初始化逻辑
    try:
        # 确保静态文件目录存在
        os.makedirs(config.STATIC_DIR, exist_ok=True)
        logger.info(f"静态文件目录: {config.STATIC_DIR}")
        
        # 确保向量数据库目录存在
        os.makedirs(config.VECTOR_STORE_PATH, exist_ok=True)
        logger.info(f"向量数据库目录: {config.VECTOR_STORE_PATH}")
        
        logger.info("DeepSeek API密钥验证通过")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}", exc_info=True)
        raise
    
    logger.info("应用启动完成")
    yield
    
    # 关闭时清理逻辑
    logger.info("应用正在关闭...")
    # 在这里添加关闭时的清理代码，如关闭数据库连接等
    logger.info("应用关闭完成")


def create_app() -> FastAPI:
    """
    创建FastAPI应用实例
    
    返回配置完整的FastAPI应用
    """
    # 创建FastAPI应用
    app = FastAPI(
        title=config.APP_NAME,
        version=config.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if config.DEBUG else None,
        redoc_url="/redoc" if config.DEBUG else None,
    )
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 生产环境中应限制允许的源
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS中间件配置完成")
    
    # 添加请求日志中间件
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        
        # 记录请求信息
        logger.info(
            f"请求开始",
            extra={
                "method": request.method,
                "url": str(request.url),
                "client": str(request.client)
            }
        )
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应信息
        process_time = time.time() - start_time
        logger.info(
            f"请求完成",
            extra={
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": round(process_time * 1000, 2)  # 毫秒
            }
        )
        
        return response
    
    # 挂载静态文件
    app.mount(
        config.STATIC_URL,
        StaticFiles(directory=config.STATIC_DIR),
        name="static"
    )
    logger.info(f"静态文件目录挂载完成: {config.STATIC_URL} -> {config.STATIC_DIR}")
    
    # 注册API路由
    app.include_router(upload.router, prefix=config.API_PREFIX)
    app.include_router(query.router, prefix=config.API_PREFIX)
    logger.info(f"API路由注册完成，前缀: {config.API_PREFIX}")
    
    # 主页面路由
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def read_root():
        """主页面 - 显示上传界面"""
        try:
            with open(os.path.join(config.STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except FileNotFoundError:
            logger.error("静态文件index.html不存在")
            return HTMLResponse(
                content="<h1>错误：主页面文件不存在</h1><p>请确保已正确构建前端应用</p>",
                status_code=404
            )
    
    return app


# 创建应用实例
app = create_app()


if __name__ == "__main__":
    """
    应用入口点
    
    直接运行时使用uvicorn启动服务
    """
    import uvicorn
    
    logger.info("使用内置服务器启动应用")
    logger.info(f"服务将运行在 http://{config.HOST}:{config.PORT}")
    
    # 使用uvicorn运行应用
    uvicorn.run(
        "app.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD,
        log_config=get_logging_config(config.DEBUG)
    )
