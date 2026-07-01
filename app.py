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
        <p style="color: #848e9c; margin: 0; font-size: 10pt;">منصة التحليل الذكي المستقلة بالكامل</p>
        
        <div class="price-box">
            <div style="color: #848e9c; font-size: 10pt;">سعر BTC/USDT اللحظي</div>
            <div id="price" class="price">0.00</div>
            <div id="badge" class="badge">جاري الاتصال بالبورصة...</div>
        </div>
        
        <div class="info-row"><span class="label">الاتجاه الحالي:</span><span id="trend" class="val">--</span></div>
        <div class="info-row"><span class="label">جني الأرباح (TP):</span><span id="tp" class="val" style="color: #0ecb81;">0.00</span></div>
        <div class="info-row"><span class="label">إيقاف الخسارة (SL):</span><span id="sl" class="val" style="color: #f6465d;">0.00</span></div>
        <div class="info-row"><span class="label">حالة المنصة:</span><span id="status" style="color: #0ecb81; font-weight: bold;">جاري ربط الويب سوكت...</span></div>
    </div>

    <script>
        let priceHistory = [];
        const WINDOW_SIZE = 8;

        // الاتصال المباشر بالويب سوكت من المتصفح بدون سيرفر بايثون!
        const ws = new WebSocket("wss://stream.binance.com:9443/ws/btcusdt@ticker");

        ws.onopen = () => {
            document.getElementById('status').innerText = "متصل مباشر بالبورصة 🟢";
            document.getElementById('status').style.color = "#0ecb81";
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const currentPrice = parseFloat(data.c);
            
            // تحديث السعر على الشاشة
            const priceElem = document.getElementById('price');
            const oldPrice = parseFloat(priceElem.innerText.replace(/,/g, '')) || 0;
            priceElem.innerText = currentPrice.toLocaleString('en-US', {minimumFractionDigits: 2});
            
            // وميض الألوان حسب الحركة
            if (currentPrice > oldPrice) priceElem.style.color = '#0ecb81';
            else if (currentPrice < oldPrice) priceElem.style.color = '#f6465d';

            // حساب الخوارزمية الذكية للاتجاه والمخاطر
            priceHistory.push(currentPrice);
            if (priceHistory.length > WINDOW_SIZE) priceHistory.shift();

            if (priceHistory.length === WINDOW_SIZE) {
                const avgPrice = priceHistory.reduce((a, b) => a + b, 0) / priceHistory.length;
                const riskPercentage = 0.01;
                const rewardPercentage = 0.02;
                
                let trend, signal, tp, sl;

                if (currentPrice > avgPrice) {
                    trend = "صاعد 📈";
                    signal = "شراء (BUY) 🟢";
                    sl = currentPrice * (1 - riskPercentage);
                    tp = currentPrice * (1 + rewardPercentage);
                    document.getElementById('badge').className = 'badge buy';
                } else {
                    trend = "هابط 📉";
                    signal = "بيع (SELL) 🔴";
                    sl = currentPrice * (1 + riskPercentage);
                    tp = currentPrice * (1 - rewardPercentage);
                    document.getElementById('badge').className = 'badge sell';
                }

                document.getElementById('trend').innerText = trend;
                document.getElementById('badge').innerText = signal;
                document.getElementById('tp').innerText = tp.toLocaleString('en-US', {minimumFractionDigits: 2});
                document.getElementById('sl').innerText = sl.toLocaleString('en-US', {minimumFractionDigits: 2});
            }
        };

        ws.onerror = () => {
            document.getElementById('status').innerText = "خطأ في الاتصال 🔴";
            document.getElementById('status').style.color = "#f6465d";
        };
    </script>
</body>
</html>
