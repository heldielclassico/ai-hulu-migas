import streamlit as st
import pandas as pd
import requests

# --- KONFIGURASI API & LOKASI ---
OPENWEATHER_API_KEY = "5763dfff82611a8770bccfca6b1b75f0"
# Contoh Koordinat: Hulu Mahakam, Kalimantan (Lokasi Tambang)
LAT = "-0.5000" 
LON = "115.0000"

st.set_page_config(page_title="Sivita Upstream AI", layout="wide", page_icon="🛢️")

# --- FUNGSI AMBIL CUACA REAL-TIME ---
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
        return {"condition": "Clear", "temp": 28, "desc": "Api Error/Offline"}

# --- LOGIKA PREDIKSI AI ---
def hitung_resiko(stok, pakai, jarak, cuaca):
    # Faktor penghambat berdasarkan data cuaca asli
    multipliers = {
        'Rain': 1.5, 'Thunderstorm': 2.0, 'Drizzle': 1.3, 
        'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.2
    }
    f_cuaca = multipliers.get(cuaca, 1.0)
    
    # Kecepatan logistik di medan berat hulu (km/hari)
    kecepatan_harian = 400 / f_cuaca 
    waktu_tempuh = jarak / kecepatan_harian
    
    sisa_hari = (stok / pakai) - waktu_tempuh
    return round(max(0, sisa_hari), 1)

# --- UI DASHBOARD ---
st.title("🚢 Sivita Smart-Logistics: Hulu Migas 2026")
st.markdown(f"**Lokasi Monitoring:** Lapangan Terpencil (Lat: {LAT}, Lon: {LON})")

# 1. Fetch Cuaca Otomatis saat Apps dibuka
weather_data = get_live_weather()

# 2. Row Atas: Informasi Cuaca & Status Global
c1, c2, c3 = st.columns(3)
with c1:
    st.info(f"☁️ **Cuaca Real-time:** {weather_data['condition']} ({weather_data['temp']}°C)")
with c2:
    st.write(f"📝 *Keterangan: {weather_data['desc'].capitalize()}*")
with c3:
    if st.button("🔄 Refresh Data Cuaca"):
        st.rerun()

st.divider()

# 3. Input Data Stok (Bisa via Sidebar atau URL dari Google Sheets)
st.sidebar.header("📦 Data Inventaris")
item = st.sidebar.text_input("Nama Material", "Semen G-Class")
stok_saat_ini = st.sidebar.number_input("Stok di Lokasi (Ton/Unit)", value=500)
pemakaian = st.sidebar.number_input("Pemakaian per Hari", value=45)
jarak_depo = st.sidebar.number_input("Jarak ke Gudang Pusat (KM)", value=250)

# 4. HASIL ANALISIS AI
sisa_hari = hitung_resiko(stok_saat_ini, pemakaian, jarak_depo, weather_data['condition'])

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.metric("Estimasi Stok Bertahan", f"{sisa_hari} Hari")

with col_res2:
    if sisa_hari <= 3:
        st.error("STATUS: 🔴 KRITIS (Segera Mobilisasi)")
    elif sisa_hari <= 7:
        st.warning("STATUS: 🟡 WASPADA (Siapkan Re-order)")
    else:
        st.success("STATUS: 🟢 AMAN")

# 5. Visualisasi Tabel
st.subheader("📋 Ringkasan Monitoring Logistik")
df = pd.DataFrame({
    "Item": [item, "Pipa Bor 5\"", "Diesel Fuel"],
    "Stok": [stok_saat_ini, 120, 2500],
    "Cuaca Lapangan": [weather_data['condition']] * 3,
    "Sisa Hari (Prediksi)": [sisa_hari, 12.5, 8.2]
})
st.dataframe(df, use_container_width=True)
