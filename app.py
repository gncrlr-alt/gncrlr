from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

BANKS = {
    "akbank": "https://www.doviz.com/altin/akbank",
    "isbank": "https://www.doviz.com/altin/is-bankasi",
    "ziraat": "https://www.doviz.com/altin/ziraat-bankasi"
}

def parse_bank(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        def get_value(key):
            el = soup.find("span", {"data-socket-key": key})
            if el:
                return el.text.strip().replace(".", "").replace(",", ".")
            return None

        eur_alis = get_value("EUR_ALIS")
        eur_satis = get_value("EUR_SATIS")
        gold_alis = get_value("GA_ALIS")
        gold_satis = get_value("GA_SATIS")
        time_el = soup.find("div", {"class": "market-time"})
        time = time_el.text.strip() if time_el else "unknown"

        return {
            "eur_alis": float(eur_alis) if eur_alis else None,
            "eur_satis": float(eur_satis) if eur_satis else None,
            "gold_alis": float(gold_alis) if gold_alis else None,
            "gold_satis": float(gold_satis) if gold_satis else None,
            "time": time
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/latest")
def latest():
    data = {"date": datetime.now().strftime("%d.%m.%Y")}
    for bank, url in BANKS.items():
        data[bank] = parse_bank(url)
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
