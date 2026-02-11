import argparse

# Parent parser with shared arguments
parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
parent_parser.add_argument("--config", help="Path to config file")

parser = argparse.ArgumentParser(prog="toolbox")
subparsers = parser.add_subparsers(dest="command", required=True)

# Subcommand: add
parser_add = subparsers.add_parser("add", parents=[parent_parser], help="Add numbers")
parser_add.add_argument("x", type=int)
parser_add.add_argument("y", type=int)

# Subcommand: greet
parser_greet = subparsers.add_parser("greet", parents=[parent_parser], help="Greet someone")
parser_greet.add_argument("name")

args = parser.parse_args()

print("Subcommand:", args.command)
print("Arguments:", vars(args))


