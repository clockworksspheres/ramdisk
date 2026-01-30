#!/usr/bin/env -S python -u
"""

Must already have an existing token for this to work.

python-jenkins and jenkinsapi libraries cannot create tokens, due to 'security risks'

"""
import argparse
import getpass

import requests
from requests.auth import HTTPBasicAuth
import sys

sys.path.append("../../..")

import jenkinstokens.jenkinstoken as token

def createToken(admin_user, target_user, token_name, admin_token):

    JENKINS_URL = "http://localhost:8080"
    ADMIN_USER = admin_user
    ADMIN_TOKEN = admin_token
    #TARGET_USER = "jenkins_user"
    TARGET_USER = target_user
    TOKEN_NAME = token_name

    url = (
        f"{JENKINS_URL}/user/{TARGET_USER}"
        "/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken"
    )

    response = requests.post(
        url,
        auth=HTTPBasicAuth(ADMIN_USER, ADMIN_TOKEN),
        data={"newTokenName": TOKEN_NAME},
        headers={"Jenkins-Crumb": requests.get(
            f"{JENKINS_URL}/crumbIssuer/api/json",
            auth=HTTPBasicAuth(ADMIN_USER, ADMIN_TOKEN)
        ).json()["crumb"]}
    )

    response.raise_for_status()

    token = response.json()["data"]["tokenValue"]
    print("New API token:", token)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create authentication tokens for jenkins user")

    # Optional argument with short and long form
    parser.add_argument('--user', '-u', type=str, default="", help='Name of the user can create a tokens')

    # Optional argument with short and long form
    parser.add_argument('--target-user', '-t', type=str, default="", help='Name of the user to create a token for')

    # Optional argument with short and long form
    parser.add_argument('--token-name', '-n', type=str, default="", help='Name of the token')


    # Boolean flag using action='store_true'
    parser.add_argument('--input-password', '-i', action='store_true', default=False, help='Ask for a password or token for authentication')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not args.user or not args.token_name or not args.target_user:
        parser.print_help()
        sys.exit(1)

    if args.input_password: 
        credential = getpass.getpass("Enter valid api-token")
    else:
        credential = token.API_TOKEN

    creds = createToken(args.user, args.target_user, args.token_name, credential.strip())

    print(f"{creds}")
    

