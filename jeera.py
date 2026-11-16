import streamlit as st
import json
import os
from datetime import datetime

# ---------- الإعدادات والتصميم ----------
st.set_page_config(page_title="جيرة", page_icon="🏘️")

st.markdown("""
<style>
.stApp {direction: rtl; text-align: right; background-color: #F7F3EC;}
h1, h2, h3 {color: #2E6B4F;}
p, label, span, div {color: #2B2B2B;}
.stButton button {background-color: #2E6B4F; color: white; border-radius: 10px; border: none;}
.stButton button:hover {background-color: #24563F; color: white;}
.card {background: white; padding: 12px 16px; border-radius: 12px;
       border-right: 5px solid #2E6B4F; margin-bottom: 10px;}
.card small {color: #777;}
input, textarea, [data-baseweb="select"] > div {background-color: white !important; color: #2B2B2B !important;}
.stButton button p {color: white !important;}
[data-testid="stAlert"] {background-color: #E3F1E8 !important;}
[data-baseweb="popover"] * {background-color: white !important; color: #2B2B2B !important;}
</style>
""", unsafe_allow_html=True)

# ---------- حفظ البيانات في ملف ----------
DATA_FILE = "jeera_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"requests": [], "announcements": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ---------- الواجهة ----------
st.title("جيرة 🏘️")
st.write("تطبيق يجمع جيران الحي في مكان واحد")

neighborhood = st.selectbox("اختر حيك", ["حي الرمال", "حي النرجس", "حي الياسمين"])
st.write("مرحباً بك في", neighborhood)

stores = {
    "حي الرمال": ["بقالة الرمال", "صيدلية الحي", "مخبز الرمال"],
    "حي النرجس": ["بقالة النرجس", "كوفي النرجس", "مغسلة ملابس"],
    "حي الياسمين": ["سوبرماركت الياسمين", "صيدلية الياسمين", "حلاق الحي"],
}

tab1, tab2, tab3 = st.tabs(["🤝 طلب مساعدة", "📢 إعلانات الحي", "🏪 المتاجر القريبة"])

# ---------- 1) طلب المساعدة ----------
with tab1:
    name = st.text_input("اسمك", key="req_name")
    request = st.text_area("وش تحتاج؟", key="req_text")
    if st.button("أرسل الطلب"):
        if name and request:
            data["requests"].append({"name": name, "text": request,
                                     "hood": neighborhood, "time": now()})
            save_data(data)
            st.success("تم إرسال طلبك للجيران ✅")
        else:
            st.warning("اكتب اسمك وطلبك")

    st.subheader("طلبات الجيران")
    found = False
    for r in reversed(data["requests"]):
        if r["hood"] == neighborhood:
            found = True
            st.markdown(f"<div class='card'><b>{r['name']}</b>: {r['text']}<br><small>{r['time']}</small></div>",
                        unsafe_allow_html=True)
    if not found:
        st.write("ما فيه طلبات للحين.")

# ---------- 2) إعلانات الحي ----------
with tab2:
    kind = st.selectbox("نوع الإعلان", ["تنبيه", "مناسبة", "مفقودات", "أخرى"])
    ad = st.text_area("نص الإعلان", key="ad_text")
    if st.button("انشر الإعلان"):
        if ad:
            data["announcements"].append({"kind": kind, "text": ad,
                                          "hood": neighborhood, "time": now()})
            save_data(data)
            st.success("تم نشر الإعلان ✅")
        else:
            st.warning("اكتب نص الإعلان")

    st.subheader("إعلانات " + neighborhood)
    icons = {"تنبيه": "⚠️", "مناسبة": "🎉", "مفقودات": "🔍", "أخرى": "📌"}
    found = False
    for a in reversed(data["announcements"]):
        if a["hood"] == neighborhood:
            found = True
            st.markdown(f"<div class='card'>{icons[a['kind']]} <b>{a['kind']}</b>: {a['text']}<br><small>{a['time']}</small></div>",
                        unsafe_allow_html=True)
    if not found:
        st.write("ما فيه إعلانات للحين.")

# ---------- 3) المتاجر القريبة ----------
with tab3:
    st.subheader("متاجر " + neighborhood)
    for store in stores[neighborhood]:
        st.markdown(f"<div class='card'>📍 {store}</div>", unsafe_allow_html=True)