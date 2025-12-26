import os

# 向量数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "data", "vector_db")

# PDF 分块参数
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
