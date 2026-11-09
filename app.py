import streamlit as st
import pandas as pd
import calendar
import re
from datetime import date
from streamlit_gsheets import GSheetsConnection
from st_click_detector import click_detector
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------
# KONFIGURASI
# -------------------------------------------------------------
# GANTI LINK INI DENGAN LINK GOOGLE SPREADSHEET YANG BARU DIBUAT (BUKAN .xlsx)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 

st.set_page_config(page_title="Jadwal Kolam", page_icon="📅", layout="wide")
st_autorefresh(interval=900000, limit=None, key="papan_refresh")

# Sembunyikan Sidebar di Publik
st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

conn = st.connection("gsheets", type=GSheetsConnection)

BULAN_INDO = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}
HARI_INDO = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}

def parse_indonesian_date(tgl_str):
    """Fungsi cerdas membaca tanggal seperti 'MINGGU, 19 November 2026' atau 'KAMIS, 30 November'"""
    tgl_str = str(tgl_str).upper().strip()
    b_num = None
    for num, name in BULAN_INDO.items():
        if name.upper() in tgl_str or name[:3].upper() in tgl_str:
            b_num = num
            break
            
    if b_num:
        nums = re.findall(r'\d+', tgl_str)
        if nums:
            day_val = int(nums[0])
            year_val = date.today().year # Default tahun saat ini jika tidak ditulis
            for n in nums[1:]:
                if len(n) == 4:
                    year_val = int(n)
                    break
            try:
                return date(year_val, b_num, day_val)
            except:
                return None
    return None

def load_data():
    try:
        # Ganti worksheet="DETAIL" menjadi nama sheet yang ada di bawah file Anda (biasanya "Sheet1" atau "DETAIL")
        df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="DETAIL", ttl=0)
        if df.empty: return []

        data = df.to_dict(orient="records")
        parsed_events = []
        current_date = None
        current_grup, current_jumlah, current_ket = [], [], []

        def simpan_grup_sebelumnya():
            if current_date and current_grup:
                parsed_events.append({
                    "TANGGAL_DATE": current_date,
                    "SEKOLAH": "<br>".join(current_grup),
                    "JUMLAH": "<br>".join(current_jumlah) if current_jumlah else "-",
                    "KETERANGAN": "<br>".join(current_ket) if current_ket else "-"
                })

        for row in data:
            tgl_raw = row.get("TANGGAL")
            sekolah_raw = row.get("SEKOLAH")
            jumlah_raw = row.get("JUMLAH")
            ket_raw = row.get("KETERANGAN")

            # Jika ketemu tanggal baru
            if pd.notna(tgl_raw) and str(tgl_raw).strip() != "" and str(tgl_raw).upper() != "TANGGAL":
                parsed_d = parse_indonesian_date(tgl_raw)
                if parsed_d:
                    simpan_grup_sebelumnya() # Simpan data tgl sebelumnya
                    current_date = parsed_d
                    current_grup, current_jumlah, current_ket = [], [], []

            # Tambahkan baris ke tanggal yang sedang aktif
            if current_date:
                if pd.notna(sekolah_raw) and str(sekolah_raw).strip():
                    current_grup.append(f"👤 {str(sekolah_raw).strip()}")
                if pd.notna(jumlah_raw) and str(jumlah_raw).strip():
                    current_jumlah.append(str(jumlah_raw).strip())
                if pd.notna(ket_raw) and str(ket_raw).strip():
                    current_ket.append(str(ket_raw).strip())

        simpan_grup_sebelumnya() # Simpan sisa data terakhir
        return parsed_events
    except Exception as e:
        st.error(f"Gagal memuat: {e}")
        return []

# Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;">
    <h1 style="color: white !important; font-size: 20px; margin: 0 0 3px 0;">📅 Papan Informasi Jadwal Kunjungan</h1>
</div>
""", unsafe_allow_html=True)

jadwal_data = load_data()

# Filter
col1, col2 = st.columns(2)
with col1: bln_pilihan = st.selectbox("Bulan", list(BULAN_INDO.values()), index=date.today().month - 1)
with col2: thn_pilihan = st.selectbox("Tahun", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
bln_idx = list(BULAN_INDO.values()).index(bln_pilihan) + 1

# Mapping ke kalender
events_map = {date(thn_pilihan, bln_idx, d): [] for d in range(1, calendar.monthrange(thn_pilihan, bln_idx)[1] + 1)}
for item in jadwal_data:
    if item["TANGGAL_DATE"].month == bln_idx and item["TANGGAL_DATE"].year == thn_pilihan:
        if item["TANGGAL_DATE"] in events_map:
            events_map[item["TANGGAL_DATE"]].append(item)

# Render HTML Kalender
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

# Menampilkan Detail Bubble
sel_date = st.session_state.selected_date
st.markdown(f"#### 💬 Detail Kunjungan: {HARI_INDO[sel_date.weekday()]}, {sel_date.day} {BULAN_INDO[sel_date.month]} {sel_date.year}")

events_selected = events_map.get(sel_date, [])
detail_html = "<div style='background: white; border: 2px solid #0284c7; border-radius: 12px; padding: 15px;'>"

if events_selected:
    for ev in events_selected:
        detail_html += f"""
        <div style='background: #f8fafc; border-left: 4px solid #0284c7; padding: 10px; margin-bottom: 10px; border-radius: 5px;'>
            <div style='font-size: 14px; font-weight: bold; color: #0284c7;'>{ev['SEKOLAH']}</div>
            <div style='font-size: 12px; margin-top:5px;'>👥 <b>Rincian Tiket:</b><br>{ev['JUMLAH']}</div>
            <div style='font-size: 12px; margin-top:5px; color: #d97706;'>📝 <b>Catatan:</b><br>{ev['KETERANGAN']}</div>
        </div>"""
else:
    detail_html += "<div style='text-align: center; color: #64748b;'>🏖️ Kosong. Belum ada jadwal.</div>"

detail_html += "</div>"
st.markdown(detail_html, unsafe_allow_html=True)
