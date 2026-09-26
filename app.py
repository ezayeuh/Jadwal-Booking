import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection
from st_click_detector import click_detector

# -------------------------------------------------------------
# KONFIGURASI SPREADSHEET
# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1XsYvF0pcBYjRm-h_oPf2jag3OwUFLK43bhRoyE-yh-M/edit"

st.set_page_config(
    page_title="Papan Informasi Jadwal Kunjungan",
    page_icon="📅",
    layout="wide"
)

# Inisialisasi State Tanggal
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

conn = st.connection("gsheets", type=GSheetsConnection)

HARI_INDO = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
BULAN_INDO = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        if df is None or df.empty:
            return []

        data = df.to_dict(orient="records")
        for item in data:
            tgl_raw = item.get("TANGGAL_DATE")
            if pd.notna(tgl_raw) and tgl_raw:
                try:
                    parsed_date = date.fromisoformat(str(tgl_raw).split(" ")[0])
                    item["TANGGAL_DATE"] = parsed_date
                except Exception:
                    item["TANGGAL_DATE"] = None
            else:
                item["TANGGAL_DATE"] = None

            hr_raw = item.get("HARI_RUTIN")
            if isinstance(hr_raw, str):
                try:
                    item["HARI_RUTIN"] = eval(hr_raw)
                except Exception:
                    item["HARI_RUTIN"] = [hr_raw] if hr_raw else []
            elif not isinstance(hr_raw, list):
                item["HARI_RUTIN"] = []

        return data
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")
        return []

# Banner Header Utama
st.markdown("""
<div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;">
    <h1 style="color: white !important; font-size: 20px; font-weight: 700; margin: 0 0 3px 0;">📅 Kalender Jadwal Kunjungan Kolam</h1>
    <p style="color: #e0f2fe; margin: 0; font-size: 12px;">Sentuh salah satu kotak tanggal pada kalender di bawah untuk melihat rincian jadwal.</p>
</div>
""", unsafe_allow_html=True)

jadwal_data = load_data()

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
# PEMETAAN DATA EVENT PER TANGGAL
# -------------------------------------------------------------
jml_hari_bulan = calendar.monthrange(thn_pilihan, bln_idx)[1]
events_map = {date(thn_pilihan, bln_idx, d): [] for d in range(1, jml_hari_bulan + 1)}

for item in jadwal_data:
    tipe_str = str(item.get("TIPE", "")).lower()
    tgl_item = item.get("TANGGAL_DATE")
    
    if tipe_str == "hari rutin / berulang" or item.get("HARI_RUTIN"):
        rutin_list = item.get("HARI_RUTIN", [])
        if isinstance(rutin_list, list):
            for d in events_map.keys():
                hari_nama = HARI_INDO[d.weekday()]
                if hari_nama in rutin_list:
                    events_map[d].append(item)
                    
    elif tgl_item and isinstance(tgl_item, date):
        if tgl_item.month == bln_idx and tgl_item.year == thn_pilihan:
            if tgl_item in events_map:
                events_map[tgl_item].append(item)

# -------------------------------------------------------------
# RENDER KALENDER (Menggunakan Click Detector)
# -------------------------------------------------------------
st.markdown(f"### 🗓️ Bulan {bln_pilihan} {thn_pilihan}")

calendar.setfirstweekday(calendar.SUNDAY)
raw_weeks = calendar.monthcalendar(thn_pilihan, bln_idx)
hari_names_singkat = ["Mgg", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]

html_code = "<style>.custom-cal-container a { text-decoration: none !important; } .cal-box { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); margin-bottom: 20px;} .cal-grid-row { display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 4px; } .cal-th { text-align: center; font-weight: bold; font-size: 12px; padding: 4px 0; } .cal-cell { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; min-height: 56px; padding: 4px 2px; text-align: center; display: flex; flex-direction: column; justify-content: space-between; transition: 0.2s ease; cursor: pointer;} .cal-cell:hover { background-color: #f1f5f9; border-color: #0284c7; } .cell-empty { background-color: transparent; border: 1px solid transparent; min-height: 56px; } .cell-booked { background-color: #fef2f2 !important; border-color: #f87171 !important; } .cell-selected { border: 2px solid #0284c7 !important; background-color: #e0f2fe !important; } .c-num { font-size: 13px; font-weight: bold; color: #1e293b; } .c-badge { font-size: 9px; padding: 2px 0; border-radius: 3px; font-weight: bold; display: block; text-align: center; margin-top: 4px;} .badge-booked { background-color: #dc2626; color: white; } .badge-empty { background-color: #e2e8f0; color: #64748b; }</style>"
html_code += "<div class='custom-cal-container'><div class='cal-box'><div class='cal-grid-row'>"

for i, h_name in enumerate(hari_names_singkat):
    c_color = "#dc2626" if i == 0 else ("#16a34a" if i == 5 else "#334155")
    html_code += f"<div class='cal-th' style='color: {c_color};'>{h_name}</div>"
html_code += "</div>"

for week in raw_weeks:
    html_code += "<div class='cal-grid-row'>"
    for day in week:
        if day == 0:
            html_code += "<div class='cell-empty'></div>"
        else:
            curr_date = date(thn_pilihan, bln_idx, day)
            jml_ev = len(events_map[curr_date])
            
            extra_cls = ""
            if jml_ev > 0:
                extra_cls += " cell-booked"
            if curr_date == st.session_state.selected_date:
                extra_cls += " cell-selected"
                
            badge_cls = "badge-booked" if jml_ev > 0 else "badge-empty"
            badge_txt = f"{jml_ev} Rombel" if jml_ev > 0 else "Kosong"
            
            html_code += f"<a href='#' id='{curr_date.isoformat()}' class='cal-cell{extra_cls}'><div class='c-num'>{day}</div><span class='c-badge {badge_cls}'>{badge_txt}</span></a>"
            
    html_code += "</div>"
html_code += "</div></div>"

# Eksekusi penangkap klik
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

events_selected = []
for item in jadwal_data:
    tipe_str = str(item.get("TIPE", "")).lower()
    
    if item.get("TANGGAL_DATE") == sel_date:
        events_selected.append(item)
    elif tipe_str == "hari rutin / berulang" or item.get("HARI_RUTIN"):
        rutin_list = item.get("HARI_RUTIN", [])
        if isinstance(rutin_list, list) and sel_hari_nama in rutin_list:
            events_selected.append(item)

# HTML diratakan ke kiri (tanpa indentasi) agar terbaca sebagai elemen HTML, bukan kode
detail_html = """<style>
.bubble-container { background: #ffffff; border: 2px solid #0284c7; border-radius: 12px; padding: 18px; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.15); margin-top: 5px; }
.event-item { background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7; padding: 10px 14px; margin-top: 10px; border-radius: 6px; }
.empty-bubble { background-color: #f1f5f9; border: 2px dashed #cbd5e1; padding: 15px; text-align: center; border-radius: 8px; color: #64748b; font-size: 13px; }
</style>
<div class="bubble-container">"""

if events_selected:
    detail_html += f"<p style='color: #0369a1; font-weight: bold; margin-bottom: 8px;'>Ditemukan {len(events_selected)} jadwal / kegiatan pada tanggal ini:</p>"
    for ev in events_selected:
        sekolah = ev.get("SEKOLAH", "-")
        pic = ev.get("PIC", "-")
        ket = ev.get("KETERANGAN", "-")
        kategori = ev.get("KATEGORI", "Sekolah")
        
        jumlah_raw = ev.get("JUMLAH")
        jumlah = str(jumlah_raw) if pd.notna(jumlah_raw) and jumlah_raw else "-"
        if jumlah.endswith(".0"):
            jumlah = jumlah.replace(".0", "")
            
        warna_badge = "#16a34a" if kategori.lower() == "kegiatan rutin" else "#0284c7"

        detail_html += f"""
<div class="event-item">
<div style="float: right; background-color: {warna_badge}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{kategori}</div>
<div style="font-size: 15px; font-weight: bold; color: #0284c7; margin-bottom: 3px;">{sekolah}</div>
<div style="font-size: 12px; color: #475569;">👤 <b>PIC/Kontak:</b> {pic}</div>
<div style="font-size: 12px; color: #475569;">👥 <b>Jumlah:</b> {jumlah} Orang</div>
<div style="font-size: 11px; color: #64748b; font-style: italic; margin-top: 3px;">📝 Catatan: {ket}</div>
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
