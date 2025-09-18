from fastapi import FastAPI
import sqlite3

app = FastAPI(title="Symptom API")

def search_symptoms(keyword: str):
    conn = sqlite3.connect("symptoms.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category_en, category_th, symptom FROM symptoms WHERE symptom LIKE ?",
        ('%' + keyword + '%',)
    )
    results = cursor.fetchall()
    conn.close()

    return [
        {"category_en": r[0], "category_th": r[1], "symptom": r[2]}
        for r in results if r[2]  # skip empty placeholders
    ]

@app.get("/search/")
def search(keyword: str):
    return {"results": search_symptoms(keyword)}
