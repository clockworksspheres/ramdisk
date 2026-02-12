import sys
import argparse

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

parser = argparse.ArgumentParser(prog="webtool")
subparsers = parser.add_subparsers(dest="command")

# Subcommand: fetch
parser_create = subparsers.add_parser(
    "create", parents=[parent_parser], help="Create a new Jenkins pipeline"
)
parser_create.add_argument("--output", help="Save response to file")

# Subcommand: check
parser_run = subparsers.add_parser(
    "run", parents=[parent_parser], help="Run a jenkins pipeline"
)

# Subcommand: parse
parser_check = subparsers.add_parser(
    "check", parents=[parent_parser], help="Check the status of a Jenkins pipeline"
)
parser_check.add_argument("--tag", help="HTML tag to extract")

args = parser.parse_args()

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

# Example logic
if args.command == "fetch":
    print(f"Fetching {args.url}...")
    if args.output:
        print(f"Saving to {args.output}")

elif args.command == "check":
    print(f"Checking reachability of {args.url}...")

elif args.command == "parse":
    print(f"Parsing {args.url} for tag <{args.tag}>...")

