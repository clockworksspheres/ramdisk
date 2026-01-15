#!/usr/bin/env python3
"""
Create Jenkins SSH credential (if missing) from a given private key FILE PATH,
then create a permanent SSH agent/node.

Usage example:
  python create_jenkins_agent.py \\
    --jenkins-url http://localhost:8080 \\
    --jenkins-user admin \\
    --jenkins-token your-api-token \\
    --credential-id macos-agent-key \\
    --private-key-file /var/jenkins_home/.ssh/jenkins_macos_agent \\
    --ssh-username amrobot \\
    --node-name macos-builder \\
    --host 192.168.172.136 \\
    --remote-fs /Users/amrobot/jenkins-agent \\
    --labels "macos arm64"
"""

import argparse
import sys
import requests
from requests.auth import HTTPBasicAuth
import jenkins
from urllib.parse import urljoin


def get_crumb(session, base_url, auth):
    """Fetch CSRF crumb if enabled"""
    try:
        crumb_url = urljoin(base_url, "crumbIssuer/api/xml?xpath=concat(//crumbRequestField,\":\",//crumb)")
        resp = session.get(crumb_url, auth=auth, timeout=10)
        if resp.status_code == 200:
            return resp.text.strip()
    except Exception:
        pass
    print("Warning: No CSRF crumb fetched (may fail if protection enabled)", file=sys.stderr)
    return None


def credential_exists(base_url, auth, cred_id):
    """Check if credential ID already exists"""
    url = urljoin(base_url, f"credentials/store/system/domain/_/credential/{cred_id}/api/json")
    resp = requests.get(url, auth=auth, timeout=10)
    return resp.status_code == 200


def create_ssh_credential(base_url, auth, cred_id, username, private_key_content, description=""):
    if credential_exists(base_url, auth, cred_id):
        print(f"Credential '{cred_id}' already exists — skipping creation.")
        return True

    session = requests.Session()
    crumb = get_crumb(session, base_url, auth)

    # XML with CDATA to handle multi-line keys safely
    xml = f"""<?xml version='1.1' encoding='UTF-8'?>
<com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey plugin="ssh-credentials@latest">
  <scope>GLOBAL</scope>
  <id>{cred_id}</id>
  <description>{description}</description>
  <username>{username}</username>
  <privateKeySource class="com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey$DirectEntryPrivateKeySource">
    <privateKey><![CDATA[{private_key_content}]]></privateKey>
  </privateKeySource>
</com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey>"""

    url = urljoin(base_url, "credentials/store/system/domain/_/createCredentials")
    headers = {'Content-Type': 'application/xml'}

    if crumb:
        field, value = crumb.split(':', 1)
        headers[field] = value

    resp = session.post(url, data=xml.encode('utf-8'), auth=auth, headers=headers, timeout=15)

    if resp.status_code in (200, 201, 302):
        print(f"Credential '{cred_id}' created successfully.")
        return True
    else:
        print(f"Failed to create credential (HTTP {resp.status_code}):", file=sys.stderr)
        print(resp.text.strip(), file=sys.stderr)
        return False


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Create SSH credential from private key FILE + Jenkins agent/node",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Jenkins connection
    parser.add_argument("--jenkins-url", required=True, help="Jenkins base URL (e.g. http://localhost:8080)")
    parser.add_argument("--jenkins-user", required=True, help="Jenkins username")
    parser.add_argument("--jenkins-token", required=True, help="Jenkins API token or password")

    # Credential
    parser.add_argument("--credential-id", required=True, help="Credential ID to create/use")
    parser.add_argument("--private-key-file", required=True,
                        help="Full path to SSH private key file (e.g. /var/jenkins_home/.ssh/jenkins_macos_agent)")
    parser.add_argument("--ssh-username", default="amrobot", help="SSH username on agent (default: amrobot)")
    parser.add_argument("--cred-description", default="Auto-created SSH key for agent")

    # Node
    parser.add_argument("--node-name", required=True, help="Agent/node name")
    parser.add_argument("--host", required=True, help="Agent host/IP")
    parser.add_argument("--port", default="22", help="SSH port")
    parser.add_argument("--remote-fs", required=True, help="Remote working dir on agent")
    parser.add_argument("--labels", default="", help="Space-separated labels")
    parser.add_argument("--executors", default=1, type=int, help="Number of executors")
    parser.add_argument("--node-description", default="macOS SSH agent")

    return parser.parse_args()


def main():
    args = parse_arguments()

    auth = HTTPBasicAuth(args.jenkins_user, args.jenkins_token)
    base_url = args.jenkins_url.rstrip('/') + '/'

    # 1. Load private key content from the provided file path
    try:
        with open(args.private_key_file, 'r', encoding='utf-8') as f:
            key_content = f.read().strip()
        print(f"Successfully loaded private key from: {args.private_key_file}")
    except Exception as e:
        print(f"Error reading private key file '{args.private_key_file}': {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Create credential if needed
    if not create_ssh_credential(
        base_url, auth,
        args.credential_id,
        args.ssh_username,
        key_content,
        args.cred_description
    ):
        sys.exit(1)

    # 3. Create node using python-jenkins
    try:
        server = jenkins.Jenkins(base_url, args.jenkins_user, args.jenkins_token)
        print(f"Connected to Jenkins at {args.jenkins_url}")

        if server.node_exists(args.node_name):
            print(f"Node '{args.node_name}' already exists!", file=sys.stderr)
            sys.exit(1)

        launcher_params = {
            "host": args.host,
            "port": args.port,
            "username": args.ssh_username,
            "credentialsId": args.credential_id,
        }

        server.create_node(
            name=args.node_name,
            nodeDescription=args.node_description,
            remoteFS=args.remote_fs,
            labels=args.labels.strip().split() if args.labels else None,
            numExecutors=str(args.executors),
            launcher="hudson.plugins.sshslaves.SSHLauncher",
            launcher_params=launcher_params
        )

        print("\n" + "═" * 70)
        print(" SUCCESS ")
        print("═" * 70)
        print(f"  • Private key file:  {args.private_key_file}")
        print(f"  • Credential ID:     {args.credential_id}")
        print(f"  • Node:              {args.node_name}")
        print(f"  • Host:              {args.host}:{args.port}")
        print(f"  • Remote FS:         {args.remote_fs}")
        print("\n→ Go to Jenkins → Manage Nodes → Launch agent and check log")
    except Exception as e:
        print(f"Node creation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

