#!/usr/bin/env python3
"""
Example: Command-line tool with subcommands
    python script.py download --url https://... --output file.mp4 --quiet
    python script.py convert --input video.mp4 --format mp3 --bitrate 192k
    python script.py info --file data.json --verbose
"""

import argparse
import sys


def create_parser():
    parser = argparse.ArgumentParser(
        description="Media processing tool with subcommands",
        epilog="Use -h after any subcommand for more help, e.g. download -h"
    )
    
    # Create subparsers (the actual subcommands)
    subparsers = parser.add_subparsers(
        dest='command',
        required=True,           # make subcommand mandatory
        help="available commands"
    )

    # ────────────────────────────────────────
    #           Subcommand: download
    # ────────────────────────────────────────
    download = subparsers.add_parser(
        'download',
        help='Download media from URL',
        description='Download video/audio from a given URL'
    )
    download.add_argument(
        '--url', '-u',
        required=True,
        help='Source URL to download from'
    )
    download.add_argument(
        '--output', '-o',
        default='downloaded_file',
        help='Output filename (default: %(default)s)'
    )
    download.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress output'
    )
    download.add_argument(
        '--retries',
        type=int,
        default=3,
        help='Number of retry attempts on failure (default: %(default)s)'
    )

    # ────────────────────────────────────────
    #           Subcommand: convert
    # ────────────────────────────────────────
    convert = subparsers.add_parser(
        'convert',
        help='Convert media file to another format',
        description='Convert between audio/video formats'
    )
    convert.add_argument(
        '--input', '-i',
        required=True,
        help='Input file to convert'
    )
    convert.add_argument(
        '--output', '-o',
        help='Output filename (default: input + new extension)'
    )
    convert.add_argument(
        '--format', '-f',
        choices=['mp3', 'wav', 'mp4', 'mkv', 'aac'],
        default='mp3',
        help='Target format (default: %(default)s)'
    )
    convert.add_argument(
        '--bitrate', '-b',
        default='128k',
        help='Target bitrate (e.g. 192k, 256k, 1M)'
    )
    convert.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite output file if it exists'
    )

    # ────────────────────────────────────────
    #           Subcommand: info
    # ────────────────────────────────────────
    info = subparsers.add_parser(
        'info',
        help='Show metadata of a file',
        description='Display information about media file'
    )
    info.add_argument(
        '--file', '-f',
        required=True,
        help='File to inspect'
    )
    info.add_argument(
        '--verbose', '-v',
        action='count',
        default=0,
        help='More detailed output (-v, -vv, -vvv)'
    )
    info.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format'
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # ── Dispatch based on subcommand ───────────────────────────────
    if args.command == 'download':
        print(f"Would download: {args.url}")
        print(f"      to file : {args.output}")
        print(f"      quiet   : {args.quiet}")
        print(f"      retries : {args.retries}")

    elif args.command == 'convert':
        output = args.output or f"converted.{args.format}"
        print(f"Would convert : {args.input}")
        print(f"         to     : {output}")
        print(f"      format    : {args.format}")
        print(f"      bitrate   : {args.bitrate}")
        print(f"      overwrite : {args.overwrite}")

    elif args.command == 'info':
        print(f"Would show info about: {args.file}")
        print(f"              verbose: {args.verbose}")
        print(f"                 json: {args.json}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

