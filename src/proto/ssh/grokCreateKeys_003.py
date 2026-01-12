from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from pathlib import Path
from datetime import datetime

# ==================== CONFIG ====================
KEY_DIR = Path.home() / ".ssh" / "jenkins_agents"
KEY_DIR.mkdir(parents=True, exist_ok=True)

NODE_NAME = "linux-build-01"
PRIVATE_KEY_PATH = KEY_DIR / f"agent_{NODE_NAME}_{datetime.now():%Y%m%d}"
PUBLIC_KEY_PATH  = PRIVATE_KEY_PATH.with_suffix(".pub")
# ===============================================

def generate_and_save_ed25519_keys():
    private_key = ed25519.Ed25519PrivateKey.generate()

    # === PRIVATE KEY: PEM-wrapped OpenSSH format (this is the correct combo) ===
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,                # ← Must be PEM
        format=serialization.PrivateFormat.OpenSSH,         # ← OpenSSH format inside PEM
        encryption_algorithm=serialization.NoEncryption()
    )

    # === PUBLIC KEY: standard OpenSSH single-line format ===
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    public_str = public_bytes.decode('utf-8').strip() + f" jenkins-agent-{NODE_NAME} {datetime.now():%Y-%m-%d}"

    # Save files
    PRIVATE_KEY_PATH.write_bytes(private_pem)
    PRIVATE_KEY_PATH.chmod(0o600)

    PUBLIC_KEY_PATH.write_text(public_str + "\n")
    PUBLIC_KEY_PATH.chmod(0o644)

    print(f"Keys saved successfully:")
    print(f"  Private key (PEM + OpenSSH format): {PRIVATE_KEY_PATH}")
    print(f"  Public key  (standard OpenSSH line): {PUBLIC_KEY_PATH}\n")

    print("Private key starts with:\n-----BEGIN OPENSSH PRIVATE KEY----- ...")
    print("This format is fully compatible with recent Paramiko + Jenkins SSH credentials.\n")

    return private_pem.decode('utf-8'), public_str


# Run it
private_key_content, public_key_line = generate_and_save_ed25519_keys()

# Optional: quick Paramiko load test
import paramiko
from io import StringIO

key_file_like = StringIO(private_key_content)
paramiko_key = paramiko.Ed25519Key.from_private_key(key_file_like)
print("Paramiko successfully parsed the key ✓")
print(f"Fingerprint: {paramiko_key.get_fingerprint().hex()}")


