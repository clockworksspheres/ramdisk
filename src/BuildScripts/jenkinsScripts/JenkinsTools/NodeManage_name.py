#!/usr/bin/env python3
import argparse
import sys
import jenkins
from jenkins import JenkinsException


class NodeManage:
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

    def delete_node(self):
        self.server.delete_node(self.args.name)
        print(f"Deleted node: {self.args.name}")

    def disable_node(self):
        self.server.disable_node(self.args.name)
        print(f"Disabled node: {self.args.name}")

    def enable_node(self):
        self.server.enable_node(self.args.name)
        print(f"Enabled node: {self.args.name}")

    def add_node(self):
        from AddJenkinsNode import AddJenkinsNode
        jnode = AddJenkinsNode(self.args)
        jnode.add_jenkins_node()

    def update_node(self):
        from update_node import cmd_update_node
        cmd_update_node(self.args)


# --------------------------------------------------------------------------- #
# ARGPARSE SETUP
# --------------------------------------------------------------------------- #

def build_parser():
    epilog = """
Examples:

  Add a node:
    jenkins_node_manage.py add agent1 --url http://jenkins:8080 --user admin --token 1234

  Delete a node:
    jenkins_node_manage.py delete agent1 --url http://jenkins:8080 --user admin --token 1234

  Disable a node:
    jenkins_node_manage.py disable agent1 --url http://jenkins:8080 --user admin --token 1234

  Enable a node:
    jenkins_node_manage.py enable agent1 --url http://jenkins:8080 --user admin --token 1234

  Update a node:
    jenkins_node_manage.py update --name agent1 --url http://jenkins:8080 --user admin --token 1234
"""

    parser = argparse.ArgumentParser(
        description="Manage Jenkins nodes via CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog
    )

    # Global arguments
    parser.add_argument("--url", required=True, help="Jenkins URL")
    parser.add_argument("--user", required=True, help="Jenkins username")
    parser.add_argument("--token", required=True, help="Jenkins API token")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared node name argument
    def add_name_arg(p):
        p.add_argument("name", required=True, help="Node name")

    # Subcommands
    add_parser = subparsers.add_parser("add", help="Add a Jenkins node")
    add_name_arg(add_parser)

    delete_parser = subparsers.add_parser("delete", help="Delete a Jenkins node")
    add_name_arg(delete_parser)

    disable_parser = subparsers.add_parser("disable", help="Disable a Jenkins node")
    add_name_arg(disable_parser)

    enable_parser = subparsers.add_parser("enable", help="Enable a Jenkins node")
    add_name_arg(enable_parser)

    update_parser = subparsers.add_parser("update", help="Update a Jenkins node")
    add_name_arg(update_parser)

    return parser


# --------------------------------------------------------------------------- #
# MAIN
# --------------------------------------------------------------------------- #

def main():
    parser = build_parser()
    args = parser.parse_args()

    nm = NodeManage(args)

    dispatch = {
        "add": nm.add_node,
        "delete": nm.delete_node,
        "disable": nm.disable_node,
        "enable": nm.enable_node,
        "update": nm.update_node,
    }

    dispatch[args.command]()


if __name__ == "__main__":
    main()

