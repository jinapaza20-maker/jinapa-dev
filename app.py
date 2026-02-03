import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Summary", layout="wide")

# ======================
# โหลด / สร้าง Excel
# ======================
FILE_NAME = "data.xlsx"

if os.path.exists(FILE_NAME):
    df = pd.read_excel(FILE_NAME)
else:
    df = pd.DataFrame(columns=[
        "Day", "Date", "Group", "Area", "Inspector", "Phone", "User"
    ])

# ======================
# ฟอร์มบันทึกข้อมูล
# ======================
st.markdown("## 📝 บันทึกข้อมูล")

with st.form("save_form"):
    col1, col2 = st.columns(2)

    with col1:
        day = st.selectbox("Day", ["Saturday", "Sunday"])
        group = st.text_input("Group")
        area = st.text_input("Area")

    with col2:
        work_date = st.date_input("Date", value=date.today())
        inspector = st.text_input("Inspector")
        phone = st.text_input("Phone")
        user = st.text_input("User")

    submitted = st.form_submit_button("💾 บันทึกข้อมูล")

    if submitted:
        new_row = {
            "Day": day,
            "Date": work_date.strftime("%Y-%m-%d"),
            "Group": group,
            "Area": area,
            "Inspector": inspector,
            "Phone": phone,
            "User": user
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(FILE_NAME, index=False)

        st.success("✅ บันทึกข้อมูลเรียบร้อยแล้ว")

# ======================
# SUMMARY
# ======================
st.markdown("---")
st.markdown("## 📊 Summary")

sat_count = len(df[df["Day"] == "Saturday"])
sun_count = len(df[df["Day"] == "Sunday"])

# กล่อง Summary ด้านบน
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="
        background:#8e44ad;
        color:white;
        padding:20px;
        border-radius:16px;
        text-align:center;
        font-size:20px;">
        <b>Saturday</b><br>
        <h1>{sat_count}</h1>
        people
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="
        background:#c0392b;
        color:white;
        padding:20px;
        border-radius:16px;
        text-align:center;
        font-size:20px;">
        <b>Sunday</b><br>
        <h1>{sun_count}</h1>
        people
    </div>
    """, unsafe_allow_html=True)

# ======================
# DETAIL CARD
# ======================
st.markdown("<br>", unsafe_allow_html=True)

for _, r in df.iterrows():
    color = "#8e44ad" if r["Day"] == "Saturday" else "#c0392b"

    st.markdown(f"""
    <div style="
        background:{color};
        color:white;
        padding:20px;
        border-radius:16px;
        margin-bottom:15px;">
        
        <b>{r['Day']} | {r['Date']}</b><br><br>
        Group: {r['Group']}<br>
        Area: {r['Area']}<br>
        Inspector: {r['Inspector']}<br><br>
        📞 {r['Phone']}<br>
        👤 {r['User']}
    </div>
    """, unsafe_allow_html=True)
