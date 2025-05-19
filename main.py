from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# DEINE echten Zugangsdaten:
API_KEY = "so8XfqEUCWHeKrf9"
API_PASSWORD = "Trading123!"
ACCOUNT_ID = "24396694"
EPIC = "BTC/USD"  # <--- jetzt mit Slash!

BASE_URL = "https://api-capital.backend-capital.com"

def place_limit_order(direction, price, size=0.01):
    headers = {
        "Content-Type": "application/json",
        "X-CAP-API-KEY": API_KEY,
    }
    order = {
        "epic": EPIC,
        "direction": direction.upper(),   # "BUY" oder "SELL"
        "size": size,                     # Positionsgröße (Lot)
        "orderType": "LIMIT",
        "level": float(price),            # Limit-Preis
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


