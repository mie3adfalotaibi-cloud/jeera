import streamlit as st
import json
import os
from datetime import datetime
import base64
import io
from PIL import Image, ImageDraw

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

def image_to_text(file):
    img = Image.open(file).convert("RGB")
    img.thumbnail((600, 600))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=70)
    return base64.b64encode(buf.getvalue()).decode()

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

tab1, tab2, tab3, tab4 = st.tabs(["🤝 طلب مساعدة", "📢 إعلانات الحي", "🏪 المتاجر القريبة", "🚁 درون الحي"])

# ---------- 1) طلب المساعدة ----------
with tab1:
    name = st.text_input("اسمك", key="req_name")
    request = st.text_area("وش تحتاج؟", key="req_text")
    photo = st.file_uploader("📷 أضف صورة (اختياري)", type=["jpg", "jpeg", "png"], key="req_photo")
    if st.button("أرسل الطلب"):
        if name and request:
            data["requests"].append({"id": now() + name, "name": name, "text": request,
                                     "hood": neighborhood, "time": now(),
                                     "photo": image_to_text(photo) if photo else None,
                                     "replies": [], "solved": False})
            save_data(data)
            st.success("تم إرسال طلبك للجيران ✅")
        else:
            st.warning("اكتب اسمك وطلبك")

    st.subheader("طلبات الجيران")
    found = False
    for i, r in enumerate(reversed(data["requests"])):
        if r["hood"] != neighborhood:
            continue
        found = True
        r.setdefault("replies", [])
        r.setdefault("solved", False)
        status = " ✅ تم الحل" if r["solved"] else ""
        st.markdown(f"<div class='card'><b>{r['name']}</b>: {r['text']}{status}<br><small>{r['time']}</small></div>",
                    unsafe_allow_html=True)
        if r.get("photo"):
            st.image(base64.b64decode(r["photo"]), width=300)

        with st.expander(f"💬 الردود ({len(r['replies'])})"):
            for rep in r["replies"]:
                st.write(f"🤝 **{rep['name']}**: {rep['text']}  ({rep['time']})")
            if not r["solved"]:
                helper = st.text_input("اسمك", key=f"h_name_{i}")
                reply = st.text_input("ردك (مثل: أقدر أساعدك الساعة 5)", key=f"h_text_{i}")
                c1, c2 = st.columns(2)
                if c1.button("🤝 أبي أساعد", key=f"h_btn_{i}"):
                    if helper and reply:
                        r["replies"].append({"name": helper, "text": reply, "time": now()})
                        save_data(data)
                        st.rerun()
                    else:
                        st.warning("اكتب اسمك وردك")
                if c2.button("✅ تم الحل", key=f"solve_{i}"):
                    r["solved"] = True
                    save_data(data)
                    st.rerun()
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

# ---------- 4) درون الحي (محاكاة) ----------
def draw_map():
    m = Image.new("RGB", (800, 600), (233, 226, 208))
    d = ImageDraw.Draw(m)
    for x in range(0, 800, 200):
        d.rectangle([x + 80, 0, x + 110, 600], fill=(120, 120, 120))
    for y in range(0, 600, 200):
        d.rectangle([0, y + 80, 800, y + 110], fill=(120, 120, 120))
    colors = [(200, 120, 90), (210, 180, 120), (170, 150, 200), (140, 180, 160)]
    k = 0
    for x in range(0, 800, 200):
        for y in range(0, 600, 200):
            if (x, y) == (400, 200):
                d.rectangle([x + 120, y + 120, x + 190, y + 190], fill=(90, 170, 90))
                d.ellipse([x + 135, y + 135, x + 175, y + 175], fill=(60, 130, 60))
            else:
                d.rectangle([x + 125, y + 125, x + 185, y + 185], fill=colors[k % 4])
                d.polygon([(x + 120, y + 125), (x + 155, y + 115), (x + 190, y + 125)], fill=(110, 60, 50))
            k += 1
    d.ellipse([610, 330, 640, 350], fill=(250, 150, 0))
    return m

with tab4:
    st.subheader("🚁 درون الحي (تجربة محاكاة)")
    st.caption("درون افتراضي يطير فوق خريطة مرسومة للحي، بدون درون حقيقي وبدون تصوير أحد.")

    if "drone" not in st.session_state:
        st.session_state.drone = [400, 300]
        st.session_state.gallery = []
    x, y = st.session_state.drone
    step = 50

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("⬆️ فوق"):
        y = max(75, y - step)
    if c2.button("⬇️ تحت"):
        y = min(525, y + step)
    if c3.button("➡️ يمين"):
        x = min(725, x + step)
    if c4.button("⬅️ يسار"):
        x = max(75, x - step)
    st.session_state.drone = [x, y]

    base = draw_map()
    view = base.copy()
    d = ImageDraw.Draw(view)
    d.rectangle([x - 75, y - 75, x + 75, y + 75], outline=(220, 0, 0), width=4)
    d.text((x - 8, y - 8), "+", fill=(220, 0, 0))

    left, right = st.columns(2)
    left.image(view, caption="الخريطة: المربع الأحمر = مكان الدرون")
    cam = base.crop((x - 75, y - 75, x + 75, y + 75)).resize((300, 300))
    right.image(cam, caption="كاميرا الدرون 📷")

    if st.button("📸 التقط صورة"):
        st.session_state.gallery.append(cam)
        st.success("تم التقاط الصورة ✅")

    if st.session_state.gallery:
        st.write("الصور الملتقطة:")
        cols = st.columns(4)
        for n, g in enumerate(st.session_state.gallery[-4:]):
            cols[n].image(g)