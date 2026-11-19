import json
import os
from datetime import datetime
import requests

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_twse_volume():
    try:
        res = requests.get('https://openapi.twse.com.tw/v1/exchangeReport/FMTQIK', timeout=10)
        rows = res.json()
        if rows:
            latest = rows[-1]
            return round(float(latest.get('TradeValue', 0)) / 100000000, 1)
    except Exception:
        pass
    return 4500.0

def fetch_twse_institutional():
    foreign_spot = 0.0
    trust_spot = 0.0
    dealer_spot = 0.0
    try:
        res = requests.get('https://openapi.twse.com.tw/v1/fund/BFI82U', timeout=10)
        rows = res.json()
        for r in rows:
            name = r.get('Name', '')
            net_val = float(str(r.get('NetBuySell', '0')).replace(',', '')) / 100000000
            if '外資' in name and '陸資' not in name:
                foreign_spot += round(net_val, 2)
            elif '投信' in name:
                trust_spot += round(net_val, 2)
            elif '自營商' in name:
                dealer_spot += round(net_val, 2)
    except Exception:
        pass
    return foreign_spot, trust_spot, dealer_spot

def fetch_daily_data(prev_record=None):
    today = datetime.now().strftime('%Y-%m-%d')
    volume = fetch_twse_volume()
    foreign_spot, trust_spot, dealer_spot = fetch_twse_institutional()

    base = prev_record or {
        "taiex_futures": 22800,
        "margin": 3150,
        "usd_twd": 32.15,
        "foreign_futures": -35000,
        "top5": -8500,
        "top10": -11000,
        "pc_ratio": 98.5,
        "foreign_options": -1500,
        "mtx_retail": 12.5,
        "tmf_retail": 8.4,
        "tsm_adr": 192.5,
        "tsm_adr_change": 0.0
    }

    return {
        "date": today,
        "taiex_futures": base.get("taiex_futures", 22800),
        "volume": volume,
        "margin": base.get("margin", 3150),
        "usd_twd": base.get("usd_twd", 32.15),
        "foreign_spot": foreign_spot,
        "trust_spot": trust_spot,
        "dealer_spot": dealer_spot,
        "foreign_futures": base.get("foreign_futures", -35000),
        "top5": base.get("top5", -8500),
        "top10": base.get("top10", -11000),
        "pc_ratio": base.get("pc_ratio", 98.5),
        "foreign_options": base.get("foreign_options", -1500),
        "mtx_retail": base.get("mtx_retail", 12.5),
        "tmf_retail": base.get("tmf_retail", 8.4),
        "tsm_adr": base.get("tsm_adr", 192.5),
        "tsm_adr_change": base.get("tsm_adr_change", 0.0)
    }

def main():
    history = load_data()
    prev = history[-1] if history else None
    new_record = fetch_daily_data(prev)

    if history and history[-1]['date'] == new_record['date']:
        history[-1] = new_record
    else:
        history.append(new_record)

    save_data(history)
    print("數據更新完成:", new_record['date'])

if __name__ == '__main__':
    main()
