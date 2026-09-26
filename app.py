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

# Tangkap klik tanggal dari tabel kalender HTML secara instan
query_params = st.query_params
if "pilih_tgl" in query_params:
    try:
        parsed_tgl = date.fromisoformat(str(query_params["pilih_tgl"]))
        if st.session_state.selected_date != parsed_tgl:
            st.session_state.selected_date = parsed_tgl
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

# CSS Tabel Kalender Murni 100% Anti-Turun ke Bawah di HP
st.markdown("""
<style>
    .banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white; padding: 15px 20px; border-radius: 12px; margin-bottom: 15px;
    }
    .banner h1 { color: white !important; font-size: 18px; font-weight: 700; margin: 0 0 3px 0; }
    .banner p { color: #e0f2fe; margin: 0; font-size: 11px; }

    /* Desain Tabel Kalender Kotak Murni */
    .kalender-container {
        width: 100%;
        overflow-x: auto;
        background: #ffffff;
        border-radius: 10px;
        padding: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #cbd5e1;
    }
    .kalender-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
    }
    .kalender-table th {
        color: #334155;
        font-size: 11px;
        padding: 6px 0;
        text-align: center;
        font-weight: bold;
        width: 14.28%;
        background-color: #f1f5f9;
        border-bottom: 1px solid #cbd5e1;
    }
    .kalender-table td {
        width: 14.28%;
        height: 62px;
        border: 1px solid #e2e8f0;
        padding: 1px;
        vertical-align: top;
        text-align: center;
        background-color: #f8fafc;
    }
    .kalender-table td.empty-cell {
        background-color: #ffffff;
    }
    .kalender-table a {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        text-decoration: none !important;
        padding: 3px;
        box-sizing: border-box;
        border-radius: 4px;
    }
    .kalender-table a:hover {
        background-color: #e0f2fe;
    }
    .cell-date {
        font-size: 12px;
        font-weight: bold;
        color: #1e293b;
    }
    .cell-badge {
        font-size: 7px;
        padding: 2px 1px;
        border-radius: 3px;
        font-weight: bold;
        text-align: center;
    }
    
    .badge-booked { background-color: #fee2e2; color: #dc2626; border: 1px solid #f87171; }
    .cell-booked-bg { background-color: #fff5f5 !important; }
    .badge-empty { background-color: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }
    
    .selected-box {
        background-color: #bae6fd !important;
        border: 2px solid #0284c7 !important;
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
    <p>Sentuh kotak tanggal di kalender bawah untuk melihat rincian jadwal.</p>
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

# Pemetaan Event per Tanggal
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

# RENDER KELOMPOK TABEL HTML KALENDER MURNI (DIJAMIN 7 KOLOM SEJAJAR DI HP)
html_table = "<div class='kalender-container'><table class='kalender-table'><thead><tr>"
for i, h_name in enumerate(hari_names_singkat):
    c_color = "color: #dc2626;" if i == 0 else ("color: #16a34a;" if i == 5 else "")
    html_table += f"<th style='{c_color}'>{h_name}</th>"
html_table += "</tr></thead><tbody>"

for week in raw_weeks:
    html_table += "<tr>"
    for day in week:
        if day == 0:
            html_table += "<td class='empty-cell'></td>"
        else:
            curr_date = date(thn_pilihan, bln_idx, day)
            jml_ev = len(events_map[curr_date])
            is_sel = (curr_date == st.session_state.selected_date)
            
            td_classes = []
            if jml_ev > 0:
                td_classes.append("cell-booked-bg")
            if is_sel:
                td_classes.append("selected-box")
            
            td_class_str = f" class='{' '.join(td_classes)}'" if td_classes else ""
            
            badge_cls = "badge-booked" if jml_ev > 0 else "badge-empty"
            badge_txt = f"{jml_ev} Rombel" if jml_ev > 0 else "Kosong"
            
            html_table += f"""
            <td{td_class_str}>
                <a href="?pilih_tgl={curr_date.isoformat()}" target="_self">
                    <span class="cell-date">{day}</span>
                    <span class="cell-badge {badge_cls}">{badge_txt}</span>
                </a>
            </td>
            """
    html_table += "</tr>"

html_table += "</tbody></table></div>"

st.markdown(html_table, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# BUBBLE RINCIAN JADWAL TANGGAL TERPILIH
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
