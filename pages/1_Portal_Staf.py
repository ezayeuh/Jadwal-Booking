import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
# GANTI LINK INI DENGAN LINK GOOGLE SPREADSHEET YANG BARU DIBUAT (BUKAN .xlsx)
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 
# -------------------------------------------------------------

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.warning("Masukkan password admin.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="DETAIL", ttl=0)
except Exception as e:
    st.error(f"Gagal memuat data. Pastikan link bukan file .xlsx: {e}")
    df = pd.DataFrame()

st.divider()
if not df.empty:
    st.dataframe(df, use_container_width=True)

st.subheader("➕ Tambah Baris Data")
st.info("💡 Karena Excel Anda memiliki baris yang menyambung (kontak di baris bawahnya), Anda bisa menggunakan Enter di form ini untuk membuat baris baru pada satu sel.")

with st.form("form_tambah"):
    col1, col2 = st.columns(2)
    
    with col1:
        tgl_input = st.date_input("Tanggal")
        sekolah = st.text_area("Sekolah / PIC / Kontak (Bisa Enter ke bawah)")
        
    with col2:
        jumlah = st.text_area("Jumlah / Harga Tiket (Bisa Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
    if st.form_submit_button("Simpan Data"):
        if not sekolah:
            st.error("Sekolah wajib diisi!")
        else:
            hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            
            # Format: KAMIS, 30 November 2026
            tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1]} {tgl_input.year}"
            
            new_row = pd.DataFrame([{
                "NO": "", 
                "TANGGAL": tgl_format,
                "SEKOLAH": sekolah,
                "JUMLAH": jumlah,
                "KETERANGAN": keterangan
            }])
            
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            try:
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="DETAIL", data=updated_df)
                st.success("✅ Data berhasil disimpan!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan (Pastikan ini Google Sheets asli): {e}")
