import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
# KONFIGURASI SPREADSHEET
# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1XsYvF0pcBYjRm-h_oPf2jag3OwUFLK43bhRoyE-yh-M/edit"

st.set_page_config(
    page_title="Papan Informasi Jadwal Kunjungan Kolam",
    page_icon="🏊",
    layout="wide"
)

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

st.markdown("""
<style>
    .banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 25px;
    }
    .banner h1 {
        color: white !important;
        font-size: 26px;
        font-weight: 700;
        margin: 0 0 8px 0;
    }
    .banner p {
        color: #e0f2fe;
        margin: 0;
        font-size: 14px;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .metric-title {
        font-size: 11px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: #0f172a;
    }
    .day-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .day-card-today {
        background-color: #f0f9ff;
        border: 2px solid #0284c7;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .today-badge {
        background-color: #0284c7;
        color: white;
        font-size: 10px;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
        margin-top: 4px;
    }
    .event-card {
        background-color: #ffffff;
        border-left: 4px solid #0284c7;
        border-top: 1px solid #e2e8f0;
        border-right: 1px solid #e2e8f0;
        border-bottom: 1px solid #e2e8f0;
        padding: 8px 10px;
        margin-top: 8px;
        border-radius: 6px;
        font-size: 12px;
    }
    .empty-text {
        color: #94a3b8;
        font-size: 12px;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 20px;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

jadwal_data = load_data()

st.markdown("""
<div class="banner">
    <h1>🏊 Papan Informasi Jadwal Kunjungan Kolam</h1>
    <p>Jadwal resmi kunjungan sekolah, grup, dan kegiatan rutin di area kolam renang</p>
</div>
""", unsafe_allow_html=True)

tot_agenda = len(jadwal_data)
tot_sekolah = sum(1 for item in jadwal_data if str(item.get("KATEGORI", "")).lower() == "sekolah")
tot_rutin = sum(1 for item in jadwal_data if str(item.get("TIPE", "")).lower() == "hari rutin / berulang" or str(item.get("KATEGORI", "")).lower() == "kegiatan rutin")

col_m1, col_m2, col_m3 = st.columns(3)

with col_m1:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">TOTAL AGENDA TERDAFTAR</div>
<div class="metric-value">{tot_agenda} <span style="font-size: 14px; font-weight: normal; color: #64748b;">Rombongan</span></div>
</div>
""", unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">KUNJUNGAN SEKOLAH</div>
<div class="metric-value" style="color: #0284c7;">{tot_sekolah}</div>
</div>
""", unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
<div class="metric-card">
<div class="metric-title">KEGIATAN RUTIN</div>
<div class="metric-value" style="color: #16a34a;">{tot_rutin}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_filter, _ = st.columns([1.2, 2])
with col_filter:
    filter_date = st.date_input("🗓️ Tampilkan Jadwal Minggu Dari Tanggal:", value=date.today())

start_of_week = filter_date - timedelta(days=filter_date.weekday())
end_of_week = start_of_week + timedelta(days=6)

periode_str = f"{start_of_week.day} {BULAN_INDO[start_of_week.month]} {start_of_week.year} s/d {end_of_week.day} {BULAN_INDO[end_of_week.month]} {end_of_week.year}"

st.markdown(f"**Periode Tampilan:** <span style='color: #0284c7; font-weight: bold;'>{periode_str}</span>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.subheader("🗓️ Jadwal Kunjungan Minggu Ini")

cols_days = st.columns(7)
hari_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
today_date = date.today()

for idx, col in enumerate(cols_days):
    curr_date = start_of_week + timedelta(days=idx)
    hari_nama = hari_names[idx]
    is_today = (curr_date == today_date)

    events_today = []
    for item in jadwal_data:
        if item.get("TANGGAL_DATE") == curr_date:
            events_today.append(item)
        elif str(item.get("TIPE", "")) == "Hari Rutin / Berulang" or item.get("HARI_RUTIN"):
            rutin_list = item.get("HARI_RUTIN", [])
            if isinstance(rutin_list, list) and hari_nama in rutin_list:
                events_today.append(item)

    card_class = "day-card-today" if is_today else "day-card"
    
    nama_bulan_singkat = BULAN_INDO[curr_date.month][:3]
    tgl_format_jelas = f"{curr_date.day:02d} {nama_bulan_singkat}"

    with col:
        html_str = f"""<div class="{card_class}">"""
        
        html_str += f"""<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
<b style="font-size: 16px;">{hari_nama}</b> 
<span style="background-color: #f1f5f9; color: #475569; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold; border: 1px solid #e2e8f0;">{tgl_format_jelas}</span>
</div>"""
        
        if is_today:
            html_str += "<div><span class='today-badge'>HARI INI</span></div>"
            
        html_str += "<hr style='margin: 8px 0; border: none; border-top: 1px solid #e2e8f0;'>"

        if events_today:
            for ev in events_today:
                sekolah = ev.get("SEKOLAH") if pd.notna(ev.get("SEKOLAH")) and ev.get("SEKOLAH") else "-"
                pic = ev.get("PIC") if pd.notna(ev.get("PIC")) and ev.get("PIC") else "-"
                
                jumlah_raw = ev.get("JUMLAH")
                jumlah = str(jumlah_raw) if pd.notna(jumlah_raw) and jumlah_raw else "-"
                if jumlah.endswith(".0"):
                    jumlah = jumlah.replace(".0", "")

                html_str += f"""<div class="event-card">
<strong style="color: #0284c7; font-size: 14px;">{sekolah}</strong><br>
<span style="color: #475569; font-size: 12px;">👤 {pic}</span><br>
<span style="color: #475569; font-size: 12px;">👥 {jumlah} Orang</span>
</div>"""
        else:
            html_str += "<div class='empty-text'>Tidak Ada Kunjungan</div>"

        html_str += "</div>"

        st.markdown(html_str, unsafe_allow_html=True)
