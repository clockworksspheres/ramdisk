import argparse
import jenkins
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec


# ------------------------------------------------------------
# SSH KEY HANDLING
# ------------------------------------------------------------
def generate_keys(key_type="rsa", key_size=2048):
    if key_type == "rsa":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
    elif key_type == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
    elif key_type == "ecdsa":
        private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
    else:
        raise ValueError("Unsupported key type")

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ).decode()

    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()

    return private_pem, public_pem


def save_keys(filename, private_pem, public_pem):
    with open(filename, "w") as f:
        f.write(private_pem)
    with open(filename + ".pub", "w") as f:
        f.write(public_pem)


def load_existing_key(filename):
    with open(filename) as f:
        return f.read()


# ------------------------------------------------------------
# JENKINS CREDENTIAL CREATION
# ------------------------------------------------------------
def add_ssh_private_key_credential(
    server,
    credential_id,
    username,
    private_key,
    description="SSH key added via python-jenkins",
    passphrase=""
):
    credentials = {
        "scope": "GLOBAL",
        "id": credential_id,
        "username": username,
        "description": description,
        "passphrase": passphrase,
        "privateKeySource": {
            "stapler-class":
                "com.cloudbees.jenkins.plugins.sshcredentials.impl."
                "BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
            "privateKey": private_key,
        },
        "stapler-class":
            "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
        "$class":
            "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
    }

    try:
        server.create_credential(domain="_", credentials=credentials)
        print(f"Credential '{credential_id}' created")
    except jenkins.JenkinsException:
        print(f"Credential '{credential_id}' already exists (skipped)")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Create Jenkins node with SSH key and credentials"
    )

    # Jenkins
    parser.add_argument("--url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)

    # Node
    parser.add_argument("--node-name", required=True)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--remote-fs", default="/home/jenkins")
    parser.add_argument("--labels", default="linux")
    parser.add_argument("--executors", type=int, default=1)
    parser.add_argument("--exclusive", action="store_true")

    # SSH
    parser.add_argument("--ssh-user", default="jenkins")
    parser.add_argument("--launcher", choices=["ssh", "jnlp"], default="ssh")

    # Keys
    parser.add_argument("--use-existing-key")
    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa")
    parser.add_argument("--key-size", type=int, default=2048)
    parser.add_argument("--key-file", default="id_jenkins")

    # Credentials
    parser.add_argument("--credential-id")
    parser.add_argument("--create-credential", action="store_true")

    args = parser.parse_args()

    private_pem = None
    public_pem = None

    # --------------------------------------------------------
    # KEY SELECTION
    # --------------------------------------------------------
    if args.use_existing_key:
        private_pem = load_existing_key(args.use_existing_key)
        print(f"Loaded existing key: {args.use_existing_key}")
    elif args.create_credential:
        private_pem, public_pem = generate_keys(args.key_type, args.key_size)
        save_keys(args.key_file, private_pem, public_pem)
        print(f"Generated SSH key: {args.key_file}")
        print("Add public key to agent ~/.ssh/authorized_keys")
    elif not args.credential_id:
        raise ValueError(
            "You must supply --credential-id or --create-credential"
        )

    # --------------------------------------------------------
    # CONNECT TO JENKINS
    # --------------------------------------------------------
    server = jenkins.Jenkins(
        args.url,
        username=args.user,
        password=args.password
    )

    # --------------------------------------------------------
    # CREATE CREDENTIAL (OPTIONAL)
    # --------------------------------------------------------
    if args.create_credential:
        if not args.credential_id:
            raise ValueError("--create-credential requires --credential-id")

        add_ssh_private_key_credential(
            server=server,
            credential_id=args.credential_id,
            username=args.ssh_user,
            private_key=private_pem,
            description=f"SSH key for node {args.node_name}",
        )

    # --------------------------------------------------------
    # NODE LAUNCHER
    # --------------------------------------------------------
    if args.launcher == "ssh":
        launcher = jenkins.LAUNCHER_SSH
        launcher_params = {
            "host": args.host,
            "port": args.port,
            "username": args.ssh_user,
        }

        if args.credential_id:
            launcher_params["credentialsId"] = args.credential_id
        else:
            launcher_params["privatekey"] = private_pem
    else:
        launcher = jenkins.LAUNCHER_JNLP
        launcher_params = {}

    # --------------------------------------------------------
    # CREATE NODE
    # --------------------------------------------------------
    server.create_node(
        name=args.node_name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labels=args.labels,
        exclusive=args.exclusive,
        launcher=launcher,
        launcher_params=launcher_params,
        nodeDescription="Created via python-jenkins",
    )

    print(f"Node '{args.node_name}' created successfully")


if __name__ == "__main__":
    main()

