#!/usr/bin/env python3

"""
 Requirements:

The Jenkins REST API must be reachable (e.g. http://jenkins-host:8080).

You need a username + API token (or password) with admin rights.

If you’re creating credentials, the account must have “Credentials → Create” permission.

"""



import argparse
import jenkins
import requests
from requests.auth import HTTPBasicAuth
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec

def generate_keys(key_type="rsa", key_size=2048):
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
        raise ValueError("Unsupported key type")

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
    with open(filename, "w") as f:
        f.write(private_pem)
    with open(filename + ".pub", "w") as f:
        f.write(public_pem)

def load_existing_key(filename):
    with open(filename, "r") as f:
        return f.read()

def get_jenkins_crumb(jenkins_url, user, token):
    resp = requests.get(f"{jenkins_url}/crumbIssuer/api/json",
                        auth=HTTPBasicAuth(user, token))
    resp.raise_for_status()
    data = resp.json()
    return {data["crumbRequestField"]: data["crumb"]}

def create_ssh_credential(jenkins_url, user, token, cred_id, ssh_user, private_key):
    """Create SSH credential in Jenkins via REST API."""
    crumb_header = get_jenkins_crumb(jenkins_url, user, token)

    payload = {
        "": "0",
        "credentials": {
            "scope": "GLOBAL",
            "id": cred_id,
            "username": ssh_user,
            "description": "SSH key created via script",
            "$class": "com.cloudbees.plugins.credentials.impl.BasicSSHUserPrivateKey",
            "privateKeySource": {
                "$class": "com.cloudbees.plugins.credentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource",
                "privateKey": private_key
            }
        }
    }

    resp = requests.post(
        f"{jenkins_url}/credentials/store/system/domain/_/createCredentials",
        auth=HTTPBasicAuth(user, token),
        headers={**crumb_header},
        data={"json": str(payload).replace("'", '"')}
    )
    if resp.status_code not in (200, 204):
        raise Exception(f"Failed to create credential: {resp.status_code} {resp.text}")
    print(f"Credential '{cred_id}' created successfully.")

def main():
    parser = argparse.ArgumentParser(description="Create Jenkins node with SSH key or credentials")
    parser.add_argument("--url", required=True)
    parser.add_argument("--user", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--node-name", required=True)
    parser.add_argument("--host", help="Agent host (required for SSH)")
    parser.add_argument("--port", type=int, default=22)
    parser.add_argument("--remote-fs", default="/home/jenkins")
    parser.add_argument("--labels", default="linux")
    parser.add_argument("--executors", type=int, default=1)
    parser.add_argument("--exclusive", action="store_true")

    # Key/credential options
    parser.add_argument("--use-existing-key")
    parser.add_argument("--key-type", choices=["rsa", "ed25519", "ecdsa"], default="rsa")
    parser.add_argument("--key-size", type=int, default=2048)
    parser.add_argument("--key-file", default="id_key")
    parser.add_argument("--ssh-user", default="jenkins")
    parser.add_argument("--launcher", choices=["ssh", "jnlp"], default="ssh")
    parser.add_argument("--credential-id", help="Use/create Jenkins credential ID")

    args = parser.parse_args()

    private_pem = None
    public_pem = None

    if args.credential_id:
        if args.use_existing_key:
            private_pem = load_existing_key(args.use_existing_key)
            create_ssh_credential(args.url, args.user, args.password,
                                  args.credential_id, args.ssh_user, private_pem)
        else:
            private_pem, public_pem = generate_keys(args.key_type, args.key_size)
            save_keys(args.key_file, private_pem, public_pem)
            create_ssh_credential(args.url, args.user, args.password,
                                  args.credential_id, args.ssh_user, private_pem)
    elif args.use_existing_key:
        private_pem = load_existing_key(args.use_existing_key)
    else:
        private_pem, public_pem = generate_keys(args.key_type, args.key_size)
        save_keys(args.key_file, private_pem, public_pem)
        print("Generated keys. Add public key to agent ~/.ssh/authorized_keys.")

    server = jenkins.Jenkins(args.url, username=args.user, password=args.password)

    if args.launcher == "ssh":
        if not args.host:
            raise ValueError("Host must be specified for SSH launcher")
        if args.credential_id:
            launcher_type = jenkins.LAUNCHER_SSH
            launcher_params = {
                "host": args.host,
                "port": args.port,
                "username": args.ssh_user,
                "credentialsId": args.credential_id,
            }
        else:
            launcher_type = jenkins.LAUNCHER_SSH
            launcher_params = {
                "host": args.host,
                "port": args.port,
                "username": args.ssh_user,
                "privatekey": private_pem,
            }
    elif args.launcher == "jnlp":
        launcher_type = jenkins.LAUNCHER_JNLP
        launcher_params = {}
    else:
        raise ValueError("Unsupported launcher")

    server.create_node(
        name=args.node_name,
        numExecutors=args.executors,
        remoteFS=args.remote_fs,
        labels=args.labels,
        exclusive=args.exclusive,
        launcher=launcher_type,
        launcher_params=launcher_params,
        node_description="Created via script"
    )

    print(f"Node '{args.node_name}' created successfully.")

if __name__ == "__main__":
    main()

