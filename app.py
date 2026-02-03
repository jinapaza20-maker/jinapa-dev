import streamlit as st
import pandas as pd
import io
from datetime import datetime
import os
import streamlit.components.v1 as components
 
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
import requests

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
            timeout=10
        )

        if res.status_code == 200:
            st.success("✅ บันทึกข้อมูลเรียบร้อย")
        else:
            st.error(f"❌ ส่งไม่สำเร็จ ({res.status_code})")

    except Exception as e:
        st.error(f"❌ Error: {e}")
 
    html += f"""
<div style="
    background:{color};
    padding:18px;
    border-radius:14px;
    margin-bottom:16px;
    color:white;
    font-family:Arial;
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
 
components.html(html, height=600, scrolling=True)
