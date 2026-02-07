#!/usr/bin/env python3
"""
CLI tool where the main --help shows ALL subcommands + their main options in the epilog

Run:
    python tool.py --help          → overview + all subcommands and options
    python tool.py                 → friendly list of commands
    python tool.py download --help → full detailed help for one command
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

    print(dedent("""
Run:
  tool.py <command> -h      detailed help for one command
  tool.py <command> --help  same as above
    """).strip())


def create_parser():
    parser = argparse.ArgumentParser(
        prog="tool",
        description="Example media / file processing CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Available commands and their options:

              download
                  Download media from URL
                  -u, --url URL           (required)
                  -o, --output PATH
                  -q, --quiet
                  --retries N             (default: 3)
                  --timeout SECONDS       (default: 30)
                  --no-progress
                  --dry-run
                  -v, --verbose

              convert
                  Convert file format / quality
                  -i, --input FILE        (required)
                  -o, --output PATH
                  -f, --format FMT        (default: mp3)
                  -b, --bitrate RATE      (default: 192k)
                  --overwrite
                  --dry-run
                  --two-pass
                  -v, --verbose

              metadata
                  Show file metadata
                  -f, --file PATH         (required)
                  --json
                  --yaml
                  --full
                  --summary
                  --no-color
                  -v, --verbose

              info
                  Show file / URL information
                  -f, --file PATH           or
                  -u, --url URL             (exactly one required)
                  --json
                  --headers-only
                  --no-color
                  --timeout SECONDS       (default: 15)
                  -v, --verbose

            Use <command> --help for full documentation, examples and more options.
            Run without arguments to see this list again.
        """)
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 0.9.5"
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
        help="download media from URL",
        description="Download video, audio or image from web URL.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'download':

              -u, --url URL             Source URL                              (required)
              -o, --output PATH         Output filename / directory
              -q, --quiet               Suppress progress and status messages
              --retries N               Number of retry attempts                (default: 3)
              --timeout SECONDS         Connection timeout                      (default: 30)
              --no-progress             Disable progress bar
              --user-agent STRING       Custom User-Agent header
              --referer URL             Custom Referer header
              --cookies FILE            Netscape-format cookies file
              --proxy URL               Use proxy
              --insecure                Skip SSL verification
              --resume                  Resume partial download
              --dry-run                 Show what would be downloaded
              -v, --verbose             Increase verbosity
              -h, --help                Show this help message and exit
        """)
    )
    dl.add_argument("-u", "--url", required=True, metavar="URL")
    dl.add_argument("-o", "--output")
    dl.add_argument("-q", "--quiet", action="store_true")
    dl.add_argument("--retries", type=int, default=3)
    dl.add_argument("--timeout", type=int, default=30)
    dl.add_argument("--no-progress", action="store_true")
    dl.add_argument("--user-agent")
    dl.add_argument("--referer")
    dl.add_argument("--cookies")
    dl.add_argument("--proxy")
    dl.add_argument("--insecure", action="store_true")
    dl.add_argument("--resume", action="store_true")
    dl.add_argument("--dry-run", action="store_true")
    dl.add_argument("-v", "--verbose", action="count", default=0)
    dl.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  convert
    # ────────────────────────────────────────────────
    conv = subparsers.add_parser(
        "convert",
        help="convert media format / quality",
        description="Convert audio/video to different format or bitrate.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'convert':

              -i, --input FILE          Input file                              (required)
              -o, --output PATH         Output filename
              -f, --format FMT          Target format                           (default: mp3)
              -b, --bitrate RATE        Target bitrate                          (default: 192k)
              -q, --quality LEVEL       Quality scale 0–10
              --overwrite               Overwrite existing file
              --dry-run                 Show plan without writing
              --two-pass                Use two-pass encoding
              --audio-only              Extract audio only
              -v, --verbose             More output
              -h, --help                Show this help message and exit
        """)
    )
    conv.add_argument("-i", "--input", required=True, metavar="FILE")
    conv.add_argument("-o", "--output")
    conv.add_argument("-f", "--format", default="mp3")
    conv.add_argument("-b", "--bitrate", default="192k")
    conv.add_argument("-q", "--quality", type=int)
    conv.add_argument("--overwrite", action="store_true")
    conv.add_argument("--dry-run", action="store_true")
    conv.add_argument("--two-pass", action="store_true")
    conv.add_argument("--audio-only", action="store_true")
    conv.add_argument("-v", "--verbose", action="count", default=0)
    conv.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  metadata
    # ────────────────────────────────────────────────
    meta = subparsers.add_parser(
        "metadata",
        help="show media file metadata",
        description="Display technical metadata of media files.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'metadata':

              -f, --file PATH           Media file to read                      (required)
              --json                    Output JSON instead of text
              --yaml                    Output YAML instead of text
              --full                    Show all available fields
              --summary                 Short summary only
              --no-color                Disable colored output
              -v, --verbose             More detailed output
              -h, --help                Show this help message and exit
        """)
    )
    meta.add_argument("-f", "--file", required=True, metavar="PATH")
    meta.add_argument("--json", action="store_true")
    meta.add_argument("--yaml", action="store_true")
    meta.add_argument("--full", action="store_true")
    meta.add_argument("--summary", action="store_true")
    meta.add_argument("--no-color", action="store_true")
    meta.add_argument("-v", "--verbose", action="count", default=0)
    meta.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  info
    # ────────────────────────────────────────────────
    info = subparsers.add_parser(
        "info",
        help="show file or URL information",
        description="Show metadata, size, type, headers, etc.",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""\
            Full options for 'info':

              -f, --file PATH           Local file to inspect
              -u, --url URL             Remote URL to inspect
              --json                    JSON output
              --headers                 Show only HTTP headers
              --no-color                Disable colors
              --timeout SECONDS         Request timeout                         (default: 15)
              -v, --verbose             More output
              -h, --help                Show this help message and exit

            Note: exactly one of --file or --url must be given.
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
    return 0


if __name__ == "__main__":
    sys.exit(main())


