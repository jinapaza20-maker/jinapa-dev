import streamlit as st
import pandas as pd
import os
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

# ================= 2. สร้าง Bubble ปฏิทิน =================
def build_calendar_bubble(month_df, year, month):
    month_label = date(year, month, 1).strftime("%B %Y")

    day_data_map = {}
    for _, r in month_df.iterrows():
        try:
            d = datetime.strptime(str(r['Date']), "%Y-%m-%d").day
            day_data_map.setdefault(d, []).append(r)
        except:
            pass

    DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    header_cells = [
        {
            "type": "box", "layout": "vertical", "flex": 1,
            "backgroundColor": "#1A1A2E", "paddingAll": "4px",
            "contents": [{"type": "text", "text": d, "color": "#FFFFFF",
                          "size": "xxs", "align": "center", "weight": "bold"}]
        }
        for d in DAY_NAMES
    ]
    header_row = {"type": "box", "layout": "horizontal", "spacing": "none", "contents": header_cells}

    first_col  = (date(year, month, 1).weekday() + 1) % 7
    total_days = calendar.monthrange(year, month)[1]
    flat       = [None] * first_col + list(range(1, total_days + 1))
    while len(flat) % 7 != 0:
        flat.append(None)
    weeks = [flat[i:i+7] for i in range(0, len(flat), 7)]

    week_rows = []
    for week in weeks:
        cells = []
        for day_num in week:
            if day_num is None:
                cells.append({
                    "type": "box", "layout": "vertical", "flex": 1,
                    "backgroundColor": "#E0E0E0", "paddingAll": "2px", "height": "64px",
                    "contents": [{"type": "filler"}]
                })
            else:
                day_dt       = date(year, month, day_num)
                weekday_name = day_dt.strftime("%A")
                bg           = WEEKDAY_COLORS.get(weekday_name, "#EEEEEE")
                txt_color    = WEEKDAY_TEXT.get(weekday_name, "#FFFFFF")
                rows_today   = day_data_map.get(day_num, [])

                if rows_today:
                    count = len(rows_today)
                    cell_contents = [
                        {"type": "text", "text": str(day_num), "size": "xxs",
                         "color": txt_color, "weight": "bold", "align": "center"},
                        {"type": "text", "text": "👤" * min(count, 3),
                         "size": "sm", "align": "center"},
                        {"type": "text", "text": str(rows_today[0].get('Area', '')),
                         "size": "xxs", "color": txt_color, "align": "center", "wrap": True}
                    ]
                    cell_bg = bg
                else:
                    cell_contents = [
                        {"type": "text", "text": str(day_num), "size": "xxs",
                         "color": txt_color, "align": "center"},
                        {"type": "filler"}
                    ]
                    cell_bg = bg + "44"

                cells.append({
                    "type": "box", "layout": "vertical", "flex": 1,
                    "backgroundColor": cell_bg, "paddingAll": "2px", "height": "64px",
                    "contents": cell_contents
                })

        week_rows.append({
            "type": "box", "layout": "horizontal",
            "spacing": "none", "contents": cells
        })

    return {
        "type": "bubble", "size": "giga",
        "header": {
            "type": "box", "layout": "vertical",
            "backgroundColor": "#1A1A2E", "paddingAll": "12px",
            "contents": [
                {"type": "text", "text": "📅 Vendor Inspection",
                 "color": "#FFFFFF", "weight": "bold", "size": "lg", "align": "center"},
                {"type": "text", "text": month_label,
                 "color": "#AAAAFF", "size": "md", "align": "center"},
                {"type": "text", "text": "👉 Swipe ซ้าย ดูรายละเอียดแต่ละวัน",
                 "color": "#AAAAAA", "size": "xxs", "align": "center"}
            ]
        },
        "body": {
            "type": "box", "layout": "vertical",
            "paddingAll": "0px", "spacing": "none",
            "contents": [header_row] + week_rows
        }
    }

# ================= 3. สร้าง Bubble รายละเอียดวัน (2 คอลัมน์ WG | BP) =================
def build_col_items(group_rows):
    """สร้างรายการคนในคอลัมน์ แบบกระชับ ไม่มีไอคอนคน"""
    if not group_rows:
        return [{"type": "text", "text": "ไม่มีข้อมูล",
                 "color": "#AAAAAA", "size": "xxs", "align": "center", "margin": "sm"}]

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
            "backgroundColor": "#FFFFFF11", "cornerRadius": "sm",
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
            # Header WG
            {
                "type": "box", "layout": "vertical",
                "backgroundColor": "#5A4500", "paddingAll": "8px",
                "contents": [
                    {"type": "text", "text": "WG", "color": "#FFD700",
                     "weight": "bold", "size": "sm", "align": "center"}
                ]
            },
            # รายการ WG
            {
                "type": "box", "layout": "vertical",
                "paddingAll": "8px", "spacing": "none",
                "contents": build_col_items(wg_rows)
            }
        ]
    }

    bp_col = {
        "type": "box", "layout": "vertical", "flex": 1,
        "spacing": "none",
        "contents": [
            # Header BP
            {
                "type": "box", "layout": "vertical",
                "backgroundColor": "#003366", "paddingAll": "8px",
                "contents": [
                    {"type": "text", "text": "BP", "color": "#66AAFF",
                     "weight": "bold", "size": "sm", "align": "center"}
                ]
            },
            # รายการ BP
            {
                "type": "box", "layout": "vertical",
                "paddingAll": "8px", "spacing": "none",
                "contents": build_col_items(bp_rows)
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

# ================= 4. หน้าเว็บ + โหลดข้อมูล =================
st.set_page_config(page_title="Vendor Inspection System", layout="wide")
FILE_PATH = "inspection_data.xlsx"

if os.path.exists(FILE_PATH):
    df = pd.read_excel(FILE_PATH, dtype=str).fillna("-")
else:
    df = pd.DataFrame(columns=["Date", "Day", "Group", "Area", "Safety", "Phone", "LINE"])

# ================= 5. ฟอร์มบันทึก =================
st.markdown("## 📝 Inspection Entry")
with st.form("inspection_form", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        group = st.selectbox("Group", ["", "WG", "BP"])
        area  = st.selectbox("Area", ["", "WG1", "WG2", "WG3", "WG5",
                                       "BP1-DET3-WH", "BP2-3", "BP5-RD1", "BP8", "BP9"])
    with c2:
        date_val = st.date_input("Inspection Date")
        safety   = st.text_input("Safety Name")
    with c3:
        phone    = st.text_input("Phone Number")
        line_val = st.text_input("LINE ID / Link")

    if st.form_submit_button("💾 Save Data", use_container_width=True):
        if group and area and safety:
            new_row = {
                "Date":   date_val.strftime("%Y-%m-%d"),
                "Day":    date_val.strftime("%A"),
                "Group":  group, "Area": area, "Safety": safety,
                "Phone":  phone.strip() if phone else "-",
                "LINE":   line_val.strip() if line_val else "-"
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_excel(FILE_PATH, index=False)
            st.rerun()
        else:
            st.warning("Please fill in required fields (Group, Area, Safety)")

# ================= 6. ตารางข้อมูล =================
st.subheader("📋 Data List")

def color_row(row):
    bg    = WEEKDAY_COLORS.get(row["Day"], "#FFFFFF")
    color = "#000000" if row["Day"] == "Monday" else "#FFFFFF"
    return [f"background-color: {bg}; color: {color}"] * len(row)

styled_df = df.style.apply(color_row, axis=1)
edited_df = st.data_editor(styled_df, use_container_width=True, num_rows="dynamic")
if not edited_df.equals(df):
    edited_df.to_excel(FILE_PATH, index=False)

# ================= 7. ส่ง LINE =================
st.divider()
st.subheader("📤 Send Calendar Report to LINE")

date_range = st.date_input(
    "Select Date Range (Start - End):",
    value=(datetime.now().date(), datetime.now().date()),
    key="send_range"
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    st.write(f"Period: **{start_date.strftime('%d %b %Y')}** to **{end_date.strftime('%d %b %Y')}**")

    if st.button("📅 Send Calendar + Detail Cards to LINE", use_container_width=True, type="primary"):
        if df.empty:
            st.warning("No data found.")
        else:
            df['Date_DT'] = pd.to_datetime(df['Date'])
            mask        = (df['Date_DT'].dt.date >= start_date) & (df['Date_DT'].dt.date <= end_date)
            filtered_df = df.loc[mask].sort_values('Date_DT')

            if filtered_df.empty:
                st.error("No data found for the selected period.")
            else:
                months      = filtered_df['Date_DT'].dt.to_period('M').unique()
                all_bubbles = []

                for p in months:
                    month_df = filtered_df[filtered_df['Date_DT'].dt.to_period('M') == p]

                    # Bubble รายละเอียดแต่ละวัน (ไม่มีปฏิทิน)
                    for d_str in sorted(month_df['Date'].unique()):
                        day_rows = month_df[month_df['Date'] == d_str].to_dict('records')
                        try:
                            day_dt = datetime.strptime(d_str, "%Y-%m-%d").date()
                            all_bubbles.append(build_day_detail_bubble(day_rows, day_dt))
                        except:
                            pass

                carousel = {"type": "carousel", "contents": all_bubbles}
                status, resp = send_to_line(carousel, "📅 Vendor Inspection Report")

                if status == 200:
                    total_days = len(all_bubbles) - len(months)
                    st.success(f"✅ ส่งสำเร็จ! ปฏิทิน {len(months)} เดือน + {total_days} วันที่มีข้อมูล")
                else:
                    st.error(f"Error {status}: {resp}")
else:
    st.warning("Please select both Start and End dates.")
