#!/usr/bin/env python3
import argparse
import jenkins
import sys

def get_jenkins():
    # Replace with your Jenkins URL and credentials
    return jenkins.Jenkins(
        'http://localhost:8080',
        username='admin',
        password='admin'
    )

# -------------------------
# Subcommand: get-config
# -------------------------
def cmd_get_config(args):
    j = get_jenkins()
    try:
        xml = j.get_job_config(args.job)
        print(xml)
    except jenkins.NotFoundException:
        print(f"Job '{args.job}' not found", file=sys.stderr)
        sys.exit(1)

# -------------------------
# Subcommand: set-config
# -------------------------
def cmd_set_config(args):
    j = get_jenkins()
    try:
        with open(args.file, "r") as f:
            xml = f.read()
        j.reconfig_job(args.job, xml)
        print(f"Updated job '{args.job}'")
    except FileNotFoundError:
        print(f"File '{args.file}' not found", file=sys.stderr)
        sys.exit(1)
    except jenkins.NotFoundException:
        print(f"Job '{args.job}' not found", file=sys.stderr)
        sys.exit(1)

# -------------------------
# Main CLI
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="Jenkins job config tool")
    sub = parser.add_subparsers(dest="command")

    # get-config
    p_get = sub.add_parser("get-config", help="Download job config XML")
    p_get.add_argument("job", help="Job name")
    p_get.set_defaults(func=cmd_get_config)

    # set-config
    p_set = sub.add_parser("set-config", help="Upload job config XML")
    p_set.add_argument("job", help="Job name")
    p_set.add_argument("file", help="XML file to upload")
    p_set.set_defaults(func=cmd_set_config)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    args.func(args)

if __name__ == "__main__":
    main()


