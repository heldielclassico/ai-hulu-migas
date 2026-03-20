/**
 * KONFIGURASI SIVITA LOGISTIK
 */
const CONFIG = {
  // Pastikan ini adalah URL dashboard Streamlit Anda yang sudah di-deploy
  STREAMLIT_URL: "https://ai-hulu-migas-8qpvdw5dkwrqyh4hut8xcq.streamlit.app/",
  SHEET_NAME: "Logistik_Hulu"
};

/**
 * Membuat Menu di Google Sheets
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('🚀 SIVITA PANEL')
      .addItem('Kirim Data ke Dashboard', 'bukaDashboardStreamlit')
      .addToUi();
}

/**
 * Membuka Dashboard dan Mengirim ID Spreadsheet
 */
function bukaDashboardStreamlit() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME);
  
  if (!sheet) {
    SpreadsheetApp.getUi().alert("Error: Nama sheet harus '" + CONFIG.SHEET_NAME + "' agar data terbaca.");
    return;
  }

  const ssId = ss.getId();
  // Mengirim ID spreadsheet sebagai parameter URL
  const finalUrl = CONFIG.STREAMLIT_URL + "?sheet_id=" + ssId;
  
  const html = `
    <script>
      window.open('${finalUrl}', '_blank');
      google.script.host.close();
    </script>
  `;
  const modal = HtmlService.createHtmlOutput(html).setHeight(10).setWidth(10);
  SpreadsheetApp.getUi().showModalDialog(modal, "Menghubungkan ke AI Dashboard...");
}import streamlit as st
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
    multipliers = {
        'Rain': 1.6, 'Thunderstorm': 2.2, 'Drizzle': 1.3, 
        'Clouds': 1.1, 'Clear': 1.0, 'Mist': 1.4
    }
    f_cuaca = multipliers.get(cuaca, 1.0)
    
    # Rumus: (Stok/Pakai) - (Jarak / Kecepatan Terkoreksi Cuaca)
    # Asumsi kecepatan dasar logistik adalah 400 unit per hari
    waktu_tiba = jarak / (400 / f_cuaca)
    sisa_hari = (stok / pakai) - waktu_tiba
    return round(max(0, sisa_hari), 1)

# --- UI DASHBOARD ---
st.title("🚢 Sivita Smart-Logistics Dashboard")
st.subheader("Monitoring Rantai Pasok Hulu Migas Real-time")

# Ambil sheet_id dari URL secara dinamis
query_params = st.query_params
sheet_id = query_params.get("sheet_id")

if sheet_id:
    # Mengonversi ID agar bisa dibaca sebagai CSV
    url_csv = f"https://docs.google.com/spreadsheets/d/141fCBIbinmZHj3UAHXadkhbyArZnaf5x7sRRudVMvdE/gviz/tq?tqx=out:csv"
    
    try:
        # 1. Baca Seluruh Data dari Sheets
        df = pd.read_csv(url_csv)
        
        # 2. Ambil Cuaca Saat Ini
        weather_now = get_live_weather()
        st.info(f"☁️ **Cuaca Lokasi Saat Ini:** {weather_now} | Data disinkronkan otomatis.")

        # 3. Proses Analisis
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

        # 5. Tampilkan Metrics
        kritis = len(df[df['Status AI'] == "🔴 KRITIS"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Material", f"{len(df)} Item")
        c2.metric("Status Kritis", f"{kritis} Item", delta="-Bahaya" if kritis > 0 else "Aman", delta_color="inverse")
        c3.metric("Kondisi Cuaca", weather_now)

        st.divider()

        # 6. Tampilkan Tabel Utama
        st.subheader("📋 Laporan Analisis Stok & Distribusi")
        st.dataframe(
            df[['Nama Barang', 'Stok Saat Ini', 'Pemakaian Harian', 'Prediksi Sisa (Hari)', 'Status AI']], 
            use_container_width=True,
            hide_index=True
        )

    except Exception as e:
        st.error(f"Gagal memuat data. Pastikan Google Sheets Anda diatur ke 'Anyone with the link can view'.")
else:
    st.warning("Menunggu sinkronisasi... Silakan klik 'Kirim Data' dari Google Sheets Anda.")

st.caption("Sivita AI v3.0 - Integrated with OpenWeather & Google Cloud")
