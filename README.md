# books-RAG

## 项目简介

books-RAG 是一个基于 FastAPI 的 PDF 文档检索增强生成 (Retrieval-Augmented Generation, RAG) 系统。该系统允许用户上传 PDF 文档，自动提取文本内容并构建向量索引，然后通过自然语言查询获取相关文档内容的精确答案。

## 技术栈

- **后端框架**: FastAPI
- **服务器**: Uvicorn
- **RAG 框架**: LlamaIndex 0.14.10
- **向量存储**: FAISS (Facebook AI Similarity Search)
- **文本分块**: LlamaIndex SentenceSplitter
- **嵌入模型**: HuggingFace sentence-transformers/all-MiniLM-L6-v2 (本地运行)
- **PDF 处理**: PyPDF2
- **配置管理**: Python 环境变量

## 功能特点

- ✅ **本地运行**: 使用本地嵌入模型，无需依赖外部 API，保护数据隐私
- ✅ **高效检索**: 基于 FAISS 向量存储的快速相似性搜索
- ✅ **智能分块**: 自动将长文本分割为语义连贯的小块
- ✅ **完整流程**: 从 PDF 上传到问答的端到端处理
- ✅ **API 友好**: 提供清晰的 RESTful API 接口
- ✅ **可扩展**: 支持添加更多文档类型和模型

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. **克隆项目**

```bash
git clone <repository-url>
cd books-RAG
```

2. **创建虚拟环境**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **安装依赖**

```bash
pip install -r requirements.txt
```

**当前项目配置说明**：
- 文本分块：使用 `llama_index.core.node_parser.SentenceSplitter`（已包含在 llama-index-core 中）
- 向量存储：使用默认的向量存储实现（依赖 faiss-cpu）
- 嵌入模型：当前使用 `MockEmbedding`（仅用于演示/调试），如需实际嵌入功能请安装上述依赖


### 运行项目

```bash
uvicorn app.main:app --log-config logging.conf  --host 0.0.0.0 --port 8000 --reload
```

服务器将在 `http://localhost:8000` 启动，API 文档可在 `http://localhost:8000/docs` 查看。

## 项目结构

```
books-RAG/
├── app/
│   ├── config.py          # 配置参数
│   ├── main.py            # FastAPI 应用入口
│   ├── models/
│   │   └── document.py    # 文档模型
│   ├── routes/
│   │   ├── upload.py      # 文件上传路由
│   │   └── query.py       # 查询路由
│   └── services/
│       ├── pdf_service.py # PDF 处理服务
│       └── vector_service.py # 向量存储服务
├── data/
│   ├── pdfs/              # PDF 文件存储目录
│   └── vector_db/         # 向量数据库存储目录
├── requirements.txt       # 项目依赖
└── README.md             # 项目说明
```

## API 文档

### 文件上传

- **URL**: `/api/upload`
- **方法**: `POST`
- **参数**: `file` (PDF 文件)
- **返回**: 上传结果和文档 ID

### 文档查询

- **URL**: `/api/query`
- **方法**: `POST`
- **参数**: `query` (查询文本)
- **返回**: 查询结果和相关文档信息

## 核心功能说明

### PDF 处理流程

1. **上传保存**: 接收用户上传的 PDF 文件并保存到本地
2. **文本提取**: 使用 PyPDF2 提取 PDF 中的文本内容
3. **文本分块**: 使用 SentenceSplitter 将长文本分割为小块
4. **节点转换**: 将文本块转换为 LlamaIndex 可处理的 Document 节点

### 向量存储流程

1. **嵌入生成**: 使用本地 HuggingFace 模型生成文本向量
2. **索引构建**: 将向量存储到 FAISS 索引中
3. **持久化**: 将索引保存到本地文件系统
4. **查询检索**: 根据用户查询生成向量，在索引中查找最相似的文本块

## 配置说明

主要配置参数在 `app/config.py` 文件中：

- `CHUNK_SIZE`: 文本分块大小 (默认: 1024)
- `CHUNK_OVERLAP`: 分块重叠大小 (默认: 20)
- `BASE_DIR`: 项目基础目录
- `VECTOR_STORE_PATH`: 向量存储路径

## 本地模型说明

本项目使用 `sentence-transformers/all-MiniLM-L6-v2` 作为本地嵌入模型：

- **模型大小**: 约 80MB
- **向量维度**: 384
- **性能**: 快速生成高质量嵌入，适合本地运行
- **语言支持**: 多语言支持，特别优化了英语

首次运行时，HuggingFace 会自动下载该模型到本地缓存目录。

## 注意事项

1. 确保有足够的磁盘空间存储 PDF 文件和向量索引
2. 大型 PDF 文件可能需要较长时间处理
3. 查询结果的质量取决于文档内容和查询的明确性
4. 本地嵌入模型的性能可能不如云端模型，但提供了更好的隐私保护

## 许可证

MIT License
