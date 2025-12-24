from app.services.vector_service import query_vector_store

def answer_question(query: str):
    # 使用向量数据库检索 + LLM生成回答
    answer = query_vector_store(query)
    return answer
