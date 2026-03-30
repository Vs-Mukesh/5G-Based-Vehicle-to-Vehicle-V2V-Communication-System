import json, time, threading, base64
import socketio
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

CAR_NAME = "carA"  # change to carB for second client
TARGET_CAR = "carB" if CAR_NAME=="carA" else "carA"

NUM_ANTENNAS = 4
SEND_INTERVAL = 0.5

with open(f"{CAR_NAME}_private.pem","rb") as f:
    PRIV_KEY = RSA.import_key(f.read())

sio = socketio.Client()
sio.connect("http://localhost:5000")

sio.emit("register", {"car_name": CAR_NAME})

def sign_message(obj):
    msg_bytes = json.dumps(obj, sort_keys=True).encode()
    h = SHA256.new(msg_bytes)
    signature = pkcs1_15.new(PRIV_KEY).sign(h)
    return base64.b64encode(signature).decode()

def send_data():
    while True:
        for speed in range(20,101,20):
            for ant in range(NUM_ANTENNAS):
                payload = {
                    "from": CAR_NAME,
                    "to": TARGET_CAR,
                    "antenna": ant,
                    "ts": int(time.time()*1000),
                    "speed": speed,
                    "distance": max(1,12-speed//10)
                }
                payload["signature"] = sign_message(payload)
                payload["pub_id"] = CAR_NAME
                sio.emit("v2v_msg", payload)
                print(f"🚗 Sent: {payload}")
                time.sleep(SEND_INTERVAL)

@sio.on("v2v_relay")
def on_relay(data):
    print(f"📥 Received from {data['from']}: speed={data['speed']} dist={data['distance']}")

@sio.on("security_alert")
def on_alert(data):
    print("🚨 SECURITY ALERT:", data)

if __name__ == "__main__":
    threading.Thread(target=send_data, daemon=True).start()
    while True:
        time.sleep(1)
