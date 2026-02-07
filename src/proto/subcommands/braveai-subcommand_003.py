import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='cmd', required=True)

# Subcommand 'run' requires --config
run = subparsers.add_parser('run')
run.add_argument('--config', required=True, help='Config file (required for run)')

# Subcommand 'test' makes --config optional
test = subparsers.add_parser('test')
test.add_argument('--config', help='Config file (optional for test)')

args = parser.parse_args()
print(args)   


