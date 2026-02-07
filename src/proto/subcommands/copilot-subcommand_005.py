#!/usr/bin/env python3

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Example CLI with arguments and subcommands",
        epilog="""
Examples:
  tool.py add 2 3
  tool.py greet Alice
  tool.py greet Alice --times 3
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ----- Global arguments -----
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    # ----- Subcommands -----
    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="command",
    )

    # ===== Subcommand: add =====
    add_parser = subparsers.add_parser(
        "add",
        help="Add two numbers",
        epilog="""
Examples:
  tool.py add 2 3
  tool.py add -1 5
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    add_parser.add_argument("a", type=int, help="First number")
    add_parser.add_argument("b", type=int, help="Second number")
    add_parser.set_defaults(func=cmd_add, _parser=add_parser)

    # ===== Subcommand: greet =====
    greet_parser = subparsers.add_parser(
        "greet",
        help="Greet someone",
        epilog="""
Examples:
  tool.py greet Alice
  tool.py greet Alice --times 3
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    greet_parser.add_argument("name", help="Name to greet")
    greet_parser.add_argument(
        "--times",
        type=int,
        default=1,
        help="How many times to greet (default: 1)"
    )
    greet_parser.set_defaults(func=cmd_greet, _parser=greet_parser)

    # ---- No arguments -> show main help ----
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # ---- Subcommand with no parameters -> show subcommand help ----
    if len(sys.argv) >= 2 and sys.argv[1] in subparsers.choices:
        subcmd = sys.argv[1]
        # Only the subcommand name itself was provided
        if len(sys.argv) == 2:
            subparsers.choices[subcmd].print_help()
            sys.exit(0)

    args = parser.parse_args()

    if args.verbose:
        print("Verbose mode enabled")
        print(f"Parsed args: {args}")

    args.func(args)


def cmd_add(args):
    result = args.a + args.b
    print(f"{args.a} + {args.b} = {result}")


def cmd_greet(args):
    for _ in range(args.times):
        print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()



