import streamlit as st
import pandas as pd
import requests

# --- KONFIGURASI API ---
OPENWEATHER_API_KEY = "5763dfff82611a8770bccfca6b1b75f0"
LAT = "-0.5000" 
LON = "115.0000"

st.set_page_config(page_title="Sivita Upstream AI", layout="wide", page_icon="🚢")

# --- FUNGSI CUACA REAL-TIME ---
def get_live_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res['weather'][0]['main']
    except:
        return "Clear"

# --- LOGIKA PREDIKSI RESIKO AI ---
def hitung_status_ai(stok, pakai, jarak, cuaca):
    # Faktor penghambat logistik (Hulu Migas)
    multipliers = {
        'Rain': 1.6, 'Thunderstorm': 2.2, 'Drizzle': 1.3, 
        'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.4
    }
    f_cuaca = multipliers.get(cuaca, 1.0)
    
    # Kecepatan distribusi terhambat medan & cuaca
    # Rumus: (Stok/Pakai) - (Jarak / Kecepatan Terkoreksi Cuaca)
    waktu_tiba = jarak / (400 / f_cuaca)
    sisa_hari = (stok / pakai) - waktu_tiba
    return round(max(0, sisa_hari), 1)

# --- UI DASHBOARD ---
st.title("🚢 Sivita Smart-Logistics Dashboard")
st.subheader("Monitoring Rantai Pasok Hulu Migas Real-time")

# Ambil sheet_id dari URL
params = st.query_params
sheet_id = params.get("sheet_id")

if sheet_id:
    # URL CSV Google Sheets
    url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    
    try:
        # 1. Baca Seluruh Data dari Sheets
        df = pd.read_csv(url_csv)
        
        # 2. Ambil Cuaca Saat Ini
        weather_now = get_live_weather()
        st.info(f"☁️ **Cuaca Lokasi Saat Ini:** {weather_now} | Data disinkronkan dari Google Sheets.")

        # 3. Proses Analisis untuk Semua Baris
        def proses_baris(row):
            return hitung_status_ai(
                row['Stok Saat Ini'], 
                row['Pemakaian Harian'], 
                row['Jarak ke Gudang (KM)'], 
                weather_now
            )

        df['Prediksi Sisa (Hari)'] = df.apply(proses_baris, axis=1)

        # 4. Tentukan Label Status
        def label_status(hari):
            if hari <= 3: return "🔴 KRITIS"
            if hari <= 7: return "🟡 WASPADA"
            return "🟢 AMAN"
        
        df['Status AI'] = df['Prediksi Sisa (Hari)'].apply(label_status)

        # 5. Tampilkan Ringkasan Ringkas (Metrics)
        total_item = len(df)
        kritis = len(df[df['Status AI'] == "🔴 KRITIS"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Material Pantauan", f"{total_item} Item")
        c2.metric("Status Kritis", f"{kritis} Item", delta="-Peringatan" if kritis > 0 else "Aman")
        c3.metric("Kondisi Cuaca", weather_now)

        st.divider()

        # 6. Tampilkan Tabel Utama
        st.subheader("📋 Laporan Analisis Stok & Distribusi")
        # Styling tabel agar lebih menarik
        st.dataframe(
            df[['Nama Barang', 'Stok Saat Ini', 'Pemakaian Harian', 'Prediksi Sisa (Hari)', 'Status AI']], 
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error(f"Gagal memuat data. Pastikan Google Sheets Anda diatur ke 'Anyone with the link' (Viewer).")
else:
    st.warning("Menunggu sinkronisasi... Silakan klik 'Kirim Data' dari Google Sheets Anda.")

st.divider()
st.caption("Sivita AI v3.0 - Integrated with OpenWeather & Google Cloud")
