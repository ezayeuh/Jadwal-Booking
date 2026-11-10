import streamlit as st
import pandas as pd
import calendar
import re
from datetime import date
import gspread
from st_click_detector import click_detector
from streamlit_autorefresh import st_autorefresh

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 

st.set_page_config(page_title="Jadwal Kolam", page_icon="📅", layout="wide")
st_autorefresh(interval=900000, limit=None, key="papan_refresh")
st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

BULAN_INDO = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
HARI_INDO = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
HARI_LIST = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]

def parse_date_universal(tgl_str, thn_default, bln_default):
    tgl_str = str(tgl_str).upper().strip()
    b_num = None
    
    for num, name in BULAN_INDO.items():
        if name.upper() in tgl_str or name[:3].upper() in tgl_str:
            b_num = num
            break
            
    if not b_num:
        for h in HARI_LIST:
            if h in tgl_str:
                b_num = bln_default
                break
        if not b_num and re.search(r'\d+', tgl_str):
            b_num = bln_default

    range_match = re.search(r'(\d+)\s*-\s*(\d+)', tgl_str)
    if range_match and b_num:
        start_d = int(range_match.group(1))
        end_d = int(range_match.group(2))
        try:
            return [date(thn_default, b_num, d) for d in range(start_d, end_d + 1)]
        except:
            return []

    nums = re.findall(r'\d+', tgl_str)
    if b_num and nums:
        day_val = int(nums[0])
        year_val = thn_default 
        for n in nums[1:]:
            if len(n) == 4:
                year_val = int(n)
                break
        try:
            return [date(year_val, b_num, day_val)]
        except:
            pass
            
    return []

@st.cache_data(ttl=5)
def load_data(tahun_sheet, bulan_terpilih):
    try:
        kredensial = dict(st.secrets["connections"]["gsheets"])
        gc = gspread.service_account_from_dict(kredensial)
        sh = gc.open_by_url(SPREADSHEET_URL)
        ws = sh.worksheet(str(tahun_sheet))
        
        rows = ws.get_all_values()
        if not rows: return []

        parsed_events = []
        active_dates = []

        # Mulai baca dari baris ke-5 ke bawah (indeks 4)
        for i in range(4, len(rows)):
            row = rows[i]
            if len(row) < 6: continue
            
            # SESUAI STRUKTUR EXCEL ANDA:
            # Kolom C (Index 2) = TANGGAL
            # Kolom D (Index 3) = SEKOLAH
            # Kolom E (Index 4) = JUMLAH
            # Kolom F (Index 5) = KETERANGAN
            tgl_raw = row[2].strip() if len(row) > 2 else ""  
            sekolah_raw = row[3].strip() if len(row) > 3 else ""  
            jumlah_raw = row[4].strip() if len(row) > 4 else ""  
            ket_raw = row[5].strip() if len(row) > 5 else ""  

            if tgl_raw and "TANGGAL" not in tgl_raw.upper() and "JADWAL" not in tgl_raw.upper():
                dates_list = parse_date_universal(tgl_raw, int(tahun_sheet), bulan_terpilih)
                if dates_list:
                    active_dates = dates_list

            if active_dates and sekolah_raw and "SEKOLAH" not in sekolah_raw.upper():
                for d_item in active_dates:
                    parsed_events.append({
                        "TANGGAL_DATE": d_item,
                        "SEKOLAH": sekolah_raw,
                        "JUMLAH": jumlah_raw if jumlah_raw else "-",
                        "KETERANGAN": ket_raw if ket_raw else "-"
                    })

        return parsed_events
    except Exception as e:
        return []

st.markdown("""
<div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;">
    <h1 style="color: white !important; font-size: 20px; margin: 0 0 3px 0;">📅 Papan Informasi Jadwal Kunjungan</h1>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1: bln_pilihan = st.selectbox("Bulan", list(BULAN_INDO.values()), index=date.today().month - 1)
with col2: thn_pilihan = st.selectbox("Tahun", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
bln_idx = list(BULAN_INDO.values()).index(bln_pilihan) + 1

jadwal_data = load_data(thn_pilihan, bln_idx)

events_map = {date(thn_pilihan, bln_idx, d): [] for d in range(1, calendar.monthrange(thn_pilihan, bln_idx)[1] + 1)}
for item in jadwal_data:
    if item["TANGGAL_DATE"].month == bln_idx and item["TANGGAL_DATE"].year == thn_pilihan:
        if item["TANGGAL_DATE"] in events_map:
            events_map[item["TANGGAL_DATE"]].append(item)

calendar.setfirstweekday(calendar.MONDAY)
html_code = """<style>
.cal-container { background: white; border: 1px solid #cbd5e1; border-radius: 10px; padding: 10px; }
.cal-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; margin-bottom: 5px; }
.cal-th { text-align: center; font-weight: bold; font-size: 13px; }
.cal-cell { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 5px; height: 65px; text-decoration: none; display: flex; flex-direction: column; cursor: pointer; color: black; }
.cal-cell:hover { border-color: #0284c7; }
.cell-booked { background: #e0f2fe; border-color: #0284c7; }
.cell-selected { border: 2px solid #0f172a; }
.badge-booked { background: #0284c7; color: white; font-size: 10px; padding: 2px; text-align: center; border-radius: 3px; margin-top: auto; }
</style><div class='cal-container'><div class='cal-row'>"""

for h in ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Mgg"]: html_code += f"<div class='cal-th'>{h}</div>"
html_code += "</div>"

for week in calendar.monthcalendar(thn_pilihan, bln_idx):
    html_code += "<div class='cal-row'>"
    for day in week:
        if day == 0:
            html_code += "<div></div>"
        else:
            c_date = date(thn_pilihan, bln_idx, day)
            jml_ev = len(events_map[c_date])
            
            cls = "cal-cell"
            if jml_ev > 0: cls += " cell-booked"
            if c_date == st.session_state.selected_date: cls += " cell-selected"
            
            badge = f"<div class='badge-booked'>{jml_ev} Booking</div>" if jml_ev > 0 else ""
            html_code += f"<a href='#' id='{c_date}' class='{cls}'><b>{day}</b>{badge}</a>"
    html_code += "</div>"
html_code += "</div>"

clicked_date = click_detector(html_code)
if clicked_date:
    st.session_state.selected_date = date.fromisoformat(clicked_date)
    st.rerun()

sel_date = st.session_state.selected_date
st.markdown(f"#### 💬 Detail Kunjungan: {HARI_INDO[sel_date.weekday()]}, {sel_date.day} {BULAN_INDO[sel_date.month]} {sel_date.year}")

events_selected = events_map.get(sel_date, [])
detail_html = "<div style='background: white; border: 2px solid #0284c7; border-radius: 12px; padding: 15px;'>"

if events_selected:
    for ev in events_selected:
        detail_html += f"""
        <div style='background: #f8fafc; border-left: 4px solid #0284c7; padding: 10px; margin-bottom: 10px; border-radius: 5px;'>
            <div style='font-size: 14px; font-weight: bold; color: #0284c7;'>🏛️ {ev['SEKOLAH']}</div>
            <div style='font-size: 12px; margin-top:5px;'>👥 <b>Jumlah/Tiket:</b> {ev['JUMLAH']}</div>
            <div style='font-size: 12px; margin-top:3px; color: #d97706;'>📝 <b>Catatan:</b> {ev['KETERANGAN']}</div>
        </div>"""
else:
    detail_html += "<div style='text-align: center; color: #64748b;'>🏖️ Kosong. Belum ada jadwal pada tanggal ini.</div>"

detail_html += "</div>"
st.markdown(detail_html, unsafe_allow_html=True)
