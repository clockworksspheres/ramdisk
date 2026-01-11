import argparse
import time
import jenkins

import sys

sys.path.append('../../..')

import jenkinstokens.jenkinstoken as token

def start_pipeline(user, name, token):
    # ========================
    # Jenkins configuration
    # ========================
    JENKINS_URL = "http://localhost:8080"
    USERNAME = user
    API_TOKEN = token

    JOB_NAME = name
    # Multibranch example:
    # JOB_NAME = "my-multibranch-pipeline/main"

    POLL_INTERVAL = 2  # seconds

    # ========================
    # Connect to Jenkins
    # ========================
    server = jenkins.Jenkins(
        JENKINS_URL,
        username=USERNAME,
        password=API_TOKEN
    )

    print("Connected to Jenkins", server.get_version())

    # ========================
    # Trigger pipeline (NO PARAMETERS)
    # ========================
    print("Triggering pipeline...")

    queue_id = server.build_job(JOB_NAME)

    print(f"Queued build (queue id: {queue_id})")

    # ========================
    # Wait for build number
    # ========================
    print("Waiting for build to start...")

    build_number = None
    while build_number is None:
        queue_item = server.get_queue_item(queue_id)
        if "executable" in queue_item:
            build_number = queue_item["executable"]["number"]
        else:
            time.sleep(POLL_INTERVAL)

    print(f"Build started: #{build_number}")

    # ========================
    # Monitor build
    # ========================
    print("Monitoring pipeline...")

    while True:
        build_info = server.get_build_info(JOB_NAME, build_number)

        if not build_info["building"]:
            print("Build finished with result:", build_info["result"])
            break

        print("Still running...")
        time.sleep(POLL_INTERVAL)

    # ========================
    # Optional: console output
    # ========================
    console = server.get_build_console_output(JOB_NAME, build_number)
    print("\n--- Last 30 lines of console ---")
    print("\n".join(console.splitlines()[-30:]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create authentication tokens for jenkins user")

    # Optional argument with short and long form
    parser.add_argument('--user', '-u', type=str, default="", help='Name of the user to create a token for')

    # Optional argument with short and long form
    parser.add_argument('--token-name', '-n', type=str, default="", help='Name of the token')


    # Boolean flag using action='store_true'
    parser.add_argument('--input-password', '-i', action='store_true', default=False, help='Ask for a password or token for authentication')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not args.user or not args.token_name:
        parser.print_help()
        sys.exit(1)

    if args.input_password: 
        credential = getpass.getpass("Enter valid api-token")
    else:
        credential = token.API_TOKEN

    creds = start_pipeline(args.user, args.token_name, credential.strip())

    print(f"{creds}")

