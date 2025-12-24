import os
from app.config import CHUNK_SIZE, CHUNK_OVERLAP, BASE_DIR
from app.models.document import PDFDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import shutil

PDF_STORAGE = os.path.join(BASE_DIR, "data", "pdfs")
os.makedirs(PDF_STORAGE, exist_ok=True)

def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def split_text_to_chunks(text: str):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_text(text)
    return chunks

async def process_pdf(file):
    # 保存 PDF
    pdf_path = os.path.join(PDF_STORAGE, file.filename)
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    # 读取 PDF 文本
    text = read_pdf(pdf_path)

    # 分块
    chunks = split_text_to_chunks(text)

    # 转 Document 节点
    docs = [PDFDocument(text=chunk, metadata={"source": file.filename}).to_node() for chunk in chunks]

    return docs, len(chunks)
