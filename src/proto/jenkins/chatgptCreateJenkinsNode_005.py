import argparse
import jenkins
import requests
import xml.etree.ElementTree as ET
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec


# ------------------------------------------------------------
# SSH KEY HANDLING
# ------------------------------------------------------------
def generate_keys(key_type="rsa", key_size=2048, passphrase=None):
    if key_type == "rsa":
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend(),
        )
    elif key_type == "ed25519":
        private_key = ed25519.Ed25519PrivateKey.generate()
    elif key_type == "ecdsa":
        private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
    else:
        raise ValueError("Unsupported key type")

    encryption = (
        serialization.BestAvailableEncryption(passphrase.encode())
        if passphrase
        else serialization.NoEncryption()
    )

    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        encryption,
    ).decode()

    public_pem = private_key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
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
# CREDENTIAL CREATION (RAW XML)
# ------------------------------------------------------------
def add_ssh_private_key_credential(
    server,
    credential_id,
    username,
    private_key,
    key_passphrase,
    description,
):
    root = ET.Element(
        "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
        {"plugin": "ssh-credentials"},
    )

    ET.SubElement(root, "scope").text = "GLOBAL"
    ET.SubElement(root, "id").text = credential_id
    ET.SubElement(root, "description").text = description
    ET.SubElement(root, "username").text = username
    ET.SubElement(root, "passphrase").text = key_passphrase or ""

    pk_source = ET.SubElement(
        root,
        "privateKeySource",
        {
            "class": (
                "com.cloudbees.jenkins.plugins.sshcredentials.impl."
                "BasicSSHUserPrivateKey$DirectEntryPrivateKeySource"
            )
        },
    )

    ET.SubElement(pk_source, "privateKey").text = private_key

    xml_payload = ET.tostring(root, encoding="utf-8")

    response = requests.post(
        f"{server.server}/credentials/store/system/domain/_/createCredentials",
        auth=(server.username, server.password),
        headers={"Content-Type": "application/xml"},
        data=xml_payload,
    )

    if response.status_code not in (200, 201, 302):
        raise RuntimeError(
            f"Credential creation failed: {response.status_code} {response.text}"
        )

    print(f"Credential '{credential_id}' ensured")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Create or update Jenkins node (kind + launcher aware)"
    )

    # Jenkins auth
    parser.add_argument("--url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)

    # Node
    parser.add_argument("--node-name", required=True, help="Name of the Jenkins node")
    parser.add_argument("--host", required=True, help="Agent host IP or hostname")
    parser.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    parser.add_argument("--remote-fs", default="/home/jenkins", help="Remote root directory on agent")
    parser.add_argument("--labels", default="linux", help="Labels for the node")
    parser.add_argument("--executors", type=int, default=1, help="Number of executors")
    parser.add_argument("--exclusive", action="store_true", help="Restrict node to jobs with matching labels only")

    # SSH user, launcher, kind, credentials
    parser.add_argument("--ssh-user", default="jenkins", help="SSH username for connecting to the agent")
    parser.add_argument("--launcher", choices=["ssh", "jnlp"], default="ssh",
                        help="Launch method for the node (ssh or jnlp)")
    parser.add_argument(
        "--kind",
        default="hudson.slaves.DumbSlave",
        help="Node kind/class (default: hudson.slaves.DumbSlave)",
    )

    # Credentials / keys
    parser.add_argument("--credential-id", help="Use an existing Jenkins credential ID instead of inline private key")
    parser.add_argument("--use-existing-key", help="Path to existing private key file")
    parser.add_argument("--update-node-with-existing-key", action="store_true")

    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa",
                        help="Type of SSH key to generate (ignored if --use-existing-key or --credential-id is set)")
    parser.add_argument("--key-size", type=int, default=2048,
                        help="RSA key size (ignored for ed25519/ecdsa)")
    parser.add_argument("--key-file", default="id_key",
                        help="Base filename for generated keys (private and public)")
    parser.add_argument("--key-passphrase", help="Passphrase for the key")

    args = parser.parse_args()

    server = jenkins.Jenkins(
        args.url,
        username=args.user,
        password=args.password,
    )

    # --------------------------------------------------------
    # UPDATE EXISTING NODE (SSH ONLY)
    # --------------------------------------------------------
    if args.update_node_with_existing_key:
        if args.launcher != "ssh":
            raise ValueError("Updating node credentials only applies to SSH launcher")
        if not args.use_existing_key or not args.credential_id:
            raise ValueError("Update requires --use-existing-key and --credential-id")

        private_pem = load_existing_key(args.use_existing_key)

        add_ssh_private_key_credential(
            server,
            args.credential_id,
            args.ssh_user,
            private_pem,
            args.key_passphrase,
            f"Updated SSH key for node {args.node_name}",
        )

        server.reconfig_node(
            name=args.node_name,
            launcher=jenkins.LAUNCHER_SSH,
            launcher_params={
                "host": args.host,
                "port": args.port,
                "username": args.ssh_user,
                "credentialsId": args.credential_id,
            },
        )

        print(f"Node '{args.node_name}' updated")
        return

    # --------------------------------------------------------
    # CREATE NODE
    # --------------------------------------------------------
    if args.launcher == "ssh":
        if not args.credential_id:
            raise ValueError("--credential-id required for SSH launcher")

        if args.use_existing_key:
            private_pem = load_existing_key(args.use_existing_key)
        else:
            private_pem, public_pem = generate_keys(
                args.key_type, args.key_size, args.key_passphrase
            )
            save_keys(args.key_file, private_pem, public_pem)
            print("Add public key to agent ~/.ssh/authorized_keys")

        launcher_type = jenkins.LAUNCHER_SSH
        launcher_params = {
            "host": args.host,
            "port": args.port,
            "username": args.ssh_user,
        }

    else:  # JNLP
        launcher_type = jenkins.LAUNCHER_JNLP
        launcher_params = {}
        private_pem = None

    server.create_node(
        name=args.node_name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labels=args.labels,
        exclusive=args.exclusive,
        launcher=launcher_type,
        launcher_params=launcher_params,
        nodeDescription="Created via automation",
    )

    print(f"Node '{args.node_name}' created (launcher={args.launcher}, kind={args.kind})")

    # --------------------------------------------------------
    # SSH CREDENTIAL + ATTACH
    # --------------------------------------------------------
    if args.launcher == "ssh":
        add_ssh_private_key_credential(
            server,
            args.credential_id,
            args.ssh_user,
            private_pem,
            args.key_passphrase,
            f"SSH key for node {args.node_name}",
        )

        server.reconfig_node(
            name=args.node_name,
            launcher=jenkins.LAUNCHER_SSH,
            launcher_params={
                "host": args.host,
                "port": args.port,
                "username": args.ssh_user,
                "credentialsId": args.credential_id,
            },
        )

        print(f"Credential attached to node '{args.node_name}'")


if __name__ == "__main__":
    main()

