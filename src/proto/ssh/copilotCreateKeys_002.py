import argparse
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec
from cryptography.hazmat.backends import default_backend
import sys

def generate_ssh_key(key_type="RSA", key_size=2048, filename="id_key"):
    """
    Generate SSH keys of different types.
    
    Parameters:
        key_type (str): "RSA", "ED25519", or "ECDSA"
        key_size (int): Key size (only for RSA/ECDSA)
        filename (str): Base filename for output
    """
    if key_type.upper() == "RSA":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
    elif key_type.upper() == "ED25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
    elif key_type.upper() == "ECDSA":
        private_key = ec.generate_private_key(
            ec.SECP256R1(),  # You can choose other curves like SECP384R1
            backend=default_backend()
        )
    else:
        raise ValueError("Unsupported key type. Use RSA, ED25519, or ECDSA.")

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    # format changed to OpenSSH above per brave AI, it's
    # a more modern approach to the previous code.

    # Serialize public key in OpenSSH format
    public_key = private_key.public_key()
    public_ssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )

    # Save to files
    with open(filename, "wb") as f:
        f.write(private_pem)
    with open(filename + ".pub", "wb") as f:
        f.write(public_ssh)

    print(f"{key_type} SSH keys generated: {filename} (private), {filename}.pub (public)")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create authentication tokens for jenkins user")

    parser.add_argument('--enc-type', '-e', type=str, default="RSA", help='Name of the user to create a token for')

    parser.add_argument('--token-name', '-n', type=str, default="", help='Name of the key pair')

    parser.add_argument('--input-password', '-i', action='store_true', default=False, help='Ask for a password or token for authentication')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not args.token_name:
        parser.print_help()
        sys.exit(1)

    if args.input_password: 
        credential = getpass.getpass("Enter valid api-token")
    else:
        credential = ""

    edFilename = f"id_{args.token_name}_ed"
    # Examples:
    generate_ssh_key("RSA", 2048, f"id_{args.token_name}_rsa")       # RSA 4096-bit
    generate_ssh_key("ed25519", filename=edFilename)                 # Ed25519
    generate_ssh_key("ECDSA", 384, f"id_{args.token_name}_ecdsa")    # ECDSA with 384-bit curve

