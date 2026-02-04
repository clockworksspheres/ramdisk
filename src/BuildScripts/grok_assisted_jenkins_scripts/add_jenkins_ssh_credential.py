#!/usr/bin/env python3
"""
Add SSH Username with private key credential to Jenkins.
Supports generating a new key OR loading from existing file.

For Git/GitHub: use --username git (common convention)
"""

import argparse
import sys
import getpass
import os
from datetime import datetime

import jenkins
from jenkins import JenkinsException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Add 'SSH Username with private key' credential to Jenkins",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:

  # 1. Generate new ed25519 key – no passphrase (quick for testing)
  python %(prog)s --url http://localhost:8080 --user admin --token 11abc... \\
    --cred-id github-ssh-deploy --username git

  # 2. Generate new key with passphrase (recommended for production)
  python %(prog)s --url https://jenkins.company.com --user roy --token xyz... \\
    --cred-id prod-server-key --username ubuntu --passphrase

  # 3. Use EXISTING private key file (most common for GitHub deploy keys)
  python %(prog)s --url http://ci.local:8080 --user admin --token 11def... \\
    --cred-id my-github-deploy-key --username git \\
    --private-key-file ~/.ssh/id_ed25519_github --description "GitHub deploy key"

  # 4. Existing encrypted key + passphrase prompt
  python %(prog)s --url http://192.168.1.150:8080 --user admin --token ... \\
    --cred-id gitlab-ssh --username git \\
    --private-key-file ./keys/id_rsa_gitlab.pem --passphrase

  # 5. RSA generation (for legacy systems)
  python %(prog)s --url http://jenkins:8080 --user admin --token ... \\
    --cred-id legacy-git --username git --type rsa --rsa-bits 4096

  Show help:
  python %(prog)s --help
        """
    )

    # Jenkins connection
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url", required=True, help="Jenkins URL (include http:// or https://)")
    conn.add_argument("--user", required=True, help="Jenkins username with Credentials/Create permission")
    conn.add_argument("--token", required=True, help="Jenkins API token")

    # Credential details
    cred = parser.add_argument_group("Credential details (required)")
    cred.add_argument("--cred-id", required=True, help="Unique ID for the credential (e.g. github-deploy-key-2026)")
    cred.add_argument("--username", required=True, help="SSH username – use 'git' for Git/GitHub/GitLab")
    cred.add_argument("--description", default=f"Added {datetime.now():%Y-%m-%d}", help="Description in Jenkins")

    # Key source – mutually exclusive
    key_group = parser.add_mutually_exclusive_group(required=True)
    key_group.add_argument("--private-key-file", metavar="PATH", help="Path to existing private key file")
    key_group.add_argument("--type", choices=["ed25519", "rsa"], default="ed25519",
                            help="Key type to generate (default: ed25519)")

    # Generation-only options
    gen = parser.add_argument_group("Generation options (only when NOT using --private-key-file)")
    gen.add_argument("--rsa-bits", type=int, default=4096, help="RSA size if --type=rsa")

    # Passphrase (used for both)
    parser.add_argument("--passphrase", nargs="?", const="", default=None,
                        help="Passphrase (prompts if needed)")

    args = parser.parse_args()

    if args.passphrase == "":
        args.passphrase = getpass.getpass("Enter passphrase (empty for none): ").strip()
    elif args.passphrase is None:
        args.passphrase = ""

    if args.private_key_file and not os.path.isfile(args.private_key_file):
        parser.error(f"File not found: {args.private_key_file}")

    return args


def load_private_key(path: str, passphrase: str) -> str:
    with open(path, "rb") as f:
        data = f.read()

    try:
        key = serialization.load_pem_private_key(
            data,
            password=passphrase.encode() if passphrase else None,
            backend=default_backend()
        )
    except Exception as e:
        raise ValueError(f"Cannot load key from {path}: {e}")

    # Re-encode to OpenSSH PEM (most compatible with Jenkins)
    return key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=(
            serialization.BestAvailableEncryption(passphrase.encode()) if passphrase
            else serialization.NoEncryption()
        )
    ).decode("utf-8")


def generate_ed25519(passphrase: str) -> tuple[str, str]:
    priv = ed25519.Ed25519PrivateKey.generate()
    enc = serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption()

    pem_priv = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=enc
    ).decode("utf-8")

    pem_pub = priv.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    ).decode("utf-8").strip()

    return pem_priv, pem_pub


def generate_rsa(bits: int, passphrase: str) -> tuple[str, str]:
    from cryptography.hazmat.primitives.asymmetric import rsa
    priv = rsa.generate_private_key(65537, bits, default_backend())
    enc = serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption()

    pem_priv = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=enc
    ).decode("utf-8")

    pem_pub = priv.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    ).decode("utf-8").strip()

    return pem_priv, pem_pub


def add_credential(server, args, private_pem: str):
    # CDATA prevents ALL XML escaping issues with PEM content
    xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@...">
  <scope>GLOBAL</scope>
  <id>{args.cred_id}</id>
  <description>{args.description}</description>
  <username>{args.username}</username>
  <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey><![CDATA[{private_pem}]]></privateKey>
  </privateKeySource>
  <passphrase>{args.passphrase}</passphrase>
</com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>"""

    server.create_credential("system", "_", xml)


def main():
    args = parse_arguments()

    try:
        server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

        if args.private_key_file:
            print(f"Loading private key: {args.private_key_file}")
            private_pem = load_private_key(args.private_key_file, args.passphrase)
            print("→ Public key must already be deployed to GitHub / servers")
        else:
            print(f"Generating new {args.type.upper()} key...")
            if args.type == "ed25519":
                private_pem, public_pem = generate_ed25519(args.passphrase)
            else:
                private_pem, public_pem = generate_rsa(args.rsa_bits, args.passphrase)

            print("\nPublic key (add to GitHub deploy keys / authorized_keys):\n")
            print(public_pem)
            print("\n" + "-" * 70 + "\n")

        print(f"Creating credential '{args.cred_id}' ...")
        add_credential(server, args, private_pem)

        print("\nSuccess!")
        print(f"  • ID          : {args.cred_id}")
        print(f"  • Username    : {args.username}  (use 'git' for GitHub/GitLab)")
        print(f"  • Description : {args.description}")
        print(f"  • Passphrase  : {'Yes' if args.passphrase else 'No'}")
        print(f"  • Source      : {'File' if args.private_key_file else 'Generated'}")
        print(f"\n→ View: {args.url.rstrip('/')}/credentials/store/system/domain/_/credential/{args.cred_id}/")

    except jenkins.JenkinsException as e:
        print(f"\nJenkins error: {e}", file=sys.stderr)
        print("→ Common causes: ID already exists, no permission, wrong URL/token", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


