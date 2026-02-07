import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='cmd', required=True)

# Subcommand 'run'
run = subparsers.add_parser('run')
run.add_argument('--verbose', action='store_true')
run.add_argument('--output', type=str)
run.add_argument('--retries', type=int, default=3)

# Subcommand 'test'
test = subparsers.add_parser('test')
test.add_argument('--debug', action='store_true')
test.add_argument('--timeout', type=float)

args = parser.parse_args()

# Execute based on command
if args.cmd == 'run':
    print(f"Running with verbose={args.verbose}, output={args.output}, retries={args.retries}")
elif args.cmd == 'test':
    print(f"Testing with debug={args.debug}, timeout={args.timeout}")
else:
    parser.print_help()   


