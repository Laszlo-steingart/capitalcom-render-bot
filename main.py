from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# DEINE Zugangsdaten (am besten später per Environment Variable)
API_KEY = "so8XfqEUCWHeKrf9"
API_PASSWORD = "Trading123!"
ACCOUNT_ID = "24396694"
EPIC = "BTCUSD"

BASE_URL = "https://api-capital.backend-capital.com"

def capital_login():
    """Login bei Capital.com – liefert Session-Token zurück."""
    url = f"{BASE_URL}/api/v1/session"
    payload = {
        "identifier": API_KEY,
        "password": API_PASSWORD
    }
    headers = {
        "Content-Type": "application/json",
        "X-CAP-API-KEY": API_KEY
    }
    resp = requests.post(url, json=payload, headers=headers)
    # Prüfe, ob Login ok war
    if resp.status_code == 200 and 'CST' in resp.headers and 'X-SECURITY-TOKEN' in resp.headers:
        cst = resp.headers['CST']
        sec = resp.headers['X-SECURITY-TOKEN']
        return cst, sec
    else:
        print("Login-Fehler:", resp.text)
        raise Exception("Login fehlgeschlagen: " + resp.text)

def place_limit_order(direction, price, size=0.01):
    """Platziert Limit-Order bei Capital.com nach erfolgreichem Login."""
    # 1. LOGIN holen (liefert Token)
    cst, sec = capital_login()
    # 2. Order aufgeben (mit Token!)
    headers = {
        "Content-Type": "application/json",
        "X-CAP-API-KEY": API_KEY,
        "CST": cst,
        "X-SECURITY-TOKEN": sec
    }
    order = {
        "epic": EPIC,
        "direction": direction.upper(),
        "size": size,
        "orderType": "LIMIT",
        "level": float(price),
        "currency": "USD"
    }
    print(f"Sende Order an Capital.com: {order}")
    r = requests.post(
        f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/orders/limit",
        json=order,
        headers=headers
    )
    print("Capital.com API Antwort:", r.text)
    return r.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook empfangen:", data)
    try:
        side = data.get("side")
        price = float(data.get("price"))
        size = float(data.get("size", 0.01))  # Optional im TV-Alert (sonst 0.01)
        response = place_limit_order(side, price, size)
        return jsonify(response)
    except Exception as e:
        print("Fehler im Webhook:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)

