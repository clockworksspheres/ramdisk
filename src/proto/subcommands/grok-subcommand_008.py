#!/usr/bin/env python3
"""
Media Toolkit – argparse with detailed per-subcommand epilogs

Shows:
- top-level help: only subcommands + short description
- each subcommand -h: full options + epilog listing every flag

Examples:
    python mediatool.py                # list subcommands
    python mediatool.py -h             # same + global options
    python mediatool.py download -h    # detailed help + all options in epilog
"""

import argparse
import sys
from textwrap import dedent


def print_no_command_message(parser):
    """Called when no subcommand is given"""
    print("No command specified.\n")
    print("Available commands:\n")

    subparsers_action = next(
        a for a in parser._actions
        if isinstance(a, argparse._SubParsersAction)
    )

    for name, subp in sorted(subparsers_action.choices.items()):
        # Use .description instead of .help
        desc = subp.description or "(no description)"
        # Shorten if very long
        if len(desc) > 68:
            desc = desc[:65] + "..."
        print(f"  {name:12}  {desc}")

    print(dedent("""
Run:
  mediatool <command> -h     for detailed help on a command
  mediatool <command> --help for the same
    """).rstrip())


def create_parser():
    parser = argparse.ArgumentParser(
        prog="mediatool",
        description="Simple media processing toolkit",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run <command> -h for detailed help on each command.\n"
               "Run without arguments to see available commands."
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 0.9.3"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        metavar="<command>",
        help="available commands (use <command> -h for options)"
    )

    # ────────────────────────────────────────────────
    #                  download
    # ────────────────────────────────────────────────
    dl = subparsers.add_parser(
        "download",
        help="download media from a URL",                  # short one-liner for main help
        description="Download video, audio or image from web location.",  # longer text shown in listing & -h
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Options for 'download':

              -u, --url       Source URL                                (required)
              -o, --output    Output filename / directory               (default: downloaded.%ext)
              -q, --quiet     Suppress progress / status messages
                  --retries   Number of retry attempts on network error (default: 3)
                  --timeout   Connection timeout in seconds             (default: 30)
                  --no-progress  Disable progress bar even if not --quiet
              -v, --verbose   Increase output verbosity
              -h, --help      Show this help message and exit
        """)
    )
    g1 = dl.add_argument_group("Required")
    g1.add_argument("-u", "--url", required=True, metavar="URL")

    g2 = dl.add_argument_group("Output")
    g2.add_argument("-o", "--output", default=None)
    g2.add_argument("-q", "--quiet", action="store_true")

    g3 = dl.add_argument_group("Network")
    g3.add_argument("--retries", type=int, default=3)
    g3.add_argument("--timeout", type=int, default=30)
    g3.add_argument("--no-progress", action="store_true")

    dl.add_argument("-v", "--verbose", action="count", default=0)
    dl.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  convert
    # ────────────────────────────────────────────────
    conv = subparsers.add_parser(
        "convert",
        help="convert media file format or quality",
        description="Convert audio/video files to different format or bitrate.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Options for 'convert':

              -i, --input       Input file                                      (required)
              -o, --output      Output filename                                 (default: input.newext)
              -f, --format      Target format (mp3, aac, mp4, wav, opus, ...)   (default: mp3)
              -b, --bitrate     Target bitrate (e.g. 128k, 256k, 4M)           (default: 192k)
                  --overwrite   Overwrite output file if it exists
                  --dry-run     Show what would be done without writing files
              -v, --verbose     Increase output detail
              -h, --help        Show this help message and exit
        """)
    )
    g1 = conv.add_argument_group("Required")
    g1.add_argument("-i", "--input", required=True, metavar="FILE")

    g2 = conv.add_argument_group("Output settings")
    g2.add_argument("-o", "--output", default=None)
    g2.add_argument("-f", "--format", default="mp3")
    g2.add_argument("-b", "--bitrate", default="192k")
    g2.add_argument("--overwrite", action="store_true")

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
            Options for 'metadata':

              -f, --file        Media file to read                              (required)
                  --json        Output machine-readable JSON instead of text
                  --full        Show all available metadata fields
                  --no-color    Disable colored output
              -v, --verbose     More detailed / debug output
              -h, --help        Show this help message and exit
        """)
    )
    g1 = meta.add_argument_group("Required")
    g1.add_argument("-f", "--file", required=True, metavar="FILE")

    g2 = meta.add_argument_group("Output format")
    g2.add_argument("--json", action="store_true")
    g2.add_argument("--full", action="store_true")
    g2.add_argument("--no-color", action="store_true")

    meta.add_argument("-v", "--verbose", action="count", default=0)
    meta.add_argument("-h", "--help", action="help")

    return parser


def main():
    parser = create_parser()

    # No subcommand → nice list
    if len(sys.argv) == 1:
        print_no_command_message(parser)
        return 0

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # Catch missing subcommand case
        if e.code == 2 and len(sys.argv) == 1:
            print_no_command_message(parser)
            return 0
        raise

    # Very minimal demo dispatch
    print(f"Running: {args.command}")
    if hasattr(args, "verbose"):
        print(f"  verbose level: {args.verbose}")

    if args.command == "download":
        print(f"  url    = {args.url}")
        print(f"  output = {args.output or '<auto>'}")
    elif args.command == "convert":
        print(f"  input  = {args.input}")
        print(f"  format = {args.format}")
    elif args.command == "metadata":
        print(f"  file   = {args.file}")
        print(f"  json   = {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


