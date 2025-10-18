from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

BANKS = {
    "akbank": "https://kur.doviz.com/akbank",
    "isbank": "https://kur.doviz.com/is-bankasi",
    "ziraat": "https://kur.doviz.com/ziraat-bankasi"
}

def get_rates(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        eur_alis = eur_satis = None
        gold_alis = gold_satis = None

        # Suche gezielt nach den data-socket-key Attributen für EUR und GA (Gram Altın)
        eur_row = soup.find("tr", {"data-socket-key": "EUR"})
        gold_row = soup.find("tr", {"data-socket-key": "GA"})

        if eur_row:
            cols = eur_row.find_all("td")
            if len(cols) >= 3:
                eur_alis = cols[1].get_text(strip=True)
                eur_satis = cols[2].get_text(strip=True)

        if gold_row:
            cols = gold_row.find_all("td")
            if len(cols) >= 3:
                gold_alis = cols[1].get_text(strip=True)
                gold_satis = cols[2].get_text(strip=True)

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
