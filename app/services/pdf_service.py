# -*- coding: utf-8 -*-
"""
PDF处理服务模块

该模块负责PDF文件的处理，包括：
1. PDF文件的保存与存储
2. PDF文本内容的提取
3. 文本内容的分块处理
4. 转换为LlamaIndex可处理的Document节点

是RAG系统中文本数据预处理的核心组件
"""
import os
# 导入配置参数：分块大小、重叠大小和基础目录
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, BASE_DIR
# 导入PDFDocument模型，用于PDF文档数据的封装
from app.models.document import PDFDocument
# 导入文本分块器，用于将长文本分割成合适大小的块
from llama_index.core.node_parser import SentenceSplitter
# 导入PDF阅读器，用于提取PDF文件中的文本内容
from PyPDF2 import PdfReader

# ------------------------------ 配置部分 ------------------------------
# PDF文件存储路径：基于BASE_DIR创建data/pdfs目录
PDF_STORAGE = os.path.join(BASE_DIR, "data", "pdfs")
# 确保PDF存储目录存在，如果不存在则创建
os.makedirs(PDF_STORAGE, exist_ok=True)


# ------------------------------ 核心函数 ------------------------------
def read_pdf(file_path: str) -> str:
    """
    从PDF文件中提取文本内容
    
    参数:
        file_path: str - PDF文件的路径
    
    返回:
        str - 提取的PDF文本内容
    """
    # 创建PDF阅读器对象
    reader = PdfReader(file_path)
    # 初始化文本变量
    text = ""
    # 遍历PDF的每一页，提取文本内容
    for page in reader.pages:
        # 提取当前页的文本，如果提取失败则使用空字符串
        text += page.extract_text() or ""
    # 返回提取的所有文本
    return text


def split_text_to_chunks(text: str):
    """
    将长文本分割成多个小块，以便后续进行向量嵌入和索引
    
    参数:
        text: str - 待分块的长文本
    
    返回:
        list - 分块后的文本列表
    """
    # 创建文本分块器，设置分块大小和重叠大小
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    # 执行分块操作
    chunks = splitter.split_text(text)
    # 返回分块后的文本列表
    return chunks


async def process_pdf(file):
    """
    处理上传的PDF文件，完成保存、文本提取、分块和节点转换的完整流程
    
    参数:
        file - 上传的PDF文件对象
    
    返回:
        tuple - (文档节点列表, 分块数量)
    """
    # 保存PDF文件到存储目录
    pdf_path = os.path.join(PDF_STORAGE, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # 从PDF文件中提取文本内容
    text = read_pdf(pdf_path)

    # 将提取的文本分割成小块
    chunks = split_text_to_chunks(text)

    # 将文本块转换为Document节点，包含元数据信息
    docs = [PDFDocument(text=chunk, metadata={"source": file.filename}).to_node() for chunk in chunks]

    # 返回文档节点列表和分块数量
    return docs, len(chunks)
