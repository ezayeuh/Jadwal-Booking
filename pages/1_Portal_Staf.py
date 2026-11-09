import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit?gid=1469221539#gid=1469221539"

st.set_page_config(
    page_title="Portal Staff - Jadwal Kunjungan",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 Portal Staff / Admin - Pengelolaan Jadwal Kunjungan")
st.write("Kelola data booking kolam sesuai format tabel master Excel (NO, TANGGAL, SEKOLAH, JUMLAH, KETERANGAN).")

# Autentikasi Sederhana Staff
PASSWORD_STAFF = "admin123"  # Ubah sesuai keinginan
input_password = st.text_input("Masukkan Password Staff:", type="password")

if input_password != PASSWORD_STAFF:
    st.warning("⚠️ Silakan masukkan password yang benar untuk mengakses panel input data.")
    st.stop()

st.success("✅ Login Staff Berhasil!")

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    df = pd.DataFrame()

st.divider()
st.subheader("📋 Tabel Data Jadwal Saat Ini")
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("Spreadsheet masih kosong.")

st.divider()
st.subheader("➕ Tambah Data Jadwal Baru")

with st.form("form_tambah_staff"):
    col1, col2 = st.columns(2)
    
    with col1:
        no_urut = st.text_input("NO (Nomor / Opsional)")
        tgl_input = st.date_input("TANGGAL Kunjungan", value=date.today())
        
        st.markdown("**Informasi Grup & Kontak (Kolom SEKOLAH)**")
        nama_grup = st.text_input("Nama Grup / Instansi / Sekolah")
        nama_pic = st.text_input("Nama Penanggung Jawab (PIC)")
        kontak_pic = st.text_input("Nomor Kontak / Telepon")
        
    with col2:
        jumlah = st.text_input("JUMLAH (Contoh: 250 SISWA / @13 RB / 30 ORANG)")
        keterangan = st.text_area("KETERANGAN (Catatan, DP, Lunas, Fasilitas, dll)")
        
    submit_btn = st.form_submit_button("Simpan Data ke Spreadsheet")
    
    if submit_btn:
        if not nama_grup:
            st.error("Nama Instansi/Grup wajib diisi!")
        else:
            formatted_tgl_str = tgl_input.strftime("%A, %d %b %Y").upper()
            sekolah_gabungan = f"{nama_grup} | {nama_pic} | {kontak_pic}".strip(" |")
            
            new_row = pd.DataFrame([{
                "NO": no_urut,
                "TANGGAL": formatted_tgl_str,
                "SEKOLAH": sekolah_gabungan,
                "JUMLAH": jumlah,
                "KETERANGAN": keterangan
            }])
            
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            try:
                conn.update(spreadsheet=SPREADSHEET_URL, data=updated_df)
                st.success("🎉 Data berhasil ditambahkan dan disinkronkan ke Google Sheets!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan ke Google Sheets: {e}")
