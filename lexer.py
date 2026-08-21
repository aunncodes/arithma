class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"{self.type}({self.value})"


class Lexer:
    single_char_tokens = {
        "+": "PLUS",
        "-": "MINUS",
        "*": "MULTIPLY",
        "/": "DIVIDE",
        "^": "POWER",
        "=": "EQUALS",
        "(": "LEFT_PAREN",
        ")": "RIGHT_PAREN",
        ",": "COMMA",
    }

    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1

    def tokenize(self):
        tokens = []

        while self.position < len(self.source):
            char = self.source[self.position]

            if char in " \t\r":
                self.advance()
                continue

            if char == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.column))
                self.advance_line()
                continue

            if char == "#":
                self.skip_comment()
                continue

            if char == '"':
                tokens.append(self.read_string())
                continue

            if char.isdigit() or char == ".":
                tokens.append(self.read_number())
                continue

            if char.isalpha() or char == "_":
                tokens.append(self.read_name())
                continue

            if char in self.single_char_tokens:
                tokens.append(
                    Token(
                        self.single_char_tokens[char],
                        char,
                        self.line,
                        self.column,
                    )
                )
                self.advance()
                continue

            raise SyntaxError(
                f"Unexpected character '{char}' at line {self.line}, column {self.column}"
            )

        tokens.append(Token("EOF", "", self.line, self.column))
        return tokens

    def read_string(self):
        start_line = self.line
        start_column = self.column
        self.advance()
        value = ""

        while self.position < len(self.source):
            char = self.source[self.position]

            if char == '"':
                self.advance()
                return Token("STRING", value, start_line, start_column)

            if char == "\n":
                raise SyntaxError(
                    f"String was not closed at line {start_line}, column {start_column}"
                )

            if char == "\\":
                self.advance()

                if self.position >= len(self.source):
                    break

                escaped = self.source[self.position]
                escapes = {
                    '"': '"',
                    "\\": "\\",
                    "n": "\n",
                    "t": "\t",
                }
                value += escapes.get(escaped, escaped)
                self.advance()
                continue

            value += char
            self.advance()

        raise SyntaxError(
            f"String was not closed at line {start_line}, column {start_column}"
        )

    def read_number(self):
        start = self.position
        start_column = self.column
        decimal_found = False

        while self.position < len(self.source):
            char = self.source[self.position]

            if char.isdigit():
                self.advance()
                continue

            if char == "." and not decimal_found:
                decimal_found = True
                self.advance()
                continue

            break

        value = self.source[start:self.position]

        if value == ".":
            raise SyntaxError(
                f"Invalid number at line {self.line}, column {start_column}"
            )

        return Token("NUMBER", value, self.line, start_column)

    def read_name(self):
        start = self.position
        start_column = self.column

        while self.position < len(self.source):
            char = self.source[self.position]

            if not (char.isalnum() or char == "_"):
                break

            self.advance()

        value = self.source[start:self.position]
        return Token("NAME", value, self.line, start_column)

    def skip_comment(self):
        while (
            self.position < len(self.source)
            and self.source[self.position] != "\n"
        ):
            self.advance()

    def advance(self):
        self.position += 1
        self.column += 1

    def advance_line(self):
        self.position += 1
        self.line += 1
        self.column = 1
