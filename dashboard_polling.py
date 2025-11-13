import streamlit as st
import json
import os
import time
import pandas as pd
import altair as alt
from google.oauth2.service_account import Credentials
import requests
import gspread

SHEET_ID = "1bGTtpeN0M4Yewb8qXOhL8Z1BYQ3r0GTYspBi3kpCnRo"
CREDENTIALS_FILE = "credentials.json"

@st.cache_resource
def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(SHEET_ID)

# === Kustomisasi CSS untuk tampilan mobile ===
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-size: 18px !important;
        }
        .main { text-align: center; }
        div.stButton > button:first-child {
            background-color: #4CAF50;
            color: white;
            padding: 16px 24px;
            font-size: 18px;
            border-radius: 12px;
            width: 100%;
            border: none;
        }
        div.stButton > button:hover {
            background-color: #45a049;
            color: white;
        }
        .info-box {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
        }
        section[data-testid="stSidebar"] {
            width: 80%;
            background-color: #f8f9fa;
        }
        @media (max-width: 600px) {
            .stRadio > div {
                flex-direction: column;
                align-items: stretch;
            }
        }
    </style>
""", unsafe_allow_html=True)

# === Tampilan Header Acara ===
st.image("Flayer TV & X Benner No Cetak (50 x 100 cm).png", use_container_width=True)
st.markdown("""
    <h1 style='text-align:center; color:#004aad;'>
        🧭 BINA TALENTA INDONESIA - STEM & KARAKTER
    </h1>
    <h3 style='text-align:center; color:#f39c12;'>
        "Asah Potensi Raih Prestasi"
    </h3>
    <hr>
""", unsafe_allow_html=True)

# === Navigasi ===
st.sidebar.title("📋 Navigasi")
page = st.sidebar.radio("Pilih Halaman:", ["Halaman Polling", "Hasil Polling"])

# -----------------------------
# 🗳️ Halaman Polling
# -----------------------------
if page == "Halaman Polling":
    st.title("🗳️ Sistem Polling Peserta")
    st.markdown('<div class="info-box">Silakan isi data diri dan pilih salah satu opsi di bawah ini:</div>', unsafe_allow_html=True)

    sheet1 = get_sheet().get_worksheet(0)
    sheet2 = get_sheet().get_worksheet(1)
    records = sheet2.get_all_records()
    data = pd.DataFrame(records)["Kelompok"].to_list()

    # --- Input identitas ---
    nama = st.text_input("👤 Nama")
    prodi = st.text_input("🏫 Asal Prodi")

    # --- Pilihan polling ---
    pilihan = st.radio("Pilih Opsi:", data, horizontal=False)

    # --- Tombol kirim suara ---
    if st.button("✅ Kirim Suara"):
        if not nama or not prodi:
            # st.warning("⚠️ Harap isi *Nama* dan *Asal Prodi* terlebih dahulu sebelum mengirim suara.")
            nama = ""
            prodi = ""

        
        update = sheet1.append_row([nama, prodi, pilihan])

        if update:
            st.success(f"Terima kasih, **{nama}** dari **{prodi}**! Anda memilih **{pilihan}** 🙌")

        # (Opsional) tampilkan ringkasan
        st.markdown(f"""
            <div class="info-box">
            <b>Rekap suara kamu:</b><br>
            Nama: {nama}<br>
            Prodi: {prodi}<br>
            Pilihan: {pilihan}
            </div>
        """, unsafe_allow_html=True)

    # st.markdown('<div class="info-box">Setelah memilih, buka halaman <b>Hasil Polling</b> untuk melihat hasil realtime.</div>', unsafe_allow_html=True)
    
# -----------------------------
# 📊 Halaman Hasil Polling
# -----------------------------
elif page == "Hasil Polling":
    st.title("📊 Hasil Polling Realtime")

    # st.markdown('<div class="info-box">Grafik diperbarui otomatis setiap 3 detik.</div>', unsafe_allow_html=True)

    placeholder = st.empty()

    while True:
        sheet = get_sheet().get_worksheet(0)
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        df = df["Pilihan"].value_counts().reset_index()
        df.columns = ["Pilihan", "Suara"]

        chart = (
            alt.Chart(df)
            .mark_bar(size=50)
            .encode(
                x=alt.X("Pilihan", sort=None, axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
                y=alt.Y("Suara", axis=alt.Axis(labelFontSize=14, titleFontSize=16)),
                color="Pilihan"
            )
            .properties(width="container", height=300)
        )

        with placeholder.container():
            st.altair_chart(chart, use_container_width=True)
            st.dataframe(df.set_index("Pilihan"))
            # st.caption("⏳ Halaman diperbarui otomatis setiap 3 detik...")

        time.sleep(5)
