import streamlit as st
import pandas as pd
import os
import requests
from datetime import datetime

# ================= 1. DEFINE FUNCTIONS (ย้ายมาไว้ข้างบนสุด) =================

def send_to_line(flex_json):
    CHANNEL_ACCESS_TOKEN ="Op7JzHFY4SzJrxz6mjqVx9cAAk8uELFSt4bPoqiXW2LGqUbNCxHCnG6ClgU7WCE2Gwf82ww3lU23mVcEt9RDc6otB7PW4Y8Qu6P1sDmMsKCjIUBhhZsGhOt9nVDyw9G5T+Cn9/7Yng3FVG6bWhw4VQdB04t89/1O/w1cDnyilFU="
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    payload = {"messages": [{"type": "flex", "altText": "Inspection Summary", "contents": flex_json}]}
    res = requests.post(url, headers=headers, json=payload)
    return res.status_code, res.text

# ================= 2. PAGE CONFIG & FILE SETUP =================

st.set_page_config(page_title="Inspection App", layout="wide")
FILE_PATH = "inspection_data.xlsx"

if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH, dtype=str).fillna("")
else:
    df = pd.DataFrame(columns=["Date", "Day", "Group", "Area", "Safety", "Phone", "LINE"])
    df.to_excel(FILE_PATH, index=False)

# ================= 3. FORM SECTION (ใช้ st.form เพื่อแก้ Error) =================

st.markdown("## 📝 Inspection Form")

# การใช้ st.form พร้อม clear_on_submit=True คือวิธีที่ Streamlit แนะนำเพื่อป้องกัน Error ที่คุณเจอ
with st.form("inspection_form", clear_on_submit=True):
    group = st.selectbox("Group", ["", "WG", "BP"])
    
    area_dict = {
        "WG": ["WG1", "WG2", "WG3", "WG5"],
        "BP": ["BP1-DET3-WH", "BP2-3", "BP5-RD1", "BP8", "BP9"]
    }
    
    # หมายเหตุ: ใน st.form ตัวแปร area จะเปลี่ยนตาม group ทันทีไม่ได้ (ต้องกด submit ก่อน) 
    # ดังนั้นผมจะรวมพื้นที่ทั้งหมดให้เลือก หรือคุณสามารถเลือกกรอกเองได้
    all_areas = [""] + area_dict["WG"] + area_dict["BP"]
    area = st.selectbox("Area", all_areas)
    
    date = st.date_input("Inspection Date")
    safety = st.text_input("Safety Name")
    phone = st.text_input("Phone")
    line = st.text_input("LINE ID")

    day_name = date.strftime("%A")
    allowed = day_name in ["Saturday", "Sunday"]

    if not allowed:
        st.warning("❗ บันทึกได้เฉพาะวันเสาร์–อาทิตย์")

    col_save, col_clear = st.columns([1, 5])
    with col_save:
        save_btn = st.form_submit_button("💾 Save", disabled=not allowed)
    with col_clear:
        # ปุ่มล้างฟอร์ม (ทำงานอัตโนมัติด้วย clear_on_submit)
        st.form_submit_button("🧹 ล้างฟอร์ม")

# ================= 4. LOGIC AFTER SUBMIT =================

if save_btn:
    if group == "" or area == "" or safety == "":
        st.error("❌ กรุณากรอกข้อมูลให้ครบ (Group, Area, Safety)")
    else:
        new_row = {
            "Date": date.strftime("%Y-%m-%d"),
            "Day": day_name,
            "Group": group,
            "Area": area,
            "Safety": safety,
            "Phone": phone,
            "LINE": line
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(FILE_PATH, index=False)
        st.success("✅ บันทึกเรียบร้อย และล้างฟอร์มแล้ว")
        st.rerun()
# ================= SUMMARY =================
st.markdown("## 📊 Summary Week")

if not df.empty:
    sat_date = df[df["Day"] == "Saturday"]["Date"].iloc[0] if "Saturday" in df["Day"].values else "-"
    sun_date = df[df["Day"] == "Sunday"]["Date"].iloc[0] if "Sunday" in df["Day"].values else "-"
else:
    sat_date = sun_date = "-"

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f"""
    <div style="
        background:#660066;
        padding:32px;
        border-radius:32px;
        text-align:center;
        color:white;
        font-weight:bold;">
        Saturday<br>
        <span style="font-size:32px;">{sat_date}</span>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown(f"""
    <div style="
        background:#B11226;
        padding:32px;
        border-radius:32px;
        text-align:center;
        color:white;
        font-weight:bold;">
        Sunday<br>
        <span style="font-size:32px;">{sun_date}</span>
    </div>
    """, unsafe_allow_html=True)

# ================= DETAIL LIST =================
st.markdown("## 📋 Detail List")

col_sat, col_sun = st.columns(2)

for idx, r in df.iterrows():

    phone = r["Phone"].strip()
    line_raw = r["LINE"].strip()
    line_id = line_raw.replace("@", "") if line_raw else ""


    if r["Day"] == "Saturday":
        bg_color = "#5E0B73"
        target_col = col_sat
    elif r["Day"] == "Sunday":
        bg_color = "#B11226"
        target_col = col_sun
    else:
        continue

    with target_col:
        st.markdown(
            f"""
            <div style="
                background:{bg_color};
                padding:20px;
                border-radius:20px;
                margin-bottom:12px;
                color:white;
                font-size:15px;
                line-height:1.7;
            ">
                <b>Area:</b> {r['Area']}<br>
                <b>Safety:</b> {r['Safety']}<br><br>
📞 <a href="tel:{phone}"
                    style="text-decoration:none; font-weight:bold; color:white;">
                    โทร {phone}
                </a><br>

💬 <a href="https://line.me/R/ti/p/{line_id}"
                    target="_blank"
                    style="text-decoration:none; font-weight:bold; color:white;">
                    LINE {line_id}
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🗑 ลบรายการนี้", key=f"del_{idx}"):
            df = df.drop(idx)
            df.to_excel(FILE_PATH, index=False)
            st.rerun()

# ================= COUNT SUMMARY =================
sat_count = len(df[df["Day"] == "Saturday"])
sun_count = len(df[df["Day"] == "Sunday"])


# ================= SUMMARY BUBBLE =================
def summary_bubble(day, date, color):
    return {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": color,
            "paddingAll": "8px",
            "cornerRadius": "8px",
            "contents": [
                {
                    "type": "text",
                    "text": day,
                    "align": "center",
                    "color": "#FFFFFF"
                },
                {
                    "type": "text",
                    "text": date,
                    "align": "center",
                    "size": "xl",
                    "weight": "bold",
                    "color": "#FFFFFF"
                }
            ]
        }
    }


# ================= DETAIL BUBBLE =================
def detail_bubble(row, color):
    line_id = "" if pd.isna(row["LINE"]) else str(row["LINE"]).replace("@", "")

    return {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": [
            {"type": "text", "text": f"Area: {row['Area']}", "color": "#FFFFFF"},
            {"type": "text", "text": f"Safety: {row['Safety']}", "color": "#FFFFFF"},
            {"type": "text", "text": f"📞 {row['Phone']}", "color": "#FFFFFF"},
            {"type": "text", "text": f"LINE: {line_id}", "color": "#FFFFFF"},
        ]
    }


# ================= BUILD CAROUSEL =================
def build_carousel_from_df(df):
    bubbles = []

    for _, row in df.iterrows():
        if row["Day"] == "Saturday":
            color = "#5E0B73"
            day_label = f"Saturday {row['Date']}"
        elif row["Day"] == "Sunday":
            color = "#B11226"
            day_label = f"Sunday {row['Date']}"
        else:
            continue

        bubble = {
            "type": "bubble",
            "size": "mega",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": color,
                "paddingAll": "6px",
                "cornerRadius": "8px",
                "contents": [
                    {
                        "type": "text",
                        "text": day_label,
                        "weight": "bold",
                        "align": "center",
                        "color": "#FFFFFF",
                        "size": "xs"
                    },
                    {"type": "separator", "margin": "sm"},
                    detail_bubble(row, color)
                ]
            }
        }

        bubbles.append(bubble)

    return {
        "type": "carousel",
        "contents": bubbles
    }

# ================= SEND TO LINE =================
st.markdown("## 📤 ส่งสรุปผลไป LINE OA")

if st.button("ส่ง Summary + Detail ไป LINE"):

    sat_list = []
    sun_list = []

    for _, r in df.iterrows():

        phone = str(r["Phone"]).strip()
        line_raw = str(r["LINE"]).strip().replace("@", "")

        # ===== ปุ่มไอค่อน =====
        phone_btn = {
            "type": "button",
            "height": "sm",
		"style": "primary",
            "action": {
                "type": "uri",
                "label": "📞",
                "uri": f"tel:{phone}"
            }
        } if phone else {"type": "filler"}

        line_btn = {
            "type": "button",
            "height": "sm",
		"style": "secondary",
            "action": {
                "type": "uri",
                "label": "💬",
                "uri": f"https://line.me/ti/p/~{line_raw}"

            }
        } if line_raw else {"type": "filler"}

        # ===== กล่อง Detail (กรอบขาว) =====
        detail_box = {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "paddingAll": "10px",
            "cornerRadius": "10px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                {
                    "type": "text",
                    "text": f"Area: {r['Area']}",
                    "weight": "bold",
                    "size": "xxs",
                    "color": "#333333",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": f"Safety: {r['Safety']}",
                    "size": "xxs",
                    "color": "#555555",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "xs", 
                    "margin": "sm",
                    "contents": [phone_btn, line_btn]
                }
            ]
        }

        if r["Day"] == "Saturday":
            sat_list.append(detail_box)
        elif r["Day"] == "Sunday":
            sun_list.append(detail_box)

    # ===== FLEX หลัก =====
    flex_json = {
        "type": "bubble",
        "size": "giga",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
		"paddingAll": "12px",
		"backgroundColor": "#FFFFFF", 
            "contents": [

                {
                    "type": "text",
                    "text": "📊 Summary Week",
                    "weight": "bold",
                    "size": "sm"
                },

                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "8px",
                            "cornerRadius": "8px",
                            "backgroundColor": "#5E0B73",
                            "contents": [
                                {"type": "text", "text": "Saturday", "size": "xs", "color": "#FFFFFF"},
                                {"type": "text", "text": sat_date, "size": "xs", "weight": "bold", "color": "#FFFFFF"}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "paddingAll": "8px",
                            "cornerRadius": "8px",
                            "backgroundColor": "#B11226",
                            "contents": [
                                {"type": "text", "text": "Sunday", "size": "xs", "color": "#FFFFFF"},
                                {"type": "text", "text": sun_date, "size": "xs", "weight": "bold", "color": "#FFFFFF"}
                            ]
                        }
                    ]
                },

                {
                    "type": "text",
                    "text": "📋 Detail",
                    "weight": "bold",
                    "size": "sm",
                    "margin": "md"
                },

                {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "8px",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "flex": 1,
                            "paddingAll": "8px",
                            "cornerRadius": "12px",
                            "backgroundColor": "#5E0B73",
                            "contents": sat_list if sat_list else [
                                {"type": "text", "text": "-", "size": "xs", "color": "#FFFFFF"}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "sm",
                            "flex": 1,
                            "paddingAll": "8px",
                            "cornerRadius": "12px",
                            "backgroundColor": "#B11226",
                            "contents": sun_list if sun_list else [
                                {"type": "text", "text": "-", "size": "xs", "color": "#FFFFFF"}
                            ]
                        }
                    ]
                }
            ]
        }
    }

    status, msg = send_to_line(flex_json)

    if status == 200:
        st.success("✅ ส่งไป LINE OA เรียบร้อย")
    else:
        st.error(msg)  
