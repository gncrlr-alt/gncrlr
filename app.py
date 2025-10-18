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
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Finde die Kurszeilen (z.B. EUR und Gram Altın)
        rows = soup.find_all("tr")

        eur_alis = None
        gold_alis = None

        for row in rows:
            cols = [c.text.strip() for c in row.find_all("td")]
            if len(cols) >= 3:
                if "EUR" in cols[0]:
                    eur_alis = cols[1]
                elif "Gram Altın" in cols[0]:
                    gold_alis = cols[1]

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
