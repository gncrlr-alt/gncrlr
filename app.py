from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# URLs für aktuelle doviz.com-Banken-Seiten
BANKS = {
    "akbank": "https://kur.doviz.com/banka/akbank",
    "isbank": "https://kur.doviz.com/banka/is-bankasi",
    "ziraat": "https://kur.doviz.com/banka/ziraat-bankasi"
}

def get_rates(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, timeout=10, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Euro-Kurs finden
        eur_row = soup.find("tr", {"data-vname": "EUR"})
        gold_row = soup.find("tr", {"data-vname": "GA"})

        def parse_row(row):
            if not row:
                return {"alis": None, "satis": None, "time": None}
            cols = row.find_all("td")
            if len(cols) >= 3:
                alis = cols[1].text.strip().replace(".", "").replace(",", ".")
                satis = cols[2].text.strip().replace(".", "").replace(",", ".")
                return {
                    "alis": alis,
                    "satis": satis,
                    "time": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                }
            return {"alis": None, "satis": None, "time": None}

        eur = parse_row(eur_row)
        gold = parse_row(gold_row)

        return {"eur": eur, "gold": gold}

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
