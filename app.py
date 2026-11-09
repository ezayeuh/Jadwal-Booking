import streamlit as st
import pandas as pd
import calendar
from datetime import date
from streamlit_gsheets import GSheetsConnection
from st_click_detector import click_detector
from streamlit_autorefresh import st_autorefresh

# -------------------------------------------------------------
# KONFIGURASI SPREADSHEET & HALAMAN
# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit?gid=1469221539#gid=1469221539"

st.set_page_config(
    page_title="Papan Informasi Jadwal Kunjungan Kolam",
    page_icon="📅",
    layout="wide"
)

# Refresh otomatis setiap 15 menit agar layar tidak sleep
st_autorefresh(interval=900000, limit=None, key="papan_refresh")

# Sembunyikan Sidebar / Navigasi Halaman di Dashboard Pengunjung
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

conn = st.connection("gsheets", type=GSheetsConnection)

HARI_INDO = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
BULAN_INDO = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def load_and_parse_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        if df is None or df.empty:
            return []

        data = df.to_dict(orient="records")
        parsed_events = []
        current_date = None
        
        current_grup = []
        current_jumlah = []
        current_ket = []

        def flush_current():
            if current_date and current_grup:
                parsed_events.append({
                    "TANGGAL_DATE": current_date,
                    "SEKOLAH": " | ".join([str(x) for x in current_grup if pd.notna(x)]),
                    "JUMLAH": " | ".join([str(x) for x in current_jumlah if pd.notna(x)]) if current_jumlah else "-",
                    "KETERANGAN": " | ".join([str(x) for x in current_ket if pd.notna(x)]) if current_ket else "-"
                })

        for item in data:
            tgl_raw = item.get("TANGGAL")
            sekolah_raw = item.get("SEKOLAH")
            jumlah_raw = item.get("JUMLAH")
            ket_raw = item.get("KETERANGAN")

            # Deteksi baris yang memiliki tanggal baru
            if pd.notna(tgl_raw) and str(tgl_raw).strip() != "" and str(tgl_raw).upper() != "TANGGAL":
                flush_current()
                current_grup = []
                current_jumlah = []
                current_ket = []
                
                parsed_date = None
                tgl_str = str(tgl_raw).upper()
                try:
                    parsed_date = date.fromisoformat(tgl_str.split(" ")[0])
                except Exception:
                    for b_num, b_name in BULAN_INDO.items():
                        if b_name[:3].upper() in tgl_str or b_name.upper() in tgl_str:
                            import re
                            nums = re.findall(r'\d+', tgl_str)
                            if len(nums) >= 2:
                                day_val = int(nums[0])
                                year_val = int(nums[1]) if len(nums[1]) == 4 else 2025
                                try:
                                    parsed_date = date(year_val, b_num, day_val)
                                except Exception:
                                    pass
                current_date = parsed_date

            if current_date:
                if pd.notna(sekolah_raw) and str(sekolah_raw).strip() != "":
                    current_grup.append(sekolah_raw)
                if pd.notna(jumlah_raw) and str(jumlah_raw).strip() != "":
                    current_jumlah.append(jumlah_raw)
                if pd.notna(ket_raw) and str(ket_raw).strip() != "":
                    current_ket.append(ket_raw)

        flush_current()
        return parsed_events
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return []

# Banner Header Utama
st.markdown("""
<div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;">
    <h1 style="color: white !important; font-size: 20px; font-weight: 700; margin: 0 0 3px 0;">📅 Kalender Jadwal Kunjungan Kolam</h1>
    <p style="color: #e0f2fe; margin: 0; font-size: 12px;">Sentuh salah satu kotak tanggal pada kalender di bawah untuk melihat rincian jadwal.</p>
</div>
""", unsafe_allow_html=True)

jadwal_data = load_and_parse_data()

# -------------------------------------------------------------
# FILTER BULAN & TAHUN
# -------------------------------------------------------------
col_b1, col_b2 = st.columns(2)
today_dt = date.today()

with col_b1:
    bln_pilihan = st.selectbox("Pilih Bulan:", list(BULAN_INDO.values()), index=today_dt.month - 1)
with col_b2:
    thn_pilihan = st.selectbox("Pilih Tahun:", range(2024, 2030), index=range(2024, 2030).index(today_dt.year))

bln_idx = list(BULAN_INDO.values()).index(bln_pilihan) + 1

# -------------------------------------------------------------
# PEMETAAN EVENT PER TANGGAL
# -------------------------------------------------------------
jml_hari_bulan = calendar.monthrange(thn_pilihan, bln_idx)[1]
events_map = {date(thn_pilihan, bln_idx, d): [] for d in range(1, jml_hari_bulan + 1)}

for item in jadwal_data:
    tgl_item = item.get("TANGGAL_DATE")
    if tgl_item and isinstance(tgl_item, date):
        if tgl_item.month == bln_idx and tgl_item.year == thn_pilihan:
            if tgl_item in events_map:
                events_map[tgl_item].append(item)

# -------------------------------------------------------------
# RENDER KALENDER
# -------------------------------------------------------------
st.markdown(f"### 🗓️ Bulan {bln_pilihan} {thn_pilihan}")

calendar.setfirstweekday(calendar.MONDAY)
raw_weeks = calendar.monthcalendar(thn_pilihan, bln_idx)
hari_names_singkat = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Mgg"]

html_code = """<style>
.custom-cal-container a { text-decoration: none !important; } 
.cal-box { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 20px;} 
.cal-grid-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 4px; } 
.cal-th { text-align: center; font-weight: bold; font-size: 12px; padding: 4px 0; } 
.cal-cell { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; min-height: 56px; padding: 4px 2px; text-align: center; display: flex; flex-direction: column; justify-content: space-between; transition: 0.2s ease; cursor: pointer;} 
.cal-cell:hover { background-color: #f1f5f9; border-color: #0284c7; } 
.cell-empty { background-color: transparent; border: 1px solid transparent; min-height: 56px; } 
.cell-weekend { background-color: #fef2f2 !important; border-color: #f87171 !important; } 
.cell-booked { background-color: #e0f2fe !important; border-color: #0284c7 !important; } 
.cell-selected { border: 2px solid #0f172a !important; box-shadow: 0 0 0 2px #38bdf8; } 
.c-num { font-size: 13px; font-weight: bold; color: #1e293b; } 
.c-badge { font-size: 9px; padding: 2px 0; border-radius: 3px; font-weight: bold; display: block; text-align: center; margin-top: 4px;} 
.badge-weekend { background-color: #dc2626; color: white; } 
.badge-booked { background-color: #0284c7; color: white; } 
.badge-empty { background-color: #e2e8f0; color: #64748b; }
</style>"""

html_code += "<div class='custom-cal-container'><div class='cal-box'><div class='cal-grid-row'>"

for i, h_name in enumerate(hari_names_singkat):
    c_color = "#dc2626" if i in [5, 6] else "#334155"
    html_code += f"<div class='cal-th' style='color: {c_color};'>{h_name}</div>"
html_code += "</div>"

for week in raw_weeks:
    html_code += "<div class='cal-grid-row'>"
    for idx_col, day in enumerate(week):
        if day == 0:
            html_code += "<div class='cell-empty'></div>"
        else:
            curr_date = date(thn_pilihan, bln_idx, day)
            jml_ev = len(events_map[curr_date])
            is_weekend = (idx_col in [5, 6])

            extra_cls = ""
            badge_cls = "badge-empty"
            badge_txt = "Kosong"

            if jml_ev > 0:
                badge_txt = f"{jml_ev} Agenda"
                if is_weekend:
                    extra_cls += " cell-weekend"
                    badge_cls = "badge-weekend"
                else:
                    extra_cls += " cell-booked"
                    badge_cls = "badge-booked"
            else:
                if is_weekend:
                    extra_cls += " cell-weekend"
                    badge_cls = "badge-weekend"

            if curr_date == st.session_state.selected_date:
                extra_cls += " cell-selected"

            html_code += f"<a href='#' id='{curr_date.isoformat()}' class='cal-cell{extra_cls}'><div class='c-num'>{day}</div><span class='c-badge {badge_cls}'>{badge_txt}</span></a>"

    html_code += "</div>"
html_code += "</div></div>"

clicked_date = click_detector(html_code, key="cal_detector")

if clicked_date:
    parsed_tgl = date.fromisoformat(clicked_date)
    if st.session_state.selected_date != parsed_tgl:
        st.session_state.selected_date = parsed_tgl
        st.rerun()

# -------------------------------------------------------------
# BUBBLE POP-UP RINCIAN JADWAL TANGGAL TERPILIH
# -------------------------------------------------------------
sel_date = st.session_state.selected_date
sel_hari_nama = HARI_INDO[sel_date.weekday()]
sel_bln_nama = BULAN_INDO[sel_date.month]
tgl_format_panjang = f"{sel_hari_nama}, {sel_date.day} {sel_bln_nama} {sel_date.year}"

st.markdown(f"#### 💬 Detail Kunjungan: <span style='color: #0284c7;'>{tgl_format_panjang}</span>", unsafe_allow_html=True)

events_selected = [item for item in jadwal_data if item.get("TANGGAL_DATE") == sel_date]

detail_html = """<style>
.bubble-container { background: #ffffff; border: 2px solid #0284c7; border-radius: 12px; padding: 18px; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.15); margin-top: 5px; }
.event-item { background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; padding: 10px 14px; margin-top: 10px; border-radius: 6px; }
.empty-bubble { background-color: #f1f5f9; border: 2px dashed #cbd5e1; padding: 15px; text-align: center; border-radius: 8px; color: #64748b; font-size: 13px; }
</style>
<div class="bubble-container">"""

if events_selected:
    detail_html += f"<p style='color: #0369a1; font-weight: bold; margin-bottom: 8px;'>Ditemukan {len(events_selected)} jadwal pada tanggal ini:</p>"
    for ev in events_selected:
        sekolah = ev.get("SEKOLAH", "-")
        jumlah = ev.get("JUMLAH", "-")
        ket = ev.get("KETERANGAN", "-")

        detail_html += f"""
<div class="event-item">
<div style="font-size: 15px; font-weight: bold; color: #0284c7; margin-bottom: 3px;">🏛️ {sekolah}</div>
<div style="font-size: 12px; color: #475569;">👥 <b>Jumlah/Tiket:</b> {jumlah}</div>
<div style="font-size: 11px; color: #64748b; font-style: italic; margin-top: 3px;">📝 <b>Keterangan:</b> {ket}</div>
</div>"""
else:
    detail_html += """
<div class="empty-bubble">
<div style="font-size: 20px; margin-bottom: 3px;">🏖️</div>
<b>Status: KOSONG</b><br>
Belum ada jadwal rombongan atau bookingan pada tanggal ini.
</div>"""

detail_html += "</div>"
st.markdown(detail_html, unsafe_allow_html=True)
