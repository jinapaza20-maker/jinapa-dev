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
