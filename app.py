import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1XsYvF0pcBYjRm-h_oPf2jag3OwUFLK43bhRoyE-yh-M/edit"

st.set_page_config(
    page_title="Papan Informasi Jadwal Kunjungan",
    page_icon="📅",
    layout="wide"
)

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
                    item["TANGGAL_DATE"] = date.fromisoformat(str(tgl_raw).split(" ")[0])
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
        st.error(f"Gagal memuat data: {e}")
        return []

# CSS Grid Murni Tanpa Pecah di HP
st.markdown("""
<style>
    .banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;
    }
    .banner h1 { color: white !important; font-size: 18px; font-weight: 700; margin: 0 0 3px 0; }
    .banner p { color: #e0f2fe; margin: 0; font-size: 11px; }

    /* Memaksa kontainer kolom Streamlit jadi Grid 7 Kolom Sejati di Mobile */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    [data-testid="column"] {
        flex: 1 1 14.28% !important;
        min-width: 0 !important;
        width: 14.28% !important;
        padding: 0px !important;
    }
    
    /* Tombol Kalender Compact */
    .stButton button {
        width: 100% !important;
        height: 52px !important;
        border-radius: 4px !important;
        font-size: 9px !important;
        padding: 0px !important;
        text-align: center !important;
        line-height: 1.1 !important;
        background-color: #f8fafc !important;
        border: 1px solid #cbd5e1 !important;
        color: #1e293b !important;
    }
    .stButton button:hover {
        background-color: #e0f2fe !important;
        border-color: #0284c7 !important;
    }

    .bubble-container {
        background: #ffffff; border: 2px solid #0284c7; border-radius: 12px;
        padding: 15px; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.15); margin-top: 15px;
    }
    .event-item {
        background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #0284c7;
        padding: 10px 12px; margin-top: 8px; border-radius: 6px;
    }
    .empty-bubble {
        background-color: #f1f5f9; border: 2px dashed #cbd5e1; padding: 12px;
        text-align: center; border-radius: 8px; color: #64748b; font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="banner">
    <h1>📅 Kalender Jadwal Kunjungan Kolam</h1>
    <p>Sentuh tombol tanggal di bawah untuk melihat rincian jadwal secara instan.</p>
</div>
""", unsafe_allow_html=True)

jadwal_data = load_data()

col_b1, col_b2 = st.columns(2)
today_dt = date.today()

with col_b1:
    bln_pilihan = st.selectbox("Pilih Bulan:", list(BULAN_INDO.values()), index=today_dt.month - 1)
with col_b2:
    thn_pilihan = st.selectbox("Pilih Tahun:", range(2024, 2030), index=range(2024, 2030).index(today_dt.year))

bln_idx = list(BULAN_INDO.values()).index(bln_pilihan) + 1

# Pemetaan Event
jml_hari_bulan = calendar.monthrange(thn_pilihan, bln_idx)[1]
events_map = {date(thn_pilihan, bln_idx, d): [] for d in range(1, jml_hari_bulan + 1)}

for item in jadwal_data:
    tipe_str = str(item.get("TIPE", "")).lower()
    tgl_item = item.get("TANGGAL_DATE")
    
    if tipe_str == "hari rutin / berulang" or item.get("HARI_RUTIN"):
        rutin_list = item.get("HARI_RUTIN", [])
        if isinstance(rutin_list, list):
            for d in events_map.keys():
                if HARI_INDO[d.weekday()] in rutin_list:
                    events_map[d].append(item)
    elif tgl_item and isinstance(tgl_item, date):
        if tgl_item.month == bln_idx and tgl_item.year == thn_pilihan:
            if tgl_item in events_map:
                events_map[tgl_item].append(item)

st.markdown(f"### 🗓️ Bulan {bln_pilihan} {thn_pilihan}")

calendar.setfirstweekday(calendar.SUNDAY)
raw_weeks = calendar.monthcalendar(thn_pilihan, bln_idx)
hari_names_singkat = ["Mgg", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"]

# Header Hari
cols_hdr = st.columns(7)
for i, h_name in enumerate(hari_names_singkat):
    c_color = "#dc2626" if i == 0 else ("#16a34a" if i == 5 else "#334155")
    with cols_hdr[i]:
        st.markdown(f"<p style='text-align: center; font-weight: bold; color: {c_color}; margin-bottom: 2px; font-size: 11px;'>{h_name}</p>", unsafe_allow_html=True)

# Render Tombol Kalender Baris demi Baris
for week_idx, week in enumerate(raw_weeks):
    cols = st.columns(7)
    for day_idx, day in enumerate(week):
        with cols[day_idx]:
            if day == 0:
                st.markdown("<div style='height: 52px;'></div>", unsafe_allow_html=True)
            else:
                curr_date = date(thn_pilihan, bln_idx, day)
                jml_ev = len(events_map[curr_date])
                
                if jml_ev > 0:
                    btn_label = f"{day}\n🔴{jml_ev} Rmb"
                else:
                    btn_label = f"{day}\nKosong"
                
                # Tombol asli Streamlit dengan session state langsung (tanpa URL query param yang bikin bug)
                if st.button(btn_label, key=f"btn_tgl_{week_idx}_{day_idx}_{day}"):
                    st.session_state.selected_date = curr_date

st.markdown("<br>", unsafe_allow_html=True)

# Bagian Detail Rincian Tanggal Terpilih
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
            <div style="font-size: 14px; font-weight: bold; color: #0284c7; margin-bottom: 2px;">{sekolah}</div>
            <div style="font-size: 12px; color: #475569;">👤 <b>PIC/Kontak:</b> {pic}</div>
            <div style="font-size: 12px; color: #475569;">👥 <b>Jumlah:</b> {jumlah} Orang</div>
            <div style="font-size: 11px; color: #64748b; font-style: italic; margin-top: 2px;">📝 Catatan: {ket}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty-bubble">
        <div style="font-size: 18px; margin-bottom: 2px;">🏖️</div>
        <b>Status: KOSONG</b><br>
        Belum ada jadwal rombongan atau bookingan pada tanggal ini.
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
