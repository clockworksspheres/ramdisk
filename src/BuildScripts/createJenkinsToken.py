"""

Must already have an existing token for this to work.

"""
import argparse
import getpass
import json
import requests
import sys

sys.path.append("../../..")

import jenkinstokens.jenkinstoken as token


def createToken(user, name, cred):

    print(f"{user}")
    print(f"{name}")
    print(f"{cred}")

    jenkins_url = "http://localhost:8080"
    #username = "your-username"
    #cred = "existing-token"

    username = user

    # Optional: fetch crumb if CSRF is enabled
    crumb_resp = requests.get(
        f"{jenkins_url}/crumbIssuer/api/json",
        auth=(username, cred)
    )
    headers = {}
    if crumb_resp.status_code == 200:
        crumb = crumb_resp.json()
        headers["Jenkins-Crumb"] = crumb["crumb"]

    # Use /me for the currently authenticated user (simpler & avoids name mismatches)
    api_url = f"{jenkins_url}/me/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken"

    payload = {
        "newTokenName": str(name.strip())
    }

    # Important: form-encoded payload, not JSON
    headers["Content-Type"] = "application/x-www-form-urlencoded"

    resp = requests.post(api_url, auth=(username, cred), data=payload, headers=headers)

    # print(f"{resp.json().dumps()}")

    if resp.status_code == 200:
        out = resp.json()
        print("Token created.")
        print("Name:", out["data"]["tokenName"])
        print("Value:", out["data"]["tokenValue"])  # save securely; shown only once
        return out
    else:
        print("Failed:", resp.status_code, resp.text)


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

    creds = createToken(args.user, args.token_name, credential.strip())

    print(f"{creds}")
    
