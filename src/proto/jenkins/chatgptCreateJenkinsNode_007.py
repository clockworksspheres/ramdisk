#!/usr/bin/env python3
import argparse
import requests
import jenkins
import xml.etree.ElementTree as ET
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec
import json

# ------------------------
# SSH key handling
# ------------------------
def generate_keys(key_type="rsa", key_size=2048):
    if key_type == "rsa":
        key = rsa.generate_private_key(65537, key_size, default_backend())
    elif key_type == "ed25519":
        key = ed25519.Ed25519PrivateKey.generate()
    elif key_type == "ecdsa":
        key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    else:
        raise ValueError("Unsupported key type")

    private_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.TraditionalOpenSSL,
        serialization.NoEncryption()
    ).decode()

    public_pem = key.public_key().public_bytes(
        serialization.Encoding.OpenSSH,
        serialization.PublicFormat.OpenSSH
    ).decode()

    return private_pem, public_pem

# ------------------------
# Jenkins SSH credential via REST
# ------------------------
def create_ssh_credential(jenkins_url, user, token, cred_id, ssh_user, private_key):
    url = f"{jenkins_url}/credentials/store/system/domain/_/createCredentials"
    payload = {
        "": "0",
        "credentials": {
            "scope": "GLOBAL",
            "id": cred_id,
            "username": ssh_user,
            "privateKeySource": {
                "stapler-class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
                "privateKey": private_key
            },
            "description": f"SSH key for node",
            "$class": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey"
        }
    }
    r = requests.post(url, auth=(user, token), headers={"Content-Type": "application/json"}, data=json.dumps(payload))
    if r.status_code in (200, 204):
        print(f"✅ Credential '{cred_id}' created successfully!")
    elif "already exists" in r.text.lower():
        print(f"⚠ Credential '{cred_id}' already exists, skipping creation")
    else:
        print("❌ Failed to create credential:", r.status_code, r.text)
        r.raise_for_status()

# ------------------------
# Main
# ------------------------
def main():
    parser = argparse.ArgumentParser(description="Create Jenkins node with SSH key")
    parser.add_argument("--url", required=True, help="Jenkins URL")
    parser.add_argument("--user", required=True, help="Jenkins username")
    parser.add_argument("--token", required=True, help="Jenkins API token")
    parser.add_argument("--node-name", required=True, help="Node/agent name")
    parser.add_argument("--host", required=True, help="Agent host/IP")
    parser.add_argument("--port", type=int, default=22, help="SSH port")
    parser.add_argument("--remote-fs", default="/home/jenkins", help="Agent remote FS root")
    parser.add_argument("--labels", default="linux", help="Node labels")
    parser.add_argument("--executors", type=int, default=1, help="Number of executors")
    parser.add_argument("--ssh-user", default="jenkins", help="SSH username")
    parser.add_argument("--credential-id", required=True, help="Jenkins credential ID")
    parser.add_argument("--use-existing-key", help="Path to existing private key file")
    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa", help="Key type")
    parser.add_argument("--key-file", default="id_key", help="Base filename for generated keys")
    args = parser.parse_args()

    # ------------------------
    # Load or generate key
    # ------------------------
    if args.use_existing_key:
        private_key = Path(args.use_existing_key).read_text()
        print(f"Using existing key: {args.use_existing_key}")
    else:
        private_key, public_key = generate_keys(args.key_type)
        Path(args.key_file).write_text(private_key)
        Path(args.key_file + ".pub").write_text(public_key)
        print("=== Generated SSH Key ===")
        print(f"Private key: {args.key_file}")
        print(f"Public key: {args.key_file}.pub")
        print("\nAdd public key to agent ~/.ssh/authorized_keys\n")

    # ------------------------
    # Create Jenkins credential
    # ------------------------
    create_ssh_credential(
        args.url, args.user, args.token,
        args.credential_id, args.ssh_user, private_key
    )

    # ------------------------
    # Connect to Jenkins
    # ------------------------
    server = jenkins.Jenkins(args.url, args.user, args.token)

    # ------------------------
    # Create node (without launcher)
    # ------------------------
    if args.node_name not in server.get_nodes():
        server.create_node(
            args.node_name,
            numExecutors=args.executors,
            remoteFS=args.remote_fs,
            labels=args.labels,
            nodeDescription="Created via Python script",
        )
        print(f"✅ Node '{args.node_name}' created")
    else:
        print(f"⚠ Node '{args.node_name}' already exists, skipping creation")

    # ------------------------
    # Patch XML for SSH launcher
    # ------------------------
    xml = server.get_node_config(args.node_name)
    root = ET.fromstring(xml)
    launcher = root.find("launcher")
    launcher.attrib["class"] = "hudson.slaves.SSHLauncher"

    def set_tag(tag, value):
        el = launcher.find(tag)
        if el is None:
            el = ET.SubElement(launcher, tag)
        el.text = str(value)

    set_tag("host", args.host)
    set_tag("port", args.port)
    set_tag("credentialsId", args.credential_id)
    set_tag("launchTimeoutSeconds", 60)

    server.reconfig_node(args.node_name, ET.tostring(root, encoding="unicode"))
    print(f"✅ Node '{args.node_name}' configured with SSH launcher")

if __name__ == "__main__":
    main()

