import streamlit as st
import pandas as pd
import os
from datetime import datetime
import streamlit.components.v1 as components

# ---------------- Page Config ----------------
st.set_page_config(page_title="Inspection App", layout="centered")

FILE_PATH = "inspection_data.xlsx"

# ---------------- Load / Create Excel ----------------
if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH)
else:
    df = pd.DataFrame(columns=[
        "Date", "Day", "Group", "Area",
        "Inspector", "Phone", "LINE"
    ])
    df.to_excel(FILE_PATH, index=False)

# ---------------- UI : FORM ----------------
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

# ---------------- Validation ----------------
day_name = date.strftime("%A")
allowed = day_name in ["Saturday", "Sunday"]

if not allowed:
    st.warning("❗ Inspection allowed only Saturday & Sunday")

# ---------------- Save ----------------
if st.button("💾 Save", disabled=not allowed):
    new_row = {
        "Date": date.strftime("%Y-%m-%d"),
        "Day": day_name,
        "Group": group,
        "Area": area,
        "Inspector": name,
        "Phone": phone,
        "LINE": line
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(FILE_PATH, index=False)
    st.success("✅ บันทึกข้อมูลเรียบร้อย")

# ---------------- SUMMARY ----------------
st.markdown("---")
st.markdown("## 📊 Summary")

sat_count = len(df[df["Day"] == "Saturday"])
sun_count = len(df[df["Day"] == "Sunday"])

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="
        background:#8e44ad;
        padding:20px;
        border-radius:16px;
        color:white;
        text-align:center;
        font-weight:bold;
    ">
        Saturday<br>
        <span style="font-size:36px;">{sat_count}</span><br>
        people
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="
        background:#c0392b;
        padding:20px;
        border-radius:16px;
        color:white;
        text-align:center;
        font-weight:bold;
    ">
        Sunday<br>
        <span style="font-size:36px;">{sun_count}</span><br>
        people
    </div>
    """, unsafe_allow_html=True)

# ---------------- DETAIL CARDS ----------------
html = ""

for _, r in df.iterrows():
    color = "#8e44ad" if r["Day"] == "Saturday" else "#c0392b"

    html += f"""
    <div style="
        background:{color};
        padding:18px;
        border-radius:14px;
        margin-top:16px;
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
