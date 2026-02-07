import argparse

def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(description='Example CLI with subcommands')
    
    # Create subparsers
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add subcommand 'greet'
    greet_parser = subparsers.add_parser('greet', help='Say hello')
    greet_parser.add_argument('name', help='Name to greet')
    
    # Add subcommand 'add'
    add_parser = subparsers.add_parser('add', help='Add two numbers')
    add_parser.add_argument('x', type=int, help='First number')
    add_parser.add_argument('y', type=int, help='Second number')

    # Parse arguments
    args = parser.parse_args()

    # Execute based on command
    if args.command == 'greet':
        print(f'Hello, {args.name}!')
    elif args.command == 'add':
        print(f'Sum: {args.x + args.y}')

if __name__ == '__main__':
    main()   

