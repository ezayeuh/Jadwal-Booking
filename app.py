import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Dashboard Booking Kolam Renang",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM STYLING (CSS SANGAT MODERN & CLEAN)
st.markdown("""
<style>
    /* Styling Dasar & Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hero Banner Header */
    .hero-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.2);
    }
    
    /* Stats Cards */
    .stat-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stat-label { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; tracking-wide: 0.05em; }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-top: 4px; }
    
    /* Day Card Container (Kalender 1 Minggu) */
    .day-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        min-height: 280px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .day-box-today {
        background: #f0f9ff;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 12px;
        min-height: 280px;
        box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.15);
    }
    
    /* Header Hari */
    .day-header {
        font-weight: 700;
        font-size: 0.95rem;
        color: #0f172a;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .day-header-today {
        color: #0284c7;
        border-bottom: 2px solid #38bdf8;
    }
    
    /* Card Kunjungan Per-Event */
    .booking-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.2s;
    }
    .booking-card:hover {
        transform: translateY(-2px);
    }
    
    /* Badge Status */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-top: 6px;
    }
    .badge-terkonfirmasi { background: #dcfce7; color: #15803d; }
    .badge-rutin { background: #e0f2fe; color: #0369a1; }
    .badge-dp { background: #fef3c7; color: #b45309; }
    .badge-pending { background: #ffe4e6; color: #be123c; }

    .text-muted { color: #64748b; font-size: 0.78rem; }
    .school-title { font-weight: 700; font-size: 0.88rem; color: #1e293b; line-height: 1.2; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# 3. DATABASE SEMENTARA (SESSION STATE)
if 'booking_list' not in st.session_state:
    st.session_state.booking_list = [
        {
            "NO": 1,
            "TIPE": "Tanggal Spesifik",
            "TANGGAL_DATE": date(2026, 9, 28), # Senin
            "TANGGAL_TEXT": "Senin, 28 Sep 2026",
            "SEKOLAH": "SDN Kedung Halang 5",
            "PIC": "Ade Supian (0815-6390-2017)",
            "JUMLAH": "115 Orang (Kls 4-5)",
            "KETERANGAN": "KKGO Bogor Utara",
            "STATUS": "Terkonfirmasi"
        },
        {
            "NO": 2,
            "TIPE": "Hari Rutin",
            "HARI_RUTIN": ["Selasa", "Rabu"],
            "TANGGAL_DATE": None,
            "TANGGAL_TEXT": "Setiap Selasa & Rabu",
            "SEKOLAH": "Grup Senam Bu Pupu / Bu Cici",
            "PIC": "Bu Pupu (0878-7873-9767)",
            "JUMLAH": "10 Orang / Hydrotherapy",
            "KETERANGAN": "Gaperi",
            "STATUS": "Rutin"
        },
        {
            "NO": 3,
            "TIPE": "Tanggal Spesifik",
            "TANGGAL_DATE": date(2026, 10, 1), # Kamis
            "TANGGAL_TEXT": "Kamis, 01 Okt 2026",
            "SEKOLAH": "TK Islam Al-Azhar",
            "PIC": "Ibu Rahma (0812-9988-7766)",
            "JUMLAH": "45 Siswa + Wali",
            "KETERANGAN": "Fun Swimming",
            "STATUS": "DP Received"
        }
    ]

# 4. SIDEBAR: FORM INPUT KUNJUNGAN
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3144/3144871.png", width=60)
    st.title("Input Booking Baru")
    st.caption("Tambahkan data jadwal kunjungan")
    
    with st.form("form_booking", clear_on_submit=True):
        tipe_kunjungan = st.radio("Tipe Kunjungan:", ["Tanggal Spesifik", "Hari Rutin / Berulang"])
        
        tgl_selected = None
        hari_rutin_selected = []
        tgl_text_display = ""
        
        if tipe_kunjungan == "Tanggal Spesifik":
            tgl_selected = st.date_input("Pilih Tanggal:", value=date.today())
            hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
            bln_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}
            tgl_text_display = f"{hari_map[tgl_selected.weekday()]}, {tgl_selected.day:02d} {bln_map[tgl_selected.month]} {tgl_selected.year}"
        else:
            hari_rutin_selected = st.multiselect(
                "Pilih Hari Rutin:",
                ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                default=["Selasa"]
            )
            catatan_rutin = st.text_input("Catatan Rutin:", placeholder="Misal: Minggu ke-3")
            tgl_text_display = f"Setiap {', '.join(hari_rutin_selected)}"
            if catatan_rutin:
                tgl_text_display += f" ({catatan_rutin})"

        st.markdown("---")
        sekolah_in = st.text_input("Nama Sekolah / Grup*", placeholder="Contoh: SMPN 1 Bogor")
        pic_in = st.text_input("PIC & Kontak (No HP)*", placeholder="Pak Budi (0812xxx)")
        jumlah_in = st.text_input("Jumlah Peserta / Paket", placeholder="80 Orang")
        ket_in = st.text_input("Keterangan", placeholder="Paket Edukasi / Seluncuran")
        status_in = st.selectbox("Status Booking", ["Terkonfirmasi", "Rutin", "DP Received", "Pending"])

        submit_btn = st.form_submit_button("✨ Simpan Booking", use_container_width=True)

        if submit_btn:
            if sekolah_in and pic_in:
                new_id = len(st.session_state.booking_list) + 1
                entry = {
                    "NO": new_id,
                    "TIPE": tipe_kunjungan,
                    "TANGGAL_DATE": tgl_selected if tipe_kunjungan == "Tanggal Spesifik" else None,
                    "HARI_RUTIN": hari_rutin_selected if tipe_kunjungan == "Hari Rutin / Berulang" else [],
                    "TANGGAL_TEXT": tgl_text_display,
                    "SEKOLAH": sekolah_in,
                    "PIC": pic_in,
                    "JUMLAH": jumlah_in,
                    "KETERANGAN": ket_in,
                    "STATUS": status_in
                }
                st.session_state.booking_list.append(entry)
                st.success("✅ Berhasil disimpan!")
                st.rerun()
            else:
                st.error("⚠️ Nama Sekolah & PIC wajib diisi!")

# 5. HERO HEADER
st.markdown("""
<div class="hero-banner">
    <h2 style="margin:0; font-weight:700;">🏊‍♂️ Dashboard Jadwal Kunjungan Waterpark</h2>
    <p style="margin:4px 0 0 0; opacity:0.9; font-size:0.95rem;">Monitoring & manajemen reservasi kolam renang secara mingguan</p>
</div>
""", unsafe_allow_html=True)

# 6. RINGKASAN METRIK (CARDS)
m1, m2, m3, m4 = st.columns(4)
total_data = len(st.session_state.booking_list)
total_ok = len([b for b in st.session_state.booking_list if b['STATUS'] == 'Terkonfirmasi'])
total_rutin = len([b for b in st.session_state.booking_list if b['STATUS'] == 'Rutin'])
total_dp = len([b for b in st.session_state.booking_list if b['STATUS'] in ['Pending', 'DP Received']])

with m1:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Total Booking</div><div class="stat-value">{total_data} <span style="font-size:0.9rem; font-weight:400; color:#64748b;">Grup</span></div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Terkonfirmasi</div><div class="stat-value" style="color:#16a34a;">{total_ok}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Grup Rutin</div><div class="stat-value" style="color:#0284c7;">{total_rutin}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Pending / DP</div><div class="stat-value" style="color:#d97706;">{total_dp}</div></div>', unsafe_allow_html=True)

st.write("")

# 7. FILTER PERIODE MINGGU
c_filter, c_blank = st.columns([2, 2])
with c_filter:
    today = date.today()
    start_of_week_default = today - timedelta(days=today.weekday())
    start_week = st.date_input("🗓️ Pilih Minggu Kunjungan (Mulai Senin):", value=start_of_week_default)

week_days = [start_week + timedelta(days=i) for i in range(7)]
end_week = week_days[-1]
hari_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

st.markdown(f"**Menampilkan Periode:** <span style='color:#0284c7; font-weight:700;'>{start_week.strftime('%d %b %Y')}</span> s/d <span style='color:#0284c7; font-weight:700;'>{end_week.strftime('%d %b %Y')}</span>", unsafe_allow_html=True)
st.write("")

# 8. TAMPILAN KALENDER 1 MINGGU (GRID INTERAKTIF)
st.subheader("📅 Jadwal Mingguan")

cols = st.columns(7)

for idx, day_date in enumerate(week_days):
    day_name = hari_names[idx]
    is_today = (day_date == date.today())
    
    # Filter booking di hari ini
    matching = []
    for b in st.session_state.booking_list:
        if b["TIPE"] == "Tanggal Spesifik" and b["TANGGAL_DATE"] == day_date:
            matching.append(b)
        elif b["TIPE"] == "Hari Rutin / Berulang" and day_name in b.get("HARI_RUTIN", []):
            matching.append(b)
            
    with cols[idx]:
        header_class = "day-header-today" if is_today else "day-header"
        box_class = "day-box-today" if is_today else "day-box"
        today_tag = "<span style='font-size:0.65rem; background:#0284c7; color:white; padding:1px 5px; border-radius:4px;'>HARI INI</span>" if is_today else ""
        
        cards_html = ""
        if matching:
            for mb in matching:
                st_class = "badge-terkonfirmasi" if mb["STATUS"] == "Terkonfirmasi" else ("badge-rutin" if mb["STATUS"] == "Rutin" else "badge-dp")
                cards_html += f"""
                <div class="booking-card">
                    <div class="school-title">{mb['SEKOLAH']}</div>
                    <div class="text-muted">👥 {mb['JUMLAH']}</div>
                    <div class="text-muted">📞 {mb['PIC']}</div>
                    <span class="badge {st_class}">{mb['STATUS']}</span>
                </div>
                """
        else:
            cards_html = "<div class='text-muted' style='text-align:center; margin-top:20px; font-style:italic;'>Kosong</div>"
            
        st.markdown(f"""
        <div class="{box_class}">
            <div class="{header_class}">
                <span>{day_name}</span>
                <span style="font-size:0.8rem; font-weight:500;">{day_date.strftime('%d/%m')}</span>
            </div>
            {today_tag}
            <div style="margin-top:8px;">
                {cards_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# 9. TABEL SEMUA DATA (DETAIL)
st.subheader("📋 Ringkasan Seluruh Data Booking")

df = pd.DataFrame(st.session_state.booking_list)
if not df.empty:
    df_display = df[["NO", "TANGGAL_TEXT", "SEKOLAH", "PIC", "JUMLAH", "KETERANGAN", "STATUS"]].copy()
    df_display.columns = ["No", "Tanggal / Hari", "Sekolah / Grup", "PIC & Kontak", "Jumlah Peserta", "Keterangan", "Status"]
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Export CSV
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data Excel/CSV",
        data=csv,
        file_name=f"jadwal_booking_kolam_{date.today()}.csv",
        mime="text/csv"
    )
