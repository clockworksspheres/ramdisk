#!/usr/bin/env python3
"""
CLI with subcommands – each subcommand has its epilog defined as a variable,
and the main --help shows ALL subcommands + their options in the main epilog.
"""

import argparse
import sys
from textwrap import dedent


def show_available_commands(parser):
    """Friendly listing when no subcommand is provided"""
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
    print("  tool <command> -h      detailed help for one command")
    print("  tool <command> --help  same as above\n")


# ────────────────────────────────────────────────
#  Epilog content defined as variables (DRY style)
# ────────────────────────────────────────────────

EPILOG_DOWNLOAD = dedent("""\
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
""")

EPILOG_CONVERT = dedent("""\
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
""")

EPILOG_METADATA = dedent("""\
    metadata
        Show file metadata
        -f, --file PATH         (required)
        --json
        --yaml
        --full
        --summary
        --no-color
        -v, --verbose
""")

EPILOG_INFO = dedent("""\
    info
        Show file / URL information
        -f, --file PATH           or
        -u, --url URL             (exactly one required)
        --json
        --headers
        --no-color
        --timeout SECONDS       (default: 15)
        -v, --verbose
""")

# Combine all subcommand summaries for main epilog
MAIN_EPILOG = dedent("""\
    Available commands and their main options:

    {download}
    {convert}
    {metadata}
    {info}

    Use <command> --help for full documentation, examples and all options.
    Run without arguments to see this list again.
""").format(
    download=EPILOG_DOWNLOAD.strip(),
    convert=EPILOG_CONVERT.strip(),
    metadata=EPILOG_METADATA.strip(),
    info=EPILOG_INFO.strip()
)


def create_parser():
    parser = argparse.ArgumentParser(
        prog="tool",
        description="Media / file processing CLI example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=MAIN_EPILOG
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version="%(prog)s 0.9.6"
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
        description="Download video, audio or image from web URL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(f"""\
            Full options for 'download':

            {EPILOG_DOWNLOAD.strip()}

            Additional / less common options:
              --user-agent STRING
              --referer URL
              --cookies FILE
              --proxy URL
              --insecure
              --resume
              -h, --help
        """)
    )
    dl.add_argument("-u", "--url", required=True, metavar="URL")
    dl.add_argument("-o", "--output")
    dl.add_argument("-q", "--quiet", action="store_true")
    dl.add_argument("--retries", type=int, default=3)
    dl.add_argument("--timeout", type=int, default=30)
    dl.add_argument("--no-progress", action="store_true")
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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(f"""\
            Full options for 'convert':

            {EPILOG_CONVERT.strip()}

            Additional / less common options:
              -q, --quality LEVEL
              --audio-only
              -h, --help
        """)
    )
    conv.add_argument("-i", "--input", required=True, metavar="FILE")
    conv.add_argument("-o", "--output")
    conv.add_argument("-f", "--format", default="mp3")
    conv.add_argument("-b", "--bitrate", default="192k")
    conv.add_argument("--overwrite", action="store_true")
    conv.add_argument("--dry-run", action="store_true")
    conv.add_argument("--two-pass", action="store_true")
    conv.add_argument("-v", "--verbose", action="count", default=0)
    conv.add_argument("-h", "--help", action="help")


    # ────────────────────────────────────────────────
    #                  metadata
    # ────────────────────────────────────────────────
    meta = subparsers.add_parser(
        "metadata",
        help="show media file metadata",
        description="Display technical metadata of media files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(f"""\
            Full options for 'metadata':

            {EPILOG_METADATA.strip()}

            Additional / less common options:
              --max-fields N
              -h, --help
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
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent(f"""\
            Full options for 'info':

            {EPILOG_INFO.strip()}

            Additional / less common options:
              --max-redirects N
              -h, --help
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
        show_available_commands(parser)
        return 0

    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 2 and len(sys.argv) == 1:
            show_available_commands(parser)
            return 0
        raise

    print(f"Command: {args.command}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


