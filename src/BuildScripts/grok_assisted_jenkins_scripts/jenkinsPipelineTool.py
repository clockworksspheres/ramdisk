#!/usr/bin/env python3
"""
"""
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
    #parser_run.add_argument("--job", help="Pipeline name to run")
    '''
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url", required=True,
                      help="Jenkins URL – MUST include scheme: http://localhost:8080 or https://ci.company.com")
    conn.add_argument("--user", required=True, help="Jenkins username")
    conn.add_argument("--token", required=True, help="Jenkins API token (from User → Configure → API Token)")
    '''
    job_group = parser_run.add_argument_group("Job to trigger (required)")
    job_group.add_argument("--job", required=True,
                           help="Job name (supports folders: folder/subfolder/job-name)")
    job_group.add_argument("--token-build", dest="build_token", default=None,
                           help="Optional: 'Trigger builds remotely' auth token (if enabled on job)")

    opts = parser_run.add_argument_group("Build & output options")
    opts.add_argument("--param", action="append", metavar="KEY=VALUE",
                      help="Build parameter KEY=VALUE (repeatable)")
    opts.add_argument("--follow", action="store_true",
                      help="Stream console output until build finishes")
    opts.add_argument("--timeout", type=int, default=3600,
                      help="Max wait time (seconds) when --follow (default: 3600)")


    # Subcommand: check
    parser_check = subparsers.add_parser(
        "check", parents=[parent_parser], help="Show status of the last (most recent) build of a Jenkins job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:

            # 1. Basic – check last build of a job
            python %(prog)s --url http://localhost:8080 --user admin --token 116b8f2a... \\
                --job nightly-tests

            # 2. Job inside folder + more details
            python %(prog)s --url https://jenkins.company.com --user <username> --token your-token \\
                --job "DevTeam/Projects/Web/build-and-deploy" --verbose

            # 3. Using IP address (common for local network Jenkins)
            python %(prog)s --url http://192.168.1.150:8080 --user admin --token 11abcdef... \\
                --job smoke-test-pipeline --verbose

            # 4. Show this help
            python %(prog)s --help
        """
        )
    )

    # Job
    job_group = parser_check.add_argument_group("Job selection (required)")
    #job_group.add_argument("--job", dest="job_name", required=True,
    job_group.add_argument("--job", required=True,
                           help="Job name (supports folders: folder/subfolder/job-name)")

    # Output style
    parser_check.add_argument("--verbose", "-v", action="store_true",
                        help="Show more details (triggered by, description, duration in seconds)")


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

    elif args.command == "create":
        print(f"Creating {args.url} for pipeline <{args.job_name}>...")
        import CreateJenkinsPipeline.CreateJenkinsPipeline as createPipeline

        cjp = createPipeline()
        cjp.create_jenkins_pipeline(args)

    elif args.command == "run":
        print(f"Running {args.url} for pipeline <{args.job}>...")
        import RunJenkinsPipeline.RunJenkinsPipeline as runPipeline

        rpipeline = runPipeline()
        rpipeline.controller(args)

    elif args.command == "check":
        print(f"Checking {args.url} for pipeline <{args.job}>...")
        import CheckJenkinsPipeline.CheckJenkinsPipeline as checkPipeline

        ckpipeline = checkPipeline()
        ckpipeline.check_run(args)


    print("\n")
    print(f"command: {args.command}")
    print(f"args: {vars(args)}")
  
