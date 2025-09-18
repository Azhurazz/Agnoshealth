# Chatbot Project & Recommender System

This repository was created as part of an **assignment for Agnos Health**.  
It contains two main tasks:  

- **Task 1** → Chatbot system (Q&A and data extraction)  
- **Task 2** → Recommender system (backend & frontend implementation)  

---

## Project Structure
```
agnoshealth/
│
├── Task_1/ # Chatbot implementation (RAG model)
│ ├── rag_model/ # Prebuilt model & data store
│ │ ├── index.faiss # FAISS vector index for similarity search
│ │ ├── index.pkl # Pickled embeddings / model index
│ │ ├── agnos_forums.csv # Forum dataset (CSV)
│ │ ├── agnos_forums.json # Forum dataset (JSON)
│ │
│ ├── ask_answer.py # Q&A pipeline script
│ ├── main.py # Entry point to run chatbot
│ ├── train_model.py # Script to train the chatbot
│ ├── web-scraping.py # Script for data collection
│ ├── README.md # Task 1 documentation
│
├── Task_2/ # Recommender system
│ ├── back-end/ # Backend (FastAPI + SQLite)
│ │ ├── main.py # FastAPI backend server
│ │ ├── ai_symptom_picker.py # Symptom extraction/processing
│ │ ├── seed.py # Script to seed the database
│ │ ├── symptoms.db # SQLite database for symptoms
│ │
│ ├── front-end/ # Frontend (Streamlit)
│ │ ├── main.py # Streamlit UI for user interaction
│ │ ├── README.md # Task 2 frontend documentation
│ │
│ ├── README.md # Task 2 documentation
│
├── requirements.txt # Python dependencies
└── README.md # Main project documentation
```
