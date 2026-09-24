import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
import os

st.set_page_config(
    page_title="Portal Staf - Kelola Jadwal",
    page_icon="🔒",
    layout="wide"
)

DB_FILE = "jadwal.json"

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
st.caption("Masukan password staf untuk menambah atau menghapus jadwal kunjungan.")

password = st.text_input("Password Staf:", type="password")

if password == "staf123":
    st.success("Akses Staf Diverifikasi")
    st.markdown("---")
    
    jadwal_kunjungan = load_data()
    
    col_input, col_manage = st.columns([1, 1], gap="large")
    
    with col_input:
        st.subheader("➕ Input Kunjungan Baru")
        
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
                if sekolah_in and pic_in:
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
                                    "SEKOLAH": sekolah_in,
                                    "PIC": pic_in,
                                    "JUMLAH": jumlah_in,
                                    "KETERANGAN": ket_in,
                                    "KATEGORI": kategori_in
                                }
                                jadwal_kunjungan.append(entry)
                            save_data(jadwal_kunjungan)
                            st.session_state.temp_dates = []
                            st.success("✅ Jadwal kunjungan berhasil disimpan!")
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
                            "SEKOLAH": sekolah_in,
                            "PIC": pic_in,
                            "JUMLAH": jumlah_in,
                            "KETERANGAN": ket_in,
                            "KATEGORI": kategori_in
                        }
                        jadwal_kunjungan.append(entry)
                        save_data(jadwal_kunjungan)
                        st.success("✅ Jadwal kunjungan berhasil disimpan!")
                        st.rerun()
                else:
                    st.error("⚠️ Nama Sekolah/Grup & PIC wajib diisi!")

    with col_manage:
        st.subheader("🗑️ Kelola & Hapus Jadwal")
        if not jadwal_kunjungan:
            st.info("Belum ada jadwal yang terdaftar.")
        else:
            jadwal_to_delete = None
            for idx, item in enumerate(jadwal_kunjungan):
                c_info, c_del = st.columns([3, 1])
                with c_info:
                    st.markdown(f"**{item['SEKOLAH']}** ({item['KATEGORI']})\n\n📅 {item['TANGGAL_TEXT']} | 👥 {item['JUMLAH']}")
                with c_del:
                    if st.button("❌ Hapus", key=f"del_{idx}"):
                        jadwal_to_delete = idx
                st.markdown("<hr style='margin:6px 0;'/>", unsafe_allow_html=True)
            
            if jadwal_to_delete is not None:
                removed_item = jadwal_kunjungan.pop(jadwal_to_delete)
                save_data(jadwal_kunjungan)
                st.success(f"Jadwal '{removed_item['SEKOLAH']}' berhasil dihapus!")
                st.rerun()

            st.write("")
            if st.button("🗑️ Hapus Semua Jadwal Terdaftar", type="secondary"):
                save_data([])
                st.success("Seluruh jadwal berhasil dihapus!")
                st.rerun()

elif password:
    st.error("Password Salah!")
