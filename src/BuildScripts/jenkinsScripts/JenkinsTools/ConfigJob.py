#!/usr/bin/env python3
import argparse
import jenkins
import sys
import textwrap

class ConfigJob():
    def __init__(self, args):
        self.args = args
        print(f"Initializing {self.__class__.__name__} class")


    def get_jenkins(self):
        """
        Jenkins connection helper
        """

        try:
            self.server = jenkins.Jenkins(
                url = self.args.url,
                username = self.args.user,
                password = self.args.token
            )

            print("Instantiated server...")

            # Quick connectivity check
            try:
                self.server.get_whoami()
            except Exception as e:
                print("\nCannot connect to Jenkins!", file=sys.stderr)
                print("Common causes:", file=sys.stderr)
                print("  • Wrong --url")
                print("  • Jenkins not running / wrong port")
                print("  • Firewall / network issue")
                print("  • Invalid --user or --token")
                print(f"\nError detail: {e}", file=sys.stderr)
                sys.exit(1)

        except jenkins.JenkinsException as e:
            print(f"\nJenkins API error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            sys.exit(1)

    def cmd_get_config(self):
        """
        Subcommand: get-config
        """
        self.get_jenkins()
        try:
            xml = self.server.get_job_config(self.args.job)
            print(xml)
        except jenkins.NotFoundException:
            print(f"Job '{self.args.job}' not found", file=sys.stderr)
            sys.exit(1)

    def cmd_set_config(self):
        """
        Subcommand: set-config
        """
        self.get_jenkins()
        try:
            with open(args.file, "r") as f:
                xml = f.read()
            self.server.reconfig_job(self.args.job, xml)
            print(f"Updated job '{self.args.job}'")
        except FileNotFoundError:
            print(f"File '{self.args.file}' not found", file=sys.stderr)
            sys.exit(1)
        except jenkins.NotFoundException:
            print(f"Job '{self.args.job}' not found", file=sys.stderr)
            sys.exit(1)


# -------------------------
# Main CLI
# -------------------------
def main():
    # Parent parser for shared options
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--url", required=True, help="Jenkins base URL")
    parent.add_argument("--user", required=True, help="Jenkins username")
    parent.add_argument("--token", required=True, help="Jenkins API token")

    parser = argparse.ArgumentParser(description="Jenkins job config tool")
    sub = parser.add_subparsers(dest="command")

    # get-config
    p_get = sub.add_parser(
        "get-config",
        parents=[parent],
        help="Download job config XML",
        epilog=textwrap.dedent("""
            Example:
              %(prog)s MyJob --url http://jenkins:8080 --user jenkins-user --token 12345

            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_get.add_argument("job", help="Job name")

    # set-config
    p_set = sub.add_parser(
        "set-config",
        parents=[parent],
        help="Upload job config XML",
        epilog=textwrap.dedent("""
            Example:
              %(prog)s MyJob config.xml --url http://jenkins:8080 --user jenkins-user --token 12345

            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p_set.add_argument("job", help="Job name")
    p_set.add_argument("file", help="XML file to upload")

    args = parser.parse_args()

    if not hasattr(args, "command"):
        parser.print_help()
        sys.exit(1)

    config = ConfigJob(args)
    if args.command == "get-config":
        config.cmd_get_config()
    elif args.command == "set-config":
        config.cmd_set_config()

if __name__ == "__main__":
    main()
