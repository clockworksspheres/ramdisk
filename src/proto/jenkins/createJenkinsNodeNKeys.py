#!/usr/bin/env python3
"""
Complete example: Generate Ed25519 SSH keys → Prepare for Jenkins agent → Create node
Run this script on your local/admin machine (NOT on the agent itself)
"""

import os
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
import paramiko
import jenkins
import sys

sys.path.append("../../..")

import jenkinstokens.jenkinstoken as token

# ==================== CONFIGURATION ====================
JENKINS_URL = "http://jenkins.example.com:8080"
JENKINS_USER = token.USER
JENKINS_TOKEN = token.API_TOKEN

# Node settings
NODE_NAME = "alma10"
NODE_DESCRIPTION = "Static Linux agent - Ed25519 SSH - created 2026"
NUM_EXECUTORS = 4
REMOTE_FS = "/home/jenkins/jenkins-agent"
LABELS = "linux docker medium build"
EXCLUSIVE = True

# SSH connection details for the target agent machine
AGENT_HOST = "192.168.10.110"           # ← CHANGE THIS!
AGENT_USERNAME = "jenkins"             # user that will run builds on agent
AGENT_SSH_PORT = 22

# Where to save keys (recommended secure location)
KEY_DIR = Path.home() / ".ssh" / "jenkins_agents"
KEY_DIR.mkdir(parents=True, exist_ok=True)

PRIVATE_KEY_PATH = KEY_DIR / f"agent_{NODE_NAME}_{datetime.now():%Y%m%d}"
PUBLIC_KEY_PATH = PRIVATE_KEY_PATH.with_suffix(".pub")
# =========================================================

def generate_ed25519_keys():
    """Generate Ed25519 key pair and save in modern OpenSSH format"""
    private_key = ed25519.Ed25519PrivateKey.generate()

    # Private key - OpenSSH format (most compatible with recent Paramiko/Jenkins)
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PrivateFormat.OpenSSH,
        encryption_algorithm=serialization.NoEncryption()
    )
    private_str = private_bytes.decode("utf-8")

    # Public key
    public_bytes = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    public_str = public_bytes.decode("utf-8").strip() + f" auto-jenkins-{NODE_NAME}-{datetime.now():%Y-%m-%d}"

    # Save files with proper permissions
    PRIVATE_KEY_PATH.write_text(private_str)
    PRIVATE_KEY_PATH.chmod(0o600)

    PUBLIC_KEY_PATH.write_text(public_str + "\n")
    PUBLIC_KEY_PATH.chmod(0o644)

    print(f"Keys generated and saved:")
    print(f"  Private: {PRIVATE_KEY_PATH}")
    print(f"  Public:  {PUBLIC_KEY_PATH}\n")

    return private_str, public_str


def verify_paramiko_can_load(private_key_path: Path):
    """Quick test: can Paramiko actually use this key?"""
    pkey = paramiko.Ed25519Key.from_private_key_file(str(private_key_path))
    print("Paramiko successfully loaded the Ed25519 private key ✓")
    print(f"Fingerprint: {pkey.get_fingerprint().hex()}\n")
    return pkey


def create_jenkins_node(private_key_str: str, public_key_str: str):
    """1. You still need to manually add the credential in Jenkins GUI first!"""
    print("STEP REQUIRED: Add credential in Jenkins GUI")
    print("------------------------------------------------")
    print("Go to: Manage Jenkins → Credentials → (global) → Add Credentials")
    print("Kind:           SSH Username with private key")
    print("Username:      ", AGENT_USERNAME)
    print("Private Key:   Paste the following:\n")
    print(private_key_str.strip())
    print("\nID suggestion:  ", f"ssh-{NODE_NAME.lower()}-{datetime.now():%Y%m}")
    print("Description:    Ed25519 key for", NODE_NAME)
    print("------------------------------------------------")
    print("After adding, copy the Credential ID and set it below ↓\n")

    # ← You must fill this in after creating the credential manually
    CREDENTIAL_ID = input("Enter the Credential ID you just created: ").strip()

    server = jenkins.Jenkins(JENKINS_URL, username=JENKINS_USER, password=JENKINS_TOKEN)

    launcher_params = {
        "host": AGENT_HOST,
        "port": str(AGENT_SSH_PORT),
        "username": AGENT_USERNAME,
        "credentialsId": CREDENTIAL_ID,
        # Optional tuning
        # "javaPath": "/usr/lib/jvm/java-17-openjdk/bin/java",
        # "jvmOptions": "-Xmx2048m",
    }

    server.create_node(
        name=NODE_NAME,
        nodeDescription=NODE_DESCRIPTION,
        numExecutors=NUM_EXECUTORS,
        remoteFS=REMOTE_FS,
        labels=LABELS,
        exclusive=EXCLUSIVE,
        launcher="hudson.plugins.sshslaves.SSHLauncher",  # modern way
        launcher_params=launcher_params
    )

    print(f"\nSuccess! Node '{NODE_NAME}' has been created.")
    print("Next steps:")
    print("1. On the agent machine: append the public key to ~jenkins/.ssh/authorized_keys")
    print("   Public key:\n", public_key_str)
    print("2. Go to Jenkins → Nodes →", NODE_NAME, "→ Launch agent (should connect automatically)")


def main():
    private_str, public_str = generate_ed25519_keys()
    verify_paramiko_can_load(PRIVATE_KEY_PATH)
    create_jenkins_node(private_str, public_str)


if __name__ == "__main__":
    main()


