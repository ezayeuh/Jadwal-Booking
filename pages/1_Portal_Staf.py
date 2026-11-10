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

# ==============================================================
# PILIH SHEET TAHUN
# ==============================================================
thn_admin = st.selectbox("📂 Pilih Sheet Tahun:", range(2024, 2030), index=range(2024, 2030).index(date.today().year))
conn = st.connection("gsheets", type=GSheetsConnection)

try:
    # BACA DATA MENTAH APA ADANYA
    df_raw = conn.read(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), ttl=600)
except Exception:
    st.error(f"⚠️ Sheet '{thn_admin}' belum ada di Google Sheets. Buat dulu Sheet-nya di Excel dengan nama {thn_admin} sebelum menyimpan data.")
    st.stop()

# ==============================================================
# TAMPILKAN TABEL PERSIS SEPERTI EXCEL
# ==============================================================
st.divider()
st.subheader(f"📋 Tampilan Excel Saat Ini - Sheet {thn_admin}")

if not df_raw.empty:
    # Tampilkan apa adanya tanpa modifikasi header, cukup ubah NaN jadi kosong agar enak dilihat
    st.dataframe(df_raw.fillna("").astype(str), width="stretch")
else:
    st.info("Spreadsheet kosong.")

st.divider()
kolom_tambah, kolom_hapus = st.columns([1.5, 1])

# ==============================================================
# FORM TAMBAH JADWAL
# ==============================================================
with kolom_tambah:
    st.subheader(f"➕ Tambah Jadwal Baru")
    with st.form("form_tambah"):
        default_date = date(thn_admin, date.today().month, date.today().day) if thn_admin != date.today().year else date.today()
        tgl_input = st.date_input("Tanggal Booking", value=default_date)
        sekolah = st.text_area("Sekolah / PIC / Kontak (Bisa pakai Enter)")
        jumlah = st.text_area("Jumlah Peserta / Harga Tiket (Bisa pakai Enter)")
        keterangan = st.text_area("Keterangan Tambahan")
        
        if st.form_submit_button("Simpan ke Excel", use_container_width=True):
            if tgl_input.year != thn_admin:
                st.error(f"Tahun tanggal ({tgl_input.year}) tidak cocok dengan Sheet ({thn_admin}).")
            elif not sekolah:
                st.error("Data Sekolah wajib diisi!")
            else:
                hari_indo = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                tgl_format = f"{hari_indo[tgl_input.weekday()].upper()}, {tgl_input.day} {bulan_indo[tgl_input.month-1].upper()} {tgl_input.year}"
                
                # --- PROSES SIMPAN PALING PRESISI ---
                # Ambil data lama
                data_list = df_raw.values.tolist()
                
                # Siapkan array kosong sepanjang kolom asli Excel
                jml_kolom_asli = len(df_raw.columns)
                baris_baru = [""] * jml_kolom_asli
                
                # MASUKKAN PAKSA KE INDEKS (INDEX 0 = NO, 1 = TGL, 2 = SEKOLAH, 3 = JML, 4 = KET)
                if jml_kolom_asli > 1: baris_baru[1] = tgl_format
                if jml_kolom_asli > 2: baris_baru[2] = sekolah
                if jml_kolom_asli > 3: baris_baru[3] = jumlah
                if jml_kolom_asli > 4: baris_baru[4] = keterangan
                
                # Tambahkan ke daftar dan bentuk ulang dataframe
                data_list.append(baris_baru)
                updated_df = pd.DataFrame(data_list, columns=df_raw.columns)
                
                try:
                    conn.update(spreadsheet=SPREADSHEET_URL, worksheet=str(thn_admin), data=updated_df)
                    st.cache_data.clear()
                    st.success("✅ Data berhasil disimpan persis sesuai format master!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan data: {e}")

# ==============================================================
# FORM HAPUS JADWAL 
# ==============================================================
with kolom_hapus:
    st.subheader(f"🗑️ Hapus Jadwal")
    if not df_raw.empty:
        opsi_hapus = []
        # Cari data baris per baris
        for idx in range(len(df_raw)):
            row = df_raw.iloc[idx]
            # Paksa baca kolom ke-2 (Index 1) dan ke-3 (Index 2)
            tgl_val = str(row.iloc[1]) if len(row) > 1 else ""
            sek_val = str(row.iloc[2]) if len(row) > 2 else ""
            
            tgl_val, sek_val = tgl_val.strip(), sek_val.strip()
            
            # Jika baris ini bukan judul dan berisi data yang valid
            if tgl_val != "nan" and sek_val != "nan" and "TANGGAL" not in tgl_val.upper() and (tgl_val or sek_val):
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
                        st.success(f"✅ Data Dihapus!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menghapus: {e}")
        else:
            st.info("Belum ada data jadwal untuk dihapus.")
