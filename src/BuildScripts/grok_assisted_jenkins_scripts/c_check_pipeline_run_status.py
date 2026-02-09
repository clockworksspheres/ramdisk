#!/usr/bin/env python3
"""
Check the status of the most recent build of a Jenkins job/pipeline.

Requires:
    pip install python-jenkins
"""

import argparse
import sys
import time
from datetime import datetime
import jenkins
from jenkins import JenkinsException


class CheckJenkinsPipelineRun():
    """
    """
    def __init__(self):
        """
        """
        print("Initialized class")

    def format_duration(self, ms: int) -> str:
        """
        Convert milliseconds to human-readable duration
        """
        if ms <= 0:
            return "—"
        seconds = ms // 1000
        minutes = seconds // 60
        seconds %= 60
        hours = minutes // 60
        minutes %= 60
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    def check_run(self, args):
        """
        """
        try:
            server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

            # Quick auth check
            server.get_whoami()

            # Get job information
            job_info = server.get_job_info(args.job, depth=1)

            # Find the last build
            last_build = job_info.get("lastBuild")
            if not last_build:
                print(f"No builds found for job '{args.job}' yet.", file=sys.stderr)
                sys.exit(1)

            build_number = last_build["number"]
            build_info = server.get_build_info(args.job, build_number)

            # Extract key fields
            result = build_info.get("result") or "RUNNING"
            building = build_info.get("building", False)
            timestamp_ms = build_info.get("timestamp", 0)
            duration_ms = build_info.get("duration", 0)

            started_at = datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S") if timestamp_ms else "—"

            print(f"Job          : {args.job}")
            print(f"Last build   : #{build_number}")
            print(f"Status       : {result}{' (still building)' if building else ''}")
            print(f"Started      : {started_at}")

            if args.verbose:
                duration_str = self.format_duration(duration_ms)
                triggered_by = "—"
                short_desc = "—"

                # Try to find who triggered it
                actions = build_info.get("actions", [])
                for action in actions:
                    if action and "_class" in action and "CauseAction" in action["_class"]:
                        causes = action.get("causes", [])
                        if causes:
                            cause = causes[0]
                            triggered_by = cause.get("shortDescription", "—")
                            if "Started by user" in triggered_by:
                                triggered_by = triggered_by.replace("Started by user ", "")
                            break

                # Short description if available
                short_desc = build_info.get("description") or "—"

                print(f"Duration     : {duration_str}")
                print(f"Triggered by : {triggered_by}")
                print(f"Description  : {short_desc}")

            # Exit code useful for scripts/CI
            if building:
                sys.exit(2)          # still running → special code
            elif result == "SUCCESS":
                sys.exit(0)
            else:
                sys.exit(1)          # FAILURE, ABORTED, UNSTABLE, etc.

        except JenkinsException as e:
            print(f"\nJenkins API error: {e}", file=sys.stderr)
            print("→ Check --url (must include http:// or https://), --user, --token, job name", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"\nUnexpected error: {e}", file=sys.stderr)
            sys.exit(4)

  
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Show status of the last (most recent) build of a Jenkins job",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
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

    # Connection
    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url", required=True,
                      help="Jenkins URL (include scheme: http://localhost:8080 or https://ci.company.com)")
    conn.add_argument("--user", required=True, help="Jenkins username")
    conn.add_argument("--token", required=True, help="Jenkins API token")

    # Job
    job_group = parser.add_argument_group("Job selection (required)")
    job_group.add_argument("--job", required=True,
                           help="Job name (supports folders: folder/subfolder/job-name)")

    # Output style
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show more details (triggered by, description, duration in seconds)")

    return parser.parse_args()


if __name__ == "__main__":
    ck_status = CheckJenkinsPipelineRun()

    args = parse_arguments()

    ck_status.check_run(args)


