import streamlit as st
import pandas as pd
from datetime import date
import gspread

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.stop()

thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))

try:
    kredensial = dict(st.secrets["connections"]["gsheets"])
    gc = gspread.service_account_from_dict(kredensial)
    sh = gc.open_by_url(SPREADSHEET_URL)
    ws = sh.worksheet(str(thn_admin))
    semua_baris = ws.get_all_values()
except Exception as e:
    st.error(f"⚠️ Gagal terhubung atau Sheet '{thn_admin}' belum dibuat di Excel Anda. Buat dulu tab-nya.")
    st.stop()

st.divider()
st.subheader(f"📋 Daftar Jadwal Kunjungan (Sheet Tahun {thn_admin})")

if semua_baris:
    df_excel = pd.DataFrame(semua_baris)
    st.dataframe(df_excel.fillna("").astype(str), width="stretch")
else:
    st.info(f"Sheet {thn_admin} masih kosong.")

st.divider()
kolom_tambah, kolom_hapus = st.columns([1, 1])

# ==============================================================
# FORM TAMBAH JADWAL (DIJAMIN MASUK KE KOLOM C, D, E, F, G DENGAN PAS)
# ==============================================================
with kolom_tambah:
    st.subheader("➕ Tambah Jadwal Baru")
    with st.form("form_tambah"):
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_input("Nama Sekolah / Instansi")
        kontak = st.text_input("Kontak Person (Nama & No HP/WhatsApp)")
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Bisa di-Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
        if st.form_submit_button("Simpan ke Excel", use_container_width=True):
            if not sekolah:
                st.error("Nama Sekolah wajib diisi!")
            else:
                hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
                
                # PEMETAAN KOLOM YANG PRESISI 100% DENGAN EXCEL ANDA:
                # Kolom A = Kosong ("")
                # Kolom B = Kosong ("")
                # Kolom C = TANGGAL (tgl_format)
                # Kolom D = SEKOLAH (sekolah)
                # Kolom E = KONTAK (kontak)
                # Kolom F = JUMLAH (jumlah)
                # Kolom G = KETERANGAN (keterangan)
                baris_baru = ["", "", tgl_format, sekolah, kontak, jumlah, keterangan]
                
                try:
                    ws.append_row(baris_baru, value_input_option="USER_ENTERED")
                    st.cache_data.clear()
                    st.success("✅ Data berhasil ditambahkan di baris baru bawah secara rapi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# ==============================================================
# FORM HAPUS JADWAL
# ==============================================================
with kolom_hapus:
    st.subheader("🗑️ Hapus Jadwal")
    
    opsi_hapus = []
    for i in range(4, len(semua_baris)):
        row = semua_baris[i]
        if len(row) >= 5:
            tgl_val = str(row[2]).strip()  # Kolom C (Tanggal)
            sek_val = str(row[3]).strip()  # Kolom D (Sekolah)
            
            if tgl_val or sek_val:
                opsi_hapus.append((i + 1, f"Baris {i + 1} | {tgl_val} - {sek_val}"))
                
    if opsi_hapus:
        with st.form("form_hapus"):
            pilihan = st.selectbox("Pilih Jadwal yang ingin dihapus:", opsi_hapus, format_func=lambda x: x[1])
            
            if st.form_submit_button("🗑️ Hapus Baris Ini", type="primary", use_container_width=True):
                try:
                    ws.delete_rows(pilihan[0])
                    st.cache_data.clear()
                    st.success("✅ Jadwal berhasil dihapus!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus: {e}")
    else:
        st.info("Belum ada data jadwal untuk dihapus.")
