import json, time, base64
from flask import Flask, request
from flask_socketio import SocketIO
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from ai_security import is_anomalous

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

AUTHORIZED = {}
for name in ("carA","carB"):
    with open(f"{name}_public.pem","rb") as f:
        AUTHORIZED[name] = RSA.import_key(f.read())

print("🔐 Authorized:", list(AUTHORIZED.keys()))
clients = {}

def verify_signature(pubkey, msg_bytes, signature_b64):
    try:
        h = SHA256.new(msg_bytes)
        signature = base64.b64decode(signature_b64)
        pkcs1_15.new(pubkey).verify(h, signature)
        return True
    except:
        return False

@socketio.on('register')
def handle_register(data):
    car_name = data.get("car_name")
    clients[car_name] = request.sid
    print(f"✅ Registered: {car_name}")

@socketio.on('v2v_msg')
def handle_v2v_msg(payload):
    required = ("from","to","antenna","ts","speed","distance","signature","pub_id")
    if not all(k in payload for k in required):
        print("❌ Invalid payload")
        return

    msg_fields = {k: payload[k] for k in ("from","to","antenna","ts","speed","distance")}
    msg_bytes = json.dumps(msg_fields, sort_keys=True).encode()
    pub_id = payload["pub_id"]

    if pub_id not in AUTHORIZED:
        print("❌ Unknown sender")
        return

    if not verify_signature(AUTHORIZED[pub_id], msg_bytes, payload["signature"]):
        print("❌ Signature failed")
        return

    dt = int(time.time()*1000) - int(payload["ts"])
    if is_anomalous(payload["speed"], payload["distance"], payload["antenna"], dt):
        print("🚨 ANOMALY detected from", payload["from"])
        socketio.emit("security_alert", {"from": payload["from"]})
        return

    print(f"📡 Forwarding {payload['from']} → {payload['to']}")
    target_sid = clients.get(payload["to"])
    if target_sid:
        socketio.emit("v2v_relay", msg_fields, room=target_sid)
