import time
import requests
import json
import threading
from flask import Flask
from datetime import datetime

# Render için sahte sunucu
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif!"
def run_flask(): app.run(host='0.0.0.0', port=10000)

# --- AYARLAR ---
TOKEN = '8136294651:AAGXvud2Mc3yu45z1w4gUkSIpQzOxFhAhw8' # Görseldeki Token
CHAT_ID = '8136294651' # Güncellediğin ID
URL = "https://api.hyperliquid.xyz/info"

def ana_tarama_dongusu():
    print(f"🚀 Tarama baslatildi: {datetime.now()}")
    gonderilenler = set()

    while True:
        try:
            # Tüm kasaları çek
            res = requests.post(URL, json={"type": "allVaults"}).json()
            
            for vault in res:
                v_addr = vault['vaultAddr']
                v_name = vault.get('name', 'Bilinmeyen')

                # Detaylı pozisyonları çek
                details = requests.post(URL, json={"type": "vaultDetails", "user": v_addr}).json()
                positions = details.get('resents', {}).get('assetPositions', [])

                for pos in positions:
                    p = pos.get('position', {})
                    pnl = float(p.get('unrealizedPnl', 0))
                    
                    # TEST İÇİN EŞİĞİ DÜŞÜK TUTALIM (Mesaj gelince -100 yaparsın)
                    if pnl < -10:
                        pos_id = f"{v_addr}_{p.get('coin')}"
                        if pos_id not in gonderilenler:
                            side = "🟢 LONG" if float(p.get('szi', 0)) > 0 else "🔴 SHORT"
                            msg = (
                                f"🚨 *TERSTE (Hyperliquid)*\n\n"
                                f"{p.get('coin')} {side}\n"
                                f"👤 {v_name}\n"
                                f"🔗 [Detay](https://app.hyperliquid.xyz/vaults/{v_addr})\n\n"
                                f"Entry: {float(p.get('entryPx', 0)):.4f}\n"
                                f"Price: {float(p.get('returnPx', 0)):.4f}\n"
                                f"PnL: {pnl:,.2f}$\n"
                                f"🕒 {datetime.now().strftime('%d.%m %H:%M:%S')}"
                            )
                            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                                          json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": True})
                            gonderilenler.add(pos_id)
            print("✅ Bir tur tarama bitti.")
        except Exception as e:
            print(f"⚠️ Hata: {e}")
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    ana_tarama_dongusu()
