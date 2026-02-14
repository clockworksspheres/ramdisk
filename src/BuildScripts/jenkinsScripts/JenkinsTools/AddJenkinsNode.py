#!/usr/bin/env python3
"""
Add a new permanent Jenkins agent (node) from the command line.
Supports two common launch methods: JNLP (inbound) and SSH.

IMPORTANT:
- Use a REAL Jenkins URL (e.g. http://localhost:8080 or https://ci.yourcompany.com)
- 'jenkins.example.com' is only a placeholder → it will NOT work
- You need admin rights or 'Overall/Manage' + 'Overall/Read' permissions

Run with --help to see detailed usage and examples.

"""

import argparse
import sys
import textwrap
import jenkins
from jenkins import JenkinsException


class AddJenkinsNode():
    def __init__(self, args):
        """
        """
        self.args = args
        print("Finished init...\n\n")

    def create_jnlp_node(self, server):
        """
        Create inbound JNLP agent (agent initiates connection to controller)
        """
        launcher_params = {
            'port': 0,                    # 0 = auto-select / random
            'jnlpProtocol': True,
        }
        if self.args.jvm_options:
            launcher_params['jvmOptions'] = self.args.jvm_options

        server.create_node(
            name=self.args.name,
            numExecutors=self.args.executors,
            remoteFS=self.args.remote_fs,
            labels=self.args.labels.strip(),
            nodeDescription=self.args.description,
            launcher='inbound',
            launcher_params=launcher_params
        )

    def create_ssh_node(self, server):
        """
        Create SSH agent (controller connects to agent)
        """
        print("Before launcher params setup")
        launcher_params = {
            'host': self.args.host,
            'port': str(self.args.port),
            'credentialsId': self.args.credentials_id,
            'jvmOptions': self.args.jvm_options or '',
            'javaPath': '',
            'prefixStartSlaveCmd': '',
            'suffixStartSlaveCmd': '',
            'launchTimeoutSeconds': '60',
            'maxNumRetries': '10',
            'retryWaitTime': '10',
        }
        print("After launcher params setup")

        server.create_node(
            name=self.args.name,
            numExecutors=self.args.executors,
            remoteFS=self.args.remote_fs,
            labels=self.args.labels.strip(),
            nodeDescription=self.args.description,
            launcher='hudson.plugins.sshslaves.SSHLauncher',
            launcher_params=launcher_params
        )

        print("Leaving creation of the ssh node...")

    def add_jenkins_node(self):
        """
        """
        print(f"Connecting to: {self.args.url}")

        try:
            server = jenkins.Jenkins(self.args.url, username=self.args.user, password=self.args.token)

            print("Instanciated server...")

            # Quick connectivity check
            try:
                server.get_whoami()
            except Exception as e:
                print("\nCannot connect to Jenkins!", file=sys.stderr)
                print("Common causes:", file=sys.stderr)
                print("  • Wrong --url (must be real address – not jenkins.example.com)", file=sys.stderr)
                print("  • Jenkins not running / wrong port", file=sys.stderr)
                print("  • Firewall / network issue", file=sys.stderr)
                print("  • Invalid --user or --token", file=sys.stderr)
                print(f"\nError detail: {e}", file=sys.stderr)
                sys.exit(1)

            if server.node_exists(self.args.name):
                print(f"Node '{self.args.name}' already exists → skipping creation.")
                return

            print(f"Creating node: {self.args.name}  ({self.args.method.upper()} method)")

            if self.args.method == "jnlp":
                self.create_jnlp_node(server)
            else:
                self.create_ssh_node(server)

            print("\nSuccess!")
            print(f"→ Node page: {self.args.url.rstrip('/')}/computer/{self.args.name}/")

            if self.args.method == "jnlp":
                print("\nNext steps for JNLP agent:")
                print("  1. Go to the node page in browser")
                print("  2. Click 'Launch agent' or copy JNLP command / secret")
                print("  3. Run agent.jar on your test machine")

            else:  # ssh
                print("\nJenkins will now try to connect automatically.")
                print(f"Make sure SSH is reachable:  {self.args.host}:{self.args.port}")
                print(f"Credential ID '{self.args.credentials_id}' must be valid.")

        except JenkinsException as e:
            print(f"\nJenkins API error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            sys.exit(1)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Create a new permanent Jenkins agent (test machine / build node)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            IMPORTANT: Replace example URLs with your ACTUAL Jenkins server address!

            Examples:
              # 1. Quick JNLP/inbound agent (easiest – agent connects to controller)
              %(prog)s --url http://localhost:8080 --user admin --token 116b8f... \\
                --name test-ubuntu-01 --executors 4 \\
                --labels "test linux docker python ubuntu" \\
                --description "Ubuntu 24.04 LTS test VM – Idaho lab"

              # 2. JNLP agent with custom remote FS root and JVM options
              %(prog)s --url http://192.168.1.150:8080 --user <username> --token your-api-token \\
                --name windows-test-03 --executors 2 \\
                --remote-fs "C:\\Jenkins\\agent" --labels "windows test dotnet" \\
                --jvm-options "-Xmx768m -XX:+UseG1GC" \\
                --description "Windows 11 test machine"

              # 3. SSH-launched agent (controller connects outbound to the node)
              %(prog)s --url https://jenkins.company.com --user admin --token 11abcdef... \\
                --name build-agent-07 --method ssh \\
                --host 10.20.30.45 --port 22 --credentials-id ssh-jenkins@agent07 \\
                --executors 8 --labels "fast linux amd64 heavy build" \\
                --remote-fs /home/jenkins --description "Dedicated build server – rack 4"

              # 4. Minimal JNLP agent with only required fields
              %(prog)s --url http://ci.local:8080 --user ci-admin --token xyz789... \\
                --name laptop-test --executors 1 --labels "local test_machine"

              # Show this help again
              %(prog)s --help
        """)
    )

    # ─── Jenkins connection (required) ──────────────────────────────────────
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url", required=True,
                      help="Jenkins server URL (e.g. http://localhost:8080 or https://ci.yourcompany.com)")
    conn.add_argument("--user", required=True, help="Jenkins username with node creation rights")
    conn.add_argument("--token", required=True, help="Jenkins API token (User → Configure → API Token)")

    # ─── Node basics (required) ─────────────────────────────────────────────
    node = parser.add_argument_group("Node basics (required)")
    node.add_argument("--name", required=True, help="Unique node name (e.g. test-ubuntu-01, build-agent-05)")
    node.add_argument("--description", default="", help="Human-readable description of the node")
    node.add_argument("--executors", type=int, default=2, help="Number of concurrent builds (default: 2)")
    node.add_argument("--remote-fs", default="/home/jenkins/agent",
                      help="Workspace root on agent (default: /home/jenkins/agent)")
    node.add_argument("--labels", default="", help="Space-separated labels (e.g. 'linux test docker amd64')")

    # ─── Launch method ──────────────────────────────────────────────────────
    launch = parser.add_argument_group("Launch method")
    launch.add_argument("--method", choices=["jnlp", "ssh"], default="jnlp",
                        help="jnlp = inbound (agent connects to Jenkins) | ssh = outbound (Jenkins connects)")

    # ─── SSH-specific options ───────────────────────────────────────────────
    ssh = parser.add_argument_group("SSH options (only used when --method=ssh)")
    ssh.add_argument("--host", help="Hostname or IP of the agent machine")
    ssh.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    ssh.add_argument("--credentials-id", help="Existing Jenkins credential ID for SSH login")
    ssh.add_argument("--jvm-options", default="", help="JVM options for the agent JVM (e.g. '-Xmx2g')")

    args = parser.parse_args()

    # Basic validation
    if args.method == "ssh":
        missing = []
        if not args.host:
            missing.append("--host")
        if not args.credentials_id:
            missing.append("--credentials-id")
        if missing:
            parser.error(f"--method ssh requires: {', '.join(missing)}")

    print("Just before returning args...")

    return args

def main():
    args = parse_arguments()

    addNode = AddJenkinsNode(args)
    addNode.add_jenkins_node()

if __name__ == "__main__":
    main()

