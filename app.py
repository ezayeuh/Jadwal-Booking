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

# Inisialisasi State untuk menyimpan tanggal yang diklik
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
                    hari_str = HARI_INDO[parsed_date.weekday()]
                    bln_str = BULAN_INDO[parsed_date.month]
                    item["TANGGAL_TEXT"] = f"{hari_str}, {parsed_date.day:02d} {bln_str} {parsed_date.year}"
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

# CSS KHUSUS UNTUK MEMPERBAIKI TAMPILAN DI HP
st.markdown("""
<style>
    .banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    .banner h1 { color: white !important; font-size: 22px; font-weight: 700; margin: 0 0 5px 0; }
    .banner p { color: #e0f2fe; margin: 0; font-size: 13px; }
    
    /* =========================================================
       MAGIC CSS: MEMAKSA KOLOM STREAMLIT MENYAMPING DI HP 
       ========================================================= */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important; /* Mencegah kolom turun ke bawah */
        gap: 2px !important; /* Jarak antar kolom diperkecil */
    }
    [data-testid="column"] {
        width: 14.28% !important; /* 100% dibagi 7 hari */
        min-width: 0 !important;
        flex: 1 1 14.28% !important;
        padding: 0 2px !important;
    }
    
    /* Menyesuaikan ukuran tombol agar muat dan rapi di HP */
    .stButton > button {
        padding: 0px !important;
        min-height: 45px !important;
        font-size: 13px !important;
        width: 100% !important;
        font-weight: bold !important;
    }
    
    /* Mempercantik Header Hari (Sen, Sel, dll) */
    .cal-header {
        text-align: center;
        font-weight: bold;
        color: #334155;
        padding-bottom: 5px;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 5px;
        font-size: 13px;
    }

    /* Styling Rincian Jadwal */
    .event-card {
        background-color: #ffffff;
        border-left: 5px solid #0284c7;
        border: 1px solid #e2e8f0;
        border-left-width: 5px;
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .event-title { color: #0284c7; font-size: 16px; font-weight: bold; margin-bottom: 4px;}
    .event-detail { color: #475569; font-size: 13px; margin-bottom: 2px;}
    .empty-state {
        background-color: #f8fafc;
        border: 2px dashed #cbd5e1;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        color: #64748b;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

jadwal_data = load_data()

st.markdown("""
<div class="banner">
    <h1>📅 Kalender Kunjungan</h1>
    <p>Pilih tanggal pada kalender di bawah untuk melihat rincian.</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# FILTER BULAN & TAHUN
# -------------------------------------------------------------
col_bln, col_thn = st.columns([1, 1])
today_dt = date.today()

with col_bln:
    bln_pilihan = st.selectbox("Bulan:", list(BULAN_INDO.values()), index=today_dt.month - 1)
with col_thn:
    thn_pilihan = st.selectbox("Tahun:", range(2024, 2030), index=range(2024, 2030).index(today_dt.year))

bln_idx = list(BULAN_INDO.values()).index(bln_pilihan) + 1

# -------------------------------------------------------------
# PERSIAPAN DATA EVENT PER TANGGAL
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
# RENDER KALENDER INTERAKTIF (VERSI GRID HP)
# -------------------------------------------------------------
st.markdown(f"#### 🗓️ {bln_pilihan} {thn_pilihan}")

cal_weeks = calendar.monthcalendar(thn_pilihan, bln_idx)
# NAMA HARI DISINGKAT AGAR MUAT DI HP
hari_names_singkat = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]

# Header Hari
cols_header = st.columns(7)
for i, col in enumerate(cols_header):
    col.markdown(f"<div class='cal-header'>{hari_names_singkat[i]}</div>", unsafe_allow_html=True)

# Grid Kalender
for week in cal_weeks:
    cols_days = st.columns(7)
    for i, day in enumerate(week):
        with cols_days[i]:
            if day == 0:
                # Kotak kosong untuk menyeimbangkan grid
                st.markdown("<div style='min-height: 45px;'></div>", unsafe_allow_html=True)
            else:
                curr_date = date(thn_pilihan, bln_idx, day)
                jumlah_event = len(events_map[curr_date])
                
                # Warna Merah/Aksen jika ada bookingan, warna standar jika kosong
                btn_type = "primary" if jumlah_event > 0 else "secondary"
                
                if st.button(str(day), key=f"btn_{curr_date}", type=btn_type, use_container_width=True):
                    st.session_state.selected_date = curr_date

st.markdown("<hr style='margin: 20px 0; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# -------------------------------------------------------------
# RENDER DETAIL JADWAL YANG DIKLIK
# -------------------------------------------------------------
sel_date = st.session_state.selected_date
sel_hari_nama = HARI_INDO[sel_date.weekday()]
sel_bln_nama = BULAN_INDO[sel_date.month]
tgl_format_panjang = f"{sel_hari_nama}, {sel_date.day} {sel_bln_nama} {sel_date.year}"

st.markdown(f"#### 📌 Rincian: <span style='color: #0284c7;'>{tgl_format_panjang}</span>", unsafe_allow_html=True)

events_selected = []
for item in jadwal_data:
    tipe_str = str(item.get("TIPE", "")).lower()
    
    if item.get("TANGGAL_DATE") == sel_date:
        events_selected.append(item)
    elif tipe_str == "hari rutin / berulang" or item.get("HARI_RUTIN"):
        rutin_list = item.get("HARI_RUTIN", [])
        if isinstance(rutin_list, list) and sel_hari_nama in rutin_list:
            events_selected.append(item)

if events_selected:
    for ev in events_selected:
        sekolah = ev.get("SEKOLAH", "-")
        pic = ev.get("PIC", "-")
        ket = ev.get("KETERANGAN", "-")
        kategori = ev.get("KATEGORI", "Sekolah")
        
        jumlah_raw = ev.get("JUMLAH")
        jumlah = str(jumlah_raw) if pd.notna(jumlah_raw) and jumlah_raw else "-"
        if jumlah.endswith(".0"):
            jumlah = jumlah.replace(".0", "")
            
        warna_kategori = "#16a34a" if kategori.lower() == "kegiatan rutin" else "#0284c7"

        st.markdown(f"""
        <div class="event-card">
            <div style="float: right; background-color: {warna_kategori}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">
                {kategori}
            </div>
            <div class="event-title">{sekolah}</div>
            <div class="event-detail">👤 <b>PIC:</b> {pic}</div>
            <div class="event-detail">👥 <b>Jumlah:</b> {jumlah} Orang</div>
            <div class="event-detail" style="margin-top: 5px; color: #64748b; font-style: italic;">📝 Catatan: {ket}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="empty-state">
        <div style="font-size: 24px; margin-bottom: 5px;">🏖️</div>
        Kosong / Tidak ada rombongan.
    </div>
    """, unsafe_allow_html=True)
