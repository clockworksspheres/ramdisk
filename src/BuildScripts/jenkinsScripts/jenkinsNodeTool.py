#!/usr/bin/env python3
"""
"""
import sys
import textwrap
import argparse

def parse_arguments():
    """
    """

    # Parent parser with shared arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--url", required=True, help="Target resource URL"
    )

    parent_parser.add_argument(
        "--user", required=True, help="User to access the Jenkins server"
    )

    parent_parser.add_argument(
        "--token", required=True, help="User's token to access the Jenkins server"
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: add
    parser_add = subparsers.add_parser(
        "add", parents=[parent_parser], help="Create a new Jenkins pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # 1. Quick JNLP/inbound agent (easiest – agent connects to controller)
              %(prog)s test-ubuntu-01 \\
                --url http://localhost:8080 --user admin --token 116b8f... \\
                --executors 4 \\
                --labels "test linux docker python ubuntu" \\
                --description "Ubuntu 24.04 LTS test VM – Idaho lab"

              # 2. JNLP agent with custom remote FS root and JVM options
              %(prog)s windows-test-03 --url http://192.168.1.150:8080 \\
                --user <username> --token your-api-token \\
                --executors 2 \\
                --remote-fs "C:\\Jenkins\\agent" --labels "windows test dotnet" \\
                --jvm-options "-Xmx768m -XX:+UseG1GC" \\
                --description "Windows 11 test machine"

              # 3. SSH-launched agent (controller connects outbound to the node)
              %(prog)s build-agent-07 --url https://jenkins.company.com --user admin --token 11abcdef... \\
                --method ssh \\
                --host 10.20.30.45 --port 22 --credentials-id ssh-jenkins@agent07 \\
                --executors 8 --labels "fast linux amd64 heavy build" \\
                --remote-fs /home/jenkins --description "Dedicated build server – rack 4"

              # 4. Minimal JNLP agent with only required fields
              %(prog)s laptop-test --url http://ci.local:8080 --user ci-admin --token xyz789... \\
                --executors 1 --labels "local test_machine"

              # Show this help again
              %(prog)s --help
        """)
    )

    # ─── Node basics (required) ─────────────────────────────────────────────
    node = parser_add.add_argument_group("Node basics (required)")
    node.add_argument('name', help="Unique node name (e.g. test-ubuntu-01, build-agent-05)")

    node.add_argument("--description", default="", help="Human-readable description of the node")
    node.add_argument("--executors", type=int, default=2, help="Number of concurrent builds (default: 2)")
    node.add_argument("--remote-fs", default="/home/jenkins/agent",
                      help="Workspace root on agent (default: /home/jenkins/agent)")
    node.add_argument("--labels", default="", help="Space-separated labels (e.g. 'linux test docker amd64')")

    # ─── Launch method ──────────────────────────────────────────────────────
    launch = parser_add.add_argument_group("Launch method")
    launch.add_argument("--method", choices=["jnlp", "ssh"], default="jnlp",
                        help="jnlp = inbound (agent connects to Jenkins) | ssh = outbound (Jenkins connects)")

    # ─── SSH-specific options ───────────────────────────────────────────────
    ssh = parser_add.add_argument_group("SSH options (only used when --method=ssh)")
    ssh.add_argument("--host", help="Hostname or IP of the agent machine")
    ssh.add_argument("--port", type=int, default=22, help="SSH port (default: 22)")
    ssh.add_argument("--credentials-id", help="Existing Jenkins credential ID for SSH login")
    ssh.add_argument("--jvm-options", default="", help="JVM options for the agent JVM (e.g. '-Xmx2g')")

    # --- update-node subcommand ---
    update = subparsers.add_parser(
        "update",
        help="Update Jenkins node configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:

              # Update only the label
              script.py update my-node \\
                  --url http://jenkins:8080 --user admin --token 12345 \\
                  --new_label "linux docker"

              # Update remoteFS and executors
              script.py update my-node \\
                  --url http://jenkins:8080 --user admin --token 12345 \\
                  --new_remoteFS /var/jenkins --new_numExecutors 4

              # Update SSH launcher settings
              script.py update my-node \\
                  --url http://jenkins:8080 --user admin --token 12345 \\
                  --new_host build01.example.com --new_port 22 --new_credentialsId ssh-creds

              # Show this help again
              %(prog)s update --help
            """
        )
    )

    update.add_argument('name', help='Jenkins node name')
    update.add_argument('--url', required=True)
    update.add_argument('--user', required=True)
    update.add_argument('--token', required=True)

    update.add_argument('--new_label', default="", help='New label to set')
    update.add_argument('--new_remoteFS', default="", help='New remoteFS to set')
    update.add_argument('--new_numExecutors', default="", help='New numExecutors to set')
    update.add_argument('--new_host', default="", help='New host to set')
    update.add_argument('--new_port', default="", help='New port to set')
    update.add_argument('--new_credentialsId', default="", help='New credentials ID to set')

    # get-nodes
    subparsers.add_parser(
        "get-nodes",
        parents=[parent_parser],
        help="List all Jenkins nodes"
    )

    # get-node-info
    p_info = subparsers.add_parser(
        "get-node-info",
        parents=[parent_parser],
        help="Show detailed info for a node"
    )
    p_info.add_argument("name")

    # get-node-config
    p_cfg = subparsers.add_parser(
        "get-node-config",
        parents=[parent_parser],
        help="Show XML config for a node"
    )
    p_cfg.add_argument("name")

    # node-exists
    p_exists = subparsers.add_parser(
        "node-exists",
        parents=[parent_parser],
        help="Check if a node exists"
    )
    p_exists.add_argument("name")

    # Subcommands
    delete_parser = subparsers.add_parser("delete", parents=[parent_parser], help="Delete a Jenkins node")
    delete_parser.add_argument("name", help="Node name")

    disable_parser = subparsers.add_parser("disable", parents=[parent_parser], help="Disable a Jenkins node")
    disable_parser.add_argument("name", help="Node name")

    enable_parser = subparsers.add_parser("enable", parents=[parent_parser], help="Enable a Jenkins node")
    enable_parser.add_argument("name", help="Node name")


    args = parser.parse_args()

    print("Just before returning args...")

    return args


if __name__=="__main__":
    args = parse_arguments()

    if args.command == "add":
        print(f"Adding {args.url} for node <{args.name}>...")
        from JenkinsTools.AddJenkinsNode import AddJenkinsNode as addNode

        add_node = addNode(args)
        add_node.add_jenkins_node()

    elif args.command == "update":
        print(f"Running {args.url} for pipeline <{args.name}>...")
        from JenkinsTools.update_node import cmd_update_node

        cmd_update_node(args)

    elif args.command == "get-nodes":
        from JenkinsTools.NodeStatus import NodeStatus
        ns = NodeStatus(args)
        print(ns.get_nodes())

    elif args.command == "get-node-info":
        from JenkinsTools.NodeStatus import NodeStatus
        ns = NodeStatus(args)
        print(ns.get_node_info())

    elif args.command == "get-node-config":
        from JenkinsTools.NodeStatus import NodeStatus
        ns = NodeStatus(args)
        print(ns.get_node_config())

    elif args.command == "node-exists":
        from JenkinsTools.NodeStatus import NodeStatus
        ns = NodeStatus(args)
        print(ns.node_exists())

    elif args.command == "delete":
        from JenkinsTools.NodeManage import NodeManage
        nm = NodeManage(args)
        print(nm.node_exists())

    elif args.command == "disable":
        from JenkinsTools.NodeManage import NodeManage
        nm = NodeManage(args)
        print(nm.node_exists())

    elif args.command == "enable":
        from JenkinsTools.NodeManage import NodeManage
        nm = NodeManage(args)
        print(nm.node_exists())


    print("\n")
    print(f"command: {args.command}")
    print(f"args: {vars(args)}")
  
    

