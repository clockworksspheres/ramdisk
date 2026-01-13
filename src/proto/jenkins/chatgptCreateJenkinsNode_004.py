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
# CREDENTIAL CREATION (RAW XML – FIXES TypeError)
# ------------------------------------------------------------
def add_ssh_private_key_credential(
    server,
    credential_id,
    username,
    private_key,
    key_passphrase,
    description,
):
    """
    Create SSH private key credential using Jenkins REST XML API.
    This avoids python-jenkins serialization bugs.
    """

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
        description="Create or update Jenkins SSH agent with proper credential handling"
    )

    # Jenkins auth
    parser.add_argument("--url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True, help="Jenkins password or API token")

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

    # Credentials / keys
    parser.add_argument("--credential-id", required=True)
    parser.add_argument("--use-existing-key")
    parser.add_argument("--update-node-with-existing-key", action="store_true")

    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa")
    parser.add_argument("--key-size", type=int, default=2048)
    parser.add_argument("--key-file", default="id_jenkins")
    parser.add_argument("--key-passphrase")

    args = parser.parse_args()

    # --------------------------------------------------------
    # CONNECT TO JENKINS
    # --------------------------------------------------------
    server = jenkins.Jenkins(
        args.url,
        username=args.user,
        password=args.password,
    )

    # --------------------------------------------------------
    # UPDATE EXISTING NODE
    # --------------------------------------------------------
    if args.update_node_with_existing_key:
        if not args.use_existing_key:
            raise ValueError("--update-node-with-existing-key requires --use-existing-key")

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
    if args.use_existing_key:
        private_pem = load_existing_key(args.use_existing_key)
    else:
        private_pem, public_pem = generate_keys(
            args.key_type, args.key_size, args.key_passphrase
        )
        save_keys(args.key_file, private_pem, public_pem)
        print("Public key must be added to agent ~/.ssh/authorized_keys")

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
            "username": args.ssh_user,
        },
        nodeDescription="Created via automation",
    )

    print(f"Node '{args.node_name}' created")

    # --------------------------------------------------------
    # CREATE CREDENTIAL + ATTACH
    # --------------------------------------------------------
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

