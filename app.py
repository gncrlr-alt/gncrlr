from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

BANKS = {
    "akbank": "https://api.doviz.com/api/v1/bank/akbank",
    "isbank": "https://api.doviz.com/api/v1/bank/is-bankasi",
    "ziraat": "https://api.doviz.com/api/v1/bank/ziraat-bankasi"
}

def get_rates(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        data = r.json()

        eur = data["currencies"].get("EUR", {})
        gold = data["currencies"].get("GA", {})

        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        return {
            "eur": {
                "alis": eur.get("alis"),
                "satis": eur.get("satis"),
                "time": now
            },
            "gold": {
                "alis": gold.get("alis"),
                "satis": gold.get("satis"),
                "time": now
            }
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/latest")
def latest():
    result = {}
    for bank, url in BANKS.items():
        result[bank] = get_rates(url)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
