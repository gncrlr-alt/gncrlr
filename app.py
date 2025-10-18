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

        def extract_value(row_selector):
            row = soup.select_one(row_selector)
            if not row:
                return None, None, None
            cols = row.find_all("td")
            if len(cols) >= 3:
                alis = cols[1].text.strip().replace(".", "").replace(",", ".")
                satis = cols[2].text.strip().replace(".", "").replace(",", ".")
                time_tag = soup.select_one("time")
                time_val = time_tag.text.strip() if time_tag else None
                return alis, satis, time_val
            return None, None, None

        # Euro (EUR) & Gram Altın (GA / A02)
        eur_alis, eur_satis, eur_time = extract_value("tr[data-code='EUR']")
        gold_alis, gold_satis, gold_time = extract_value("tr[data-code='GA']")

        return {
            "eur": {"alis": eur_alis, "satis": eur_satis, "time": eur_time},
            "gold": {"alis": gold_alis, "satis": gold_satis, "time": gold_time}
        }

    except Exception as e:
        return {"error": str(e)}

@app.route("/latest")
def latest():
    data = {}
    for bank, url in BANK_URLS.items():
        data[bank] = parse_bank(url)
    data["checked_at"] = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
