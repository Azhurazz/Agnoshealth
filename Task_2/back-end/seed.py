import pandas as pd
import ast
import sqlite3
import re

# Load Data
df = pd.read_csv("ai_symptom_picker.csv")
df["summary"] = df["summary"].apply(ast.literal_eval)

def extract_all_symptoms(summary):
    yes_symptoms = summary.get("yes_symptoms", [])
    return [item["text"] for item in yes_symptoms]

all_symptoms_lists = df["summary"].apply(extract_all_symptoms)

# flatten + unique
all_symptoms = sorted(set(s for sublist in all_symptoms_lists for s in sublist))

# Thai-only symptoms
thai_symptoms = [s for s in all_symptoms if any("\u0e00" <= ch <= "\u0e7f" for ch in s)]

# Category Mapping (English ↔ Thai)
CATEGORY_MAP = {
    "Ache": "อาการปวด",
    "Rash": "ผื่น",
    "Cough": "ไอ",
    "Phlegm": "เสมหะ",
    "RunnyNose": "น้ำมูกไหล",
    "Nasal": "จมูก",
    "Throat": "คอ",
    "Eye": "ตา",
    "Ear": "หู",
    "Skin": "ผิวหนัง",
    "Breathing": "การหายใจ",
    "Digestive": "ทางเดินอาหาร",
    "Neurological": "ระบบประสาท",
    "Mental": "สุขภาพจิต",
    "Urine": "ปัสสาวะ",
    "Lump": "ก้อน/บวม",
    "Syncope": "วูบ/เป็นลม",
    "General": "ทั่วไป",   # will be filled later
}

# Categorization Rules
rules = {
    "Ache":       lambda s: s.startswith("ปวด"),
    "Cough":      lambda s: "ไอ" in s,
    "Phlegm":     lambda s: "เสมหะ" in s,
    "RunnyNose":  lambda s: "น้ำมูก" in s,
    "Nasal":      lambda s: "จมูก" in s and "น้ำมูก" not in s,
    "Throat":     lambda s: "คอ" in s or "กลืน" in s,
    "Eye":        lambda s: any(k in s for k in ["ตา", "ขี้ตา", "กระบอกตา", "ลูกตา", "มอง"]) and "ตาย" not in s,
    "Ear":        lambda s: any(k in s for k in ["หู", "ได้ยิน"]),
    "Skin":       lambda s: any(k in s for k in ["ผื่น", "ผิว", "แผล", "คัน", "บวม"]),
    "Breathing":  lambda s: any(k in s for k in ["หอบ", "หายใจไม่ออก", "หายใจไม่สะดวก", "อก", "เสียงวี๊ด"]),
    "Digestive":  lambda s: any(k in s for k in ["ท้อง", "อาเจียน", "คลื่นไส้", "ถ่าย", "จุกเสียด", "อุดจาระ"]),
    "Neurological": lambda s: any(k in s for k in ["เวียนศีรษะ", "หน้ามืด", "ล้ม", "สั่น", "ชา"]),
    "Mental":     lambda s: any(k in s for k in ["ฆ่า", "คิด", "ตาย", "อยากตาย", "ซึมเศร้า", "เก็บตัว", "เครียด", "วิตก", "กังวล", "รู้สึก"]),
    "Urine":      lambda s: any(k in s for k in ["ปัสสาวะ", "ฉี่", "เจ็บขัด"]),
    "Lump":       lambda s: any(k in s for k in ["ก้อน", "ตุ่ม", "บวม"]),
    "Syncope":    lambda s: any(k in s for k in ["วูบ", "หน้ามืด", "เป็นลม", "ล้ม", "หมุน", "มึน", "เซ", "ทรงตัว"]),
    "Period":     lambda s: "ประจำเดือน" in s or "ตกขาว" in s,
    "Fever":      lambda s: "ไข้" in s,
}

# Categorize all symptoms
categories = {cat: [s for s in thai_symptoms if cond(s)] for cat, cond in rules.items()}

# Add General (leftovers)
used = {s for v in categories.values() for s in v}
categories["General"] = [s for s in thai_symptoms if s not in used]

# Ensure General exists even if empty
if "General" not in categories:
    categories["General"] = []

# Validation / Cleaning
def clean_symptom(symptom: str):
    parts = re.findall(r'(?:ปวด\w+|คอ\w*|ตา\w*|ผื่น\w*|ไข้\w*|หายใจ\w*)', symptom)
    return parts if parts and "".join(parts) == symptom else [symptom]

cleaned_symptoms = []
for cat in CATEGORY_MAP.keys():
    symptoms = categories.get(cat, [])
    if symptoms:
        for s in symptoms:
            for sym in clean_symptom(s):
                cleaned_symptoms.append((cat, CATEGORY_MAP[cat], sym))
    else:
        # Insert empty marker row so category still exists in DB
        cleaned_symptoms.append((cat, CATEGORY_MAP[cat], ""))

# Save to SQLite
with sqlite3.connect("symptoms.db") as conn:
    conn.execute("DROP TABLE IF EXISTS symptoms")
    conn.execute("""
        CREATE TABLE symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_en TEXT,
            category_th TEXT,
            symptom TEXT
        )
    """)

    # Sort General to always come first
    sorted_data = [row for row in cleaned_symptoms if row[0] == "General"] + \
                  sorted([row for row in cleaned_symptoms if row[0] != "General"], key=lambda x: x[0])

    conn.executemany("INSERT INTO symptoms (category_en, category_th, symptom) VALUES (?, ?, ?)", sorted_data)

print("Seed completed: saved symptoms into symptoms.db (English + Thai categories)")
