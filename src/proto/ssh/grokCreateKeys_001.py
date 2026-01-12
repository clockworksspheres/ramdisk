from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import base64
import os

def generate_ed25519_key_pair(private_key_path="jenkins_agent_ed25519",
                             public_key_path=None,
                             comment="jenkins-agent@yourcompany.com"):
    """
    Generate Ed25519 SSH key pair (recommended in 2025+)
    Returns: (private_key_str, public_key_str)
    """
    # Generate private key
    private_key = ed25519.Ed25519PrivateKey.generate()

    # Private key in OpenSSH format (unencrypted)
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_str = private_bytes.decode('utf-8')

    # Public key in OpenSSH format
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    public_str = public_bytes.decode('utf-8').strip() + f" {comment}\n"

    # Save to files (optional but recommended)
    os.makedirs(os.path.dirname(private_key_path) or '.', exist_ok=True)
    with open(private_key_path, "w") as f:
        f.write(private_str)
    os.chmod(private_key_path, 0o600)  # Very important!

    if public_key_path is None:
        public_key_path = private_key_path + ".pub"

    with open(public_key_path, "w") as f:
        f.write(public_str)

    print(f"Ed25519 keys generated:\n  Private: {private_key_path}\n  Public:  {public_key_path}")

    return private_str, public_str


# Usage example
priv, pub = generate_ed25519_key_pair(
    private_key_path="/tmp/jenkins_agent_key",
    comment="auto-generated for Jenkins node 2026"
)

print("\nPublic key (copy to remote ~/.ssh/authorized_keys):\n")
print(pub)


