from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

BANKS = {
    "akbank": "https://kur.doviz.com/serbest-piyasa/akbank",
    "isbank": "https://kur.doviz.com/serbest-piyasa/is-bankasi",
    "ziraat": "https://kur.doviz.com/serbest-piyasa/ziraat-bankasi",
}

def parse_bank(url):
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    eur_alis = soup.find("span", {"data-socket-key": "EUR_ALIS"}).text.strip().replace(".", "").replace(",", ".")
    eur_satis = soup.find("span", {"data-socket-key": "EUR_SATIS"}).text.strip().replace(".", "").replace(",", ".")
    gold_alis = soup.find("span", {"data-socket-key": "GA_ALIS"}).text.strip().replace(".", "").replace(",", ".")
    gold_satis = soup.find("span", {"data-socket-key": "GA_SATIS"}).text.strip().replace(".", "").replace(",", ".")
    time = soup.find("div", {"class": "market-time"}).text.strip().split()[-1]
    return {
        "eur_alis": round(float(eur_alis), 2),
        "eur_satis": round(float(eur_satis), 2),
        "gold_alis": round(float(gold_alis), 2),
        "gold_satis": round(float(gold_satis), 2),
        "time": time
    }

@app.route("/latest")
def latest():
    data = {}
    for key, url in BANKS.items():
        data[key] = parse_bank(url)
    data["date"] = datetime.now().strftime("%d.%m.%Y")
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
