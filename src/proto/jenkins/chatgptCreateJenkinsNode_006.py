#!/usr/bin/env python3
import argparse
import jenkins
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec

# ------------------------
# SSH KEY HANDLING
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
# MAIN
# ------------------------

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--user", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--node-name", required=True)
    p.add_argument("--host", required=True)
    p.add_argument("--port", type=int, default=22)
    p.add_argument("--remote-fs", default="/home/jenkins")
    p.add_argument("--labels", default="linux")
    p.add_argument("--executors", type=int, default=1)
    p.add_argument("--ssh-user", default="jenkins")
    p.add_argument("--credential-id", required=True)
    p.add_argument("--key-file", default="id_key")
    args = p.parse_args()

    # ------------------------
    # Generate SSH key
    # ------------------------

    private_key, public_key = generate_keys()
    Path(args.key_file).write_text(private_key)
    Path(args.key_file + ".pub").write_text(public_key)

    print("Public key (add to agent ~/.ssh/authorized_keys):\n")
    print(public_key)

    # ------------------------
    # Create credential (Groovy)
    # ------------------------

    groovy = f"""
import com.cloudbees.jenkins.plugins.sshcredentials.impl.*
import com.cloudbees.plugins.credentials.*
import com.cloudbees.plugins.credentials.domains.*
import jenkins.model.*

def store = Jenkins.instance
  .getExtensionList('com.cloudbees.plugins.credentials.SystemCredentialsProvider')[0]
  .getStore()

if (!store.getCredentials(Domain.global()).find{{ it.id == "{args.credential_id}" }}) {{
  store.addCredentials(Domain.global(),
    new BasicSSHUserPrivateKey(
      CredentialsScope.GLOBAL,
      "{args.credential_id}",
      "{args.ssh_user}",
      new BasicSSHUserPrivateKey.DirectEntryPrivateKeySource(\"\"\"{private_key}\"\"\"),
      null,
      "SSH key for {args.node_name}"
    )
  )
  println("Credential created")
}} else {{
  println("Credential already exists")
}}
"""

    subprocess.run(
        ["java", "-jar", "jenkins-cli.jar",
         "-s", args.url,
         "-auth", f"{args.user}:{args.password}",
         "groovy", "="],
        input=groovy.encode(),
        check=True
    )

    # ------------------------
    # Create node (NO launcher)
    # ------------------------

    server = jenkins.Jenkins(args.url, args.user, args.password)

    if args.node_name not in server.get_nodes():
        server.create_node(
            args.node_name,
            numExecutors=args.executors,
            remoteFS=args.remote_fs,
            labels=args.labels,
            exclusive=False,
            nodeDescription="Created via script"
        )

    # ------------------------
    # Patch node XML (SSH launcher)
    # ------------------------

    xml = server.get_node_config(args.node_name)
    root = ET.fromstring(xml)

    launcher = root.find("launcher")
    launcher.attrib["class"] = "hudson.slaves.SSHLauncher"

    def set(tag, value):
        el = launcher.find(tag)
        if el is None:
            el = ET.SubElement(launcher, tag)
        el.text = str(value)

    set("host", args.host)
    set("port", args.port)
    set("credentialsId", args.credential_id)
    set("launchTimeoutSeconds", 60)

    server.reconfig_node(args.node_name, ET.tostring(root, encoding="unicode"))

    print(f"✅ Node '{args.node_name}' created and configured")

if __name__ == "__main__":
    main()

