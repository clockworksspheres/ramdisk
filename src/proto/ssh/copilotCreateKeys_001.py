from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

# 1. Generate a new RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,  # You can use 4096 for stronger security
    backend=default_backend()
)

# 2. Serialize the private key in PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# 3. Serialize the public key in OpenSSH format
public_key = private_key.public_key()
public_ssh = public_key.public_bytes(
    encoding=serialization.Encoding.OpenSSH,
    format=serialization.PublicFormat.OpenSSH
)

# 4. Save keys to files
with open("id_rsa", "wb") as f:
    f.write(private_pem)

with open("id_rsa.pub", "wb") as f:
    f.write(public_ssh)

print("SSH keys generated: id_rsa (private), id_rsa.pub (public)")


