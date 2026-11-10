import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
# LINK SPREADSHEET (Pastikan Sheet tersebut sudah berformat Google Sheets)
# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.warning("Masukkan password admin.")
    st.stop()

# ==============================================================
# PILIH SHEET TAHUN
# ==============================================================
thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # Membaca data mentah
    df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), ttl=600)
except Exception as e:
    st.warning(f"Sheet '{thn_admin}' tidak ditemukan. Pastikan nama Sheet di bawah berformat angka tahun (misal: '2026').")
    df_raw = pd.DataFrame()

# ==============================================================
# TAMPILAN TABEL AGAR RAPI (TIDAK ERROR PYARROW)
# ==============================================================
st.divider()
st.subheader(f"📋 Tabel Data Jadwal - Tahun {thn_admin}")

if not df_raw.empty:
    df_display = df_raw.copy()
    header_idx = None
    # Mencari baris yang mengandung tulisan TANGGAL dan SEKOLAH
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

# ==============================================================
# FORM INPUT & PENYIMPANAN DATA (ANTI GESER)
# ==============================================================
st.subheader(f"➕ Tambah Jadwal ke Sheet {thn_admin}")
st.info("💡 Tekan Enter pada kotak isian jika ingin teks memanjang ke bawah (misal baris 1 Nama, baris 2 Nomor).")

with st.form("form_tambah"):
    col1, col2 = st.columns(2)
    
    with col1:
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_area("Sekolah / PIC / Kontak (Gunakan Enter)")
        
    with col2:
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Gunakan Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
    if st.form_submit_button("Simpan Data ke Sheets"):
        if tgl_input.year != thn_admin:
            st.error(f"Tahun pada tanggal ({tgl_input.year}) tidak cocok dengan Sheet yang sedang dibuka ({thn_admin}).")
        elif not sekolah:
            st.error("Data Sekolah / PIC wajib diisi!")
        else:
            hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            
            tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
            
            # --- BAGIAN PALING PENTING: MEMASUKKAN DATA TEPAT KE INDEKS KOLOM ---
            # Kita mengambil baris data dari Google Sheets sebagai List (Daftar), lalu menambah 1 baris baru ke paling bawah
            data_list = df_raw.values.tolist()
            
            # Memastikan baris baru punya jumlah kolom yang sama persis dengan tabel mentah
            jml_kolom_asli = len(df_raw.columns)
            baris_baru = [""] * jml_kolom_asli
            
            # Memasukkan input tepat ke urutan kolom visual di Excel:
            # Kolom A (Index 0) = NO (kosong)
            # Kolom B (Index 1) = TANGGAL
            # Kolom C (Index 2) = SEKOLAH
            # Kolom D (Index 3) = JUMLAH
            # Kolom E (Index 4) = KETERANGAN
            if jml_kolom_asli > 1: baris_baru[1] = tgl_format
            if jml_kolom_asli > 2: baris_baru[2] = sekolah
            if jml_kolom_asli > 3: baris_baru[3] = jumlah
            if jml_kolom_asli > 4: baris_baru[4] = keterangan
            
            data_list.append(baris_baru)
            
            # Mengubah list kembali menjadi DataFrame dengan header mentah bawaan
            updated_df = pd.DataFrame(data_list, columns=df_raw.columns)
            
            try:
                # Simpan ke Worksheet
                conn.update(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), data=updated_df)
                
                # Bersihkan cache
                st.cache_data.clear()
                
                st.success(f"✅ Data berhasil disimpan ke Sheet {thn_admin}! Cek Excel Anda, sekarang pasti RAPI.")
                st.rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")
