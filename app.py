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

        eur_alis = None
        gold_alis = None

        # Suche nach Tabellenzeilen mit EUR oder Gram Altın
        for tr in soup.find_all("tr"):
            tds = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(tds) >= 3:
                if "EUR" in tds[0]:
                    eur_alis = tds[1]
                elif "Gram Altın" in tds[0] or "Gram Altin" in tds[0]:
                    gold_alis = tds[1]

        # Wenn Gold noch nicht gefunden, zusätzliche Suche (manche Seiten haben separaten Bereich)
        if not gold_alis:
            gold_section = soup.find_all("div", class_="item")
            for item in gold_section:
                if "Gram Altın" in item.get_text() or "Gram Altin" in item.get_text():
                    span = item.find("span", class_="value")
                    if span:
                        gold_alis = span.get_text(strip=True)
                        break

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
