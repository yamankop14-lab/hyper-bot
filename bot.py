import time
import requests
import json
from datetime import datetime

# --- AYARLAR ---
TOKEN = '8136294651:AAGXvud2Hc3yv45zlw4gUkSIpQz0xfhAhw8'
CHAT_ID = '@VULCI_TERS_BOT'
URL = "https://api.hyperliquid.xyz/info"

def main():
    print(f"🚀 Bot profesyonel modda baslatildi: {datetime.now()}")
    sent_notifications = set()

    # Sunucu engelini asmak icin en iyi tarayici kimligi
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
    }

    while True:
        try:
            # En temiz veri paketi
            payload = {"type": "allVaults"}
            response = requests.post(URL, data=json.dumps(payload), headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Basarili: {len(data)} kasa tarandi.")
                
                for vault in data:
                    try:
                        # PnL verisini cek
                        pnl = float(vault['pnlHistory'][-1][1])
                        addr = vault['vaultAddr']
                        
                        # KRITER: -100$ zarar
                        if pnl < -100 and addr not in sent_notifications:
                            name = vault.get('name', 'Bilinmeyen')
                            msg = f"🚨 *ZARARDAKI TRADER*\n\nKasa: {name}\nPnL: {pnl:,.2f} USDT\n[Detay](https://app.hyperliquid.xyz/vaults/{addr})"
                            
                            # Telegram'a gonder
                            tg_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
                            requests.post(tg_url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
                            
                            sent_notifications.add(addr)
                            print(f"🔔 Bildirim gonderildi: {name}")
                    except: continue
            else:
                print(f"❌ Sunucu Engeli (422). IP Adresiniz bloklu. Durum: {response.status_code}")

        except Exception as e:
            print(f"❌ Baglanti hatasi: {e}")

        time.sleep(120) # 2 dakikada bir kontrol

if __name__ == "__main__":
    main()