import streamlit as st
import pandas as pd
from datetime import date

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Jadwal Booking Kolam Renang",
    page_icon="🏊‍♂️",
    layout="wide"
)

# Custom Styling CSS singkat
st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# 2. Inisialisasi Data Default (Menggunakan Session State)
if 'booking_data' not in st.session_state:
    initial_data = [
        {
            "NO": 1,
            "TANGGAL": "Selasa, 9 Juni 2026",
            "SEKOLAH / GRUP": "SDN KEDUNG HALANG 5",
            "PIC & KONTAK": "Ade Supian (0815-6390-2017)",
            "JUMLAH PESERTA": "115 Orang (Kls 4-5)",
            "KETERANGAN": "KKGO BGR UTARA",
            "STATUS": "Terkonfirmasi"
        },
        {
            "NO": 2,
            "TANGGAL": "Setiap Selasa & Rabu",
            "SEKOLAH / GRUP": "Group Senam Bu Pupu / Bu Cici Gaperi",
            "PIC & KONTAK": "Bu Pupu (0878-7873-9767)",
            "JUMLAH PESERTA": "1 Team 10 Orang (@15 RB)",
            "KETERANGAN": "Hydrotherapy / Akuatik",
            "STATUS": "Rutin"
        },
        {
            "NO": 3,
            "TANGGAL": "Setiap Rabu (Minggu ke-3)",
            "SEKOLAH / GRUP": "Pound Fit",
            "PIC & KONTAK": "Pro Dyah (0877-8456-4833)",
            "JUMLAH PESERTA": "Grup Fitness (HTM @20 RB)",
            "KETERANGAN": "Sewa Area Kolam",
            "STATUS": "DP Received"
        }
    ]
    st.session_state.booking_data = pd.DataFrame(initial_data)

# HEADER
st.title("🏊‍♂️ Dashboard Jadwal Booking Kolam")
st.caption("Sistem Manajemen Jadwal Kunjungan Sekolah & Grup Waterpark")
st.divider()

# SIDEBAR: FORM TAMBAH DATA
st.sidebar.header("➕ Tambah Booking Baru")
with st.sidebar.form("form_tambah_booking", clear_on_submit=True):
    tgl_input = st.text_input("Tanggal / Hari", placeholder="Contoh: Kamis, 15 Juli 2026")
    sekolah_input = st.text_input("Nama Sekolah / Grup", placeholder="Contoh: SMPN 1 Bogor")
    pic_input = st.text_input("Nama PIC & No HP", placeholder="Contoh: Pak Budi (0812xxx)")
    jumlah_input = st.text_input("Jumlah Peserta / Paket", placeholder="Contoh: 80 Orang")
    ket_input = st.text_input("Keterangan Tambahan", placeholder="Contoh: Paket Edukasi")
    status_input = st.selectbox("Status Booking", ["Terkonfirmasi", "Rutin", "DP Received", "Pending"])
    
    submitted = st.form_submit_button("Simpan Booking")
    
    if submitted:
        if sekolah_input and tgl_input:
            new_no = len(st.session_state.booking_data) + 1
            new_row = {
                "NO": new_no,
                "TANGGAL": tgl_input,
                "SEKOLAH / GRUP": sekolah_input,
                "PIC & KONTAK": pic_input,
                "JUMLAH PESERTA": jumlah_input,
                "KETERANGAN": ket_input,
                "STATUS": status_input
            }
            # Gunakan pd.concat untuk menambahkan baris baru
            st.session_state.booking_data = pd.concat([st.session_state.booking_data, pd.DataFrame([new_row])], ignore_index=True)
            st.sidebar.success("Jadwal booking berhasil ditambahkan!")
            st.rerun()
        else:
            st.sidebar.error("Mohon isi Nama Sekolah dan Tanggal!")

# METRICS / CARDS RINGKASAN
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Booking", value=f"{len(st.session_state.booking_data)} Grup")
with col2:
    st.metric(label="Status Terkonfirmasi", value=len(st.session_state.booking_data[st.session_state.booking_data['STATUS'] == 'Terkonfirmasi']))
with col3:
    st.metric(label="Grup Rutin", value=len(st.session_state.booking_data[st.session_state.booking_data['STATUS'] == 'Rutin']))
with col4:
    st.metric(label="Status Pending/DP", value=len(st.session_state.booking_data[st.session_state.booking_data['STATUS'].isin(['Pending', 'DP Received'])]))

st.divider()

# FITUR PENCARIAN & FILTER
col_search, col_filter = st.columns([3, 1])
with col_search:
    search_query = st.text_input("🔍 Cari Sekolah / PIC / Keterangan:", placeholder="Ketik kata kunci pencarian...")
with col_filter:
    filter_status = st.selectbox("Filter Status:", ["Semua Status"] + list(st.session_state.booking_data['STATUS'].unique()))

# Filter Dataframe
df_display = st.session_state.booking_data.copy()

if search_query:
    df_display = df_display[
        df_display['SEKOLAH / GRUP'].str.contains(search_query, case=False, na=False) |
        df_display['PIC & KONTAK'].str.contains(search_query, case=False, na=False) |
        df_display['KETERANGAN'].str.contains(search_query, case=False, na=False)
    ]

if filter_status != "Semua Status":
    df_display = df_display[df_display['STATUS'] == filter_status]

# TABEL DATA
st.subheader("📋 Daftar Jadwal Kunjungan")

# Menampilkan tabel interaktif
st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True
)

# TOMBOL DOWNLOAD / EXPORT
st.divider()
col_down1, col_down2 = st.columns([1, 4])
with col_down1:
    # Mengonversi dataframe ke CSV untuk di-download
    csv_data = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data (CSV)",
        data=csv_data,
        file_name=f"jadwal_booking_kolam_{date.today()}.csv",
        mime="text/csv"
    )
