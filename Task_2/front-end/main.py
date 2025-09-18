import streamlit as st
import sqlite3
import requests

# ===============================
# CONFIG
# ===============================
BACKEND_URL = "http://127.0.0.1:8001"  # backend FastAPI

# ===============================
# PAGE SETTINGS
# ===============================
st.set_page_config(
    page_title="Symptom Checker",
    page_icon="🩺",
    layout="centered"
)

# ===============================
# CSS THEME
# ===============================
st.markdown(
    """
    <style>
    body {
        background-color: white;
        color: #000080;
    }
    .stTextInput > div > div > input {
        background-color: #f0f8ff;
        color: black;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #0000FF;
    }
    .recommend-box {
        background-color: #ADD8E660;
        color: #000080;
        padding: 6px;
        border-radius: 12px;
        margin-bottom: 8px;
        font-weight: 500;
    }
    .category-title {
        color: #0000FF;
        font-size: 20px;
        margin-top: 15px;
        margin-bottom: 5px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# TITLE
st.title("🩺 Symptom Search")

# SEARCH INPUT
col1, col2 = st.columns([4, 1])

with col1:
    query = st.text_input(
        "พิมพ์อาการ", 
        placeholder="เช่น ผื่น, ไอ, ปวดหัว", 
        label_visibility="collapsed"
    )

with col2:
    search_clicked = st.button("🔍 ค้นหา", use_container_width=True)

# SEARCH BUTTON (call backend API)
if search_clicked:
    if query.strip():
        try:
            response = requests.get(f"{BACKEND_URL}/search/", params={"keyword": query.strip()})
            results = response.json().get("results", [])

            if results:
                st.subheader("ผลการค้นหา")
                grouped = {}
                cat_map = {}

                # Expect backend to return category_en + category_th + symptom
                for r in results:
                    cat_en = r.get("category_en", r.get("category", ""))  # fallback if API still sends "category"
                    cat_th = r.get("category_th", "")
                    sym = r.get("symptom", "")
                    if not cat_en or not sym:
                        continue
                    grouped.setdefault(cat_en, []).append(sym)
                    cat_map[cat_en] = cat_th

                for cat_en, symptoms in grouped.items():
                    cat_th = cat_map.get(cat_en, "")
                    st.markdown(f"<div class='category-title'>{cat_en} ({cat_th})</div>", unsafe_allow_html=True)
                    for s in symptoms:
                        st.markdown(f"<div class='recommend-box'>{s}</div>", unsafe_allow_html=True)
            else:
                st.warning("ไม่พบอาการที่ค้นหา")
        except Exception as e:
            st.error(f"❌ Error calling backend: {e}")

# BROWSE ALL DATA FROM DB
else:
    try:
        conn = sqlite3.connect("../back-end/symptoms.db")  # adjust path if needed
        cursor = conn.cursor()
        cursor.execute("SELECT category_en, category_th, symptom FROM symptoms")
        rows = cursor.fetchall()
        conn.close()

        grouped = {}
        cat_map = {}

        for cat_en, cat_th, sym in rows:
            grouped.setdefault(cat_en, []).append(sym)
            cat_map[cat_en] = cat_th

        categories = list(grouped.keys())
        selected_category = st.selectbox("เลือกหมวดหมู่อาการ", ["ทั้งหมด"] + categories)

        if selected_category == "ทั้งหมด":
            for cat_en, symptoms in grouped.items():
                cat_th = cat_map.get(cat_en, "")
                st.markdown(f"<div class='category-title'>{cat_en} ({cat_th})</div>", unsafe_allow_html=True)
                for s in symptoms:
                    st.markdown(f"<div class='recommend-box'>{s}</div>", unsafe_allow_html=True)
        else:
            cat_th = cat_map.get(selected_category, "")
            st.markdown(f"<div class='category-title'>{selected_category} ({cat_th})</div>", unsafe_allow_html=True)
            for s in grouped[selected_category]:
                st.markdown(f"<div class='recommend-box'>{s}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error reading database: {e}")