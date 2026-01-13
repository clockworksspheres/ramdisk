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

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
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
    parser = argparse.ArgumentParser(description="Create Jenkins node with SSH key or credentials")
    parser.add_argument("--url", required=True, help="Jenkins URL (e.g. http://localhost:8080)")
    parser.add_argument("--user", required=True, help="Jenkins username")
    parser.add_argument("--password", required=True, help="Jenkins password or API token")
    parser.add_argument("--node-name", required=True, help="Name of the Jenkins node")
    parser.add_argument("--host", help="Agent host IP or hostname (required for SSH)")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--remote-fs", default="/home/jenkins", help="Remote root directory on agent")
    parser.add_argument("--labels", default="linux", help="Labels for the node")
    parser.add_argument("--executors", type=int, default=1, help="Number of executors")
    parser.add_argument("--exclusive", action="store_true", help="Restrict node to jobs with matching labels only")

    # Key options
    parser.add_argument("--use-existing-key", help="Path to existing private key file")
    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa",
                        help="Type of SSH key to generate (ignored if --use-existing-key or --credential-id is set)")
    parser.add_argument("--key-size", type=int, default=2048,
                        help="RSA key size (ignored for ed25519/ecdsa)")
    parser.add_argument("--key-file", default="id_key",
                        help="Base filename for generated keys (private and public)")

    # SSH user, launcher, credentials
    parser.add_argument("--ssh-user", default="jenkins", help="SSH username for connecting to the agent")
    parser.add_argument("--launcher", choices=["ssh", "jnlp"], default="ssh",
                        help="Launch method for the node (ssh or jnlp)")
    parser.add_argument("--credential-id", help="Use an existing Jenkins credential ID instead of inline private key")

    args = parser.parse_args()

    private_pem = None
    public_pem = None

    if args.credential_id:
        print(f"Using Jenkins credential ID: {args.credential_id}")
    elif args.use_existing_key:
        private_pem = load_existing_key(args.use_existing_key)
        print(f"Using existing private key from: {args.use_existing_key}")
    else:
        private_pem, public_pem = generate_keys(args.key_type, args.key_size)
        save_keys(args.key_file, private_pem, public_pem)
        print("=== Generated SSH Keys ===")
        print(f"Private key saved to: {args.key_file}")
        print(f"Public key saved to: {args.key_file}.pub")
        print("\nAdd the public key to agent ~/.ssh/authorized_keys.\n")

    # Connect to Jenkins
    server = jenkins.Jenkins(args.url, username=args.user, password=args.password)

    # Map launcher string to python-jenkins constant
    if args.launcher == "ssh":
        if not args.host:
            raise ValueError("Host must be specified for SSH launcher")
        launcher_type = jenkins.LAUNCHER_SSH
        if args.credential_id:
            launcher_params = {
                "host": args.host,
                "port": args.port,
                "username": args.ssh_user,
                "credentialsId": args.credential_id,
            }
        else:
            launcher_params = {
                "host": args.host,
                "port": args.port,
                "username": args.ssh_user,
                "privatekey": private_pem,
            }
    elif args.launcher == "jnlp":
        launcher_type = jenkins.LAUNCHER_JNLP
        launcher_params = {}  # JNLP agents connect back, so fewer params here
    else:
        raise ValueError("Unsupported launcher type")

    # Create node
    server.create_node(
        name=args.node_name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labels=args.labels,
        exclusive=args.exclusive,
        launcher=launcher_type,
        launcher_params=launcher_params,
        nodeDescription="Created via python-jenkins",
    )

    print(f"Node '{args.node_name}' created successfully!")

if __name__ == "__main__":
    main()


