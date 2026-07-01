import asyncio
import json
import threading
import websockets
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# قاعدة البيانات اللحظية للمنصة
market_data = {
    "price": 0.0,
    "trend": "جاري التحليل...",
    "signal": "انتظار",
    "tp": 0.0,
    "sl": 0.0
}

price_history = []
WINDOW_SIZE = 8  # سرعة استجابة الخوارزمية للحركة اللحظية

def calculate_trend_and_signals(current_price):
    global price_history
    price_history.append(current_price)
    
    if len(price_history) > WINDOW_SIZE:
        price_history.pop(0)
        
    if len(price_history) < WINDOW_SIZE:
        return "جاري جمع البيانات...", "انتظار", 0.0, 0.0

    avg_price = sum(price_history) / len(price_history)
    
    # إدارة مخاطر صارمة: 1% وقف خسارة و 2% هدف جني أرباح لحماية الأموال
    risk_percentage = 0.01 
    reward_percentage = 0.02

    if current_price > avg_price:
        trend = "صاعد 📈"
        signal = "شراء (BUY) 🟢"
        sl = current_price * (1 - risk_percentage)
        tp = current_price * (1 + reward_percentage)
    elif current_price < avg_price:
        trend = "هابط 📉"
        signal = "بيع (SELL) 🔴"
        sl = current_price * (1 + risk_percentage)
        tp = current_price * (1 - reward_percentage)
    else:
        trend = "مستقر ⚖️"
        signal = "انتظار"
        tp, sl = 0.0, 0.0

    return trend, signal, round(tp, 2), round(sl, 2)

async def btc_stream():
    # الاتصال المباشر بـ WebSocket الخاص بمنصة Binance لجلب أسعار البيتكوين الحية
    uri = "wss://stream.binance.com:9443/ws/btcusdt@ticker"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)
                    current_price = float(data['c'])
                    
                    trend, signal, tp, sl = calculate_trend_and_signals(current_price)
                    
                    market_data["price"] = current_price
                    market_data["trend"] = trend
                    market_data["signal"] = signal
                    market_data["tp"] = tp
                    market_data["sl"] = sl
                    
                    await asyncio.sleep(0.5)
        except Exception as e:
            await asyncio.sleep(3)

def start_websocket_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(btc_stream())

threading.Thread(target=start_websocket_thread, daemon=True).start()

# المسار المصلح ليتوافق مع طلب الواجهة تلقائياً لمنع خطأ 404
@app.route('/api/market-data')
def get_data():
    return jsonify(market_data)

# واجهة المستخدم الاحترافية بتصميم Dark Mode الفاخر القابل للبيع لزملائك
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MAX SYSTEM | منصة التداول الذكية</title>
    <style>
        body { font-family: sans-serif; background-color: #0b0e11; color: #eaecef; margin: 0; padding: 15px; text-align: center; }
        .container { max-width: 500px; margin: auto; background: #1e2329; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border-top: 4px solid #f0b90b; }
        h1 { color: #f0b90b; font-size: 18pt; margin-bottom: 5px; }
        .price-box { background: #161a1e; padding: 20px; border-radius: 8px; margin: 15px 0; }
        .price { font-size: 28pt; font-weight: bold; color: #0ecb81; font-family: monospace; }
        .badge { display: inline-block; padding: 6px 12px; border-radius: 20px; font-weight: bold; margin-top: 10px; font-size: 11pt; }
        .buy { background: rgba(14,203,129,0.2); color: #0ecb81; }
        .sell { background: rgba(246,70,93,0.2); color: #f6465d; }
        .info-row { display: flex; justify-content: space-between; padding: 10px; border-bottom: 1px solid #2b3139; font-size: 11pt; }
        .label { color: #848e9c; }
        .val { font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>MAX SYSTEM v1.0</h1>
        <p style="color: #848e9c; margin: 0; font-size: 10pt;">منصة التحليل الذكي وبث الأسعار اللحظي</p>
        
        <div class="price-box">
            <div style="color: #848e9c; font-size: 10pt;">سعر BTC/USDT اللحظي</div>
            <div id="price" class="price">0.00</div>
            <div id="badge" class="badge buy">جاري الاتصال...</div>
        </div>
        
        <div class="info-row"><span class="label">الاتجاه الحالي:</span><span id="trend" class="val">--</span></div>
        <div class="info-row"><span class="label">جني الأرباح (TP):</span><span id="tp" class="val" style="color: #0ecb81;">0.00</span></div>
        <div class="info-row"><span class="label">إيقاف الخسارة (SL):</span><span id="sl" class="val" style="color: #f6465d;">0.00</span></div>
        <div class="info-row"><span class="label">حالة السيرفر:</span><span style="color: #0ecb81; font-weight: bold;">نشط 🟢</span></div>
    </div>

    <script>
        async function refresh() {
            try {
                const res = await fetch('/api/market-data');
                const data = await res.json();
                document.getElementById('price').innerText = data.price.toLocaleString();
                document.getElementById('trend').innerText = data.trend;
                document.getElementById('tp').innerText = data.tp.toLocaleString();
                document.getElementById('sl').innerText = data.sl.toLocaleString();
                
                const badge = document.getElementById('badge');
                badge.innerText = data.signal;
                if(data.signal.includes('شراء')) badge.className = 'badge buy';
                else if(data.signal.includes('بيع')) badge.className = 'badge sell';
                else badge.className = 'badge';
            } catch (e) {}
        }
        setInterval(refresh, 500);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
