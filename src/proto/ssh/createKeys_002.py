from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import paramiko
from io import StringIO

# 1. Generate Ed25519 key
private_key = ed25519.Ed25519PrivateKey.generate()

# 2. Export in PEM format (this is key!)
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.OpenSSH,   # ← still OpenSSH but PEM-wrapped
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

# 3. Load into Paramiko via StringIO (no file needed)
key_file = StringIO(private_pem)
paramiko_key = paramiko.Ed25519Key.from_private_key(key_file)

print("Paramiko Ed25519Key loaded successfully!")
print("Public key base64:", paramiko_key.get_base64())

# Bonus: also get public key for authorized_keys
public_bytes = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.OpenSSH,
    format=serialization.PublicFormat.OpenSSH
).decode('utf-8').strip()
print("Public key line:", public_bytes + " jenkins-agent@auto")


