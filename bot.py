import time
import requests
import json
import threading
from flask import Flask
from datetime import datetime

# --- RENDER İÇİN SAHTE SUNUCU (BOTUN KAPANMAMASI İÇİN) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Aktif ve Tarama Yapıyor!"

def run_flask():
    app.run(host='0.0.0.0', port=10000) # Render bu portu bekler

# --- BOT AYARLARI ---
TOKEN = '8136294651:AAGXvud2Hc3yv45zlw4gUkSIpQz0xfhAhw8'
CHAT_ID = '@VULCI_TERS_BOT'
URL = "https://api.hyperliquid.xyz/info"

def main_bot():
    print(f"🚀 Bot taramaya basladi: {datetime.now()}")
    sent_notifications = set()
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    }

    while True:
        try:
            payload = {"type": "allVaults"}
            response = requests.post(URL, data=json.dumps(payload), headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Tarama basarili: {len(data)} kasa kontrol edildi.")
                for vault in data:
                    try:
                        pnl = float(vault['pnlHistory'][-1][1])
                        addr = vault['vaultAddr']
                        if pnl < -100 and addr not in sent_notifications:
                            name = vault.get('name', 'Bilinmeyen')
                            msg = f"🚨 *TERSTE KALAN TRADER*\n\nKasa: {name}\nPnL: {pnl:,.2f} USDT\n[Detay](https://app.hyperliquid.xyz/vaults/{addr})"
                            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            requests.post(tg_url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                            sent_notifications.add(addr)
                    except: continue
            else:
                print(f"⚠️ Sunucu yanit vermedi (422/500). Bekleniyor...")
        except Exception as e:
            print(f"❌ Hata: {e}")
        
        time.sleep(120)

if __name__ == "__main__":
    # Flask sunucusunu arka planda baslat
    threading.Thread(target=run_flask).start()
    # Ana bot döngüsünü baslat
    main_bot()
