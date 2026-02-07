#!/usr/bin/env python3
"""
Example: argparse with detailed per-subcommand epilogs listing all options

Usage examples:
  python tool.py backup --help
  python tool.py backup -h
  python tool.py restore -h
"""

import argparse


def create_parser():
    parser = argparse.ArgumentParser(
        description="Simple backup & restore utility",
        add_help=False,  # we'll add --help manually per subcommand
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        title="commands",
        description="Run <command> --help for detailed usage of each command"
    )

    # ────────────────────────────────────────────────
    #                   backup
    # ────────────────────────────────────────────────
    backup = subparsers.add_parser(
        "backup",
        help="create a new backup",
        description="Creates a compressed backup of files or directories.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Options for 'backup' command:

  -s, --source       Source directory or file to back up (required)
  -d, --destination  Where to store the backup archive
  -n, --name         Custom name for the backup (default: timestamp-based)
  -c, --compress     Compression level 0–9 (default: 6 = good balance)
  --exclude          Patterns to exclude (can be used multiple times)
  --dry-run          Show what would be backed up without writing anything
  -v, --verbose      Show more detailed output
  -q, --quiet        Show only errors
  -h, --help         Show this help message and exit
""",
    )

    backup.add_argument(
        "-s", "--source", required=True, metavar="PATH",
        help="source directory or file"
    )
    backup.add_argument(
        "-d", "--destination", default="./backups",
        help="backup storage directory (default: ./backups)"
    )
    backup.add_argument(
        "-n", "--name", help="custom backup name (default: auto timestamp)"
    )
    backup.add_argument(
        "-c", "--compress", type=int, default=6, choices=range(0,10),
        help="compression level 0–9 (default: 6)"
    )
    backup.add_argument(
        "--exclude", action="append", default=[],
        help="exclude files matching pattern (can be repeated)"
    )
    backup.add_argument(
        "--dry-run", action="store_true",
        help="simulate backup without writing files"
    )
    backup.add_argument(
        "-v", "--verbose", action="store_true",
        help="increase output verbosity"
    )
    backup.add_argument(
        "-q", "--quiet", action="store_true",
        help="suppress non-error messages"
    )
    backup.add_argument(
        "-h", "--help", action="help",
        help="show this help message and exit"
    )

    # ────────────────────────────────────────────────
    #                   restore
    # ────────────────────────────────────────────────
    restore = subparsers.add_parser(
        "restore",
        help="restore from a backup",
        description="Extracts files from a previously created backup archive.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Options for 'restore' command:

  -b, --backup       Path to the backup archive to restore from (required)
  -t, --target       Directory where files should be restored
  --overwrite        Overwrite existing files without asking
  --dry-run          Show what would be restored without extracting
  --list             Only list contents of the backup, don't extract
  -v, --verbose      Show detailed extraction progress
  -h, --help         Show this help message and exit
""",
    )

    restore.add_argument(
        "-b", "--backup", required=True, metavar="ARCHIVE",
        help="backup file to restore from"
    )
    restore.add_argument(
        "-t", "--target", default="./restored",
        help="where to extract files (default: ./restored)"
    )
    restore.add_argument(
        "--overwrite", action="store_true",
        help="overwrite files without prompting"
    )
    restore.add_argument(
        "--dry-run", action="store_true",
        help="simulate restore without writing files"
    )
    restore.add_argument(
        "--list", action="store_true",
        help="only show contents of archive, do not extract"
    )
    restore.add_argument(
        "-v", "--verbose", action="store_true",
        help="show detailed progress"
    )
    restore.add_argument(
        "-h", "--help", action="help",
        help="show this help message and exit"
    )

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "backup":
        print(f"Would backup: {args.source}")
        print(f"      to:     {args.destination}")
        print(f"      name:   {args.name or '<auto>'}")
        print(f"      level:  {args.compress}")
        print(f"      dry-run:{args.dry_run}")

    elif args.command == "restore":
        print(f"Would restore: {args.backup}")
        print(f"       to:     {args.target}")
        print(f"  overwrite:   {args.overwrite}")
        print(f"    dry-run:   {args.dry_run}")
        print(f"       list:   {args.list}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()


