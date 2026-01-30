import argparse
import jenkins
import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec

# ------------------------------
# SSH Key Generation
# ------------------------------
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
        format=serialization.PrivateFormat.PKCS8,  # PKCS8 works for all types
        encryption_algorithm=serialization.NoEncryption()
    ).decode("utf-8")

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
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

# ------------------------------
# Jenkins Credential Creation
# ------------------------------
def get_crumb(jenkins_url, user, password):
    """Fetch Jenkins CSRF crumb if required."""
    crumb_url = f"{jenkins_url}/crumbIssuer/api/json"
    resp = requests.get(crumb_url, auth=(user, password))
    if resp.status_code == 200:
        data = resp.json()
        return {data["crumbRequestField"]: data["crumb"]}
    return {}

def create_ssh_credentials(jenkins_url, user, password, credential_id, ssh_user, private_key, description="SSH Key"):
    """Create SSH credentials in Jenkins using the Credentials plugin REST API."""
    xml_payload = f"""
<com.cloudbees.plugins.credentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@1.18">
  <scope>GLOBAL</scope>
  <id>{credential_id}</id>
  <description>{description}</description>
  <username>{ssh_user}</username>
  <privateKeySource class="com.cloudbees.plugins.credentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey>{private_key}</privateKey>
  </privateKeySource>
</com.cloudbees.plugins.credentials.impl.BasicSSHUserPrivateKey>
    """

    url = f"{jenkins_url}/credentials/store/system/domain/_/createCredentials"
    headers = {"Content-Type": "application/xml"}
    headers.update(get_crumb(jenkins_url, user, password))

    response = requests.post(
        url,
        data=xml_payload,
        auth=(user, password),
        headers=headers
    )

    if response.status_code == 200:
        print(f"Credential '{credential_id}' created successfully in Jenkins.")
    else:
        print(f"Failed to create credential: {response.status_code} {response.text}")

# ------------------------------
# Main
# ------------------------------
def main():
    parser = argparse.ArgumentParser(description="Create Jenkins node with SSH key or credentials")
    parser.add_argument("--url", required=True, help="Jenkins URL (e.g. http://localhost:8080)")
    parser.add_argument("--user", required=True, help="Jenkins username")
    parser.add_argument("--password", required=True, help="Jenkins password or API token")
    parser.add_argument("--node-name", required=True, help="Name of the Jenkins node")
    parser.add_argument("--host", required=True, help="Agent host IP or hostname")
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

    # SSH user, launcher, kind, credentials
    parser.add_argument("--ssh-user", default="jenkins", help="SSH username for connecting to the agent")
    parser.add_argument("--launcher", choices=["ssh", "jnlp"], default="ssh",
                        help="Launch method for the node (ssh or jnlp)")
    parser.add_argument("--kind", default="hudson.slaves.DumbSlave",
                        help="Node kind (default: hudson.slaves.DumbSlave)")
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

        # Create Jenkins credential
        cred_id = f"{args.node_name}-ssh"
        create_ssh_credentials(
            jenkins_url=args.url,
            user=args.user,
            password=args.password,
            credential_id=cred_id,
            ssh_user=args.ssh_user,
            private_key=private_pem,
            description=f"SSH key for {args.node_name}"
        )
        args.credential_id = cred_id

    # Connect to Jenkins
    server = jenkins.Jenkins(args.url, username=args.user, password=args.password)

    # Map launcher string to python-jenkins constant
    if args.launcher == "ssh":
        launcher_type = jenkins.LAUNCHER_SSH
        launcher_params = {
            "host": args.host,
            "port": args.port,
            "username": args.ssh_user,
            "credentialsId": args.credential_id,
        }
    elif args.launcher == "jnlp":
        launcher_type = jenkins.LAUNCHER_JNLP
        launcher_params = {}
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
        nodeDescription="Created via python-jenkins"
    )

    print(f"Node '{args.node_name}' created successfully!")

if __name__ == "__main__":
    main()

