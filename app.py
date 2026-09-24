import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import json
import os

# 1. KONFIGURASI HALAMAN
st.set_page_config(
    page_title="Dashboard Jadwal Kunjungan",
    page_icon="🏊‍♂️",
    layout="wide"
)

# Sembunyikan Navigasi Sidebar bawaan Streamlit
st.markdown("""
<style>
    [data-testid="aria/Navigation"] {display: none;}
    [data-testid="stSidebarNav"] {display: none;}
    
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        padding: 24px 32px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(2, 132, 199, 0.2);
    }
    
    .stat-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stat-label { font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; }
    .stat-value { font-size: 1.6rem; font-weight: 700; color: #0f172a; margin-top: 4px; }
    
    .day-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 12px;
        min-height: 280px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }
    .day-box-today {
        background: #f0f9ff;
        border: 2px solid #0284c7;
        border-radius: 12px;
        padding: 12px;
        min-height: 280px;
        box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.15);
    }
    
    .day-header {
        font-weight: 700;
        font-size: 0.95rem;
        color: #0f172a;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 2px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .day-header-today {
        color: #0284c7;
        border-bottom: 2px solid #38bdf8;
    }
    
    .visit-card {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #0284c7;
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    
    .school-title { font-weight: 700; font-size: 0.9rem; color: #1e293b; line-height: 1.2; margin-bottom: 4px; }
    .text-muted { color: #64748b; font-size: 0.78rem; margin-bottom: 2px; }
    
    .cat-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.68rem;
        font-weight: 700;
        margin-top: 6px;
    }
    .cat-sekolah { background: #e0f2fe; color: #0369a1; }
    .cat-rutin { background: #dcfce7; color: #15803d; }
    .cat-umum { background: #fef3c7; color: #b45309; }
</style>
""", unsafe_allow_html=True)

DB_FILE = "jadwal.json"

# FUNGSI MEMBACA DATA PERMANEN
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

jadwal_kunjungan = load_data()

# HERO HEADER
st.markdown("""
<div class="hero-banner">
    <h2 style="margin:0; font-weight:700;">🏊‍♂️ Papan Informasi Jadwal Kunjungan Kolam</h2>
    <p style="margin:4px 0 0 0; opacity:0.9; font-size:0.95rem;">Jadwal resmi kunjungan sekolah, grup, dan kegiatan rutin di area kolam renang</p>
</div>
""", unsafe_allow_html=True)

# RINGKASAN METRIK
m1, m2, m3 = st.columns(3)
total_kunjungan = len(jadwal_kunjungan)
total_sekolah = len([b for b in jadwal_kunjungan if b.get('KATEGORI') == 'Sekolah'])
total_rutin = len([b for b in jadwal_kunjungan if b.get('KATEGORI') == 'Kegiatan Rutin'])

with m1:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Total Agenda Terdaftar</div><div class="stat-value">{total_kunjungan} <span style="font-size:0.85rem; color:#64748b; font-weight:400;">Rombongan</span></div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Kunjungan Sekolah</div><div class="stat-value" style="color:#0284c7;">{total_sekolah}</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-card"><div class="stat-label">Kegiatan Rutin</div><div class="stat-value" style="color:#16a34a;">{total_rutin}</div></div>', unsafe_allow_html=True)

st.write("")

# FILTER PERIODE MINGGU
c_filter, c_blank = st.columns([2, 2])
with c_filter:
    input_date = st.date_input("🗓️ Tampilkan Jadwal Minggu Dari Tanggal:", value=date.today())
    start_week = input_date - timedelta(days=input_date.weekday())

week_days = [start_week + timedelta(days=i) for i in range(7)]
end_week = week_days[-1]
hari_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]

st.markdown(f"**Periode Tampilan:** <span style='color:#0284c7; font-weight:700;'>{start_week.strftime('%d %b %Y')}</span> s/d <span style='color:#0284c7; font-weight:700;'>{end_week.strftime('%d %b %Y')}</span>", unsafe_allow_html=True)
st.write("")

# KALENDER 1 MINGGU
st.subheader("📅 Jadwal Kunjungan Minggu Ini")

cols = st.columns(7)

for idx, day_date in enumerate(week_days):
    day_name = hari_names[idx]
    is_today = (day_date == date.today())
    
    matching = []
    for b in jadwal_kunjungan:
        if b.get("TIPE") == "Tanggal Spesifik" and b.get("TANGGAL_DATE") == day_date:
            matching.append(b)
        elif b.get("TIPE") == "Hari Rutin / Berulang" and day_name in b.get("HARI_RUTIN", []):
            matching.append(b)
            
    with cols[idx]:
        header_class = "day-header-today" if is_today else "day-header"
        box_class = "day-box-today" if is_today else "day-box"
        today_tag = '<span style="font-size:0.65rem; background:#0284c7; color:white; padding:1px 5px; border-radius:4px;">HARI INI</span>' if is_today else ""
        
        cards_html = ""
        if matching:
            for mb in matching:
                badge_style = "cat-sekolah" if mb.get("KATEGORI") == "Sekolah" else ("cat-rutin" if mb.get("KATEGORI") == "Kegiatan Rutin" else "cat-umum")
                cards_html += f"""<div class="visit-card">
                    <div class="school-title">{mb['SEKOLAH']}</div>
                    <div class="text-muted">👥 {mb['JUMLAH']}</div>
                    <div class="text-muted">📞 {mb['PIC']}</div>
                    <div class="text-muted">📌 {mb['KETERANGAN']}</div>
                    <span class="cat-badge {badge_style}">{mb['KATEGORI']}</span>
                </div>"""
        else:
            cards_html = '<div class="text-muted" style="text-align:center; margin-top:20px; font-style:italic;">Tidak Ada Kunjungan</div>'
            
        full_box_html = f"""
        <div class="{box_class}">
            <div class="{header_class}">
                <span>{day_name}</span>
                <span style="font-size:0.8rem; font-weight:500;">{day_date.strftime('%d/%m')}</span>
            </div>
            {today_tag}
            <div style="margin-top:8px;">
                {cards_html}
            </div>
        </div>
        """
        st.html(full_box_html)
