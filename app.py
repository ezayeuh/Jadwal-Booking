import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
# KONFIGURASI SPREADSHEET
# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1XsYvF0pcBYjRm-h_oPf2jag3OwUFLK43bhRoyE-yh-M/edit"

st.set_page_config(
    page_title="Papan Informasi Jadwal Kunjungan",
    page_icon="📅",
    layout="wide"
)

# Inisialisasi State untuk tanggal yang dipilih
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = date.today()

# Menangani parameter klik tanggal dari elemen HTML kustom menggunakan query_params
query_params = st.query_params
if "klik_tgl" in query_params:
    try:
        tgl_parsed = date.fromisoformat(query_params["klik_tgl"])
        st.session_state.selected_date = tgl_parsed
    except Exception:
        pass

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

# -------------------------------------------------------------
# CSS KUSTOM UNTUK MEMBUAT TAMPILAN MATRIKS 7 KOLOM SEPERTI KALENDER
# -------------------------------------------------------------
st.markdown("""
<style>
    .banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    .banner h1 { color: white !important; font-size: 20px; font-weight: 700; margin: 0 0 3px 0; }
    .banner p { color: #e0f2fe; margin: 0; font-size: 12px; }

    /* Struktur Grid Kalender Murni (7 Kolom Sejajar) */
    .cal-container {
        display: flex;
        flex-direction: column;
        gap: 4px;
        background: #ffffff;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .cal-row {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
    }
    .cal-header-cell {
        text-align: center;
        font-weight: bold;
        font-size: 12px;
        padding: 6px 0;
    }
    .cal-day-cell {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 6px;
        min-height: 60px;
        padding: 4px;
        text-align: center;
        text-decoration: none;
        color: #1e293b;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.15s ease;
    }
    .cal-day-cell:hover {
        background-color: #f1f5f9;
        border-color: #0284c7;
        transform: translateY(-1px);
    }
    .cal-day-empty {
        background-color: #f8fafc;
        border: 1px dashed #f1f5f9;
        border-radius: 6px;
        min-height: 60px;
    }
    .cell-booked {
        background-color: #fef2f2 !important;
        border-color: #fca5a5 !important;
    }
    .cell-selected {
        border: 2px solid #0284c7 !important;
        box-shadow: 0 0 5px rgba(2, 132, 199, 0.4);
        background-color: #e0f2fe !important;
    }
    .day-num {
        font-size: 13px;
        font-weight: bold;
    }
    .badge-info {
        font-size: 9px;
        padding: 1px 3px;
        border-radius: 4px;
        font-weight: bold;
        margin-top: 2px;
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .badge-red { background-color: #dc2626; color: white; }
    .badge-gray { background-color: #e2e8f0; color: #64748b; }

    /* Bubble Rincian */
    .bubble-container {
        background: #ffffff;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.15);
        margin-top: 15px;
    }
    .event-item {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #0284c7;
        padding: 10px 14px;
        margin-top: 10px;
        border-radius: 6px;
    }
    .empty-bubble {
        background-color: #f1f5f9;
        border: 2px dashed #cbd5e1;
        padding: 15px;
        text-align: center;
        border-radius: 8px;
        color: #64748b;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

jadwal_data = load_data()

st.markdown("""
<div class="banner">
    <h1>📅 Kalender Jadwal Kunjungan Kolam</h1>
    <p>Ketuk salah satu kotak tanggal pada kalender di bawah untuk melihat rincian jadwal.</p>
</div>
""", unsafe_allow_html=True)

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
# RENDER TAMPILAN KALENDER HTML GRID (7 KOLOM RATA)
# -------------------------------------------------------------
st.markdown(f"### 🗓️ Bulan {bln_pilihan} {thn_pilihan}")

cal_weeks = calendar.monthcalendar(thn_pilihan, bln_idx)
hari_names_singkat = ["Mgg", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]

html_kalender = "<div class='cal-container'>"

# Baris Header Nama Hari
html_kalender += "<div class='cal-row'>"
for i, h_name in enumerate(hari_names_singkat):
    clr = "#dc2626" if i == 0 else ("#16a34a" if i == 5 else "#334155")
    html_kalender += f"<div class='cal-header-cell' style='color: {clr};'>{h_name}</div>"
html_kalender += "</div>"

# Baris Tanggal
for week in cal_weeks:
    # Geser Minggu ke posisi indeks 0
    adjusted_week = [week[6], week[0], week[1], week[2], week[3], week[4], week[5]]
    
    html_kalender += "<div class='cal-row'>"
    for day in adjusted_week:
        if day == 0:
            html_kalender += "<div class='cal-day-empty'></div>"
        else:
            curr_date = date(thn_pilihan, bln_idx, day)
            jml_ev = len(events_map[curr_date])
            
            # Cek kelas status
            cls_extras = ""
            if jml_ev > 0:
                cls_extras += " cell-booked"
            if curr_date == st.session_state.selected_date:
                cls_extras += " cell-selected"
                
            badge_cls = "badge-red" if jml_ev > 0 else "badge-gray"
            badge_txt = f"{jml_ev} Rombel" if jml_ev > 0 else "Kosong"
            
            # Link interaktif berbasis query parameters agar bisa diklik di Streamlit
            html_kalender += f"""
            <a href="?klik_tgl={curr_date.isoformat()}" target="_self" class="cal-day-cell{cls_extras}">
                <div class="day-num">{day}</div>
                <span class="badge-info {badge_cls}">{badge_txt}</span>
            </a>
            """
    html_kalender += "</div>"

html_kalender += "</div>"
st.markdown(html_kalender, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

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

# Wadah Bubble Rincian
st.markdown("<div class='bubble-container'>", unsafe_allow_html=True)

if events_selected:
    st.markdown(f"<p style='color: #0369a1; font-weight: bold; margin-bottom: 8px;'>Ditemukan {len(events_selected)} jadwal / kegiatan pada tanggal ini:</p>", unsafe_allow_html=True)
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

        st.markdown(f"""
        <div class="event-item">
            <div style="float: right; background-color: {warna_badge}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                {kategori}
            </div>
            <div style="font-size: 15px; font-weight: bold; color: #0284c7; margin-bottom: 3px;">{sekolah}</div>
            <div style="font-size: 12px; color: #475569;">👤 <b>PIC/Kontak:</b> {pic}</div>
            <div style="font-size: 12px; color: #475569;">👥 <b>Jumlah:</b> {jumlah} Orang</div>
            <div style="font-size: 11px; color: #64748b; font-style: italic; margin-top: 3px;">📝 Catatan: {ket}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-bubble">
        <div style="font-size: 20px; margin-bottom: 3px;">🏖️</div>
        <b>Status: KOSONG</b><br>
        Belum ada jadwal rombongan atau bookingan pada tanggal ini.
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
