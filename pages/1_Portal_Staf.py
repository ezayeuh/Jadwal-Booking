import streamlit as st
from datetime import date
import gspread # Mesin baru yang tidak merusak format Excel

# -------------------------------------------------------------
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/14XyLKqesumeBBDhPGlko5Iea3a0PG4nyJw-m_eS_BCY/edit" 
# -------------------------------------------------------------

st.set_page_config(page_title="Portal Staff", page_icon="🔐", layout="wide")
st.title("🔐 Portal Staff / Admin")

if st.text_input("Password:", type="password") != "admin123":
    st.stop()

# ==============================================================
# KONEKSI AMAN TANPA OVERWRITE
# ==============================================================
thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))

try:
    # Mengambil kunci akses langsung dari rahasia Streamlit Anda
    kredensial = dict(st.secrets["connections"]["gsheets"])
    gc = gspread.service_account_from_dict(kredensial)
    sh = gc.open_by_url(SPREADSHEET_URL)
    ws = sh.worksheet(str(thn_admin))
except Exception as e:
    st.error(f"⚠️ Gagal terhubung atau Sheet '{thn_admin}' belum dibuat di Excel Anda. Buka Excel dan klik (+) untuk membuat tab {thn_admin}.")
    st.stop()

st.divider()
kolom_tambah, kolom_hapus = st.columns([1.5, 1])

# ==============================================================
# FORM TAMBAH JADWAL (TEMBAK BAWAH)
# ==============================================================
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
                
                # Susun array khusus untuk Kolom A (NO), B (TGL), C (SEKOLAH), D (JML), E (KET)
                baris_baru = ["", tgl_format, sekolah, jumlah, keterangan]
                
                try:
                    # Fungsi ajaib: HANYA MENAMBAH 1 BARIS di bawah. Tidak mengganggu atasnya sama sekali!
                    ws.append_row(baris_baru, value_input_option="USER_ENTERED")
                    st.cache_data.clear()
                    st.success("✅ Data berhasil disimpan! Silakan cek Excel Anda, dijamin formatnya tetap rapi.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# ==============================================================
# FORM HAPUS JADWAL (HAPUS BARIS AMAN)
# ==============================================================
with kolom_hapus:
    st.subheader(f"🗑️ Hapus Jadwal")
    
    # Baca seluruh isi baris Excel persis sebagaimana adanya
    semua_baris = ws.get_all_values()
    opsi_hapus = []
    
    # Looping dari baris ke-1 sampai bawah (Index + 1 karena Excel dimulai dari baris 1)
    for i, row in enumerate(semua_baris):
        if len(row) >= 3:
            tgl_val = str(row[1]).strip() # Kolom B
            sek_val = str(row[2]).strip() # Kolom C
            
            # Cuma ambil baris yang ada isinya dan BUKAN merupakan judul tabel
            if tgl_val and "TANGGAL" not in tgl_val.upper() and "JADWAL" not in tgl_val.upper():
                opsi_hapus.append((i + 1, f"Baris {i + 1} | {tgl_val} - {sek_val}"))
                
    if opsi_hapus:
        with st.form("form_hapus"):
            pilihan = st.selectbox("Pilih Jadwal yang batal/dihapus:", opsi_hapus, format_func=lambda x: x[1])
            
            if st.form_submit_button("🗑️ Hapus Baris Ini", type="primary", use_container_width=True):
                try:
                    # Menghapus spesifik 1 baris di Excel tanpa menyentuh baris lainnya
                    ws.delete_rows(pilihan[0])
                    st.cache_data.clear()
                    st.success("✅ Jadwal berhasil dihapus dari Excel!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus: {e}")
    else:
        st.info("Belum ada data jadwal untuk dihapus.")
