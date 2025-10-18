from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

app = Flask(__name__)

BANKS = {
    "akbank": "https://kur.doviz.com/akbank",
    "isbank": "https://kur.doviz.com/is-bankasi",
    "ziraat": "https://kur.doviz.com/ziraat-bankasi"
}

def parse_number_tr(s):
    """Wandelt türkische Zahlen (5.123,45) → float (5123.45)"""
    s = s.strip().replace('\xa0', ' ')
    s = s.replace('.', '').replace(',', '.')
    m = re.search(r'-?\d+(\.\d+)?', s)
    return float(m.group()) if m else None

def get_rates(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        eur_alis = eur_satis = None
        gold_alis = gold_satis = None

        # NEUE Struktur – alle "currency" Blöcke durchgehen
        rows = soup.select("div.table div.table-row")

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.select("div.table-cell")]
            if len(cols) < 3:
                continue

            name = cols[0].lower()
            alis = parse_number_tr(cols[1])
            satis = parse_number_tr(cols[2])

            if not alis or not satis:
                continue

            if "eur" in name or "euro" in name:
                eur_alis, eur_satis = alis, satis

            if "gram" in name and "alt" in name:
                gold_alis, gold_satis = alis, satis

        # Plausibilitäts-Check
        if gold_alis and gold_alis < 4000:
            gold_alis = gold_satis = None

        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        return {
            "eur": {"alis": eur_alis, "satis": eur_satis, "time": now},
            "gold": {"alis": gold_alis, "satis": gold_satis, "time": now}
        }

    except Exception as e:
        return {"error": str(e)}

@app.route("/latest")
def latest():
    data = {}
    for bank, url in BANKS.items():
        data[bank] = get_rates(url)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
