from flask import Flask, request, jsonify
from hashlib import sha256
import requests

app = Flask(__name__)
SECRET_KEY = "92ojdYYqpSyf07VuOsDDisk4N"
USER_ID = "307488"
API_BASE_URL = "https://user-api.neverlose.cc/api/market/give-for-free"

def generate_signature(data, secret):
    sorted_data = "".join([f"{key}{data[key]}" for key in sorted(data)])
    return sha256((sorted_data + secret).encode()).hexdigest()

def validate_signature(data, secret):
    received_signature = data.pop("signature", None)
    expected_signature = generate_signature(data, secret)
    return received_signature == expected_signature

def deliver_item(username, item_code):
    payload = {
        "user_id": USER_ID,
        "id": "unique_request_id",
        "username": username,
        "code": item_code,
    }
    payload["signature"] = generate_signature(payload, SECRET_KEY)
    response = requests.post(API_BASE_URL, json=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"HTTP {response.status_code}", "details": response.text}

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    if not validate_signature(data, SECRET_KEY):
        return jsonify({"error": "Invalid signature"}), 400
    if data.get("kind") == "purchase":
        username = data.get("username")
        item_code = data.get("item_id")
        if username and item_code:
            result = deliver_item(username, item_code)
            return jsonify({"status": "success", "result": result}), 200
        else:
            return jsonify({"error": "Missing username or item_id"}), 400
    return jsonify({"error": "Unhandled event type"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
