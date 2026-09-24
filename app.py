import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Jadwal Kunjungan Kolam Renang / Waterpark",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CUSTOM STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.2);
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stat-label { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-top: 4px; }
    
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
    
    .visit-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .school-title { font-weight: 700; font-size: 0.9rem; color: #1e293b; line-height: 1.2; margin-bottom: 4px; }
    .text-muted { color: #64748b; font-size: 0.78rem; margin-bottom: 2px; }
    
    .cat-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.68rem;
        font-weight: 700;
        margin-top: 6px;
    }
    .cat-sekolah { background: #e0f2fe; color: #0369a1; }
    .cat-rutin { background: #dcfce7; color: #15803d; }
    .cat-umum { background: #fef3c7; color: #b45309; }
</style>
""", unsafe_allow_html=True)

# 3. DATABASE SEMENTARA (SESSION STATE)
if 'jadwal_kunjungan' not in st.session_state:
    st.session_state.jadwal_kunjungan = [
        {
            "NO": 1,
            "TIPE": "Tanggal Spesifik",
            "TANGGAL_DATE": date(2026, 9, 28), # Senin
            "TANGGAL_TEXT": "Senin, 28 Sep 2026",
            "SEKOLAH": "SDN Kedung Halang 5",
            "PIC": "Ade Supian (0815-6390-2017)",
            "JUMLAH": "115 Orang (Kls 4-5)",
            "KETERANGAN": "KKGO Bogor Utara",
            "KATEGORI": "Sekolah"
        },
        {
            "NO": 2,
            "TIPE": "Hari Rutin / Berulang",
            "HARI_RUTIN": ["Selasa", "Rabu"],
            "TANGGAL_DATE": None,
            "TANGGAL_TEXT": "Setiap Selasa & Rabu",
            "SEKOLAH": "Grup Senam Bu Pupu / Bu Cici",
            "PIC": "Bu Pupu (0878-7873-9767)",
            "JUMLAH": "10 Orang / Hydrotherapy",
            "KETERANGAN": "Gaperi",
            "KATEGORI": "Kegiatan Rutin"
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
            "KATEGORI": "Sekolah"
        }
    ]

if 'temp_dates' not in st.session_state:
    st.session_state.temp_dates = []

# 4. SIDEBAR: AKSES STAF & FORM INPUT
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3144/3144871.png", width=50)
    st.title("Akses Portal")
    
    is_staff = st.checkbox("🔒 Login Mode Staf (Untuk Input)")
    
    if is_staff:
        password = st.text_input("Password Staf:", type="password", value="staf123")
        if password == "staf123":
            st.success("Akses Staf Aktif")
            st.markdown("---")
            st.subheader("➕ Input Kunjungan Baru")
            
            tipe_kunjungan = st.radio("Metode Tanggal:", ["Pilih Bebas Beberapa Tanggal", "Hari Rutin / Berulang"])
            
            selected_dates_final = []
            hari_rutin_selected = []
            
            hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
            bln_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}

            if tipe_kunjungan == "Pilih Bebas Beberapa Tanggal":
                st.caption("Pilih tanggal satu per satu lalu klik 'Tambah Tanggal Ini':")
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    picker_date = st.date_input("Pilih Tanggal:", value=date.today(), key="picker_date")
                with col_d2:
                    st.write("")
                    st.write("")
                    if st.button("➕ Tambah"):
                        if picker_date not in st.session_state.temp_dates:
                            st.session_state.temp_dates.append(picker_date)
                            st.session_state.temp_dates.sort()

                if st.session_state.temp_dates:
                    st.write("**Daftar Tanggal Terpilih:**")
                    for d_item in st.session_state.temp_dates:
                        t_label = f"{hari_map[d_item.weekday()]}, {d_item.day:02d} {bln_map[d_item.month]} {d_item.year}"
                        st.markdown(f"- 🗓️ `{t_label}`")
                    if st.button("🗑️ Hapus Semua Pilihan Tanggal"):
                        st.session_state.temp_dates = []
                        st.rerun()
                
                selected_dates_final = st.session_state.temp_dates
            else:
                hari_rutin_selected = st.multiselect(
                    "Pilih Hari Rutin:",
                    ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                    default=["Selasa"]
                )
                catatan_rutin = st.text_input("Keterangan Rutin:", placeholder="Misal: Minggu ke-3")

            st.markdown("---")
            with st.form("form_kunjungan_staf", clear_on_submit=True):
                sekolah_in = st.text_input("Nama Sekolah / Grup*", placeholder="SDN 01 Bogor")
                pic_in = st.text_input("PIC & Kontak*", placeholder="Pak Budi (0812xxx)")
                jumlah_in = st.text_input("Jumlah Peserta", placeholder="80 Orang")
                ket_in = st.text_input("Keterangan", placeholder="Paket Edukasi")
                kategori_in = st.selectbox("Kategori", ["Sekolah", "Kegiatan Rutin", "Umum / Komunitas"])

                submit_btn = st.form_submit_button("➕ Simpan Ke Jadwal", use_container_width=True)

                if submit_btn:
                    if sekolah_in and pic_in:
                        if tipe_kunjungan == "Pilih Bebas Beberapa Tanggal":
                            if not selected_dates_final:
                                st.error("⚠️ Pilih minimal 1 tanggal terlebih dahulu!")
                            else:
                                for d in selected_dates_final:
                                    tgl_text = f"{hari_map[d.weekday()]}, {d.day:02d} {bln_map[d.month]} {d.year}"
                                    new_id = len(st.session_state.jadwal_kunjungan) + 1
                                    entry = {
                                        "NO": new_id,
                                        "TIPE": "Tanggal Spesifik",
                                        "TANGGAL_DATE": d,
                                        "HARI_RUTIN": [],
                                        "TANGGAL_TEXT": tgl_text,
                                        "SEKOLAH": sekolah_in,
                                        "PIC": pic_in,
                                        "JUMLAH": jumlah_in,
                                        "KETERANGAN": ket_in,
                                        "KATEGORI": kategori_in
                                    }
                                    st.session_state.jadwal_kunjungan.append(entry)
                                st.session_state.temp_dates = []
                                st.success("✅ Jadwal kunjungan berhasil ditambahkan!")
                                st.rerun()
                        else:
                            tgl_text = f"Setiap {', '.join(hari_rutin_selected)}"
                            if catatan_rutin:
                                tgl_text += f" ({catatan_rutin})"
                            new_id = len(st.session_state.jadwal_kunjungan) + 1
                            entry = {
                                "NO": new_id,
                                "TIPE": "Hari Rutin / Berulang",
                                "TANGGAL_DATE": None,
                                "HARI_RUTIN": hari_rutin_selected,
                                "TANGGAL_TEXT": tgl_text,
                                "SEKOLAH": sekolah_in,
                                "PIC": pic_in,
                                "JUMLAH": jumlah_in,
                                "KETERANGAN": ket_in,
                                "KATEGORI": kategori_in
                            }
                            st.session_state.jadwal_kunjungan.append(entry)
                            st.success("✅ Jadwal kunjungan berhasil ditambahkan!")
                            st.rerun()
                    else:
                        st.error("⚠️ Nama Sekolah/Grup & PIC wajib diisi!")
        else:
            st.error("Password Salah!")
    else:
        st.info("ℹ️ Tampilan Pengunjung (Read-Only). Centang 'Login Mode Staf' di atas untuk menginput data kunjungan.")

# 5. HERO HEADER
st.markdown("""
<div class="hero-banner">
    <h2 style="margin:0; font-weight:700;">🏊‍♂️ Papan Informasi Jadwal Kunjungan Kolam</h2>
    <p style="margin:4px 0 0 0; opacity:0.9; font-size:0.95rem;">Jadwal resmi kunjungan sekolah, grup, dan kegiatan rutin di area kolam renang</p>
</div>
""", unsafe_allow_html=True)

# 6. RINGKASAN METRIK
m1, m2, m3 = st.columns(3)
total_kunjungan = len(st.session_state.jadwal_kunjungan)
total_sekolah = len([b for b in st.session_state.jadwal_kunjungan if b['KATEGORI'] == 'Sekolah'])
total_rutin = len([b for b in st.session_state.jadwal_kunjungan if b['KATEGORI'] == 'Kegiatan Rutin'])

with m1:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Total Agenda Terdaftar</div><div class="stat-value">{total_kunjungan} <span style="font-size:0.85rem; color:#64748b; font-weight:400;">Rombongan</span></div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Kunjungan Sekolah</div><div class="stat-value" style="color:#0284c7;">{total_sekolah}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Kegiatan Rutin</div><div class="stat-value" style="color:#16a34a;">{total_rutin}</div></div>', unsafe_allow_html=True)

st.write("")

# 7. FILTER PERIODE MINGGU (Sistem Otomatis Menghitung Hari Senin)
c_filter, c_blank = st.columns([2, 2])
with c_filter:
    input_date = st.date_input("🗓️ Tampilkan Jadwal Minggu Dari Tanggal:", value=date.today())
    # Menghitung otomatis hari Senin dari tanggal yang dipilih
    start_week = input_date - timedelta(days=input_date.weekday())

week_days = [start_week + timedelta(days=i) for i in range(7)]
end_week = week_days[-1]
hari_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

st.markdown(f"**Periode Tampilan:** <span style='color:#0284c7; font-weight:700;'>{start_week.strftime('%d %b %Y')}</span> s/d <span style='color:#0284c7; font-weight:700;'>{end_week.strftime('%d %b %Y')}</span>", unsafe_allow_html=True)
st.write("")

# 8. TAMPILAN KALENDER 1 MINGGU
st.subheader("📅 Jadwal Kunjungan Minggu Ini")

cols = st.columns(7)

for idx, day_date in enumerate(week_days):
    day_name = hari_names[idx]
    is_today = (day_date == date.today())
    
    matching = []
    for b in st.session_state.jadwal_kunjungan:
        if b["TIPE"] == "Tanggal Spesifik" and b["TANGGAL_DATE"] == day_date:
            matching.append(b)
        elif b["TIPE"] == "Hari Rutin / Berulang" and day_name in b.get("HARI_RUTIN", []):
            matching.append(b)
            
    with cols[idx]:
        header_class = "day-header-today" if is_today else "day-header"
        box_class = "day-box-today" if is_today else "day-box"
        today_tag = '<span style="font-size:0.65rem; background:#0284c7; color:white; padding:1px 5px; border-radius:4px;">HARI INI</span>' if is_today else ""
        
        cards_html = ""
        if matching:
            for mb in matching:
                badge_style = "cat-sekolah" if mb["KATEGORI"] == "Sekolah" else ("cat-rutin" if mb["KATEGORI"] == "Kegiatan Rutin" else "cat-umum")
                cards_html += f"""<div class="visit-card">
                    <div class="school-title">{mb['SEKOLAH']}</div>
                    <div class="text-muted">👥 {mb['JUMLAH']}</div>
                    <div class="text-muted">📞 {mb['PIC']}</div>
                    <div class="text-muted">📌 {mb['KETERANGAN']}</div>
                    <span class="cat-badge {badge_style}">{mb['KATEGORI']}</span>
                </div>"""
        else:
            cards_html = '<div class="text-muted" style="text-align:center; margin-top:20px; font-style:italic;">Tidak Ada Kunjungan</div>'
            
        full_box_html = f"""
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
        """
        st.html(full_box_html)

st.divider()

# 9. TABEL RINCIAN KUNJUNGAN
st.subheader("📋 Rincian Lengkap Seluruh Jadwal")

df = pd.DataFrame(st.session_state.jadwal_kunjungan)
if not df.empty:
    df_display = df[["NO", "TANGGAL_TEXT", "SEKOLAH", "PIC", "JUMLAH", "KETERANGAN", "KATEGORI"]].copy()
    df_display.columns = ["No", "Hari / Tanggal", "Sekolah / Instansi", "PIC & Kontak", "Jumlah Peserta", "Keterangan", "Kategori"]
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # Export CSV
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Rekap Jadwal (CSV)",
        data=csv,
        file_name=f"jadwal_kunjungan_kolam_{date.today()}.csv",
        mime="text/csv"
    )
