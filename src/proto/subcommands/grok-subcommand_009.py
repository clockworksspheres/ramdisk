#!/usr/bin/env python3
"""
Media Toolkit CLI – main --help shows subcommands + key options in epilog

Examples:
    python mediatool.py --help          # ← shows subcommands + their main options
    python mediatool.py                 # friendly list of commands
    python mediatool.py download --help # detailed help for that command
"""

import argparse
import sys
from textwrap import dedent


def print_available_commands(parser):
    print("No command specified.\n")
    print("Available commands:\n")

    subparsers_action = next(
        a for a in parser._actions
        if isinstance(a, argparse._SubParsersAction)
    )

    for name, subp in sorted(subparsers_action.choices.items()):
        desc = subp.description or subp.help or "(no description)"
        if len(desc) > 68:
            desc = desc[:65] + "..."
        print(f"  {name:12}  {desc}")

    print("\nRun:   mediatool <command> --help   for full options & examples")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="mediatool",
        description="Simple media processing toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Available commands and their most common options:

              download
                  Download media from URL
                  -u, --url URL           (required)
                  -o, --output FILE
                  -q, --quiet
                  --retries N

              convert
                  Convert file format / quality
                  -i, --input FILE        (required)
                  -f, --format FMT        (mp3, mp4, wav, ...)
                  -b, --bitrate RATE
                  --overwrite

              metadata
                  Show file metadata
                  -f, --file PATH         (required)
                  --json
                  --full
                  --no-color

            Use <command> --help for full list of options and examples.
            Run without arguments to see this list again.
        """)
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 0.9.4"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        metavar="<command>",
        help="one of the commands above (use <command> --help for details)"
    )

    # ────────────────────────────────────────────────
    #                  download
    # ────────────────────────────────────────────────
    dl = subparsers.add_parser(
        "download",
        help="download media from a URL",
        description="Download video, audio or image from a web URL.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'download':

              -u, --url URL         Source location                              (required)
              -o, --output PATH     Where to save the file
              -q, --quiet           Suppress progress output
                  --retries N       Retry attempts on failure                  (default: 3)
                  --timeout SEC     Connection timeout                         (default: 30)
                  --no-progress     Disable progress bar
              -v, --verbose         More output
              -h, --help            Show this help message
        """)
    )
    dl.add_argument_group("Required").add_argument("-u", "--url", required=True, metavar="URL")
    dl.add_argument_group("Output").add_argument("-o", "--output")
    dl.add_argument_group("Output").add_argument("-q", "--quiet", action="store_true")
    dl.add_argument_group("Network").add_argument("--retries", type=int, default=3)
    dl.add_argument_group("Network").add_argument("--timeout", type=int, default=30)
    dl.add_argument_group("Network").add_argument("--no-progress", action="store_true")
    dl.add_argument("-v", "--verbose", action="count", default=0)
    dl.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  convert
    # ────────────────────────────────────────────────
    conv = subparsers.add_parser(
        "convert",
        help="convert media format or quality",
        description="Convert between audio/video formats or adjust quality.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'convert':

              -i, --input FILE      Input media file                           (required)
              -o, --output PATH     Output filename
              -f, --format FMT      Target format                              (default: mp3)
              -b, --bitrate RATE    Target bitrate                             (default: 192k)
                  --overwrite       Overwrite existing file
                  --dry-run         Show plan without doing anything
              -v, --verbose         More detailed output
              -h, --help            Show this help message
        """)
    )
    conv.add_argument_group("Required").add_argument("-i", "--input", required=True, metavar="FILE")
    conv.add_argument("-o", "--output")
    conv.add_argument("-f", "--format", default="mp3")
    conv.add_argument("-b", "--bitrate", default="192k")
    conv.add_argument("--overwrite", action="store_true")
    conv.add_argument("--dry-run", action="store_true")
    conv.add_argument("-v", "--verbose", action="count", default=0)
    conv.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  metadata
    # ────────────────────────────────────────────────
    meta = subparsers.add_parser(
        "metadata",
        help="show technical metadata of media file",
        description="Display format, duration, bitrate, resolution, tags, etc.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'metadata':

              -f, --file PATH       Media file to analyze                        (required)
                  --json            Output as JSON
                  --full            Include all available fields
                  --no-color        Disable colored terminal output
              -v, --verbose         More detailed output
              -h, --help            Show this help message
        """)
    )
    meta.add_argument_group("Required").add_argument("-f", "--file", required=True, metavar="PATH")
    meta.add_argument("--json", action="store_true")
    meta.add_argument("--full", action="store_true")
    meta.add_argument("--no-color", action="store_true")
    meta.add_argument("-v", "--verbose", action="count", default=0)
    meta.add_argument("-h", "--help", action="help")

    return parser


def main():
    parser = create_parser()

    if len(sys.argv) == 1:
        print_available_commands(parser)
        return 0

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 2 and len(sys.argv) == 1:
            print_available_commands(parser)
            return 0
        raise

    # Minimal demo dispatch
    print(f"Command: {args.command}")
    print(f"  verbose: {getattr(args, 'verbose', 0)}")

    if args.command == "download":
        print(f"  url     = {getattr(args, 'url', '?')}")
    elif args.command == "convert":
        print(f"  input   = {getattr(args, 'input', '?')}")
    elif args.command == "metadata":
        print(f"  file    = {getattr(args, 'file', '?')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


