import requests
import sys

sys.path.append("../../..")

import jenkinstokens.jenkinstoken as token

"""
To create an api token
1 : Log in to Jenkins.
2 : Go to User > Configure > API Token.
3 : Click Add new Token, name it, and generate.
4 : Copy and store it securely—it won't be shown again.

no luck trying to gen one via python yet.

"""

print(f"{token.USER}")
print(f"{token.API_TOKEN}")



jenkins_url = "http://localhost:8080"  # Replace with your Jenkins URL
job_name = "ramdisk"  # Replace with your job name
auth = (f"{token.USER}", f"{token.API_TOKEN}")  # Use API token instead of password for security# Trigger the build
build_url = f"{jenkins_url}/job/{job_name}/build"
response = requests.post(build_url, auth=auth)

# Check if the request was successful
if response.status_code == 201:
    print("Build triggered successfully")
else:
    print(f"Failed to trigger build: {response.status_code} - {response.text}")


