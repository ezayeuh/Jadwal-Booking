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
# 1. PILIH SHEET TAHUN
# ==============================================================
thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
conn = st.connection("gsheets", type=GSheetsConnection)

sheet_exists = True
try:
    # Membaca data mentah TANPA MENGUBAH HEADER BAWAAN
    df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), ttl=600)
except Exception:
    sheet_exists = False
    df_raw = pd.DataFrame()

# ==============================================================
# 2. TAMPILAN TABEL AGAR RAPI (TIDAK ERROR PYARROW)
# ==============================================================
st.divider()
st.subheader(f"📋 Tabel Data Jadwal - Tahun {thn_admin}")

if sheet_exists and not df_raw.empty:
    df_display = df_raw.copy()
    
    # Mencari baris yang mengandung tulisan TANGGAL dan SEKOLAH untuk dijadikan Header Tampilan
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
    st.error(f"⚠️ **Sheet '{thn_admin}' tidak ditemukan.**\n\nSilakan buka Google Sheets Anda, klik tombol **(+) Tambah Sheet** di pojok kiri bawah, dan beri nama **{thn_admin}** agar Anda bisa mengisi jadwal.")

st.divider()

kolom_tambah, kolom_hapus = st.columns([1.5, 1])

# ==============================================================
# 3. FORM TAMBAH JADWAL (PAKSA INDEKS AGAR TIDAK ACAK-ACAKAN)
# ==============================================================
with kolom_tambah:
    st.subheader(f"➕ Tambah Jadwal")
    with st.form("form_tambah"):
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_area("Sekolah / PIC / Kontak (Gunakan Enter untuk baris baru)")
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket")
        keterangan = st.text_area("Keterangan Tambahan")
        
        if st.form_submit_button("Simpan Data ke Sheets", use_container_width=True):
            if not sheet_exists:
                st.error(f"Buat dulu Sheet '{thn_admin}' di Google Sheets Anda sebelum menyimpan data!")
            elif tgl_input.year != thn_admin:
                st.error(f"Tahun tanggal ({tgl_input.year}) tidak cocok dengan Sheet ({thn_admin}).")
            elif not sekolah:
                st.error("Data Sekolah / PIC wajib diisi!")
            else:
                hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
                
                data_list = df_raw.values.tolist()
                jml_kolom_asli = len(df_raw.columns)
                baris_baru = [""] * jml_kolom_asli
                
                # --- SISTEM TEMBAK INDEKS PASTI ---
                # Tidak peduli nama header apa yang dibaca sistem, kita paksakan:
                # Kolom 0 = NO
                # Kolom 1 = TANGGAL
                # Kolom 2 = SEKOLAH
                # Kolom 3 = JUMLAH
                # Kolom 4 = KETERANGAN
                
                if jml_kolom_asli > 1: baris_baru[1] = tgl_format
                if jml_kolom_asli > 2: baris_baru[2] = sekolah
                if jml_kolom_asli > 3: baris_baru[3] = jumlah
                if jml_kolom_asli > 4: baris_baru[4] = keterangan
                
                data_list.append(baris_baru)
                updated_df = pd.DataFrame(data_list, columns=df_raw.columns)
                
                try:
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), data=updated_df)
                    st.cache_data.clear()
                    st.success("✅ Data berhasil disimpan! Silakan cek Excel, formatnya PASTI rapi seperti master 2025.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# ==============================================================
# 4. FORM HAPUS JADWAL
# ==============================================================
with kolom_hapus:
    st.subheader(f"🗑️ Hapus Jadwal")
    if sheet_exists and not df_raw.empty:
        # Cari baris judul "NO, TANGGAL, SEKOLAH"
        header_idx_hapus = None
        for i in range(min(15, len(df_raw))):
            row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
            if "TANGGAL" in row_str and "SEKOLAH" in row_str:
                header_idx_hapus = i
                break
                
        if header_idx_hapus is not None:
            opsi_hapus = []
            for idx in range(header_idx_hapus + 1, len(df_raw)):
                row = df_raw.iloc[idx]
                
                # Membaca paksa dari Kolom ke-2 (Index 1) dan Kolom ke-3 (Index 2)
                tgl_val = str(row.iloc[1]) if len(row) > 1 else ""
                sek_val = str(row.iloc[2]) if len(row) > 2 else ""
                
                tgl_val, sek_val = tgl_val.strip(), sek_val.strip()
                
                # Hindari baris yang semuanya nan
                if tgl_val != "nan" and sek_val != "nan" and (tgl_val or sek_val):
                    label_teks = f"{tgl_val} - {sek_val}".strip(" - ")
                    opsi_hapus.append((idx, f"Baris {idx + 2} | {label_teks}"))
                    
            if opsi_hapus:
                with st.form("form_hapus"):
                    pilihan_hapus = st.selectbox(
                        "Pilih Jadwal yang ingin dihapus:", 
                        opsi_hapus, 
                        format_func=lambda x: x[1]
                    )
                    
                    submit_hapus = st.form_submit_button("🗑️ Hapus Baris Ini", type="primary", use_container_width=True)
                    
                    if submit_hapus:
                        idx_to_drop = pilihan_hapus[0]
                        df_updated_hapus = df_raw.drop(index=idx_to_drop).reset_index(drop=True)
                        
                        try:
                            conn.update(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), data=df_updated_hapus)
                            st.cache_data.clear()
                            st.success(f"✅ {pilihan_hapus[1]} Berhasil Dihapus!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menghapus data: {e}")
            else:
                st.info("Tidak ada data jadwal di bawah judul yang bisa dihapus.")
        else:
            st.info("Format kolom belum ada. Isi jadwal pertama terlebih dahulu.")
