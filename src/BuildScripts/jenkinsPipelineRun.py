import time
import jenkins

import sys

sys.path.append('../../..')

import jenkinstokens.jenkinstoken as token


# ========================
# Jenkins configuration
# ========================
JENKINS_URL = "http://localhost:8080"
USERNAME = token.USER
API_TOKEN = token.API_TOKEN

JOB_NAME = "ramdisk"
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

