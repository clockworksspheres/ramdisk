#!/usr/bin/env python3
"""
argparse example – each subcommand shows ALL its options in the epilog

2025 style: groups + complete epilog listing every flag

Usage examples:
    tool.py                     # shows available commands
    tool.py -h                  # global help
    tool.py download --help     # detailed help + full option list in epilog
    tool.py upload -h
"""

import argparse
import sys
from textwrap import dedent


def show_command_list(parser):
    """Nice listing when no subcommand is given"""
    print("No command specified.\n")
    print("Available commands:\n")

    subparsers_action = next(
        a for a in parser._actions
        if isinstance(a, argparse._SubParsersAction)
    )

    for name, subp in sorted(subparsers_action.choices.items()):
        desc = subp.description or "(no description)"
        if len(desc) > 68:
            desc = desc[:65] + "..."
        print(f"  {name:<12}  {desc}")

    print("\nRun:")
    print("  tool.py <command> -h      detailed help + all options")
    print("  tool.py <command> --help  same as above\n")


def create_parser():
    parser = argparse.ArgumentParser(
        prog="tool",
        description="Example file transfer & processing tool",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run <command> -h for full options of each command.\n"
               "Run without arguments to see available commands."
    )

    parser.add_argument("-V", "--version", action="version", version="%(prog)s 0.8.1")

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
        help="download file from URL",
        description="Download file from HTTP/HTTPS/FTP/S3/... location.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            All available options for 'download':

              -u, --url URL             Source URL                              (required)
              -o, --output PATH         Output filename / directory
              -q, --quiet               Suppress progress and status messages
              --retries N               Number of retry attempts                (default: 3)
              --timeout SECONDS         Connection timeout                      (default: 30)
              --no-progress             Disable progress bar
              --user-agent STRING       Custom User-Agent header
              --referer URL             Custom Referer header
              --cookies FILE            Netscape-format cookies file
              --proxy URL               Use HTTP/HTTPS/SOCKS proxy
              --insecure                Skip SSL certificate verification
              --resume                  Resume partial download if possible
              --speed-limit RATE        Limit download speed (e.g. 500K, 2M)
              --dry-run                 Show what would be downloaded
              -v, --verbose             Increase verbosity (can be repeated)
              -h, --help                Show this help message and exit
        """)
    )
    dl.add_argument_group("Required").add_argument("-u", "--url", required=True, metavar="URL")
    dl.add_argument_group("Output").add_argument("-o", "--output")
    dl.add_argument_group("Output").add_argument("-q", "--quiet", action="store_true")
    dl.add_argument_group("Network").add_argument("--retries", type=int, default=3)
    dl.add_argument_group("Network").add_argument("--timeout", type=int, default=30)
    dl.add_argument_group("Network").add_argument("--no-progress", action="store_true")
    dl.add_argument_group("Headers").add_argument("--user-agent")
    dl.add_argument_group("Headers").add_argument("--referer")
    dl.add_argument_group("Headers").add_argument("--cookies")
    dl.add_argument_group("Proxy & Security").add_argument("--proxy")
    dl.add_argument_group("Proxy & Security").add_argument("--insecure", action="store_true")
    dl.add_argument_group("Advanced").add_argument("--resume", action="store_true")
    dl.add_argument_group("Advanced").add_argument("--speed-limit")
    dl.add_argument_group("Simulation").add_argument("--dry-run", action="store_true")
    dl.add_argument("-v", "--verbose", action="count", default=0)
    dl.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  upload
    # ────────────────────────────────────────────────
    up = subparsers.add_parser(
        "upload",
        help="upload file to server",
        description="Upload local file to remote server (HTTP/S3/FTP/...).",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            All available options for 'upload':

              -f, --file PATH           Local file to upload                    (required)
              -u, --url URL             Destination URL                         (required)
              --name NAME               Remote filename (default: same as local)
              --content-type MIME       Force Content-Type header
              --chunk-size BYTES        Upload in chunks of this size           (default: 8MB)
              --retries N               Retry failed chunks                     (default: 3)
              --no-progress             Disable upload progress bar
              --proxy URL               Use proxy server
              --insecure                Skip SSL verification
              --dry-run                 Show what would be uploaded
              -v, --verbose             Increase verbosity
              -h, --help                Show this help message and exit
        """)
    )
    up.add_argument_group("Required").add_argument("-f", "--file", required=True, metavar="PATH")
    up.add_argument_group("Required").add_argument("-u", "--url", required=True, metavar="URL")
    up.add_argument_group("Naming").add_argument("--name")
    up.add_argument_group("HTTP").add_argument("--content-type")
    up.add_argument_group("Performance").add_argument("--chunk-size", type=int, default=8*1024*1024)
    up.add_argument_group("Reliability").add_argument("--retries", type=int, default=3)
    up.add_argument_group("Display").add_argument("--no-progress", action="store_true")
    up.add_argument_group("Network").add_argument("--proxy")
    up.add_argument_group("Network").add_argument("--insecure", action="store_true")
    up.add_argument_group("Simulation").add_argument("--dry-run", action="store_true")
    up.add_argument("-v", "--verbose", action="count", default=0)
    up.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  info
    # ────────────────────────────────────────────────
    info = subparsers.add_parser(
        "info",
        help="show file / URL information",
        description="Show metadata, size, type, headers etc.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            All available options for 'info':

              -f, --file PATH           Local file to inspect
              -u, --url URL             Remote URL to inspect
              --json                    Output in JSON format
              --headers                 Show only HTTP response headers
              --no-color                Disable colored output
              --timeout SECONDS         Request timeout                         (default: 15)
              -v, --verbose             More detailed output
              -h, --help                Show this help message and exit

            Note: exactly one of --file or --url must be provided.
        """)
    )
    g = info.add_mutually_exclusive_group(required=True)
    g.add_argument("-f", "--file", metavar="PATH")
    g.add_argument("-u", "--url", metavar="URL")
    info.add_argument("--json", action="store_true")
    info.add_argument("--headers", action="store_true")
    info.add_argument("--no-color", action="store_true")
    info.add_argument("--timeout", type=int, default=15)
    info.add_argument("-v", "--verbose", action="count", default=0)
    info.add_argument("-h", "--help", action="help")

    return parser


def main():
    parser = create_parser()

    if len(sys.argv) == 1:
        show_command_list(parser)
        return 0

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 2 and len(sys.argv) == 1:
            show_command_list(parser)
            return 0
        raise

    print(f"Command: {args.command}")
    print(f"  verbose = {getattr(args, 'verbose', 0)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


