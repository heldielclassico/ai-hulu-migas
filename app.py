from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        weather = data.get('weather', 'Clear')
        usage_rate = float(data.get('usage', 1))
        current_stock = float(data.get('stock', 0))
        distance = float(data.get('distance', 0))
        
        # BUMBU CERDAS: Mapping Faktor Penghambat Distribusi (Weather Multiplier)
        # Jika hujan/badai, perjalanan logistik melambat 50% (faktor 1.5)
        if weather in ['Rain', 'Thunderstorm', 'Drizzle', 'Squall']:
            weather_multiplier = 1.5 
        elif weather in ['Clouds', 'Fog', 'Mist']:
            weather_multiplier = 1.2
        else:
            weather_multiplier = 1.0
            
        # Perhitungan estimasi waktu tempuh logistik (Asumsi truk 60km/jam)
        # Ditambah faktor hambatan cuaca
        travel_risk_days = (distance / 480) * weather_multiplier # 480km = estimasi jarak tempuh truk/hari
        
        # Prediksi Sisa Hari = (Stok/Pakai) - Resiko Perjalanan
        predicted_days = (current_stock / usage_rate) - travel_risk_days
        
        # Penentuan Status
        if predicted_days <= 2:
            status = "🔴 KRITIS: Stok Segera Habis & Jalur Terhambat"
        elif predicted_days <= 5:
            status = "🟡 WASPADA: Re-order Sekarang"
        else:
            status = "🟢 AMAN: Stok Mencukupi"

        return jsonify({
            "predicted_days": round(max(0, predicted_days), 1),
            "status": status
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
