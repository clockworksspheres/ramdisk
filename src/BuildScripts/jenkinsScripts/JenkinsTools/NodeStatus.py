#!/usr/bin/env python3
import argparse
import sys
import jenkins
from jenkins import JenkinsException


class NodeStatus:

    def __init__(self, args):
        self.args = args
        print(f"Initializing {self.__class__.__name__} class")

        try:
            self.server = jenkins.Jenkins(
                self.args.url,
                username=self.args.user,
                password=self.args.token
            )

            print("Instantiated server...")

            # Quick connectivity check
            try:
                self.server.get_whoami()
            except Exception as e:
                print("\nCannot connect to Jenkins!", file=sys.stderr)
                print("Common causes:", file=sys.stderr)
                print("  • Wrong --url")
                print("  • Jenkins not running / wrong port")
                print("  • Firewall / network issue")
                print("  • Invalid --user or --token")
                print(f"\nError detail: {e}", file=sys.stderr)
                sys.exit(1)

        except JenkinsException as e:
            print(f"\nJenkins API error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    def get_nodes(self):
        return self.server.get_nodes()

    def get_node_info(self):
        return self.server.get_node_info(self.args.name)

    def get_node_config(self):
        return self.server.get_node_config(self.args.name)

    def node_exists(self):
        return self.server.node_exists(self.args.name)


def build_parser():
    # Parent parser for global options (shared by all subcommands)
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--url", required=True, help="Jenkins base URL")
    parent.add_argument("--user", required=True, help="Jenkins username")
    parent.add_argument("--token", required=True, help="Jenkins API token")

    epilog_text = """
Examples:

  jnode get-nodes --url http://jenkins:8080 --user admin --token ABC

  jnode get-node-info --name builder01 --url http://jenkins:8080 --user admin --token ABC

  jnode get-node-config --name builder01 --url http://jenkins:8080 --user admin --token ABC

  jnode node-exists --name builder01 --url http://jenkins:8080 --user admin --token ABC
"""

    parser = argparse.ArgumentParser(
        description="Jenkins Node Utility — manage and inspect Jenkins nodes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog_text
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-nodes
    subparsers.add_parser(
        "get-nodes",
        parents=[parent],
        help="List all Jenkins nodes"
    )

    # get-node-info
    p_info = subparsers.add_parser(
        "get-node-info",
        parents=[parent],
        help="Show detailed info for a node"
    )
    p_info.add_argument("name")

    # get-node-config
    p_cfg = subparsers.add_parser(
        "get-node-config",
        parents=[parent],
        help="Show XML config for a node"
    )
    p_cfg.add_argument("name")

    # node-exists
    p_exists = subparsers.add_parser(
        "node-exists",
        parents=[parent],
        help="Check if a node exists"
    )
    p_exists.add_argument("name")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    ns = NodeStatus(args)

    if args.command == "get-nodes":
        print(ns.get_nodes())

    elif args.command == "get-node-info":
        print(ns.get_node_info())

    elif args.command == "get-node-config":
        print(ns.get_node_config())

    elif args.command == "node-exists":
        print(ns.node_exists())


if __name__ == "__main__":
    main()

