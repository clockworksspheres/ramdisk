import sys
import textwrap
import argparse

def parse_arguments():
    """
    """

    # Parent parser with shared arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--url", required=True, help="Target resource URL"
    )

    parent_parser.add_argument(
        "--user", required=True, help="User to access the Jenkins server"
    )

    parent_parser.add_argument(
        "--token", required=True, help="User's token to access the Jenkins server"
    )

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: create
    parser_create = subparsers.add_parser(
        "create", parents=[parent_parser], help="Create a new Jenkins pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              # Inline script
              %(prog)s --url http://localhost:8080 --user admin --token ABC123 \\
                --job-name test-inline --type inline --script "echo Hello from CLI!"

              # From Git (Jenkinsfile in root)
              %(prog)s --url http://jenkins --user admin --token XYZ \\
                --job-name my-app-ci --type scm \\
                --repo https://github.com/company/app.git --branch main

              # With custom Jenkinsfile path and credentials
              %(prog)s ... --jenkinsfile ci/Jenkinsfile --credentials-id git-token

              %(prog)s --url http://localhost:8080 --user admin --token a212a654... \\
               --job-name ramdisk_redhat --type scm \\
               --repo https://github.com/company/app.git --branch main \\
               --jenkinsfile ci/Jenkinsfile --credentials-id git-token 

        """)
    )
    parser_create.add_argument("--output", help="Save response to file")

    # Job definition
    job = parser_create.add_argument_group("Job details")
    job.add_argument("--job-name", required=True, help="Name of the new Pipeline job")
    job.add_argument("--description", default="Created via CLI script", help="Job description")

    # Pipeline type & config
    pipeline = parser_create.add_argument_group("Pipeline configuration")
    pipeline.add_argument("--type", required=True, choices=["inline", "scm"],
                          help="Pipeline type: 'inline' (script) or 'scm' (from Git)")
    
    # Inline mode
    inline = parser_create.add_argument_group("Inline Pipeline options (used when --type=inline)")
    inline.add_argument("--script", help="Pipeline script content (string)")
    inline.add_argument("--script-path", help="Path to .groovy/.jenkinsfile file to read as script")

    # SCM mode
    scm = parser_create.add_argument_group("SCM Pipeline options (used when --type=scm)")
    scm.add_argument("--repo", help="Git repository URL")
    scm.add_argument("--branch", default="main", help="Branch name (default: main)")
    scm.add_argument("--jenkinsfile", default="Jenkinsfile", help="Path to Jenkinsfile in repo")
    scm.add_argument("--credentials-id", default="", help="Jenkins credentials ID for Git (optional)")


    # Subcommand: run
    parser_run = subparsers.add_parser(
        "run", parents=[parent_parser], help="Run a jenkins pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=textwrap.dedent("""\
        Examples (note: always include http:// or https:// in --url):

        # 1. Basic trigger
        python %(prog)s --url http://localhost:8080 --user admin --token 116b8f2a... \\
            --job nightly-tests

        # 2. With parameters + real-time console output
        python %(prog)s --url http://jenkins:8080 --user <username> --token your-token-here \\
            --job deploy-service --follow \\
            --param ENVIRONMENT=staging --param VERSION=2.5.0 --param DRY_RUN=true

        # 3. Job inside folder + remote trigger token
        python %(prog)s --url https://ci.company.com --user admin --token abc123... \\
            --job "DevTeam/Mobile/Android/build" \\
            --token-build REMOTE_TRIGGER_KEY_2026 --follow

        # 4. Using IP address (common for local network Jenkins)
        python %(prog)s --url http://192.168.1.150:8080 --user admin --token 11abcdef... \\
            --job smoke-test

        # 5. Show this help
        python %(prog)s --help
                """
        )
    )
    parser_run.add_argument("--job", help="Pipeline name to run")

    # Subcommand: check
    parser_check = subparsers.add_parser(
        "check", parents=[parent_parser], help="Check the status of a Jenkins pipeline"
    )
    parser_check.add_argument("--job", help="Pipeline name to run")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return args


if __name__=="__main__":
    args = parse_arguments()

    # Example logic
    if args.command == "fetch":
        print(f"Fetching {args.url}...")
        if args.output:
            print(f"Saving to {args.output}")

    elif args.command == "check":
        print(f"Checking reachability of {args.url}...")

    elif args.command == "parse":
        print(f"Parsing {args.url} for tag <{args.tag}>...")

