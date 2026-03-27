import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# ================= 1. ฟังก์ชันส่ง LINE =================

def send_to_line(flex_json):
    # ใส่ Token ของคุณตรงนี้
    TOKEN = "Op7JzHFY4SzJrxz6mjqVx9cAAk8uELFSt4bPoqiXW2LGqUbNCxHCnG6ClgU7WCE2Gwf82ww3lU23mVcEt9RDc6otB7PW4Y8Qu6P1sDmMsKCjIUBhhZsGhOt9nVDyw9G5T+Cn9/7Yng3FVG6bWhw4VQdB04t89/1O/w1cDnyilFU="
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    payload = {
        "messages": [{
            "type": "flex",
            "altText": "Summary Week Report",
            "contents": flex_json
        }]
    }

    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.status_code, res.text
    except Exception as e:
        return 500, str(e)

WEEKDAY_COLORS = {
    "Monday": "#FFD700",
    "Tuesday": "#FF69B4",
    "Wednesday": "#2E8B57",
    "Thursday": "#FF8C00",
    "Friday": "#1E90FF",
    "Saturday": "#5E0B73",
    "Sunday": "#B11226"
}

# ================= 2. ตั้งค่าระบบและโหลดข้อมูล =================

st.set_page_config(
    page_title="Vendor Inspection",
    layout="wide"
)

FILE_PATH = "inspection_data.xlsx"

if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH, dtype=str).fillna("")
else:
    df = pd.DataFrame(columns=["Date", "Day", "Group", "Area", "Safety", "Phone", "LINE"])

# ================= 3. SIDEBAR =================

with st.sidebar:
    st.header("⚙️ ระบบจัดการ")
    st.info("💡 เคล็ดลับ: ในช่อง LINE ID หากนำ 'ลิงก์คัดลอก QR Code' ของตัวเองมาวาง จะทำให้คนกดเด้งเข้าแชทได้แม่นยำที่สุดครับ")

# ================= 4. ส่วนบันทึกข้อมูล =================

st.markdown("## 📝 บันทึกข้อมูลการตรวจ")

with st.form("inspection_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        group = st.selectbox("Group", ["", "WG", "BP"])
        area = st.selectbox("Area", ["", "WG1-5-ChiHuang", "WG2-3", "BP1-DET3-WH", "BP2-3", "BP5-RD1", "BP8", "BP9"])
    with c2:
        date_val = st.date_input("วันที่ตรวจ")
        safety = st.text_input("ชื่อ Safety")
    with c3:
        phone = st.text_input("เบอร์โทร")
        line_val = st.text_input("LINE ID หรือ ลิงก์ QR", placeholder="เช่น safety_id หรือ https://line.me/ti/p/...")

    if st.form_submit_button("💾 บันทึกข้อมูล", use_container_width=True):
        if group and area and safety:
            new_row = {
                "Date": date_val.strftime("%Y-%m-%d"), 
                "Day": date_val.strftime("%A"), 
                "Group": group, "Area": area, "Safety": safety, 
                "Phone": phone.strip(), "LINE": line_val.strip()
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(FILE_PATH, index=False)
            st.rerun()

# ================= 5. ตารางข้อมูล =================

st.subheader("📋 รายการข้อมูล")

def color_row_by_day(row):
    day = row["Day"]
    bg = WEEKDAY_COLORS.get(day, "#FFFFFF")
    text_color = "#000000" if day == "Monday" else "#FFFFFF"
    return [f"background-color: {bg}; color: {text_color}"] * len(row)

styled_df = df.style.apply(color_row_by_day, axis=1)

edited_df = st.data_editor(
    styled_df,
    use_container_width=True,
    num_rows="dynamic",
    key="main_editor"
)

if not edited_df.equals(df):
    edited_df.to_excel(FILE_PATH, index=False)
    st.rerun()

# ================= 6. ส่วนส่ง LINE =================

st.divider()
st.subheader("📤 ส่งสรุปรายงานเข้า LINE")

mode = st.radio("เลือกรูปแบบ:", ["ส่งข้อมูลวันนี้ (แถบยาว)", "ส่งสรุปเสาร์-อาทิตย์ (Summary Week)"], horizontal=True)

if st.button("🚀 ยืนยันการส่ง LINE", use_container_width=True, type="primary"):
    if df.empty:
        st.warning("ไม่มีข้อมูล")
    else:
        # ฟังก์ชันสร้างปุ่ม (แก้ไขเรื่อง Indentation แล้ว)
        def get_styled_buttons(r, size="sm"):
            btns = []
            
            # ปุ่มโทร
            p_val = str(r['Phone']).strip()
            if p_val:
                btns.append({
                    "type": "box", "layout": "vertical", "backgroundColor": "#00B900", "cornerRadius": "md", "paddingAll": "4px", "flex": 1,
                    "contents": [{"type": "text", "text": "📞 โทร", "color": "#FFFFFF", "align": "center", "weight": "bold", "size": size}],
                    "action": {"type": "uri", "uri": f"tel:{p_val}"}
                })

            # ปุ่ม LINE (รองรับทั้งลิงก์ QR และ ID/เบอร์)
            l_val = str(r['LINE']).strip()
            if l_val:
                # ถ้าเป็นลิงก์ QR เต็มๆ มาอยู่แล้ว
                if "line.me" in l_val:
                    final_url = l_val
                else:
                    # ถ้าเป็น ID หรือ เบอร์โทร
                    final_url = f"https://line.me/ti/p/~{l_val}"

                btns.append({
                    "type": "box", "layout": "vertical", "backgroundColor": "#007BFF", "cornerRadius": "md", "paddingAll": "4px", "flex": 1,
                    "contents": [{"type": "text", "text": "💬 LINE", "color": "#FFFFFF", "align": "center", "weight": "bold", "size": size}],
                    "action": {"type": "uri", "uri": final_url}
                })
            
            return {"type": "box", "layout": "horizontal", "margin": "md", "spacing": "sm", "contents": btns} if btns else {"type": "spacer", "size": "xxs"}

        # ส่วนสร้างโครงสร้าง Flex Message
        if mode == "ส่งข้อมูลวันนี้ (แถบยาว)":
            last_date = df["Date"].max()
            today_df = df[df["Date"] == last_date]
            day_name = today_df["Day"].iloc[0]
            date_obj = datetime.strptime(last_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d %B %Y")

            items = []
            for _, r in today_df.iterrows():
                items.append({
                    "type": "box", "layout": "vertical", "backgroundColor": "#F8F9FA", "paddingAll": "10px", "cornerRadius": "md", "margin": "md",
                    "contents": [
                        {"type": "text", "text": f"📍 {r['Area']} ({r['Group']})", "weight": "bold"},
                        {"type": "text", "text": f"👤 Safety: {r['Safety']}", "margin": "xs", "size": "sm"},
                        get_styled_buttons(r, "sm")
                    ]
                })
            flex_json = {"type": "bubble", "size": "mega", "header": {"type": "box", "layout": "vertical", "backgroundColor": WEEKDAY_COLORS.get(day_name, "#333333"), "contents": [{"type": "text", "text": f"{day_name} {formatted_date}", "color": "#FFFFFF" if day_name != "Monday" else "#000000", "align": "center", "weight": "bold"}]}, "body": {"type": "box", "layout": "vertical", "contents": items}}

        else: # Summary Week
            sat_df = df[df["Day"] == "Saturday"]
            sun_df = df[df["Day"] == "Sunday"]
            
            sat_date_str = datetime.strptime(sat_df["Date"].iloc[0], "%Y-%m-%d").strftime("%d %b %Y") if not sat_df.empty else ""
            sun_date_str = datetime.strptime(sun_df["Date"].iloc[0], "%Y-%m-%d").strftime("%d %b %Y") if not sun_df.empty else ""

            def create_mini_box(r):
                return {
                    "type": "box", "layout": "vertical", "backgroundColor": "#FFFFFF", "margin": "sm", "paddingAll": "5px", "cornerRadius": "sm",
                    "contents": [
                        {"type": "text", "text": r['Area'], "weight": "bold", "size": "xs"},
                        {"type": "text", "text": r['Safety'], "size": "xxs", "color": "#666666"},
                        get_styled_buttons(r, "xxs")
                    ]
                }

            flex_json = {
                "type": "bubble", "size": "giga",
                "header": {"type": "box", "layout": "vertical", "backgroundColor": "#333333", "contents": [{"type": "text", "text": "Summary Week", "color": "#FFFFFF", "weight": "bold", "align": "center"}]},
                "body": {"type": "box", "layout": "horizontal", "spacing": "md", "contents": [
                    {
                        "type": "box", "layout": "vertical", "flex": 1, "backgroundColor": "#5E0B73", "paddingAll": "10px", "cornerRadius": "md",
                        "contents": [
                            {"type": "text", "text": "SATURDAY", "color": "#FFFFFF", "weight": "bold", "align": "center", "size": "sm"},
                            {"type": "text", "text": sat_date_str, "color": "#FFFFFF", "align": "center", "size": "xxs", "margin": "xs"}
                        ] + [create_mini_box(r) for _, r in sat_df.iterrows()]
                    } if not sat_df.empty else {"type": "filler"},
                    {
                        "type": "box", "layout": "vertical", "flex": 1, "backgroundColor": "#B11226", "paddingAll": "10px", "cornerRadius": "md",
                        "contents": [
                            {"type": "text", "text": "SUNDAY", "color": "#FFFFFF", "weight": "bold", "align": "center", "size": "sm"},
                            {"type": "text", "text": sun_date_str, "color": "#FFFFFF", "align": "center", "size": "xxs", "margin": "xs"}
                        ] + [create_mini_box(r) for _, r in sun_df.iterrows()]
                    } if not sun_df.empty else {"type": "filler"}
                ]}
            }

        status, response = send_to_line(flex_json)
        if status == 200: st.success("✅ ส่งเข้า LINE สำเร็จ!")
        else: st.error(f"❌ Error: {response}")
