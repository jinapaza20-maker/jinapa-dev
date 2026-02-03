import streamlit as st

import pandas as pd

import os

import streamlit.components.v1 as components

from datetime import datetime

import requests
 
# ---------------- Page Config ----------------

st.set_page_config(page_title="Inspection App", layout="centered")
 
FILE_PATH = "inspection_data.xlsx"
 
# 🔴 วางลิงก์จาก Power Automate ตรงนี้

POWER_AUTOMATE_URL ="https://default19f2582317ff421fad4e8fed035aed.da.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/e14910468fc44cdb93d9fd9e851c04af/triggers/manual/paths/invoke?api-version=1%22
 
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

    "WG": ["WG1", "WG2", "WG3", "WG5"],

    "BP": ["BP1-DET3-WH", "BP2-3", "BP5-RD1", "BP8", "BP9"]

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
 
    # ✅ 1) Save to local Excel (ใช้ Summary)

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df.to_excel(FILE_PATH, index=False)
 
    # ✅ 2) Send to Power Automate

    try:

        res = requests.post(

            POWER_AUTOMATE_URL,

            json=new_row,

            headers={"Content-Type": "application/json"},

            timeout=10

        )
 
        if res.status_code in [200, 202]:

            st.success("✅ บันทึกและส่งข้อมูลเรียบร้อย")

        else:

            st.warning(f"⚠️ ส่ง Flow ไม่สำเร็จ ({res.status_code})")
 
    except Exception as e:

        st.warning(f"⚠️ ส่ง Flow error : {e}")
 
    st.rerun()
 
# ---------------- SUMMARY ----------------

st.markdown("---")

st.markdown("## 📊 Summary")
 
sat_count = len(df[df["Day"] == "Saturday"])

sun_count = len(df[df["Day"] == "Sunday"])
 
col1, col2 = st.columns(2)
 
with col1:

    st.markdown(f"""
<div style="background:#8e44ad;padding:20px;border-radius:16px;color:white;text-align:center;font-weight:bold;">

        Saturday<br>
<span style="font-size:36px;">{sat_count}</span><br>

        people
</div>

    """, unsafe_allow_html=True)
 
with col2:

    st.markdown(f"""
<div style="background:#c0392b;padding:20px;border-radius:16px;color:white;text-align:center;font-weight:bold;">

        Sunday<br>
<span style="font-size:36px;">{sun_count}</span><br>

        people
</div>

    """, unsafe_allow_html=True)

# ---------------- DETAIL LIST (DELETE ENABLED) ----------------

import streamlit.components.v1 as components
 
st.markdown("### 📋 Detail List")
 
for idx, r in df.iterrows():

    color = "#8e44ad" if r["Day"] == "Saturday" else "#c0392b"
 
    with st.container():

        # ใช้ columns เพื่อให้ปุ่มลบอยู่ในกรอบ

        left, right = st.columns([5, 1])
 
        with left:

            card_html = f"""
<div style="

                background:{color};

                padding:18px;

                border-radius:14px;

                color:white;

                min-height:160px;

            ">
<b>{r['Day']} | {r['Date']}</b><br><br>
<b>Group:</b> {r['Group']}<br>
<b>Area:</b> {r['Area']}<br>
<b>Inspector:</b> {r['Inspector']}<br><br>
 
                📞 <a href="tel:{r['Phone']}"

                     style="color:white;text-decoration:none;">

                    {r['Phone']}
</a><br>
 
                💬 <a href="https://line.me/ti/p/~{r['LINE']}"

                     target="_blank"

                     style="color:white;text-decoration:none;">

                    {r['LINE']}
</a>
</div>

            """

            components.html(card_html, height=200)
 
        with right:

            st.markdown("<br><br>", unsafe_allow_html=True)

            if st.button("🗑 ลบ", key=f"delete_{idx}"):

                df = df.drop(idx).reset_index(drop=True)

                df.to_excel(FILE_PATH, index=False)

                st.rerun()
