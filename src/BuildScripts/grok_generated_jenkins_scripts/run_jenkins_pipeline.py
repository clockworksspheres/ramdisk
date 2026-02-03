#!/usr/bin/env python3
"""
Trigger (run) a Jenkins job or Pipeline from the command line.

Requires: pip install python-jenkins
"""

import argparse
import sys
import time
import urllib.parse
import jenkins
from jenkins import JenkinsException


def normalize_url(url: str) -> str:
    """Add http:// if missing scheme, warn user"""
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        print("Warning: No scheme (http/https) in --url → assuming http://", file=sys.stderr)
        url = "http://" + url
    return url.rstrip("/")  # clean trailing slash


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Trigger a Jenkins job / Pipeline from the CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples (note: always include http:// or https:// in --url):

  # 1. Basic trigger
  python %(prog)s --url http://localhost:8080 --user admin --token 116b8f2a... \\
    --job nightly-tests

  # 2. With parameters + real-time console output
  python %(prog)s --url http://jenkins:8080 --user roy --token your-token-here \\
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

    conn = parser.add_argument_group("Jenkins connection (required)")
    conn.add_argument("--url", required=True,
                      help="Jenkins URL – MUST include scheme: http://localhost:8080 or https://ci.company.com")
    conn.add_argument("--user", required=True, help="Jenkins username")
    conn.add_argument("--token", required=True, help="Jenkins API token (from User → Configure → API Token)")

    job_group = parser.add_argument_group("Job to trigger (required)")
    job_group.add_argument("--job", required=True,
                           help="Job name (supports folders: folder/subfolder/job-name)")
    job_group.add_argument("--token-build", dest="build_token", default=None,
                           help="Optional: 'Trigger builds remotely' auth token (if enabled on job)")

    opts = parser.add_argument_group("Build & output options")
    opts.add_argument("--param", action="append", metavar="KEY=VALUE",
                      help="Build parameter KEY=VALUE (repeatable)")
    opts.add_argument("--follow", action="store_true",
                      help="Stream console output until build finishes")
    opts.add_argument("--timeout", type=int, default=3600,
                      help="Max wait time (seconds) when --follow (default: 3600)")

    return parser.parse_args()


def parse_parameters(param_list):
    params = {}
    if param_list:
        for item in param_list:
            if '=' not in item:
                print(f"Invalid param: {item!r} — use KEY=VALUE", file=sys.stderr)
                sys.exit(1)
            k, v = item.split("=", 1)
            params[k.strip()] = v.strip()
    return params


def follow_build_output(server, job_name, build_number, timeout_sec):
    print(f"\nFollowing {job_name} #{build_number} console... (Ctrl+C to stop watching)\n")
    
    offset = 0
    start = time.time()

    while time.time() - start < timeout_sec:
        try:
            console = server.get_build_console_output(job_name, build_number)
            if console and len(console) > offset:
                print(console[offset:], end="", flush=True)
                offset = len(console)

            info = server.get_build_info(job_name, build_number)
            if not info.get("building", True):
                result = info.get("result", "UNKNOWN")
                print(f"\n\nFinished → {result}")
                return result == "SUCCESS"
            
            time.sleep(2)
        except KeyboardInterrupt:
            print("\nStopped watching – build continues in Jenkins.")
            return None
        except Exception as e:
            print(f"\nFollow error: {e}", file=sys.stderr)
            return False

    print(f"\nTimeout ({timeout_sec}s) – still running.", file=sys.stderr)
    return False


def main():
    args = parse_arguments()
    args.url = normalize_url(args.url)  # fix common mistake automatically

    params = parse_parameters(args.param)

    try:
        server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

        # Basic connectivity check
        server.get_whoami()  # will raise if auth/URL wrong

        if not server.job_exists(args.job):
            print(f"Job '{args.job}' not found – check name or permissions.", file=sys.stderr)
            sys.exit(1)

        print(f"Triggering: {args.job}")
        if params:
            print(f"  Params: {params}")

        queue_id = server.build_job(args.job, parameters=params, token=args.build_token)

        time.sleep(2)
        queue_item = server.get_queue_item(queue_id)

        if "executable" not in queue_item or queue_item["executable"] is None:
            print("Queued, but no build number yet – check Jenkins UI.")
            sys.exit(0)

        build_number = queue_item["executable"]["number"]
        print(f"→ Started: #{build_number}")
        print(f"→ View: {args.url}/job/{args.job.replace('/', '/job/')}/{build_number}")

        if args.follow:
            success = follow_build_output(server, args.job, build_number, args.timeout)
            if success is False:
                sys.exit(1)

    except jenkins.JenkinsException as e:
        print(f"\nJenkins error: {e}", file=sys.stderr)
        print("→ Double-check --url (include http:// or https://), --user, --token", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


