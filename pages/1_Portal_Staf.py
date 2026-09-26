import streamlit as st
import pandas as pd
from datetime import datetime, date
from streamlit_gsheets import GSheetsConnection

SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1XsYvF0pcBYjRm-h_oPf2jag3OwUFLK43bhRoyE-yh-M/edit"

st.set_page_config(
    page_title="Portal Staf - Kelola Jadwal",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

HARI_INDO = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
BULAN_INDO = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
    7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

st.markdown("""
<style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stSidebarCollapsedControl"] { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

conn = st.connection("gsheets", type=GSheetsConnection)

def clean_text(value, default="-"):
    if pd.isna(value) or value is None:
        return default
    val_str = str(value).strip()
    if val_str == "" or val_str.lower() == "nan" or val_str.lower() == "none":
        return default
    return val_str

def load_data():
    try:
        df = conn.read(spreadsheet=SPREADSHEET_URL, ttl=0)
        if df is None or df.empty:
            return []
        data = df.to_dict(orient="records")
        for item in data:
            if item.get("TANGGAL_DATE") and pd.notna(item["TANGGAL_DATE"]):
                try:
                    parsed_date = date.fromisoformat(str(item["TANGGAL_DATE"]).split(" ")[0])
                    item["TANGGAL_DATE"] = parsed_date
                    hari_str = HARI_INDO[parsed_date.weekday()]
                    bln_str = BULAN_INDO[parsed_date.month]
                    item["TANGGAL_TEXT"] = f"{hari_str}, {parsed_date.day:02d} {bln_str} {parsed_date.year}"
                except Exception:
                    item["TANGGAL_DATE"] = None
            else:
                item["TANGGAL_DATE"] = None

            if isinstance(item.get("HARI_RUTIN"), str):
                try:
                    item["HARI_RUTIN"] = eval(item["HARI_RUTIN"])
                except Exception:
                    item["HARI_RUTIN"] = []
            elif not isinstance(item.get("HARI_RUTIN"), list):
                item["HARI_RUTIN"] = []
        return data
    except Exception:
        return []

def save_data(data):
    default_columns = [
        "TIPE", "TANGGAL_DATE", "HARI_RUTIN", "TANGGAL_TEXT", 
        "SEKOLAH", "PIC", "JUMLAH", "KETERANGAN", "KATEGORI"
    ]
    
    if not data or len(data) == 0:
        df = pd.DataFrame(columns=default_columns)
    else:
        df = pd.DataFrame(data)

    if not df.empty:
        if "TANGGAL_DATE" in df.columns:
            df["TANGGAL_DATE"] = df["TANGGAL_DATE"].astype(str)
        if "HARI_RUTIN" in df.columns:
            df["HARI_RUTIN"] = df["HARI_RUTIN"].astype(str)
            
    conn.update(spreadsheet=SPREADSHEET_URL, data=df)

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

        with tab_manual:
            tipe_kunjungan = st.radio("Metode Tanggal:", ["Pilih Bebas Beberapa Tanggal", "Hari Rutin / Berulang"])

            selected_dates_final = []
            hari_rutin_selected = []

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
                        t_label = f"{HARI_INDO[d_item.weekday()]}, {d_item.day:02d} {BULAN_INDO[d_item.month]} {d_item.year}"
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
                        if str(jumlah_clean).endswith(".0"):
                            jumlah_clean = str(jumlah_clean).replace(".0", "")
                        ket_clean = clean_text(ket_in)
                        kategori_clean = clean_text(kategori_in, "Sekolah")

                        if tipe_kunjungan == "Pilih Bebas Beberapa Tanggal":
                            if not selected_dates_final:
                                st.error("⚠️ Pilih minimal 1 tanggal terlebih dahulu!")
                            else:
                                for d in selected_dates_final:
                                    tgl_text = f"{HARI_INDO[d.weekday()]}, {d.day:02d} {BULAN_INDO[d.month]} {d.year}"
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
                                        if str(existing.get("SEKOLAH")).lower() == sekolah_clean.lower() and existing.get("TANGGAL_DATE") == d:
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
                                st.success(f"✅ Berhasil Disimpan ke Google Sheet! Data Baru: {added_count}, Diperbarui: {updated_count}")
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
                                if str(existing.get("SEKOLAH")).lower() == sekolah_clean.lower() and existing.get("TIPE") == "Hari Rutin / Berulang":
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
                            
                            jumlah_raw = clean_text(row.get("JUMLAH"))
                            jumlah_val = str(jumlah_raw).replace(".0", "") if str(jumlah_raw).endswith(".0") else jumlah_raw
                            
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
                                tgl_text_val = f"{HARI_INDO[tgl_parsed.weekday()]}, {tgl_parsed.day:02d} {BULAN_INDO[tgl_parsed.month]} {tgl_parsed.year}"
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
                                same_school = str(exist_item.get("SEKOLAH")).lower() == sekolah_val.lower()
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
                        st.success(f"✅ Data Tersimpan Permanen di Google Sheet! Data Baru: {count_added} | Diperbarui: {count_updated}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Gagal membaca file. Pastikan format kolom sesuai. Error: {e}")

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
                jml_str = clean_text(item.get("JUMLAH"))
                if jml_str.endswith(".0"):
                    jml_str = jml_str.replace(".0", "")

                table_data.append({
                    "Tanggal": clean_text(item.get("TANGGAL_TEXT")),
                    "Sekolah / Grup": clean_text(item.get("SEKOLAH")),
                    "PIC": clean_text(item.get("PIC")),
                    "Jumlah": jml_str,
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
                    st.success(f"Jadwal '{target_item['SEKOLAH']}' berhasil dihapus dari Google Sheets!")
                    st.rerun()

            with c_del2:
                if st.button("🗑️ Hapus Semua Data", type="secondary", use_container_width=True):
                    save_data([])
                    st.success("Seluruh jadwal di Google Sheet berhasil dikosongkan!")
                    st.rerun()

elif password:
    st.error("Password Salah!")
