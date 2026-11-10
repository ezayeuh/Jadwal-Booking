import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
# LINK SPREADSHEET
# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.warning("Masukkan password admin.")
    st.stop()

# ==============================================================
# 1. PILIH SHEET TAHUN & BACA DATA
# ==============================================================
thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
conn = st.connection("gsheets", type=GSheetsConnection)

sheet_exists = True
try:
    df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), ttl=600)
except Exception:
    sheet_exists = False
    df_raw = pd.DataFrame()

# ==============================================================
# 2. PENCARIAN POSISI KOLOM SECARA OTOMATIS
# ==============================================================
header_idx = None
col_tgl, col_sek, col_jum, col_ket = -1, -1, -1, -1

if sheet_exists and not df_raw.empty:
    for i in range(min(15, len(df_raw))):
        row_str = " ".join([str(x).upper() for x in df_raw.iloc[i].values])
        if "TANGGAL" in row_str and "SEKOLAH" in row_str:
            header_idx = i
            header_row_vals = [str(x).upper().strip() for x in df_raw.iloc[i].values]
            break
            
    if header_idx is None:
        header_row_vals = [str(x).upper().strip() for x in df_raw.columns]

    for idx, val in enumerate(header_row_vals):
        if "TANGGAL" in val: col_tgl = idx
        if "SEKOLAH" in val: col_sek = idx
        if "JUMLAH" in val: col_jum = idx
        if "KETERANGAN" in val: col_ket = idx

# ==============================================================
# 3. TAMPILAN TABEL
# ==============================================================
st.divider()
if sheet_exists and not df_raw.empty:
    st.subheader(f"📋 Tabel Data Jadwal - Tahun {thn_admin}")
    df_display = df_raw.copy()
    if header_idx is not None:
        df_display.columns = [str(c).upper().strip() for c in df_display.iloc[header_idx].values]
        df_display = df_display.iloc[header_idx + 1:].reset_index(drop=True)
    st.dataframe(df_display.fillna("").astype(str), width="stretch")
else:
    st.error(f"⚠️ **Sheet '{thn_admin}' tidak ditemukan.**\n\nSilakan buka Google Sheets Anda, klik tombol **(+) Tambah Sheet** di pojok kiri bawah, dan beri nama **{thn_admin}** agar Anda bisa mengisi jadwal.")

st.divider()

kolom_tambah, kolom_hapus = st.columns([1.5, 1])

# ==============================================================
# 4. FORM TAMBAH JADWAL
# ==============================================================
with kolom_tambah:
    st.subheader(f"➕ Tambah Jadwal")
    with st.form("form_tambah"):
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_area("Sekolah / PIC / Kontak (Gunakan Enter)")
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Gunakan Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
        if st.form_submit_button("Simpan Data", use_container_width=True):
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
                
                if col_tgl != -1:
                    if col_tgl < jml_kolom_asli: baris_baru[col_tgl] = tgl_format
                    if col_sek != -1 and col_sek < jml_kolom_asli: baris_baru[col_sek] = sekolah
                    if col_jum != -1 and col_jum < jml_kolom_asli: baris_baru[col_jum] = jumlah
                    if col_ket != -1 and col_ket < jml_kolom_asli: baris_baru[col_ket] = keterangan
                else:
                    if jml_kolom_asli >= 5:
                        baris_baru[1], baris_baru[2], baris_baru[3], baris_baru[4] = tgl_format, sekolah, jumlah, keterangan
                
                data_list.append(baris_baru)
                updated_df = pd.DataFrame(data_list, columns=df_raw.columns)
                
                try:
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), data=updated_df)
                    st.cache_data.clear()
                    st.success("✅ Data berhasil disimpan!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# ==============================================================
# 5. FORM HAPUS JADWAL
# ==============================================================
with kolom_hapus:
    st.subheader(f"🗑️ Hapus Jadwal")
    if sheet_exists and not df_raw.empty and header_idx is not None:
        opsi_hapus = []
        for idx in range(header_idx + 1, len(df_raw)):
            row = df_raw.iloc[idx]
            tgl_val = str(row.iloc[col_tgl]) if col_tgl != -1 and col_tgl < len(row) else (str(row.iloc[1]) if len(row) > 1 else "")
            sek_val = str(row.iloc[col_sek]) if col_sek != -1 and col_sek < len(row) else (str(row.iloc[2]) if len(row) > 2 else "")
            
            tgl_val, sek_val = tgl_val.strip(), sek_val.strip()
            
            if tgl_val or sek_val:
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
        st.info("Sheet kosong, tidak ada jadwal untuk dihapus.")
