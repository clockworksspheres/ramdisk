#!/usr/bin/env python3
"""
aws-like CLI example – modern argparse style

Examples:
    mytool.py user create --name alice --email alice@corp --admin
    mytool.py bucket list --all-regions
    mytool.py -h
    mytool.py bucket -h
"""

import argparse
import sys
from textwrap import dedent


def create_parent_parser():
    """Arguments inherited by all subcommands"""
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--verbose", "-v",
        action="count", default=0,
        help="increase verbosity (can be repeated)"
    )
    parent.add_argument(
        "--config",
        metavar="FILE",
        help="path to config file"
    )
    parent.add_argument(
        "--dry-run", "--dry",
        action="store_true",
        help="simulate operation without making changes"
    )
    return parent


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mytool",
        description="Example modern CLI tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,                     # we add help manually per command
        epilog=dedent("""\
            Use <command> --help for more information about a command.
            Exit codes: 0 = success, 1 = usage error, 2 = runtime error
        """)
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 1.2.3"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        metavar="<command>",
        help="for more help: <command> --help"
    )

    # ── user ────────────────────────────────────────────────
    user_p = subparsers.add_parser(
        "user",
        help="manage users",
        description="Create, list, update or delete users.",
        parents=[create_parent_parser()],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    user_sub = user_p.add_subparsers(dest="user_cmd", required=True)

    # user create
    create = user_sub.add_parser(
        "create",
        help="create a new user",
        description="Creates a new user account.",
        epilog=dedent("""\
            examples:
              mytool user create --name bob --email bob@corp.com
              mytool user create --name alice --admin --dry-run

            options:
              --name        full name (required)
              --email       email address (required)
              --admin       grant admin privileges
              --dry-run     simulate creation
              --verbose     show more output
              --help        show this help
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[create_parent_parser()],
        add_help=False,
    )
    create.add_argument("--name", required=True)
    create.add_argument("--email", required=True)
    create.add_argument("--admin", action="store_true")
    create.add_argument("-h", "--help", action="help")

    # ── bucket ───────────────────────────────────────────────
    bucket = subparsers.add_parser(
        "bucket",
        help="manage storage buckets",
        parents=[create_parent_parser()],
        add_help=False,
    )
    bucket.add_argument("--region", default="us-east-1")
    bucket.add_argument("-h", "--help", action="help")

    return parser


def main():
    parser = build_parser()

    # Modern: better control over errors
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        parser.exit(2, f"error: {e}\n")

    # Dispatch
    if args.command == "user":
        if args.user_cmd == "create":
            print(f"Creating user {args.name} <{args.email}> "
                  f"(admin={args.admin}, dry-run={args.dry_run})")
    elif args.command == "bucket":
        print(f"Bucket operations in region {args.region}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


