import sys

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def run_file(path):
    with open(path, "r") as file:
        source = file.read()

    tokens = Lexer(source).tokenize()
    statements = Parser(tokens).parse()
    Interpreter().run(statements)


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <file.ari>")
        return

    path = sys.argv[1]

    if not path.endswith(".ari"):
        print("Arithma files must end in .ari")
        return

    run_file(path)


if __name__ == "__main__":
    main()
