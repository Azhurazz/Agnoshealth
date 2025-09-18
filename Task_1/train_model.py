# train_ingest.py
import os
import json
import subprocess
from typing import List
from tqdm import tqdm
from langchain.docstore.document import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy

SAVE_DIR = "rag_store"
os.makedirs(SAVE_DIR, exist_ok=True)

EMBEDDING_MODEL_NAME = "sentence-transformers/distiluse-base-multilingual-cased-v2"
DATA_FILE = "agnos_forums.json"
device = "cuda" if torch.cuda.is_available() else "cpu"

UPDATE_DATA = "No"

def update_data_file():
    if (UPDATE_DATA.lower() == "yes") or (UPDATE_DATA.lower() == "Yes"):
        print("Running web-scraping.py to update data...")
        subprocess.run(["python", "web-scraping.py"], check=True)
        print("Data file updated")
    else:
        print("Skipping web-scraping update")

def load_json_data(file_path: str) -> List[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_age_group(age: int) -> str:
    if age <= 20:
        return "วัยเด็ก"
    elif 21 <= age <= 45:
        return "วัยรุ่น"
    elif 46 <= age <= 60:
        return "วัยผู้ใหญ่"
    elif 61 <= age <= 70:
        return "วัยกลางคน"
    elif 71 <= age <= 80:
        return "วัยสูงอายุ"
    else:
        return "วัยชรา"

def build_knowledge_base(raw_data: List[dict], embedding_model_name: str):
    raw_docs = []
    for doc in tqdm(raw_data, desc="Preparing raw docs"):
        gender = doc.get("gender", "")
        age = int(doc.get("age", 0)) if str(doc.get("age", "")).isdigit() else 0
        age_group = get_age_group(age)

        # Augment detail_symptom
        augmented_text = f"{doc['detail_symptom']} (เพศ: {gender}, ช่วงวัย: {age_group})"

        raw_docs.append(
            LangchainDocument(
                page_content=augmented_text,
                metadata={
                    "title": doc.get("title", ""),
                    "gender": gender,
                    "age": age,
                    "age_group": age_group,
                    "date": doc.get("date", ""),
                    "symptom_badge": doc.get("symptom_badge", "")
                }
            )
        )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        add_start_index=True,
        strip_whitespace=True,
    )
    docs_processed = text_splitter.split_documents(raw_docs)

    embedding_model = HuggingFaceEmbeddings(
        model_name=embedding_model_name,
        multi_process=True,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )

    knowledge_index = FAISS.from_documents(
        docs_processed, embedding_model, distance_strategy=DistanceStrategy.COSINE
    )

    return knowledge_index

if __name__ == "__main__":
    update_data_file()
    data = load_json_data(DATA_FILE)
    knowledge_index = build_knowledge_base(data, EMBEDDING_MODEL_NAME)
    knowledge_index.save_local(SAVE_DIR)
    print(f"Knowledge base saved in {SAVE_DIR}/")
