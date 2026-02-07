#!/usr/bin/env python3

import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Example CLI with arguments and subcommands"
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
        required=True
    )

    # ===== Subcommand: add =====
    add_parser = subparsers.add_parser(
        "add",
        help="Add two numbers"
    )
    add_parser.add_argument(
        "a",
        type=int,
        help="First number"
    )
    add_parser.add_argument(
        "b",
        type=int,
        help="Second number"
    )
    add_parser.set_defaults(func=cmd_add)

    # ===== Subcommand: greet =====
    greet_parser = subparsers.add_parser(
        "greet",
        help="Greet someone"
    )
    greet_parser.add_argument(
        "name",
        help="Name to greet"
    )
    greet_parser.add_argument(
        "--times",
        type=int,
        default=1,
        help="How many times to greet (default: 1)"
    )
    greet_parser.set_defaults(func=cmd_greet)

    args = parser.parse_args()

    if args.verbose:
        print("Verbose mode enabled")
        print(f"Parsed args: {args}")

    # Call the function associated with the subcommand
    args.func(args)


def cmd_add(args):
    result = args.a + args.b
    print(f"{args.a} + {args.b} = {result}")


def cmd_greet(args):
    for _ in range(args.times):
        print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()

