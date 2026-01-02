import time
import requests
import json
import threading
from flask import Flask
from datetime import datetime

# --- RENDER KAPANMAMA AYARI ---
app = Flask('')
@app.route('/')
def home(): return "Bot Aktif!"
def run_flask(): app.run(host='0.0.0.0', port=10000)

# --- AYARLAR ---
TOKEN = '8136294651:AAGXvud2Hc3yv45zlw4gUkSIpQz0xfhAhw8'
CHAT_ID = '8136294651' # Sadece rakamlar!
URL = "https://api.hyperliquid.xyz/info"

def main_bot():
    print(f"🚀 Detayli Takip Botu Baslatildi: {datetime.now()}")
    sent_positions = set() # Tekrar mesaj atmamak icin

    while True:
        try:
            # 1. Tum kasalari cek
            vaults_res = requests.post(URL, json={"type": "allVaults"}).json()
            
            for vault in vaults_res:
                vault_addr = vault['vaultAddr']
                vault_name = vault.get('name', 'Bilinmeyen')

                # 2. Her kasanin icindeki acik pozisyonlari tara
                details = requests.post(URL, json={"type": "vaultDetails", "user": vault_addr}).json()
                
                # Pozisyon verisine ulas (Path: details -> respects -> positions)
                positions = details.get('resents', {}).get('assetPositions', [])

                for pos in positions:
                    p = pos.get('position', {})
                    coin = p.get('coin')
                    pnl = float(p.get('unrealizedPnl', 0))
                    
                    # KRITER: Sadece -100$ ve alti zararları yakala
                    pos_id = f"{vault_addr}_{coin}_{pnl}" # Benzersiz kimlik
                    
                    if pnl < -100 and pos_id not in sent_positions:
                        entry_price = float(p.get('entryPx', 0))
                        current_price = float(p.get('returnPx', 0))
                        side = "🟢 LONG" if float(p.get('szi', 0)) > 0 else "🔴 SHORT"
                        
                        msg = (
                            f"🚨 *TERSTE (Hyperliquid)*\n\n"
                            f"{coin} {side}\n"
                            f"👤 {vault_name}\n"
                            f"🔗 [Detay](https://app.hyperliquid.xyz/vaults/{vault_addr})\n\n"
                            f"Entry: {entry_price:.4f}\n"
                            f"Price: {current_price:.4f}\n"
                            f"PnL: {pnl:,.2f}$\n"
                            f"🕒 {datetime.now().strftime('%H:%M:%S')}"
                        )
                        
                        # Telegram'a gonder
                        tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                        requests.post(tg_url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown", "disable_web_page_preview": True})
                        
                        sent_positions.add(pos_id)
                        print(f"🔔 Bildirim: {vault_name} - {coin} ({pnl}$)")

        except Exception as e:
            print(f"⚠️ Hata olustu: {e}")
        
        time.sleep(60) # Her dakika kontrol et

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main_bot()


