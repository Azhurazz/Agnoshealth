# Symptom Search Project

This project provides a simple **Symptom Search system** that:

- Extracts symptoms from a CSV dataset  
- Categorizes them (e.g., Ache, Rash, Cough, etc.)  
- Saves them into a lightweight **SQLite database**  
- Provides a **FastAPI backend** for querying symptoms  
- Provides a **Streamlit frontend** to interact with the system  

---

## Tools Used

- **Python** → Core programming language  
- **Pandas** → Read and process CSV file  
- **SQLite** → Lightweight database to store symptoms & categories  
- **FastAPI** → Backend API to search for symptoms  
- **Uvicorn** → ASGI server to run FastAPI  
- **Streamlit** → Frontend UI for symptom search  

---

## How to Run the Project

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed the Database
```bash
cd back-end
python seed.py
```

### 3. Start the Backend (FastAPI)
```bash
cd back-end
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
``` 
can test search using API as
http://127.0.0.1:8001/search/?keyword=ผื่น

### 4. Start the Frontend (Streamlit)
```bash
cd front-end
streamlit run main.py --server.port 8000
```

