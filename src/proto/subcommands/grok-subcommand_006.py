#!/usr/bin/env python3
"""
Media Toolkit CLI
Simple example showing modern argparse + subparsers style

Usage:
    mediatool             # shows available commands
    mediatool -h          # global help
    mediatool download -h
    mediatool convert -h
    mediatool metadata -h
"""

import argparse
import sys
from textwrap import dedent


def create_parent_parser():
    """Arguments shared across all subcommands"""
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--verbose", "-v",
        action="count",
        default=0,
        help="increase verbosity level (-v, -vv, -vvv)"
    )
    parent.add_argument(
        "--dry-run",
        action="store_true",
        help="simulate the operation without making changes"
    )
    parent.add_argument(
        "--config",
        metavar="FILE",
        help="path to configuration file"
    )
    return parent


def print_available_commands(parser):
    """Friendly message when no subcommand is provided"""
    print("No command specified.\n")
    print("Available commands:\n")

    subparsers_action = next(
        a for a in parser._actions
        if isinstance(a, argparse._SubParsersAction)
    )

    commands = sorted(subparsers_action.choices.items(), key=lambda x: x[0])

    for name, subp in commands:
        help_line = subp.description or subp.help or "(no description)"
        if len(help_line) > 68:
            help_line = help_line[:65] + "..."
        print(f"  {name:12}  {help_line}")

    print(dedent("""
Run a command with -h for detailed help, for example:
  mediatool download -h
  mediatool convert -h
    """).strip())


def create_parser():
    parser = argparse.ArgumentParser(
        prog="mediatool",
        description="Media processing toolkit",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
Use <command> -h for detailed help on each command.
Run without arguments to see the list of available commands.
        """)
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 0.9.2"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        metavar="<command>",
        help="available commands (run without arguments to list them)"
    )

    # ────────────────────────────────────────────────
    #                  download
    # ────────────────────────────────────────────────
    dl = subparsers.add_parser(
        "download",
        help="download media from URL",
        description="Download video, audio or image from a web URL.",
        parents=[create_parent_parser()],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog=dedent("""\
            Options for 'download':

              --url, -u       Source URL (required)
              --output, -o    Output filename or directory
              --quiet, -q     Suppress progress output
              --retries       Number of retry attempts (default: 3)
              --timeout       Connection timeout in seconds (default: 30)
              --dry-run       Show what would be downloaded
              --verbose, -v   Increase output detail
              --help, -h      Show this help message
        """)
    )
    dl_req = dl.add_argument_group("required arguments")
    dl_req.add_argument("--url", "-u", required=True, help="source URL")

    dl_out = dl.add_argument_group("output control")
    dl_out.add_argument("--output", "-o", default="downloaded", help="output path")
    dl_out.add_argument("--quiet", "-q", action="store_true", help="be quiet")

    dl_net = dl.add_argument_group("network behavior")
    dl_net.add_argument("--retries", type=int, default=3, help="retry count")
    dl_net.add_argument("--timeout", type=int, default=30, help="timeout (s)")

    dl.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  convert
    # ────────────────────────────────────────────────
    conv = subparsers.add_parser(
        "convert",
        help="convert media format / quality",
        description="Convert between audio/video formats or adjust quality.",
        parents=[create_parent_parser()],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog=dedent("""\
            Options for 'convert':

              --input, -i       Input file (required)
              --output, -o      Output filename
              --format, -f      Target format (mp3, mp4, wav, aac, ...)
              --bitrate, -b     Target bitrate (128k, 192k, 4M, ...)
              --overwrite       Overwrite existing output file
              --dry-run         Simulate conversion
              --verbose, -v     More detailed output
              --help, -h        Show this help message
        """)
    )
    conv_req = conv.add_argument_group("required arguments")
    conv_req.add_argument("--input", "-i", required=True, help="input file")

    conv_fmt = conv.add_argument_group("format & quality")
    conv_fmt.add_argument("--format", "-f", default="mp3",
                          help="target format")
    conv_fmt.add_argument("--bitrate", "-b", default="192k",
                          help="target bitrate")

    conv_beh = conv.add_argument_group("behavior")
    conv_beh.add_argument("--overwrite", action="store_true",
                          help="overwrite without asking")
    conv.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  metadata
    # ────────────────────────────────────────────────
    meta = subparsers.add_parser(
        "metadata",
        help="show media file information",
        description="Display metadata and technical information about media files.",
        parents=[create_parent_parser()],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
        epilog=dedent("""\
            Options for 'metadata':

              --file, -f        Media file to analyze (required)
              --json            Output in JSON format
              --full            Show all available metadata fields
              --verbose, -v     More detailed output
              --help, -h        Show this help message
        """)
    )
    meta_req = meta.add_argument_group("required arguments")
    meta_req.add_argument("--file", "-f", required=True, help="file to inspect")

    meta_out = meta.add_argument_group("output format")
    meta_out.add_argument("--json", action="store_true", help="JSON output")
    meta_out.add_argument("--full", action="store_true", help="all fields")

    meta.add_argument("-h", "--help", action="help")

    return parser


def main():
    parser = create_parser()

    # Handle case when no subcommand is given
    if len(sys.argv) == 1:
        print_available_commands(parser)
        return 0

    try:
        args = parser.parse_args()
    except SystemExit as e:
        # Catch argparse's exit when required subcommand is missing
        if e.code == 2 and len(sys.argv) == 1:
            print_available_commands(parser)
            return 0
        parser.exit(e.code)

    # Demo dispatch (replace with real logic)
    print(f"Command: {args.command}")
    print(f"Verbose level: {args.verbose}")
    print(f"Dry run: {args.dry_run}")

    if args.command == "download":
        print(f"  Would download: {args.url}")
        print(f"         to:      {args.output}")
    elif args.command == "convert":
        print(f"  Would convert:  {args.input}")
        print(f"      to format:  {args.format}")
    elif args.command == "metadata":
        print(f"  Would read metadata from: {args.file}")
        print(f"               JSON output: {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


