import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Inspection App", layout="centered")

# ---------- UI ----------
st.markdown("## 📝 Inspection Form")

group = st.selectbox("Group", ["", "WG", "BP"])

area_dict = {
    "WG": ["WG1", "WG2", "WG3", "WG4"],
    "BP": ["BP1", "BP2-3", "DET3-WH", "BP5", "BP8", "BP9"]
}

area = st.selectbox("Area", area_dict.get(group, []))

date = st.date_input("Inspection Date")
name = st.text_input("Inspector Name")
phone = st.text_input("Phone")
line = st.text_input("LINE ID")

# ---------- Validation ----------
day_name = date.strftime("%A")
allowed = day_name in ["Saturday", "Sunday"]

if not allowed:
    st.warning("❗ Inspection allowed only Saturday & Sunday")

# ---------- Save ----------
if st.button("💾 Save", disabled=not allowed):

    payload = {
        "Date": date.strftime("%Y-%m-%d"),
        "Day": day_name,
        "Group": group,
        "Area": area,
        "Inspector": name,
        "Phone": phone,
        "LINE": line
    }

    try:
        res = requests.post(
            "https://default19f2582317ff421fad4e8fed035aed.da.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/e14910468fc44cdb93d9fd9e851c04af/triggers/manual/paths/invoke?api-version=1",
            json=payload,
            timeout=15
        )

        if res.status_code in [200, 202]:
            st.success("✅ ส่งข้อมูลเรียบร้อยแล้ว")
        else:
            st.error(f"❌ ส่งไม่สำเร็จ ({res.status_code})")

    except Exception as e:
        st.error(f"❌ Error: {e}")
# ---------- Summary ----------
st.markdown("---")
st.markdown("## 📊 Summary")

# 🔹 นับจำนวนคน
sat_count = len(df[df["Day"] == "Saturday"])
sun_count = len(df[df["Day"] == "Sunday"])

# 🔹 กล่องสรุป 2 ช่อง
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="
        background:#8e44ad;
        padding:18px;
        border-radius:16px;
        color:white;
        text-align:center;
        font-weight:bold;
    ">
        Saturday<br>
        <span style="font-size:32px;">{sat_count}</span><br>
        people
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="
        background:#c0392b;
        padding:18px;
        border-radius:16px;
        color:white;
        text-align:center;
        font-weight:bold;
    ">
        Sunday<br>
        <span style="font-size:32px;">{sun_count}</span><br>
        people
    </div>
    """, unsafe_allow_html=True)

# 🔹 การ์ดรายละเอียดรายคน
import streamlit.components.v1 as components

html = ""

for _, r in df.iterrows():
    color = "#8e44ad" if r["Day"] == "Saturday" else "#c0392b"

    html += f"""
    <div style="
        background:{color};
        padding:16px;
        border-radius:14px;
        margin-top:14px;
        color:white;
        font-family:Arial;
    ">
        <b>{r['Day']} | {r['Date']}</b><br><br>

        <b>Group:</b> {r['Group']}<br>
        <b>Area:</b> {r['Area']}<br>
        <b>Inspector:</b> {r['Inspector']}<br><br>

        📞 <a href="tel:{r['Phone']}" style="color:white;text-decoration:none;">
            {r['Phone']}
        </a><br>

        💬 <a href="https://line.me/ti/p/~{r['LINE']}" target="_blank"
             style="color:white;text-decoration:none;">
            {r['LINE']}
        </a>
    </div>
    """

components.html(html, height=600, scrolling=True)
# =================================================
