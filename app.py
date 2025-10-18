from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# -------------------------------------------------
#  Funktion: Bankkurse (Akbank, İşbank, Ziraat)
# -------------------------------------------------
def get_bank_rates():
    url = "https://www.doviz.com"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    data = {"akbank": {}, "isbank": {}, "ziraat": {}}

    for row in soup.select("tr"):
        text = row.get_text(strip=True).lower()
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        # Nur Spalten mit Zahlen (verhindert %-Werte)
        numeric_cols = [c.text.strip() for c in cols if any(ch.isdigit() for ch in c.text)]
        if len(numeric_cols) < 2:
            continue

        if "akbank" in text:
            data["akbank"]["alis"] = numeric_cols[0]
            data["akbank"]["satis"] = numeric_cols[1]

        if "işbank" in text or "isbank" in text:
            data["isbank"]["alis"] = numeric_cols[0]
            data["isbank"]["satis"] = numeric_cols[1]

        if "ziraat" in text:
            data["ziraat"]["alis"] = numeric_cols[0]
            data["ziraat"]["satis"] = numeric_cols[1]

    return data


# -------------------------------------------------
#  Route /latest
# -------------------------------------------------
@app.route("/latest")
def latest():
    try:
        rates = get_bank_rates()
        date = datetime.now().strftime("%d.%m.%Y")
        return jsonify({"date": date, **rates})
    except Exception as e:
        return jsonify({"error": str(e)})


# -------------------------------------------------
#  Render Startbefehl
# -------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
