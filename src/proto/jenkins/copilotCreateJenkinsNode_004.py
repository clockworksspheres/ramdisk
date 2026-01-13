#!/usr/bin/env python3
import argparse
import jenkins
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec

def generate_keys(key_type="rsa", key_size=2048):
    """Generate SSH key pair of given type and return (private_pem, public_pem)."""
    if key_type.lower() == "rsa":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
    elif key_type.lower() == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
    elif key_type.lower() == "ecdsa":
        private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
    else:
        raise ValueError("Unsupported key type. Choose rsa, ed25519, or ecdsa.")

    #####
    # Use OpenSSH instead of TraditionalOpenSSL as TraditionalSSL is outdated,
    # and doesn't work with ed25519
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode("utf-8")

    return private_pem, public_pem

def save_keys(filename, private_pem, public_pem):
    """Save private and public keys to files."""
    with open(filename, "w") as f:
        f.write(private_pem)
    with open(filename + ".pub", "w") as f:
        f.write(public_pem)

def load_existing_key(filename):
    """Load an existing private key from file."""
    with open(filename, "r") as f:
        private_pem = f.read()
    return private_pem

def main():
    parser = argparse.ArgumentParser(description="Create Jenkins node with SSH key")
    parser.add_argument("--url", default="http://localhost:8080", help="Jenkins URL (e.g. http://localhost:8080)")
    parser.add_argument("--user", "-u", required=True, help="Jenkins username")
    parser.add_argument("--password", help="Jenkins password or API token")
    parser.add_argument("--node-name", "-n", required=True, help="Name of the Jenkins node")
    parser.add_argument("--host", required=True, help="Agent host IP or hostname")
    parser.add_argument("--port", "-p", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--remote-fs", default="/home/jenkins/jenkins-agent", help="Remote root directory on agent")
    parser.add_argument("--labels", "-l", required=True, help="Labels for the node")
    parser.add_argument("--executors", "-e", type=int, default=1, help="Number of executors")
    parser.add_argument("--exclusive", action="store_true", help="Restrict node to jobs with matching labels only")

    # Key options
    parser.add_argument("--use-existing-key", help="Path to existing private key file")
    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa", help="Type of SSH key to generate (ignored if --use-existing-key is set)")
    parser.add_argument("--key-size", type=int, default=2048, help="RSA key size (ignored for ed25519/ecdsa)")
    parser.add_argument("--key-file", default="id_key", help="Base filename for generated keys (private and public)")

    args = parser.parse_args()

    if args.use_existing_key:
        # Load existing private key
        private_pem = load_existing_key(args.use_existing_key)
        public_pem = None
        print(f"Using existing private key from: {args.use_existing_key}")
    else:
        # Generate new keys
        private_pem, public_pem = generate_keys(args.key_type, args.key_size)
        save_keys(args.key_file, private_pem, public_pem)
        print("=== Generated SSH Keys ===")
        print(f"Private key saved to: {args.key_file}")
        print(f"Public key saved to: {args.key_file}.pub")
        print("\nAdd the public key to agent ~/.ssh/authorized_keys.\n")

    # Connect to Jenkins
    server = jenkins.Jenkins(args.url, username=args.user, password=args.password)

    # Create node
    server.create_node(
        name=args.node_name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labels=args.labels,
        exclusive=args.exclusive,
        launcher=jenkins.LAUNCHER_SSH,
        launcher_params={
            "host": args.host,
            "port": args.port,
            "username": "jenkins",   # adjust if different user on agent
            "privatekey": private_pem,
        }
    )

    print(f"Node '{args.node_name}' created successfully!")

if __name__ == "__main__":
    main()

