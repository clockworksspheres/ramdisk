#!/usr/bin/env python3
import argparse
import xml.etree.ElementTree as ET
import requests
import os
import sys


class SshKeyWrangling():
    """
    """
    def __init__(self):
        """
        """
        print(f"Initializing {self.__class__.__name__} class")

    def load_private_key(self, path):
        """
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Private key not found: {path}")
        with open(path, "r") as f:
            return f.read()

    def add_ssh_private_key_credential(self,
        jenkins_url,
        jenkins_user,
        jenkins_token,
        credential_id,
        ssh_username,
        private_key,
        passphrase,
        description,
    ):
        """
        Create an SSH private key credential in Jenkins using raw XML REST API.
        """

        root = ET.Element(
            "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
            {"plugin": "ssh-credentials"},
        )

        ET.SubElement(root, "scope").text = "GLOBAL"
        ET.SubElement(root, "id").text = credential_id
        ET.SubElement(root, "description").text = description
        ET.SubElement(root, "username").text = ssh_username
        ET.SubElement(root, "passphrase").text = passphrase or ""

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
            f"{jenkins_url}/credentials/store/system/domain/_/createCredentials",
            auth=(jenkins_user, jenkins_token),
            headers={"Content-Type": "application/xml"},
            data=xml_payload,
        )

        if response.status_code not in (200, 201, 302):
            raise RuntimeError(
                f"Failed to create credential: {response.status_code}\n{response.text}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Add an existing SSH private key as a Jenkins credential",
        epilog="""
Examples:

  Add ~/.ssh/id_rsa as a Jenkins credential:
    python add_ssh_key_credential.py \\
      --url http://localhost:8080 \\
      --jenkins-user admin \\
      --jenkins-token API_TOKEN \\
      --credential-id linux-agent-key \\
      --ssh-user jenkins \\
      --private-key ~/.ssh/id_rsa

  Add an encrypted SSH key:
    python add_ssh_key_credential.py \\
      --url http://jenkins:8080 \\
      --jenkins-user admin \\
      --jenkins-token API_TOKEN \\
      --credential-id secure-key \\
      --ssh-user jenkins \\
      --private-key ~/.ssh/id_rsa_secure \\
      --key-passphrase "mySecretPassphrase"

Notes:
  • Credential ID must be unique in Jenkins
  • The key is stored securely in Jenkins
  • This script overwrites an existing credential with the same ID
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--url", required=True, help="Jenkins base URL")
    parser.add_argument("--jenkins-user", required=True, help="Jenkins username")
    parser.add_argument(
        "--jenkins-token",
        required=True,
        help="Jenkins API token or password",
    )

    parser.add_argument(
        "--credential-id",
        required=True,
        help="Credential ID to create/update in Jenkins",
    )
    parser.add_argument(
        "--ssh-user",
        required=True,
        help="SSH username (e.g. jenkins)",
    )
    parser.add_argument(
        "--private-key",
        required=True,
        help="Path to existing SSH private key",
    )
    parser.add_argument(
        "--key-passphrase",
        help="Passphrase for encrypted private key (optional)",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Credential description",
    )

    args = parser.parse_args()

    keyWrangling = SshKeyWrangling()

    try:
        private_key = keyWrangling.load_private_key(args.private_key)
        keyWrangling.add_ssh_private_key_credential(
            jenkins_url=args.url,
            jenkins_user=args.jenkins_user,
            jenkins_token=args.jenkins_token,
            credential_id=args.credential_id,
            ssh_username=args.ssh_user,
            private_key=private_key,
            passphrase=args.key_passphrase,
            description=args.description,
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Credential '{args.credential_id}' added to Jenkins successfully")


if __name__ == "__main__":
    main()

