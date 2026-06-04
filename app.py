import streamlit as st
import pandas as pd
import os
import json
import requests
import calendar
from datetime import datetime, date

# ================= 1. ส่ง LINE =================
def send_to_line(flex_json, alt_text="Report"):
    TOKEN = "Op7JzHFY4SzJrxz6mjqVx9cAAk8uELFSt4bPoqiXW2LGqUbNCxHCnG6ClgU7WCE2Gwf82ww3lU23mVcEt9RDc6otB7PW4Y8Qu6P1sDmMsKCjIUBhhZsGhOt9nVDyw9G5T+Cn9/7Yng3FVG6bWhw4VQdB04t89/1O/w1cDnyilFU="
    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
    payload = {"messages": [{"type": "flex", "altText": alt_text, "contents": flex_json}]}
    try:
        res = requests.post(url, headers=headers, json=payload)
        return res.status_code, res.text
    except Exception as e:
        return 500, str(e)

# ================= สีประจำวัน =================
WEEKDAY_COLORS = {
    "Monday":    "#FFD700",
    "Tuesday":   "#FF69B4",
    "Wednesday": "#2E8B57",
    "Thursday":  "#FF8C00",
    "Friday":    "#1E90FF",
    "Saturday":  "#5E0B73",
    "Sunday":    "#B11226"
}
WEEKDAY_TEXT = {
    "Monday": "#000000"
}

# ================= ลำดับ Area =================
WG_ORDER = ["WG1-WG5", "WG2-WG3"]
BP_ORDER = ["BP1-DET3-WH", "BP2-3", "BP5-RD1", "BP8", "BP9" "BP10", "External BP", "External WG"]

# ================= 2. สร้าง Bubble รายละเอียดวัน =================
def build_col_items(group_rows, group=""):
    if not group_rows:
        return [{"type": "text", "text": "ไม่มีข้อมูล",
                 "color": "#AAAAAA", "size": "xxs", "align": "center", "margin": "sm"}]

    # เรียงตาม order ที่กำหนด
    order = WG_ORDER if group.upper() == "WG" else BP_ORDER
    def sort_key(r):
        area = str(r.get('Area', '')).strip()
        return order.index(area) if area in order else 999
    group_rows = sorted(group_rows, key=sort_key)

    items = []
    for i, r in enumerate(group_rows):
        area   = str(r.get('Area',   '-')).strip()
        safety = str(r.get('Safety', '-')).strip()
        phone  = str(r.get('Phone',  '-')).strip()
        line_v = str(r.get('LINE',   '-')).strip()

        action_btns = []
        if phone and phone != '-':
            action_btns.append({
                "type": "box", "layout": "vertical",
                "backgroundColor": "#00B900", "cornerRadius": "sm",
                "paddingAll": "3px",
                "action": {"type": "uri", "uri": f"tel:{phone}"},
                "contents": [{"type": "text", "text": "📞",
                              "color": "#FFFFFF", "align": "center", "size": "xxs"}]
            })
        if line_v and line_v != '-':
            final_url = line_v if "line.me" in line_v else f"https://line.me/ti/p/~{line_v}"
            action_btns.append({
                "type": "box", "layout": "vertical",
                "backgroundColor": "#007BFF", "cornerRadius": "sm",
                "paddingAll": "3px",
                "action": {"type": "uri", "uri": final_url},
                "contents": [{"type": "text", "text": "💬",
                              "color": "#FFFFFF", "align": "center", "size": "xxs"}]
            })

        row_contents = [
            {"type": "text", "text": safety,
             "size": "xxs", "weight": "bold", "color": "#FFFFFF", "wrap": True},
            {"type": "text", "text": f"📍{area}",
             "size": "xxs", "color": "#FFFFFFBB", "wrap": True},
        ]
        if action_btns:
            row_contents.append({
                "type": "box", "layout": "horizontal",
                "spacing": "xs", "margin": "xs",
                "contents": action_btns
            })

        items.append({
            "type": "box", "layout": "vertical",
            "backgroundColor": "#00000033",
            "borderColor": "#FFFFFF44",
            "borderWidth": "1px",
            "cornerRadius": "sm",
            "paddingAll": "6px", "spacing": "xs",
            "margin": "xs" if i > 0 else "none",
            "contents": row_contents
        })

    return items


def build_day_detail_bubble(day_rows, day_dt):
    weekday_name = day_dt.strftime("%A")
    bg           = WEEKDAY_COLORS.get(weekday_name, "#333333")
    txt_color    = WEEKDAY_TEXT.get(weekday_name, "#FFFFFF")
    date_label   = day_dt.strftime("%A, %d %B %Y")

    wg_rows = [r for r in day_rows if str(r.get('Group', '')).strip().upper() == 'WG']
    bp_rows = [r for r in day_rows if str(r.get('Group', '')).strip().upper() == 'BP']

    wg_col = {
        "type": "box", "layout": "vertical", "flex": 1,
        "spacing": "none",
        "contents": [
            {
                "type": "box", "layout": "vertical",
                "backgroundColor": "#5A4500", "paddingAll": "8px",
                "contents": [{"type": "text", "text": "WG", "color": "#FFD700",
                               "weight": "bold", "size": "sm", "align": "center"}]
            },
            {
                "type": "box", "layout": "vertical",
                "paddingAll": "8px", "spacing": "none",
                "contents": build_col_items(wg_rows, "WG")
            }
        ]
    }

    bp_col = {
        "type": "box", "layout": "vertical", "flex": 1,
        "spacing": "none",
        "contents": [
            {
                "type": "box", "layout": "vertical",
                "backgroundColor": "#003366", "paddingAll": "8px",
                "contents": [{"type": "text", "text": "BP", "color": "#66AAFF",
                               "weight": "bold", "size": "sm", "align": "center"}]
            },
            {
                "type": "box", "layout": "vertical",
                "paddingAll": "8px", "spacing": "none",
                "contents": build_col_items(bp_rows, "BP")
            }
        ]
    }

    return {
        "type": "bubble", "size": "giga",
        "header": {
            "type": "box", "layout": "vertical",
            "backgroundColor": bg, "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "📋 รายละเอียดการตรวจ",
                 "color": txt_color, "size": "xs"},
                {"type": "text", "text": date_label,
                 "color": txt_color, "size": "md", "weight": "bold", "wrap": True}
            ]
        },
        "body": {
            "type": "box", "layout": "vertical",
            "backgroundColor": bg + "CC",
            "paddingAll": "0px", "spacing": "none",
            "contents": [
                {
                    "type": "box", "layout": "horizontal",
                    "spacing": "none",
                    "contents": [
                        wg_col,
                        {"type": "separator", "color": "#000000"},
                        bp_col
                    ]
                }
            ]
        }
    }

# ================= 3. หน้าเว็บ + โหลดข้อมูล =================
st.set_page_config(page_title="Vendor Inspection System", layout="wide")
FILE_PATH = "inspection_data.xlsx"

if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH, dtype=str).fillna("-")
else:
    df = pd.DataFrame(columns=["Date", "Day", "Group", "Area", "Safety", "Phone", "LINE"])

# ================= 4. ฟอร์มบันทึก =================
DRAFT_PATH = "form_draft.json"

def save_draft():
    draft = {
        "form_group":  st.session_state.get("form_group", ""),
        "form_area":   st.session_state.get("form_area", ""),
        "form_date":   st.session_state.get("form_date", datetime.now().date()).strftime("%Y-%m-%d"),
        "form_safety": st.session_state.get("form_safety", ""),
        "form_phone":  st.session_state.get("form_phone", ""),
        "form_line":   st.session_state.get("form_line", ""),
    }
    with open(DRAFT_PATH, "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False)

def load_draft():
    if os.path.exists(DRAFT_PATH):
        with open(DRAFT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

_draft = load_draft()
if "form_group"  not in st.session_state: st.session_state["form_group"]  = _draft.get("form_group", "")
if "form_area"   not in st.session_state: st.session_state["form_area"]   = _draft.get("form_area", "")
if "form_date"   not in st.session_state:
    _d = _draft.get("form_date", "")
    st.session_state["form_date"] = datetime.strptime(_d, "%Y-%m-%d").date() if _d else datetime.now().date()
if "form_safety" not in st.session_state: st.session_state["form_safety"] = _draft.get("form_safety", "")
if "form_phone"  not in st.session_state: st.session_state["form_phone"]  = _draft.get("form_phone", "")
if "form_line"   not in st.session_state: st.session_state["form_line"]   = _draft.get("form_line", "")

AREA_OPTIONS = ["", "WG1-WG5", "WG2-WG3", "BP1-DET3-WH", "BP2-3", "BP5-RD1", "BP8", "BP9", "External WH"]

if st.session_state.get("clear_form"):
    st.session_state["form_group"]  = ""
    st.session_state["form_area"]   = ""
    st.session_state["form_date"]   = datetime.now().date()
    st.session_state["form_safety"] = ""
    st.session_state["form_phone"]  = ""
    st.session_state["form_line"]   = ""
    st.session_state["clear_form"]  = False
    if os.path.exists(DRAFT_PATH):
        os.remove(DRAFT_PATH)
st.markdown("## 📝 Inspection Entry")
c1, c2, c3 = st.columns(3)
with c1:
    st.selectbox("Group", ["", "WG", "BP"],
        index=["", "WG", "BP"].index(st.session_state["form_group"])
              if st.session_state["form_group"] in ["", "WG", "BP"] else 0,
        key="form_group")
    st.selectbox("Area", AREA_OPTIONS,
        index=AREA_OPTIONS.index(st.session_state["form_area"])
              if st.session_state["form_area"] in AREA_OPTIONS else 0,
        key="form_area")
with c2:
    st.date_input("Inspection Date", key="form_date")
    st.text_input("Safety Name",     value=st.session_state["form_safety"], key="form_safety")
with c3:
    st.text_input("Phone Number",    value=st.session_state["form_phone"], key="form_phone")
    st.text_input("LINE ID / Link",  value=st.session_state["form_line"],  key="form_line")

if st.button("💾 Save Data", use_container_width=True, type="primary"):
    if st.session_state["form_group"] and st.session_state["form_area"] and st.session_state["form_safety"]:
        new_row = {
            "Date":   st.session_state["form_date"].strftime("%Y-%m-%d"),
            "Day":    st.session_state["form_date"].strftime("%A"),
            "Group":  st.session_state["form_group"],
            "Area":   st.session_state["form_area"],
            "Safety": st.session_state["form_safety"],
            "Phone":  st.session_state["form_phone"].strip() if st.session_state["form_phone"] else "-",
            "LINE":   st.session_state["form_line"].strip()  if st.session_state["form_line"]  else "-",
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(FILE_PATH, index=False)
        st.session_state["clear_form"] = True
        st.rerun()
    else:
        st.warning("กรุณากรอกข้อมูลที่จำเป็น (Group, Area, Safety)")

# ================= 5. ตารางข้อมูล =================
st.subheader("📋 Data List")

def color_row(row):
    bg    = WEEKDAY_COLORS.get(row["Day"], "#FFFFFF")
    color = "#000000" if row["Day"] == "Monday" else "#FFFFFF"
    return [f"background-color: {bg}; color: {color}"] * len(row)

styled_df = df.style.apply(color_row, axis=1)
edited_df = st.data_editor(styled_df, use_container_width=True, num_rows="dynamic")
if not edited_df.equals(df):
    edited_df.to_excel(FILE_PATH, index=False)

# ================= 6. ส่ง LINE =================
st.divider()
st.subheader("📤 Send Report to LINE")

date_range = st.date_input(
    "Select Date Range (Start - End):",
    value=(datetime.now().date(), datetime.now().date()),
    key="send_range"
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    st.write(f"Period: **{start_date.strftime('%d %b %Y')}** to **{end_date.strftime('%d %b %Y')}**")

    if st.button("📅 Send Detail Cards to LINE", use_container_width=True, type="primary"):
        if df.empty:
            st.warning("No data found.")
        else:
            df['Date_DT'] = pd.to_datetime(df['Date'])
            mask        = (df['Date_DT'].dt.date >= start_date) & (df['Date_DT'].dt.date <= end_date)
            filtered_df = df.loc[mask].sort_values('Date_DT')

            if filtered_df.empty:
                st.error("No data found for the selected period.")
            else:
                all_bubbles = []
                for d_str in sorted(filtered_df['Date'].unique()):
                    day_rows = filtered_df[filtered_df['Date'] == d_str].to_dict('records')
                    try:
                        day_dt = datetime.strptime(d_str, "%Y-%m-%d").date()
                        all_bubbles.append(build_day_detail_bubble(day_rows, day_dt))
                    except:
                        pass

                # แบ่งส่ง batch ละ 5 bubble
                errors = []
                for i in range(0, len(all_bubbles), 5):
                    chunk   = all_bubbles[i:i+5]
                    carousel = {"type": "carousel", "contents": chunk}
                    size_kb  = len(json.dumps(carousel, ensure_ascii=False).encode('utf-8')) / 1024
                    st.write(f"Batch {i//5+1}: {len(chunk)} วัน | {size_kb:.1f} KB")
                    status, resp = send_to_line(carousel, "📅 Vendor Inspection Report")
                    if status != 200:
                        errors.append(f"Batch {i//5+1} Error {status}: {resp}")

                if not errors:
                    st.success(f"✅ ส่งสำเร็จ! {len(all_bubbles)} วัน")
                else:
                    for e in errors:
                        st.error(e)
else:
    st.warning("Please select both Start and End dates.")
