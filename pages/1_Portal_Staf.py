import streamlit as st
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
except Exception as e:
    st.error(f"⚠️ Gagal terhubung atau Sheet '{thn_admin}' belum dibuat di Excel Anda. Buat dulu tab-nya.")
    st.stop()

st.divider()
kolom_tambah, kolom_hapus = st.columns([1.5, 1])

# FORM TAMBAH JADWAL (AMAN, MENYELIPKAN BARIS DI BAWAH TANPA MERUSAK FORMAT ATAS)
with kolom_tambah:
    st.subheader(f"➕ Tambah Jadwal Baru")
    with st.form("form_tambah"):
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_area("Sekolah / PIC / Kontak (Bisa di-Enter)")
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Bisa di-Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
        if st.form_submit_button("Simpan Data", use_container_width=True):
            if not sekolah:
                st.error("Data Sekolah wajib diisi!")
            else:
                hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
                
                baris_baru = ["", tgl_format, sekolah, jumlah, keterangan]
                
                try:
                    ws.append_row(baris_baru, value_input_option="USER_ENTERED")
                    st.cache_data.clear()
                    st.success("✅ Data berhasil disimpan secara terpisah dan rapi!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# FORM HAPUS JADWAL (DIKUNCI MULAI BARIS 5 KE BAWAH)
with kolom_hapus:
    st.subheader(f"🗑️ Hapus Jadwal")
    
    semua_baris = ws.get_all_values()
    opsi_hapus = []
    
    # Membaca mulai dari baris ke-5 ke bawah (mengabaikan judul dan header tabel)
    for i in range(4, len(semua_baris)):
        row = semua_baris[i]
        if len(row) >= 3:
            tgl_val = str(row[1]).strip()
            sek_val = str(row[2]).strip()
            
            if tgl_val or sek_val:
                opsi_hapus.append((i + 1, f"Baris {i + 1} | {tgl_val} - {sek_val}"))
                
    if opsi_hapus:
        with st.form("form_hapus"):
            pilihan = st.selectbox("Pilih Jadwal yang ingin dihapus:", opsi_hapus, format_func=lambda x: x[1])
            
            if st.form_submit_button("🗑️ Hapus Baris Ini", type="primary", use_container_width=True):
                try:
                    ws.delete_rows(pilihan[0])
                    st.cache_data.clear()
                    st.success("✅ Jadwal berhasil dihapus dari Excel!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus: {e}")
    else:
        st.info("Belum ada data jadwal di bawah baris header yang bisa dihapus.")
