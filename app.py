from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# 1️⃣ Neue Funktion, um alle Bankdaten direkt von der Doviz-Hauptseite zu holen
def get_bank_rates():
    url = "https://www.doviz.com"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Datenstruktur für die drei Banken
    data = {"akbank": {}, "isbank": {}, "ziraat": {}}

    # Jede Bankzeile auf der Seite finden
    rows = soup.find_all("tr")
    for row in rows:
        text = row.get_text(strip=True).lower()

        # AKBANK
        if "akbank" in text:
            cols = row.find_all("td")
            if len(cols) >= 3:
                data["akbank"]["alis"] = cols[1].text.strip()
                data["akbank"]["satis"] = cols[2].text.strip()

        # İŞBANK
        if "işbank" in text or "isbank" in text:
            cols = row.find_all("td")
            if len(cols) >= 3:
                data["isbank"]["alis"] = cols[1].text.strip()
                data["isbank"]["satis"] = cols[2].text.strip()

        # ZİRAAT
        if "ziraat" in text:
            cols = row.find_all("td")
            if len(cols) >= 3:
                data["ziraat"]["alis"] = cols[1].text.strip()
                data["ziraat"]["satis"] = cols[2].text.strip()

    return data


# 2️⃣ Route für /latest
@app.route("/latest")
def latest():
    try:
        rates = get_bank_rates()
        date = datetime.now().strftime("%d.%m.%Y")
        return jsonify({"date": date, **rates})
    except Exception as e:
        return jsonify({"error": str(e)})


# 3️⃣ Start für Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
