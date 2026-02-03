import streamlit as st
import pandas as pd

FILE_PATH = "inspection.xlsx"

st.set_page_config(layout="wide")

# โหลดข้อมูล
df = pd.read_excel(FILE_PATH)

# แปลง Date เป็น datetime (เผื่อยังไม่ใช่)
df["Date"] = pd.to_datetime(df["Date"])

# แยกวัน
df_sat = df[df["Day"] == "Saturday"]
df_sun = df[df["Day"] == "Sunday"]

# ===== Summary =====
st.markdown("## 📊 Summary")

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"""
        <div style="background:#8e44ad;padding:20px;border-radius:15px;color:white;text-align:center">
        <h4>Saturday</h4>
        <h1>{len(df_sat)}</h1>
        <p>people</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"""
        <div style="background:#c0392b;padding:20px;border-radius:15px;color:white;text-align:center">
        <h4>Sunday</h4>
        <h1>{len(df_sun)}</h1>
        <p>people</p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ===== Detail List =====
st.markdown("## 📋 Detail List")

col_sat, col_sun = st.columns(2)

# ----- Saturday -----
with col_sat:
    st.subheader("🟣 Saturday")
    for _, r in df_sat.iterrows():
        st.markdown(
            f"""
            <div style="background:#8e44ad;padding:15px;border-radius:12px;color:white;margin-bottom:10px">
            <b>{r['Day']} | {r['Date'].date()}</b><br>
            Group: {r['Group']}<br>
            Area: {r['Area']}<br>
            Inspector: {r['Inspector']}<br>
            📞 {r['Phone']}<br>
            💬 {r['LINE']}
            </div>
            """,
            unsafe_allow_html=True
        )

# ----- Sunday -----
with col_sun:
    st.subheader("🔴 Sunday")
    for _, r in df_sun.iterrows():
        st.markdown(
            f"""
            <div style="background:#c0392b;padding:15px;border-radius:12px;color:white;margin-bottom:10px">
            <b>{r['Day']} | {r['Date'].date()}</b><br>
            Group: {r['Group']}<br>
            Area: {r['Area']}<br>
            Inspector: {r['Inspector']}<br>
            📞 {r['Phone']}<br>
            💬 {r['LINE']}
            </div>
            """,
            unsafe_allow_html=True
        )
