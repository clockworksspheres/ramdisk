import argparse

# Parent parser with shared arguments
url_parent = argparse.ArgumentParser(add_help=False)
url_parent.add_argument("--url", required=True, help="Target resource URL")

parser = argparse.ArgumentParser(prog="toolbox")
subparsers = parser.add_subparsers(dest="command", required=True)

# Subcommand: fetch (inherits --url)
parser_fetch = subparsers.add_parser(
    "fetch", parents=[url_parent], help="Fetch content from a URL"
)
parser_fetch.add_argument("--output", help="Save response to file")

# Subcommand: check (inherits --url)
parser_check = subparsers.add_parser(
    "check", parents=[url_parent], help="Check if a URL is reachable"
)

# Subcommand: greet (does NOT inherit --url)
parser_greet = subparsers.add_parser(
    "greet", help="Greet someone"
)
parser_greet.add_argument("name")

args = parser.parse_args()

# Example logic
if args.command == "fetch":
    print(f"Fetching {args.url}...")
    if args.output:
        print(f"Saving to {args.output}")

elif args.command == "check":
    print(f"Checking reachability of {args.url}...")

elif args.command == "greet":
    print(f"Hello, {args.name}!")



