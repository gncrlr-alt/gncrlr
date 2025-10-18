from flask import Flask, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# Stabile Doviz-API-Links
BANK_APIS = {
    "akbank": {
        "eur": "https://api.doviz.com/api/v1/bank/akbank/EUR",
        "gold": "https://api.doviz.com/api/v1/bank/akbank/GA"
    },
    "isbank": {
        "eur": "https://api.doviz.com/api/v1/bank/is-bankasi/EUR",
        "gold": "https://api.doviz.com/api/v1/bank/is-bankasi/GA"
    },
    "ziraat": {
        "eur": "https://api.doviz.com/api/v1/bank/ziraat-bankasi/EUR",
        "gold": "https://api.doviz.com/api/v1/bank/ziraat-bankasi/GA"
    }
}

def get_data(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        j = r.json()

        alis = j.get("buying")
        satis = j.get("selling")
        updated = j.get("updateDate")

        if updated:
            ts = datetime.fromtimestamp(updated / 1000).strftime("%d.%m.%Y %H:%M:%S")
        else:
            ts = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        return {
            "alis": alis,
            "satis": satis,
            "time": ts
        }

    except Exception as e:
        return {"error": str(e)}

@app.route("/latest")
def latest():
    result = {}
    for bank, urls in BANK_APIS.items():
        result[bank] = {
            "eur": get_data(urls["eur"]),
            "gold": get_data(urls["gold"])
        }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
