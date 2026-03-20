import streamlit as st
import pandas as pd
import requests
import io

# --- KONFIGURASI ---
OPENWEATHER_API_KEY = "5763dfff82611a8770bccfca6b1b75f0"
LAT = "-0.5000" 
LON = "115.0000"

st.set_page_config(page_title="Sivita Smart-Logistics", layout="wide", page_icon="🚢")

def get_live_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res['weather'][0]['main']
    except:
        return "Clear"

def hitung_status_ai(stok, pakai, jarak, cuaca):
    multipliers = {'Rain': 1.6, 'Thunderstorm': 2.2, 'Drizzle': 1.3, 'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.4}
    f_cuaca = multipliers.get(cuaca, 1.0)
    # Proteksi pembagi nol
    if pakai <= 0: return 99
    waktu_tiba = jarak / (400 / f_cuaca)
    sisa_hari = (stok / pakai) - waktu_tiba
    return round(max(0, sisa_hari), 1)

st.title("🚢 Sivita Smart-Logistics Dashboard")
st.subheader("Monitoring Rantai Pasok Hulu Migas Real-time")

query_params = st.query_params
sheet_id = query_params.get("sheet_id")

if sheet_id:
    url_csv = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    
    try:
        # 1. Ambil data mentah
        response = requests.get(url_csv)
        response.encoding = 'utf-8'
        raw_text = response.text
        
        # 2. Baca CSV dengan penanganan tanda kutip ganda
        df = pd.read_csv(io.StringIO(raw_text), quotechar='"', skipinitialspace=True)
        
        # 3. Bersihkan nama kolom dari spasi atau karakter aneh
        df.columns = df.columns.str.strip().str.replace('"', '')

        # Tentukan kolom yang wajib ada
        cols_needed = ['Nama Barang', 'Stok Saat Ini', 'Pemakaian Harian', 'Jarak ke Gudang (KM)']
        
        if all(col in df.columns for col in cols_needed):
            # 4. Paksa konversi ke angka (karena di gambar Anda data terbungkus kutip)
            for col in ['Stok Saat Ini', 'Pemakaian Harian', 'Jarak ke Gudang (KM)']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            weather_now = get_live_weather()
            st.info(f"☁️ **Cuaca Lokasi Saat Ini:** {weather_now} | Data Terhubung.")

            # 5. Hitung Prediksi
            df['Sisa (Hari)'] = df.apply(lambda r: hitung_status_ai(
                r['Stok Saat Ini'], r['Pemakaian Harian'], r['Jarak ke Gudang (KM)'], weather_now
            ), axis=1)

            def label_status(hari):
                if hari <= 3: return "🔴 KRITIS"
                if hari <= 7: return "🟡 WASPADA"
                return "🟢 AMAN"
            df['Status AI'] = df['Sisa (Hari)'].apply(label_status)

            # Metrics Summary
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Material", f"{len(df)} Item")
            c2.metric("Status Kritis", len(df[df['Status AI'] == "🔴 KRITIS"]))
            c3.metric("Kondisi Cuaca", weather_now)

            st.divider()
            
            # Tampilkan Tabel
            st.dataframe(
                df[['Nama Barang', 'Stok Saat Ini', 'Pemakaian Harian', 'Jarak ke Gudang (KM)', 'Sisa (Hari)', 'Status AI']], 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.error(f"Kolom tidak cocok! Kolom yang terbaca: {list(df.columns)}")
            st.write("Cek apakah baris pertama di Google Sheets adalah Header.")

    except Exception as e:
        st.error(f"Kesalahan sistem: {e}")
else:
    st.warning("Menunggu data dari Google Sheets... Silakan klik menu '🚀 SIVITA PANEL'.")

st.caption("Sivita AI v3.0")
