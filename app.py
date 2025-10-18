from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

BANK_URLS = {
    "akbank": "https://kur.doviz.com/akbank",
    "isbank": "https://kur.doviz.com/is-bankasi",
    "ziraat": "https://kur.doviz.com/ziraat-bankasi"
}

def parse_bank(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        def get_value(label):
            el = soup.find("td", string=label)
            if el and el.find_next("td"):
                return el.find_next("td").text.strip()
            return None

        eur_alis = get_value("EUR")
        gold_alis = get_value("Gram Altın")

        return {
            "eur": eur_alis,
            "gold": gold_alis
        }

    except Exception as e:
        return {"error": str(e)}

@app.route("/latest")
def latest():
    data = {bank: parse_bank(url) for bank, url in BANK_URLS.items()}
    data["checked_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
