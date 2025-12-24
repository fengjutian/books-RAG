from llama_index.core import Document

class PDFDocument:
    def __init__(self, text, metadata=None):
        self.text = text
        self.metadata = metadata or {}

    def to_node(self):
        return Document(text=self.text, metadata=self.metadata)
