from Crypto.PublicKey import RSA

def generate_keypair(name):
    key = RSA.generate(2048)
    with open(f"{name}_private.pem", "wb") as f:
        f.write(key.export_key())
    with open(f"{name}_public.pem", "wb") as f:
        f.write(key.publickey().export_key())
    print(f"✅ Generated keys for {name}")

if __name__ == "__main__":
    generate_keypair("carA")
    generate_keypair("carB")
