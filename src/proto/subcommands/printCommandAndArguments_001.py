import argparse

def main():
    parser = argparse.ArgumentParser(
        prog="toolbox",
        description="A command-line tool with multiple subcommands.",
        epilog="Use `toolbox <subcommand> --help` for details on each subcommand."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Subcommand: add ---
    parser_add = subparsers.add_parser(
        "add",
        help="Add two numbers together.",
        description="Adds two integers and prints the result.",
        epilog="""Examples:
  toolbox add 5 10
  toolbox add -3 7"""
    )
    parser_add.add_argument("x", type=int, help="First integer")
    parser_add.add_argument("y", type=int, help="Second integer")

    #parser_add_args = parser_add.parse_args()
    #print(str(parser_add_args))

    # --- Subcommand: greet ---
    parser_greet = subparsers.add_parser(
        "greet",
        help="Print a personalized greeting.",
        description="Greets a user by name with an optional title.",
        epilog="""Examples:
  toolbox greet Alice
  toolbox greet Bob --title Dr."""
    )
    parser_greet.add_argument("name", help="Name of the person to greet")
    parser_greet.add_argument("--title", help="Optional title (e.g., Mr., Dr.)")

    # --- Subcommand: convert ---
    parser_convert = subparsers.add_parser(
        "convert",
        help="Convert temperatures between Celsius and Fahrenheit.",
        description="Converts a temperature value between Celsius and Fahrenheit.",
        epilog="""Examples:
  toolbox convert --to-fahrenheit 100
  toolbox convert --to-celsius 212"""
    )
    group = parser_convert.add_mutually_exclusive_group(required=True)
    group.add_argument("--to-fahrenheit", type=float, help="Convert Celsius to Fahrenheit")
    group.add_argument("--to-celsius", type=float, help="Convert Fahrenheit to Celsius")

    args = parser.parse_args()

    # --- Command Logic ---
    if args.command == "add":
        result = args.x + args.y
        print(f"Result: {result}")

    elif args.command == "greet":
        if args.title:
            print(f"Hello, {args.title} {args.name}!")
        else:
            print(f"Hello, {args.name}!")

    elif args.command == "convert":
        if args.to_fahrenheit is not None:
            result = (args.to_fahrenheit * 9/5) + 32
            print(f"{args.to_fahrenheit}°C = {result:.2f}°F")
        elif args.to_celsius is not None:
            result = (args.to_celsius - 32) * 5/9
            print(f"{args.to_celsius}°F = {result:.2f}°C")

    return args


if __name__ == "__main__":
    args = main()

    print("\n\n")
    print(f"{args.command}")
    print(f"{vars(args)}")


