import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# -------------------------------------------------------------
# SANITASI PRIVATE KEY 
# -------------------------------------------------------------
# Ambil dictionary secrets dan perbaiki format newline pada private_key
gsheets_config = dict(st.secrets["connections"]["gsheets"])
if "private_key" in gsheets_config:
    gsheets_config["private_key"] = gsheets_config["private_key"].replace("\\n", "\n")

# 1. KONFIGURASI HALAMAN UTAMA
st.set_page_config(
    page_title="Sistem Jadwal Kunjungan",
    page_icon="📅",
    layout="wide"
)

# KONEKSI GOOGLE SHEETS
# Gunakan service_account_info=gsheets_config alih-alih **gsheets_config
conn = st.connection(
    "gsheets", 
    type=GSheetsConnection, 
    service_account_info=gsheets_config
)
