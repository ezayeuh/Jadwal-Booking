import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.warning("Masukkan password admin.")
    st.stop()

# ==============================================================
# PILIH SHEET TAHUN DI PORTAL ADMIN
# ==============================================================
thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), ttl=600)
except Exception as e:
    st.warning(f"Sheet '{thn_admin}' tidak ditemukan di Google Sheets Anda. Silakan buat sheet baru bernama '{thn_admin}' terlebih dahulu di Excel/Google Sheets.")
    df_raw = pd.DataFrame()

st.divider()
st.subheader(f"📋 Tabel Data Jadwal - Tahun {thn_admin}")

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
    
    st.dataframe(df_display.fillna("").astype(str), width="stretch")
else:
    st.info("Spreadsheet kosong atau Sheet tidak ditemukan.")

st.subheader(f"➕ Tambah Jadwal ke Sheet {thn_admin}")
st.info("💡 Tekan Enter pada kotak isian jika ingin teks memanjang ke bawah (misal baris 1 Nama, baris 2 Nomor).")

with st.form("form_tambah"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Default date mengikuti tahun sheet yang dipilih admin
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_area("Sekolah / PIC / Kontak (Gunakan Enter)")
        
    with col2:
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Gunakan Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
    if st.form_submit_button("Simpan Data ke Sheets"):
        if tgl_input.year != thn_admin:
            st.error(f"Tahun pada tanggal ({tgl_input.year}) tidak cocok dengan Sheet yang sedang dibuka ({thn_admin}). Ubah Sheet Tahun di atas.")
        elif not sekolah:
            st.error("Data Sekolah / PIC wajib diisi!")
        else:
            hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            
            tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
            
            new_data = {col: "" for col in df_raw.columns}
            
            if len(df_raw.columns) > 1: new_data[df_raw.columns[1]] = ""
            if len(df_raw.columns) > 2: new_data[df_raw.columns[2]] = tgl_format
            if len(df_raw.columns) > 3: new_data[df_raw.columns[3]] = sekolah
            if len(df_raw.columns) > 4: new_data[df_raw.columns[4]] = jumlah
            if len(df_raw.columns) > 5: new_data[df_raw.columns[5]] = keterangan
            
            new_row = pd.DataFrame([new_data])
            updated_df = pd.concat([df_raw, new_row], ignore_index=True)
            
            try:
                # Simpan ke Worksheet Tahun Tersebut
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), data=updated_df)
                
                # Bersihkan cache agar Dashboard publik otomatis terupdate
                st.cache_data.clear()
                
                st.success(f"✅ Data berhasil disimpan ke Sheet {thn_admin}!")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")
