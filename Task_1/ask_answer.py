# ask_answer.py
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

SAVE_DIR = "rag_store"
EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"

def load_index():
    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        multi_process=True,
        model_kwargs={"device": "cuda"},
        encode_kwargs={"normalize_embeddings": True},
    )
    return FAISS.load_local(
        SAVE_DIR,
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )

def answer_with_title(question: str, knowledge_index: FAISS) -> str:
    relevant_docs = knowledge_index.similarity_search(question, k=10)

    if not relevant_docs:
        return "please wait doctor answers"

    best_doc = relevant_docs[0]
    title = best_doc.metadata.get("title", "").strip()

    return title if title else "please wait doctor answers"

if __name__ == "__main__":
    knowledge_index = load_index()

    question = "คันที่ิอวัยวะเพศ"
    answer = answer_with_title(question, knowledge_index)

    print("Question:", question)
    print("Answer:", answer)
