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

# CSS UNTUK TAMPILAN GRID KOTAK KALENDER & BUBBLE POP-UP
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

    /* Styling Kotak Kalender Grid Header */
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 6px;
        margin-bottom: 10px;
    }
    .cal-header-cell {
        text-align: center;
        font-weight: bold;
        padding: 8px 0;
        font-size: 13px;
    }

    /* Styling Bubble Pop-up Rincian */
    .bubble-container {
        background: #ffffff;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.15);
        margin-top: 15px;
    }
    .event-item {
        background-color: #f8fafc;
        border-left: 4px solid #0284c7;
        border: 1px solid #e2e8f0;
        border-left-width: 4px;
        padding: 10px 14px;
        margin-top: 10px;
        border-radius: 6px;
    }
    .empty-bubble {
        background-color: #f1f5f9;
        border: 2px dashed #cbd5e1;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        color: #64748b;
    }
</style>
""", unsafe_allow_html=True)

jadwal_data = load_data()

st.markdown("""
<div class="banner">
    <h1>📅 Kalender Jadwal Kunjungan Kolam</h1>
    <p>Pilih tanggal pada kotak kalender di bawah untuk melihat rincian status bookingan pada bubble informasi.</p>
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
# RENDER VISUAL TEMPLATE KALENDER GRID (MINGGU - SABTU)
# -------------------------------------------------------------
st.markdown(f"### 🗓️ Kalender Bulan {bln_pilihan} {thn_pilihan}")

cal_weeks = calendar.monthcalendar(thn_pilihan, bln_idx)
hari_names_singkat = ["Mgg", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]

# Header Hari (Minggu merah, Jumat hijau, lainnya abu gelap)
header_html = "<div class='cal-grid'>"
for i, h_name in enumerate(hari_names_singkat):
    color_txt = "#dc2626" if i == 0 else ("#16a34a" if i == 5 else "#334155")
    header_html += f"<div class='cal-header-cell' style='color: {color_txt};'>{h_name}</div>"
header_html += "</div>"
st.markdown(header_html, unsafe_allow_html=True)

# Render Grid Kotak Tanggal dengan Kunci Unik Berbasis Minggu & Tanggal
for w_idx, week in enumerate(cal_weeks):
    # Atur agar Minggu di awal (indeks 6 dipindah ke depan)
    adjusted_week = [week[6], week[0], week[1], week[2], week[3], week[4], week[5]]
    
    cols = st.columns(7)
    for i, day in enumerate(adjusted_week):
        with cols[i]:
            if day == 0:
                st.markdown("<div style='min-height: 65px;'></div>", unsafe_allow_html=True)
            else:
                curr_date = date(thn_pilihan, bln_idx, day)
                jumlah_event = len(events_map[curr_date])
                
                # Mengatur tipe tombol (primary jika ada booking, secondary jika kosong)
                btn_type = "primary" if jumlah_event > 0 else "secondary"
                btn_label = f"{day}\n({jumlah_event} Rombel)" if jumlah_event > 0 else f"{day}\n(Kosong)"
                
                # Kunci unik mutlak menggabungkan minggu dan tanggal lengkap
                unique_key = f"cal_w{w_idx}_d{curr_date.isoformat()}"
                
                if st.button(btn_label, key=unique_key, type=btn_type, use_container_width=True):
                    st.session_state.selected_date = curr_date
                    st.rerun()

st.markdown("<hr style='margin: 25px 0; border: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# -------------------------------------------------------------
# BUBBLE POP-UP INFORMASI / RINCIAN TANGGAL TERPILIH
# -------------------------------------------------------------
sel_date = st.session_state.selected_date
sel_hari_nama = HARI_INDO[sel_date.weekday()]
sel_bln_nama = BULAN_INDO[sel_date.month]
tgl_format_panjang = f"{sel_hari_nama}, {sel_date.day} {sel_bln_nama} {sel_date.year}"

st.markdown(f"#### 💬 Bubble Rincian Jadwal: <span style='color: #0284c7;'>{tgl_format_panjang}</span>", unsafe_allow_html=True)

events_selected = []
for item in jadwal_data:
    tipe_str = str(item.get("TIPE", "")).lower()
    
    if item.get("TANGGAL_DATE") == sel_date:
        events_selected.append(item)
    elif tipe_str == "hari rutin / berulang" or item.get("HARI_RUTIN"):
        rutin_list = item.get("HARI_RUTIN", [])
        if isinstance(rutin_list, list) and sel_hari_nama in rutin_list:
            events_selected.append(item)

# Kotak Bubble
st.markdown("<div class='bubble-container'>", unsafe_allow_html=True)

if events_selected:
    st.markdown(f"<p style='color: #0369a1; font-weight: bold; margin-bottom: 10px;'>Ditemukan {len(events_selected)} agenda/bookingan pada tanggal ini:</p>", unsafe_allow_html=True)
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
            <div style="font-size: 16px; font-weight: bold; color: #0284c7; margin-bottom: 4px;">{sekolah}</div>
            <div style="font-size: 13px; color: #475569;">👤 <b>PIC:</b> {pic}</div>
            <div style="font-size: 13px; color: #475569;">👥 <b>Jumlah:</b> {jumlah} Orang</div>
            <div style="font-size: 12px; color: #64748b; font-style: italic; margin-top: 4px;">📝 Catatan: {ket}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-bubble">
        <div style="font-size: 24px; margin-bottom: 5px;">🏖️</div>
        <b>Status: KOSONG / TERSEDIA</b><br>
        Belum ada agenda atau rombongan booking pada tanggal ini.
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
