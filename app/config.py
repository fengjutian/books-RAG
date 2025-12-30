import os
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础目录配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class AppConfig:
    """应用配置类"""
    
    # 应用基本配置
    APP_NAME: str = "PDF RAG FastAPI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # 服务器配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    RELOAD: bool = os.getenv("RELOAD", "True").lower() == "true"
    
    # API配置
    API_PREFIX: str = "/api"
    
    # 静态文件配置
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")
    STATIC_URL: str = "/static"
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    
    # 向量数据库配置
    VECTOR_STORE_PATH: str = os.path.join(BASE_DIR, "data", "vector_db")
    
    # PDF 分块参数
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    
    @classmethod
    def validate(cls) -> None:
        """验证配置的有效性"""
        # 验证DeepSeek API密钥
        if not cls.DEEPSEEK_API_KEY or cls.DEEPSEEK_API_KEY == "your_deepseek_api_key_here":
            raise ValueError("请配置有效的DeepSeek API密钥。请编辑.env文件并设置DEEPSEEK_API_KEY")
        
        # 确保必要的目录存在
        os.makedirs(os.path.dirname(cls.VECTOR_STORE_PATH), exist_ok=True)

# 创建全局配置实例
config = AppConfig()

# 验证配置
config.validate()
