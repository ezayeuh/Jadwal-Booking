import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Portal Staf - Kelola Jadwal",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SEMBUNYIKAN SIDEBAR DAN TOMBOL NAVIGASI DENGAN CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "jadwal.json"

def clean_text(value, default="-"):
    if pd.isna(value) or value is None:
        return default
    val_str = str(value).strip()
    if val_str == "" or val_str.lower() == "nan" or val_str.lower() == "none":
        return default
    return val_str

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    if item.get("TANGGAL_DATE"):
                        item["TANGGAL_DATE"] = date.fromisoformat(item["TANGGAL_DATE"])
                return data
        except Exception:
            return []
    return []

def save_data(data):
    data_to_save = []
    for item in data:
        item_copy = item.copy()
        if isinstance(item_copy.get("TANGGAL_DATE"), date):
            item_copy["TANGGAL_DATE"] = item_copy["TANGGAL_DATE"].isoformat()
        data_to_save.append(item_copy)
    with open(DB_FILE, "w") as f:
        json.dump(data_to_save, f, indent=4)

if 'temp_dates' not in st.session_state:
    st.session_state.temp_dates = []

st.title("🔒 Portal Khusus Staf")
st.caption("Masukan password staf untuk menambah, mengimpor, atau mengelola jadwal.")

password = st.text_input("Password Staf:", type="password")

if password == "staf123":
    st.success("Akses Staf Diverifikasi")
    st.markdown("---")
    
    jadwal_kunjungan = load_data()
    
    col_input, col_manage = st.columns([1, 1.1], gap="large")
    
    with col_input:
        st.subheader("➕ Input Kunjungan")
        
        tab_manual, tab_excel = st.tabs(["📝 Form Manual", "📊 Import Excel / CSV"])
        
        # --- TAB 1: FORM MANUAL ---
        with tab_manual:
            tipe_kunjungan = st.radio("Metode Tanggal:", ["Pilih Bebas Beberapa Tanggal", "Hari Rutin / Berulang"])
            
            selected_dates_final = []
            hari_rutin_selected = []
            
            hari_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
            bln_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "Mei", 6: "Jun", 7: "Jul", 8: "Agu", 9: "Sep", 10: "Okt", 11: "Nov", 12: "Des"}

            if tipe_kunjungan == "Pilih Bebas Beberapa Tanggal":
                st.caption("Pilih tanggal satu per satu lalu klik 'Tambah':")
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    picker_date = st.date_input("Pilih Tanggal:", value=date.today(), key="picker_date")
                with col_d2:
                    st.write("")
                    st.write("")
                    if st.button("➕ Tambah Tanggal"):
                        if picker_date not in st.session_state.temp_dates:
                            st.session_state.temp_dates.append(picker_date)
                            st.session_state.temp_dates.sort()

                if st.session_state.temp_dates:
                    st.write("**Daftar Tanggal Terpilih:**")
                    for d_item in st.session_state.temp_dates:
                        t_label = f"{hari_map[d_item.weekday()]}, {d_item.day:02d} {bln_map[d_item.month]} {d_item.year}"
                        st.markdown(f"- 🗓️ `{t_label}`")
                    if st.button("🗑️ Hapus Pilihan Tanggal"):
                        st.session_state.temp_dates = []
                        st.rerun()
                
                selected_dates_final = st.session_state.temp_dates
            else:
                hari_rutin_selected = st.multiselect(
                    "Pilih Hari Rutin:",
                    ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"],
                    default=["Selasa"]
                )
                catatan_rutin = st.text_input("Keterangan Rutin:", placeholder="Misal: Minggu ke-3")

            st.markdown("---")
            with st.form("form_kunjungan_staf", clear_on_submit=True):
                sekolah_in = st.text_input("Nama Sekolah / Grup*", placeholder="SDN 01 Bogor")
                pic_in = st.text_input("PIC & Kontak*", placeholder="Pak Budi (0812xxx)")
                jumlah_in = st.text_input("Jumlah Peserta", placeholder="80 Orang")
                ket_in = st.text_input("Keterangan", placeholder="Paket Edukasi")
                kategori_in = st.selectbox("Kategori", ["Sekolah", "Kegiatan Rutin", "Umum / Komunitas"])

                submit_btn = st.form_submit_button("➕ Simpan Ke Jadwal", use_container_width=True)

                if submit_btn:
                    sekolah_clean = clean_text(sekolah_in, "")
                    pic_clean = clean_text(pic_in, "")
                    
                    if sekolah_clean and pic_clean:
                        updated_count = 0
                        added_count = 0
                        
                        jumlah_clean = clean_text(jumlah_in)
                        ket_clean = clean_text(ket_in)
                        kategori_clean = clean_text(kategori_in, "Sekolah")
                        
                        if tipe_kunjungan == "Pilih Bebas Beberapa Tanggal":
                            if not selected_dates_final:
                                st.error("⚠️ Pilih minimal 1 tanggal terlebih dahulu!")
                            else:
                                for d in selected_dates_final:
                                    tgl_text = f"{hari_map[d.weekday()]}, {d.day:02d} {bln_map[d.month]} {d.year}"
                                    entry = {
                                        "TIPE": "Tanggal Spesifik",
                                        "TANGGAL_DATE": d,
                                        "HARI_RUTIN": [],
                                        "TANGGAL_TEXT": tgl_text,
                                        "SEKOLAH": sekolah_clean,
                                        "PIC": pic_clean,
                                        "JUMLAH": jumlah_clean,
                                        "KETERANGAN": ket_clean,
                                        "KATEGORI": kategori_clean
                                    }
                                    
                                    match_idx = -1
                                    for idx_e, existing in enumerate(jadwal_kunjungan):
                                        if existing.get("SEKOLAH").lower() == sekolah_clean.lower() and existing.get("TANGGAL_DATE") == d:
                                            match_idx = idx_e
                                            break
                                            
                                    if match_idx >= 0:
                                        jadwal_kunjungan[match_idx] = entry
                                        updated_count += 1
                                    else:
                                        jadwal_kunjungan.append(entry)
                                        added_count += 1
                                        
                                save_data(jadwal_kunjungan)
                                st.session_state.temp_dates = []
                                st.success(f"✅ Berhasil! Data Baru: {added_count}, Diperbarui: {updated_count}")
                                st.rerun()
                        else:
                            tgl_text = f"Setiap {', '.join(hari_rutin_selected)}"
                            if catatan_rutin:
                                tgl_text += f" ({catatan_rutin})"
                            entry = {
                                "TIPE": "Hari Rutin / Berulang",
                                "TANGGAL_DATE": None,
                                "HARI_RUTIN": hari_rutin_selected,
                                "TANGGAL_TEXT": tgl_text,
                                "SEKOLAH": sekolah_clean,
                                "PIC": pic_clean,
                                "JUMLAH": jumlah_clean,
                                "KETERANGAN": ket_clean,
                                "KATEGORI": kategori_clean
                            }
                            
                            match_idx = -1
                            for idx_e, existing in enumerate(jadwal_kunjungan):
                                if existing.get("SEKOLAH").lower() == sekolah_clean.lower() and existing.get("TIPE") == "Hari Rutin / Berulang":
                                    match_idx = idx_e
                                    break
                                    
                            if match_idx >= 0:
                                jadwal_kunjungan[match_idx] = entry
                            else:
                                jadwal_kunjungan.append(entry)
                                
                            save_data(jadwal_kunjungan)
                            st.success("✅ Jadwal rutin berhasil disimpan/diperbarui!")
                            st.rerun()
                    else:
                        st.error("⚠️ Nama Sekolah/Grup & PIC wajib diisi!")

        # --- TAB 2: IMPORT VIA EXCEL / CSV ---
        with tab_excel:
            st.caption("Unggah file Excel (.xlsx / .xls) atau CSV (.csv). Kolom kosong otomatis diisi '-'.")
            
            uploaded_file = st.file_uploader("Pilih File Excel/CSV:", type=["xlsx", "xls", "csv"])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df_excel = pd.read_csv(uploaded_file)
                    else:
                        df_excel = pd.read_excel(uploaded_file)
                    
                    df_preview = df_excel.fillna("-")
                    st.write("**Pratinjau Data:**")
                    st.dataframe(df_preview, use_container_width=True)
                    
                    if st.button("📥 Import & Perbarui Data", use_container_width=True):
                        count_added = 0
                        count_updated = 0
                        hari_names_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
                        
                        for _, row in df_excel.iterrows():
                            tgl_val = row.get("TANGGAL", "")
                            sekolah_val = clean_text(row.get("SEKOLAH"), "")
                            pic_val = clean_text(row.get("PIC"))
                            jumlah_val = clean_text(row.get("JUMLAH"))
                            ket_val = clean_text(row.get("KETERANGAN"))
                            kategori_val = clean_text(row.get("KATEGORI"), "Sekolah")
                            
                            if not sekolah_val:
                                continue
                                
                            tgl_parsed = None
                            tipe_val = "Tanggal Spesifik"
                            hari_rutin_val = []
                            tgl_text_val = str(tgl_val)
                            
                            try:
                                if isinstance(tgl_val, (pd.Timestamp, datetime, date)):
                                    tgl_parsed = tgl_val.date() if isinstance(tgl_val, (pd.Timestamp, datetime)) else tgl_val
                                else:
                                    tgl_str = str(tgl_val).split(" ")[0].strip()
                                    tgl_parsed = datetime.strptime(tgl_str, "%Y-%m-%d").date()
                                
                                tgl_text_val = f"{hari_map[tgl_parsed.weekday()]}, {tgl_parsed.day:02d} {bln_map[tgl_parsed.month]} {tgl_parsed.year}"
                            except Exception:
                                tipe_val = "Hari Rutin / Berulang"
                                for h_name in hari_names_list:
                                    if h_name.lower() in str(tgl_val).lower():
                                        hari_rutin_val.append(h_name)

                            entry = {
                                "TIPE": tipe_val,
                                "TANGGAL_DATE": tgl_parsed,
                                "HARI_RUTIN": hari_rutin_val,
                                "TANGGAL_TEXT": clean_text(tgl_text_val),
                                "SEKOLAH": sekolah_val,
                                "PIC": pic_val,
                                "JUMLAH": jumlah_val,
                                "KETERANGAN": ket_val,
                                "KATEGORI": kategori_val
                            }
                            
                            match_index = -1
                            for idx_exist, exist_item in enumerate(jadwal_kunjungan):
                                same_school = exist_item.get("SEKOLAH", "").lower() == sekolah_val.lower()
                                same_date = (exist_item.get("TANGGAL_DATE") == tgl_parsed) if tgl_parsed else (exist_item.get("TANGGAL_TEXT") == tgl_text_val)
                                
                                if same_school and same_date:
                                    match_index = idx_exist
                                    break
                            
                            if match_index >= 0:
                                jadwal_kunjungan[match_index] = entry
                                count_updated += 1
                            else:
                                jadwal_kunjungan.append(entry)
                                count_added += 1
                            
                        save_data(jadwal_kunjungan)
                        st.success(f"✅ Impor Selesai! Data Baru: {count_added} | Data Diperbarui: {count_updated}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Gagal membaca file. Pastikan format kolom sesuai. Error: {e}")

    # --- KOLOM KANAN: KELOLA & TABEL JADWAL ---
    with col_manage:
        st.subheader("📋 Daftar Jadwal Tersimpan")
        
        if not jadwal_kunjungan:
            st.info("Belum ada jadwal yang terdaftar.")
        else:
            jadwal_sorted = sorted(
                jadwal_kunjungan,
                key=lambda x: x.get("TANGGAL_DATE") if x.get("TANGGAL_DATE") else date(2099, 12, 31)
            )
            
            table_data = []
            for item in jadwal_sorted:
                table_data.append({
                    "Tanggal": clean_text(item.get("TANGGAL_TEXT")),
                    "Sekolah / Grup": clean_text(item.get("SEKOLAH")),
                    "PIC": clean_text(item.get("PIC")),
                    "Jumlah": clean_text(item.get("JUMLAH")),
                    "Kategori": clean_text(item.get("KATEGORI")),
                    "Keterangan": clean_text(item.get("KETERANGAN"))
                })
            
            df_display = pd.DataFrame(table_data)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.write("**🗑️ Hapus Jadwal Spesifik:**")
            
            options = [f"{item['SEKOLAH']} ({item['TANGGAL_TEXT']})" for item in jadwal_sorted]
            selected_option = st.selectbox("Pilih Jadwal Yang Ingin Dihapus:", options)
            
            c_del1, c_del2 = st.columns([1, 1])
            with c_del1:
                if st.button("❌ Hapus Jadwal Terpilih", use_container_width=True):
                    idx_del = options.index(selected_option)
                    target_item = jadwal_sorted[idx_del]
                    jadwal_kunjungan.remove(target_item)
                    save_data(jadwal_kunjungan)
                    st.success(f"Jadwal '{target_item['SEKOLAH']}' berhasil dihapus!")
                    st.rerun()
                    
            with c_del2:
                if st.button("🗑️ Hapus Semua Data", type="secondary", use_container_width=True):
                    save_data([])
                    st.success("Seluruh jadwal berhasil dihapus!")
                    st.rerun()

elif password:
    st.error("Password Salah!")
