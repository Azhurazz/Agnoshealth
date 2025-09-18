# Symptom Classifier (RAG-based)

This project provides a **Retrieval-Augmented Symptom Classifier** that:

- Collects and updates symptom data (`agnos_forums.json`) via **web-scraping**  
- Builds a **vector knowledge base** using FAISS and multilingual embeddings  
- Retrieves the most relevant condition (`title`) from user symptom descriptions  
- Provides a **training pipeline** (`train_ingest.py`) to build the index  
- Provides a **query pipeline** (`ask_answer.py`) to search and classify symptoms  
- Provides a **Streamlit frontend** for interactive Q&A  

---

## Tools Used

- **Python** → Core programming language  
- **FAISS** → Vector similarity search engine  
- **Sentence-Transformers** → Multilingual embeddings (Thai + English)  
- **LangChain** → Document splitting and FAISS integration  
- **RAGatouille** → (Optional) ColBERT reranker for better retrieval  
- **Streamlit** → Frontend chatbot UI for classification  
- **tqdm** → Progress visualization  

---

## How to Run the Project

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Update & Train Knowledge Base
By default, `train_model.py` check the `UPDATE_DATA` flag:

- "Yes" -> runs `web-scraping.py` to update `agnos_forums.json`
- "No" -> rskips scraping and uses the existing dataset

```bash
cd Task_1
python train_model.py
```
This will build and save a FAISS index into the `rag_model/` folder.

### 3. Start the Frontend (Streamlit)
```bash
cd Task_1
streamlit run main.py --server.port 8000
```
This opens a chatbot-style UI where users can enter symptom descriptions and receive predicted diceases.

---

## Next Steps
- Add reranker (ColBERT-XM) for imporved retrieval
- Fine-tune LLM model 

