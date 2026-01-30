#!/usr/bin/env -S python -u

import argparse
import requests
import sys

sys.path.append("../../..")

import jenkinstokens.jenkinstoken as token

"""
requires the requests library to be installed vi pip...

To create an api token
1 : Log in to Jenkins.
2 : Go to User > Configure > API Token.
3 : Click Add new Token, name it, and generate.
4 : Copy and store it securely—it won't be shown again.

no luck trying to gen one via python yet.

"""


def start_jenkins_job(user, name, token):

    print(f"{user}")
    print(f"{token}")

    jenkins_url = "http://localhost:8080"  # Replace with your Jenkins URL
    job_name = "ramdisk"  # Replace with your job name
    auth = (f"{user}", f"{token}")  # Use API token instead of password for security# Trigger the build
    build_url = f"{jenkins_url}/job/{name}/build"
    response = requests.post(build_url, auth=auth)

    # Check if the request was successful
    if response.status_code == 201:
        print("Build triggered successfully")
    else:
        print(f"Failed to trigger build: {response.status_code} - {response.text}")

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

    creds = start_jenkins_job(args.user, args.token_name, credential.strip())

    print(f"{creds}")
    

