import streamlit as st
import pandas as pd
import requests

# --- KONFIGURASI ---
OPENWEATHER_API_KEY = "5763dfff82611a8770bccfca6b1b75f0"
LAT = "-0.5000"  # Koordinat lokasi lapangan (Contoh: Kalimantan)
LON = "115.0000"

st.set_page_config(page_title="Sivita Logistics AI", layout="wide", page_icon="🚢")

# --- FUNGSI CUACA REAL-TIME ---
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return {
            "main": res['weather'][0]['main'],
            "temp": res['main']['temp'],
            "desc": res['weather'][0]['description']
        }
    except:
        return {"main": "Clear", "temp": 30, "desc": "Api Offline"}

# --- LOGIKA PREDIKSI & RESIKO ---
def hitung_ai_status(stok, pakai, jarak, cuaca):
    # Faktor penghambat logistik berdasarkan cuaca
    multipliers = {
        'Rain': 1.6, 'Thunderstorm': 2.2, 'Drizzle': 1.3, 
        'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.4
    }
    f_cuaca = multipliers.get(cuaca, 1.0)
    
    # Estimasi waktu tiba logistik dari depo (Asumsi 400km/hari dalam kondisi ideal)
    waktu_tempuh = jarak / (400 / f_cuaca)
    
    # Sisa hari stok bertahan dikurangi potensi keterlambatan pengiriman
    sisa_hari = (stok / pakai) - waktu_tempuh
    return round(max(0, sisa_hari), 1)

# --- UI DASHBOARD ---
st.title("🚢 Smart Logistics Dashboard")

# Tangkap data dari Apps Script via URL
params = st.query_params
item_gs = params.get("item", "Menunggu Data...")
stok_gs = float(params.get("stok", 0))
pakai_gs = float(params.get("pakai", 1))
jarak_gs = float(params.get("jarak", 0))

# Jalankan API Cuaca
weather = get_weather()

st.info(f"📍 **Kondisi Lapangan:** {weather['main']} ({weather['temp']}°C) | *{weather['desc'].capitalize()}*")

st.divider()

if "item" in params:
    sisa = hitung_ai_status(stok_gs, pakai_gs, jarak_gs, weather['main'])
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📦 Detail Barang")
        st.write(f"**Nama:** {item_gs}")
        st.write(f"**Stok:** {stok_gs} Unit")
        st.write(f"**Jarak Depo:** {jarak_gs} KM")

    with col2:
        st.subheader("📊 Analisis Resiko AI")
        st.metric("Estimasi Stok Aman", f"{sisa} Hari")
        
        if sisa <= 3:
            st.error(f"🔴 STATUS KRITIS: Stok {item_gs} harus segera dikirim karena faktor cuaca {weather['main']} menghambat jalur distribusi!")
        elif sisa <= 7:
            st.warning(f"🟡 STATUS WASPADA: Persiapkan pemesanan ulang.")
        else:
            st.success(f"🟢 STATUS AMAN: Operasional berjalan normal.")
else:
    st.warning("Silakan pilih data di Google Sheets lalu klik menu 'Kirim Baris Ini ke Dashboard'.")

st.divider()
st.caption("Sistem ini mengintegrasikan Google Sheets, OpenWeather API, dan Streamlit Cloud.")
