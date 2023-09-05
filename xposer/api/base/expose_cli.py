# cli_interface.py

import argparse

from my_class import Calculator


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=['add', 'subtract'])
    parser.add_argument("x", type=float)
    parser.add_argument("y", type=float)

    args = parser.parse_args()

    calculator = Calculator()

    if args.operation == 'add':
        print(calculator.add(args.x, args.y))
    elif args.operation == 'subtract':
        print(calculator.subtract(args.x, args.y))

if __name__ == "__main__":
    main()
