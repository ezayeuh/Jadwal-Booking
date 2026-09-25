import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. KONFIGURASI HALAMAN UTAMA
st.set_page_config(
    page_title="Sistem Jadwal Kunjungan",
    page_icon="📅",
    layout="wide"
)

# KONEKSI GOOGLE SHEETS
# Langsung panggil tanpa parameter tambahan
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl=0)
        return df
    except Exception as e:
        st.error(f"Gagal memuat data dari Google Sheets: {e}")
        return None

# TAMPILAN UTAMA
st.title("📅 Sistem Jadwal Kunjungan")
st.caption("Selamat datang di portal informasi jadwal kunjungan.")
st.markdown("---")

df_jadwal = load_data()

if df_jadwal is not None and not df_jadwal.empty:
    st.subheader("📋 Jadwal Kunjungan Terbaru")
    
    display_cols = [col for col in ["TANGGAL_TEXT", "SEKOLAH", "PIC", "JUMLAH", "KATEGORI", "KETERANGAN"] if col in df_jadwal.columns]
    
    if display_cols:
        st.dataframe(df_jadwal[display_cols].fillna("-"), use_container_width=True, hide_index=True)
    else:
        st.dataframe(df_jadwal.fillna("-"), use_container_width=True, hide_index=True)
else:
    st.info("Belum ada data jadwal kunjungan yang terdaftar.")
