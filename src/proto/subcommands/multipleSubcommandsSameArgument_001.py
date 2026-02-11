import argparse

parser = argparse.ArgumentParser(prog="toolbox")
subparsers = parser.add_subparsers(dest="command", required=True)

# Subcommand: upload
parser_upload = subparsers.add_parser("upload", help="Upload a file")
parser_upload.add_argument("--file", dest="upload_file", help="File to upload")

# Subcommand: delete
parser_delete = subparsers.add_parser("delete", help="Delete a file")
parser_delete.add_argument("--file", dest="delete_file", help="File to delete")

args = parser.parse_args()

if args.command == "upload":
    print("Uploading:", args.upload_file)
elif args.command == "delete":
    print("Deleting:", args.delete_file)

print(f"command: {args.command}")
print(f"args: {vars(args)}")

