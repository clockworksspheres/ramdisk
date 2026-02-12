#!/usr/bin/env python3
import argparse
import jenkins
import textwrap

def main():
    parser = argparse.ArgumentParser(
        description="Create Jenkins node without SSH credentials",
        epilog=textwrap.dedent('''\
Examples: 

  Create a node named 'agent1' on localhost: 
    python3 createJenkinsNode.py \\
            --url http://localhost:8080 \\
            --user admin \\
            --token 12345 \\
            --node-name agent1 

  Create a node with custom labels and executors: 
    python3 createJenkinsNode.py \\
            --url http://jenkins.example.com \\
            --user admin \\
            --token abcdef \\
            --node-name build-node \\
            --labels 'docker linux' \\
            --executors 4 

  Specify a different remote FS root: 
    python3 createJenkinsNode.py \\
            --url http://jenkins.example.com \\
            --user admin \\
            --token abcdef \\
            --node-name test-node \\
            --remote-fs /opt/jenkins 
'''), formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--url", required=True, help="Jenkins URL")
    parser.add_argument("--user", required=True, help="Jenkins username")
    parser.add_argument("--token", required=True, help="Jenkins API token")
    parser.add_argument("--node-name", required=True, help="Node/agent name")
    parser.add_argument("--remote-fs", default="/home/jenkins", help="Agent remote FS root")
    parser.add_argument("--labels", default="linux", help="Node labels")
    parser.add_argument("--executors", type=int, default=1, help="Number of executors")
    args = parser.parse_args()

    # Connect to Jenkins
    server = jenkins.Jenkins(args.url, args.user, args.token)

    # Create node
    if args.node_name not in [n['name'] for n in server.get_nodes()]:
        server.create_node(
            name=args.node_name,
            numExecutors=args.executors,
            remoteFS=args.remote_fs,
            labels=args.labels,
            nodeDescription="Node without SSH credentials",
            exclusive=False,
            launcher=jenkins.LAUNCHER_SSH   # Important: no SSH, no JNLP
        )
        print(f"✅ Node '{args.node_name}' created (no credentials needed)")
    else:
        print(f"⚠ Node '{args.node_name}' already exists")

if __name__ == "__main__":
    main()

