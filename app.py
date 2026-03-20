import streamlit as st
import pandas as pd
import requests
from flask import Flask, request, jsonify
import threading

# --- BAGIAN 1: LOGIKA PREDIKSI AI (TIDAK BERUBAH) ---
def calculate_prediction(data):
    weather = data.get('weather', 'Clear')
    usage_rate = float(data.get('usage', 1))
    current_stock = float(data.get('stock', 0))
    distance = float(data.get('distance', 0))
    
    if weather in ['Rain', 'Thunderstorm', 'Drizzle', 'Squall']:
        weather_multiplier = 1.5 
    elif weather in ['Clouds', 'Fog', 'Mist']:
        weather_multiplier = 1.2
    else:
        weather_multiplier = 1.0
        
    travel_risk_days = (distance / 480) * weather_multiplier
    predicted_days = (current_stock / usage_rate) - travel_risk_days
    
    if predicted_days <= 2:
        status = "🔴 KRITIS"
    elif predicted_days <= 5:
        status = "🟡 WASPADA"
    else:
        status = "🟢 AMAN"
        
    return {"predicted_days": round(max(0, predicted_days), 1), "status": status}

# --- BAGIAN 2: FLASK API (UNTUK GOOGLE APPS SCRIPT) ---
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def api_predict():
    result = calculate_prediction(request.json)
    return jsonify(result)

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Jalankan Flask di thread terpisah agar tidak mengganggu Streamlit
threading.Thread(target=run_flask, daemon=True).start()

# --- BAGIAN 3: DASHBOARD STREAMLIT (UI UNTUK JURI) ---
st.set_page_config(page_title="Sivita Logistics AI", layout="wide")

st.title("🚢 Smart Logistics Dashboard - Hulu Migas 2026")
st.write("Sistem Prediksi Rantai Pasok Berbasis AI & Cuaca Real-time")

# Sidebar untuk Input Manual (Simulasi)
st.sidebar.header("Input Simulasi Lapangan")
item_name = st.sidebar.text_input("Nama Barang", "Pipa Bor 5\"")
stock = st.sidebar.number_input("Stok Saat Ini", value=100)
usage = st.sidebar.number_input("Pemakaian per Hari", value=10)
dist = st.sidebar.number_input("Jarak ke Depo (KM)", value=250)
weather_input = st.sidebar.selectbox("Kondisi Cuaca", ["Clear", "Rain", "Clouds", "Thunderstorm"])

if st.sidebar.button("Hitung Prediksi"):
    res = calculate_prediction({
        "weather": weather_input,
        "usage": usage,
        "stock": stock,
        "distance": dist
    })
    
    # Menampilkan Hasil dalam Metric Card
    col1, col2 = st.columns(2)
    col1.metric("Estimasi Sisa Hari", f"{res['predicted_days']} Hari")
    col2.metric("Status Resiko", res['status'])
    
    if "KRITIS" in res['status']:
        st.error(f"Peringatan: Stok {item_name} hampir habis. Segera lakukan pengiriman!")
    else:
        st.success(f"Kondisi stok {item_name} terpantau stabil.")

# Menampilkan Tabel Monitoring (Contoh Data)
st.subheader("📊 Monitoring Real-time Seluruh Item")
df_sample = pd.DataFrame({
    'Item': ['Pipa Bor', 'Semen G-Class', 'Fuel Diesel'],
    'Stok': [120, 500, 2000],
    'Status': ['🟢 AMAN', '🟡 WASPADA', '🟢 AMAN']
})
st.table(df_sample)
