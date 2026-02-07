import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='cmd')

# Subcommand 'greet'
greet = subparsers.add_parser('greet')
greet.add_argument('--name', default='World', help='Name to greet')

# Subcommand 'add'
add = subparsers.add_parser('add')
add.add_argument('--x', type=int, default=0)
add.add_argument('--y', type=int, default=0)

args = parser.parse_args()

if args.cmd == 'greet':
    print(f"Hello, {args.name}!")
elif args.cmd == 'add':
    print(f"Sum: {args.x + args.y}")   


