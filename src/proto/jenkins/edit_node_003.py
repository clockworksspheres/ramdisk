import sys
import jenkins
import xml.etree.ElementTree as ET
import argparse


def cmd_update_node(args):
    server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

    # Get current node config
    config_xml = server.get_node_config(args.node_name)

    print("\nCurrent config:\n")
    print(config_xml)
    print("\n")

    root = ET.fromstring(config_xml)

    # remoteFS
    if args.new_remoteFS:
        elem = root.find('remoteFS')
        if elem is not None:
            elem.text = args.new_remoteFS

    # numExecutors
    if args.new_numExecutors:
        elem = root.find('numExecutors')
        if elem is not None:
            elem.text = args.new_numExecutors

    # label
    if args.new_label:
        elem = root.find('label')
        if elem is not None:
            elem.text = args.new_label
        else:
            elem = ET.SubElement(root, 'label')
            elem.text = args.new_label

    # host
    if args.new_host:
        elem = root.find('.//host')
        if elem is not None:
            elem.text = args.new_host

    # port
    if args.new_port:
        elem = root.find('.//port')
        if elem is not None:
            elem.text = args.new_port

    # credentialsId
    if args.new_credentialsId:
        elem = root.find('.//credentialsId')
        if elem is not None:
            elem.text = args.new_credentialsId

    # Convert back to string
    new_config = ET.tostring(root, encoding='unicode')

    print("\nNew config:\n")
    print(new_config)
    print("\n")

    # Apply updated config
    server.reconfig_node(args.node_name, new_config)
    print(f"Node '{args.node_name}' updated.")


def build_parser():
    epilog_text = """
Examples:

  # Update only the label
  script.py update-node my-node \\
      --url http://jenkins:8080 --user admin --token 12345 \\
      --new_label "linux docker"

  # Update remoteFS and executors
  script.py update-node my-node \\
      --url http://jenkins:8080 --user admin --token 12345 \\
      --new_remoteFS /var/jenkins --new_numExecutors 4

  # Update SSH launcher settings
  script.py update-node my-node \\
      --url http://jenkins:8080 --user admin --token 12345 \\
      --new_host build01.example.com --new_port 22 --new_credentialsId ssh-creds
"""

    parser = argparse.ArgumentParser(
        description="Jenkins node management tool",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- update-node subcommand ---
    update = subparsers.add_parser(
        "update",
        help="Update Jenkins node configuration",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    update.add_argument('node_name', help='Jenkins node name')
    update.add_argument('--url', required=True)
    update.add_argument('--user', required=True)
    update.add_argument('--token', required=True)

    update.add_argument('--new_label', default="", help='New label to set')
    update.add_argument('--new_remoteFS', default="", help='New remoteFS to set')
    update.add_argument('--new_numExecutors', default="", help='New numExecutors to set')
    update.add_argument('--new_host', default="", help='New host to set')
    update.add_argument('--new_port', default="", help='New port to set')
    update.add_argument('--new_credentialsId', default="", help='New credentials ID to set')

    update.set_defaults(func=cmd_update_node)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

