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

        # Alle Währungszeilen suchen
        rows = soup.select("table tbody tr")

        eur_alis = eur_satis = None
        gold_alis = gold_satis = None

        for row in rows:
            cells = [c.text.strip() for c in row.find_all("td")]
            if not cells or len(cells) < 3:
                continue
            name = cells[0].lower()
            if "eur" in name:
                eur_alis = cells[1]
                eur_satis = cells[2]
            elif "gram altın" in name or "gram" in name:
                gold_alis = cells[1]
                gold_satis = cells[2]

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
