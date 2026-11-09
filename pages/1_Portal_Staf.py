import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 
# -------------------------------------------------------------

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.warning("Masukkan password admin.")
    st.stop()

conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet="DETAIL", ttl=0)
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    df_raw = pd.DataFrame()

# ==============================================================
# LOGIKA PEMBERSIHAN HANYA UNTUK TAMPILAN DI LAYAR AGAR RAPI
# ==============================================================
st.divider()
st.subheader("📋 Tabel Data Jadwal Saat Ini")

if not df_raw.empty:
    df_display = df_raw.copy()
    header_idx = None
    for i in range(min(15, len(df_display))):
        row_str = " ".join([str(x).upper() for x in df_display.iloc[i].values])
        if "TANGGAL" in row_str and "SEKOLAH" in row_str:
            header_idx = i
            break
            
    if header_idx is not None:
        df_display.columns = [str(c).upper().strip() for c in df_display.iloc[header_idx].values]
        df_display = df_display.iloc[header_idx + 1:].reset_index(drop=True)
    
    # astype(str) mencegah ERROR PyArrow dari data tipe campuran
    # width='stretch' menghilangkan warning use_container_width
    st.dataframe(df_display.fillna("").astype(str), width="stretch")
else:
    st.info("Spreadsheet masih kosong.")

# ==============================================================
# FORM INPUT & PENYIMPANAN DATA
# ==============================================================
st.subheader("➕ Tambah Baris Data")
st.info("💡 Karena format Excel Anda naratif, Anda bisa menekan tombol Enter di dalam form di bawah ini untuk membuat teks baris baru (misal baris 1 Nama, baris 2 Nomor HP).")

with st.form("form_tambah"):
    col1, col2 = st.columns(2)
    
    with col1:
        tgl_input = st.date_input("Tanggal Booking")
        sekolah = st.text_area("Sekolah / PIC / Kontak (Gunakan Enter)")
        
    with col2:
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Gunakan Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
    if st.form_submit_button("Simpan Data ke Sheets"):
        if not sekolah:
            st.error("Data Sekolah / PIC wajib diisi!")
        else:
            hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            
            # Buat format tanggal huruf besar misal: KAMIS, 30 NOVEMBER 2026
            tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
            
            # Kita injeksi data ke kerangka df_raw (sehingga header asli Excel tidak rusak)
            new_data = {col: "" for col in df_raw.columns}
            
            # Asumsi standar struktur kolom Excel berdasarkan index (0: kosong, 1: NO, 2: TANGGAL, 3: SEKOLAH, 4: JUMLAH, 5: KET)
            if len(df_raw.columns) > 1: new_data[df_raw.columns[1]] = ""
            if len(df_raw.columns) > 2: new_data[df_raw.columns[2]] = tgl_format
            if len(df_raw.columns) > 3: new_data[df_raw.columns[3]] = sekolah
            if len(df_raw.columns) > 4: new_data[df_raw.columns[4]] = jumlah
            if len(df_raw.columns) > 5: new_data[df_raw.columns[5]] = keterangan
            
            new_row = pd.DataFrame([new_data])
            updated_df = pd.concat([df_raw, new_row], ignore_index=True)
            
            try:
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet="DETAIL", data=updated_df)
                st.success("✅ Data berhasil disimpan secara sinkron tanpa merusak format atas Excel!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")
