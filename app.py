import streamlit as st
import pandas as pd
import requests

# --- KONFIGURASI API ---
OPENWEATHER_API_KEY = "5763dfff82611a8770bccfca6b1b75f0"
LAT = "-0.5000" 
LON = "115.0000"

st.set_page_config(page_title="Sivita Upstream AI", layout="wide", page_icon="🛢️")

# --- FUNGSI AMBIL CUACA ---
def get_live_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        return {
            "condition": data['weather'][0]['main'],
            "temp": data['main']['temp'],
            "desc": data['weather'][0]['description']
        }
    except:
        return {"condition": "Clear", "temp": 28, "desc": "Offline Mode"}

# --- LOGIKA PREDIKSI ---
def hitung_resiko(stok, pakai, jarak, cuaca):
    multipliers = {'Rain': 1.5, 'Thunderstorm': 2.0, 'Drizzle': 1.3, 'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.2}
    f_cuaca = multipliers.get(cuaca, 1.0)
    # Kecepatan distribusi terhambat cuaca
    waktu_tempuh = jarak / (400 / f_cuaca) 
    sisa_hari = (stok / pakai) - waktu_tempuh
    return round(max(0, sisa_hari), 1)

# --- TANGKAP DATA URL ---
params = st.query_params
item_val = params.get("item", "Pilih Data di Sheets")
stok_val = float(params.get("stok", 0))
pakai_val = float(params.get("pakai", 1))
jarak_val = float(params.get("jarak", 0))

# --- UI ---
st.title("🚢 Sivita Smart-Logistics: Hulu Migas 2026")
weather = get_live_weather()

st.info(f"📍 **Lokasi Tambang:** {weather['condition']} ({weather['temp']}°C) - {weather['desc'].capitalize()}")

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📦 Detail Inventaris")
    st.write(f"**Item:** {item_val}")
    st.write(f"**Stok:** {stok_val} Unit")
    st.write(f"**Pemakaian:** {pakai_val}/hari")
    st.write(f"**Jarak Depo:** {jarak_val} KM")

with col2:
    sisa = hitung_resiko(stok_val, pakai_val, jarak_val, weather['condition'])
    st.subheader("📊 Analisis Resiko AI")
    
    st.metric("Prediksi Sisa Hari", f"{sisa} Hari")
    
    if sisa <= 3:
        st.error("🔴 STATUS: KRITIS - Segera kirim ulang logistik!")
    elif sisa <= 7:
        st.warning("🟡 STATUS: WASPADA - Siapkan perencanaan re-order.")
    else:
        st.success("🟢 STATUS: AMAN - Stok mencukupi operasional.")

st.divider()
st.caption("Data disinkronkan secara otomatis dari Google Sheets melalui SIVITA PANEL.")
