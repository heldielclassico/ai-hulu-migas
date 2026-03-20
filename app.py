import streamlit as st
import pandas as pd
import requests

# --- KONFIGURASI ---
OPENWEATHER_API_KEY = "5763dfff82611a8770bccfca6b1b75f0"
LAT = "-0.5000" 
LON = "115.0000"

st.set_page_config(page_title="Sivita Smart-Logistics", layout="wide", page_icon="🚢")

# --- FUNGSI CUACA ---
def get_live_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res['weather'][0]['main']
    except:
        return "Clear"

# --- LOGIKA ANALISIS AI ---
def hitung_status_ai(stok, pakai, jarak, cuaca):
    multipliers = {'Rain': 1.6, 'Thunderstorm': 2.2, 'Drizzle': 1.3, 'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.4}
    f_cuaca = multipliers.get(cuaca, 1.0)
    waktu_tiba = jarak / (400 / f_cuaca)
    sisa_hari = (stok / pakai) - waktu_tiba
    return round(max(0, sisa_hari), 1)

# --- UI DASHBOARD ---
st.title("🚢 Sivita Smart-Logistics Dashboard")
st.subheader("Monitoring Rantai Pasok Hulu Migas Real-time")

# Ambil sheet_id dari URL parameter
query_params = st.query_params
sheet_id = query_params.get("sheet_id")

if sheet_id:
    # URL CSV dinamis berdasarkan ID dari Google Sheets
    url_csv = f"https://docs.google.com/spreadsheets/d/141fCBIbinmZHj3UAHXadkhbyArZnaf5x7sRRudVMvdE/gviz/tq?tqx=out:csv"
    
    try:
        df = pd.read_csv(url_csv)
        weather_now = get_live_weather()
        
        st.info(f"☁️ **Cuaca Saat Ini:** {weather_now} | Data tersinkronisasi.")

        # Hitung Prediksi
        df['Sisa (Hari)'] = df.apply(lambda r: hitung_status_ai(r['Stok Saat Ini'], r['Pemakaian Harian'], r['Jarak ke Gudang (KM)'], weather_now), axis=1)

        # Label Status
        def get_label(hari):
            if hari <= 3: return "🔴 KRITIS"
            if hari <= 7: return "🟡 WASPADA"
            return "🟢 AMAN"
        df['Status AI'] = df['Sisa (Hari)'].apply(get_label)

        # Tampilan Metrics
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Material", f"{len(df)} Item")
        c2.metric("Kritis", len(df[df['Status AI'] == "🔴 KRITIS"]))
        c3.metric("Cuaca", weather_now)

        st.divider()
        st.dataframe(df[['Nama Barang', 'Stok Saat Ini', 'Pemakaian Harian', 'Sisa (Hari)', 'Status AI']], use_container_width=True, hide_index=True)

    except Exception as e:
        st.error("Gagal membaca data. Pastikan Google Sheets diatur ke 'Anyone with the link can view'.")
else:
    st.warning("Menunggu data... Silakan klik 'Kirim Data' dari Google Sheets Anda.")

st.caption("Sivita AI v3.0")
