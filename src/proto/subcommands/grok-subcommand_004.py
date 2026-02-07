#!/usr/bin/env python3
"""
Tool that lists subcommands nicely when none is given.

Examples:
    python tool.py          # ← shows subcommand list
    python tool.py -h       # global help
    python tool.py backup -h
"""

import argparse
import sys
from textwrap import dedent


def create_parser():
    parser = argparse.ArgumentParser(
        description="Simple backup / restore tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,  # we'll control help manually
        epilog=dedent("""\
            Use <command> -h for detailed help on each command.
            Run without arguments to see available commands.
        """)
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 1.0"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,                # still required → we'll catch the error
        title="commands",
        metavar="<command>",
        help="available commands (run without arguments to list them)"
    )

    # ── backup ────────────────────────────────────────────────
    p_backup = subparsers.add_parser(
        "backup",
        help="create a backup",
        description="Create a new backup archive.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_backup.add_argument("-h", "--help", action="help")
    p_backup.add_argument("paths", nargs="+", metavar="PATH", help="files/directories to back up")
    p_backup.add_argument("--output", "-o", default="backup.tar.gz")

    # ── restore ────────────────────────────────────────────────
    p_restore = subparsers.add_parser(
        "restore",
        help="restore from backup",
        description="Extract files from a backup archive.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p_restore.add_argument("-h", "--help", action="help")
    p_restore.add_argument("archive", help="backup file to restore from")
    p_restore.add_argument("--target", "-t", default="./restored")

    # ── list ───────────────────────────────────────────────────
    p_list = subparsers.add_parser(
        "list",
        help="list backups",
        description="Show available backup archives.",
        add_help=False,
    )
    p_list.add_argument("-h", "--help", action="help")
    p_list.add_argument("--all", action="store_true")

    return parser


def print_available_commands(parser):
    """Custom message when no subcommand is given"""
    print("No command specified.\n")
    print("Available commands:")
    print("")

    # Get subparsers actions
    subparsers_action = next(
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)
    )

    # Sort commands alphabetically
    commands = sorted(subparsers_action.choices.items(), key=lambda x: x[0])

    for name, subparser in commands:
        help_text = subparser.description or subparser.help or "(no description)"
        # Shorten if too long
        if len(help_text) > 60:
            help_text = help_text[:57] + "..."
        print(f"  {name:12}  {help_text}")

    print("\nRun with a command + -h for detailed help, e.g.:")
    print("  tool.py backup -h")


def main():
    parser = create_parser()

    # ── Handle no-subcommand case nicely ───────────────────────
    if len(sys.argv) == 1:
        print_available_commands(parser)
        sys.exit(0)

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparse calls sys.exit(2) when required subcommand is missing
        if e.code == 2 and len(sys.argv) == 1:  # only when truly no args
            print_available_commands(parser)
            sys.exit(0)
        else:
            sys.exit(e.code)

    # Normal dispatch
    if args.command == "backup":
        print(f"Backing up: {args.paths} → {args.output}")
    elif args.command == "restore":
        print(f"Restoring {args.archive} → {args.target}")
    elif args.command == "list":
        print("Listing backups...")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


