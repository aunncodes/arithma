class Number:
    def __init__(self, value):
        self.value = value


class String:
    def __init__(self, value):
        self.value = value


class Name:
    def __init__(self, value):
        self.value = value


class Binary:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right


class Unary:
    def __init__(self, operator, value):
        self.operator = operator
        self.value = value


class Call:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class Assignment:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class FunctionDefinition:
    def __init__(self, name, parameter, body):
        self.name = name
        self.parameter = parameter
        self.body = body


class ExpressionStatement:
    def __init__(self, expression):
        self.expression = expression


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        statements = []

        while not self.is_at_end():
            self.skip_newlines()

            if self.is_at_end():
                break

            statements.append(self.statement())

            if not self.check("NEWLINE") and not self.check("EOF"):
                self.error("Expected a new line")

        return statements

    def statement(self):
        if self.looks_like_function_definition():
            return self.function_definition()

        if self.check("NAME") and self.peek(1).type == "EQUALS":
            return self.assignment()

        return ExpressionStatement(self.expression())

    def assignment(self):
        name = self.consume("NAME", "Expected a variable name")
        self.consume("EQUALS", "Expected '=' after the variable name")
        return Assignment(name.value, self.expression())

    def function_definition(self):
        name = self.consume("NAME", "Expected a function name")
        self.consume("LEFT_PAREN", "Expected '(' after the function name")
        parameter = self.consume("NAME", "Expected a parameter name")
        self.consume("RIGHT_PAREN", "Expected ')' after the parameter")
        self.consume("EQUALS", "Expected '=' after the function")
        return FunctionDefinition(name.value, parameter.value, self.expression())

    def expression(self):
        return self.addition()

    def addition(self):
        expression = self.multiplication()

        while self.match("PLUS", "MINUS"):
            operator = self.previous().value
            right = self.multiplication()
            expression = Binary(expression, operator, right)

        return expression

    def multiplication(self):
        expression = self.power()

        while True:
            if self.match("MULTIPLY", "DIVIDE"):
                operator = self.previous().value
                right = self.power()
                expression = Binary(expression, operator, right)
                continue

            if self.starts_implicit_multiplication():
                right = self.power()
                expression = Binary(expression, "*", right)
                continue

            break

        return expression

    def power(self):
        expression = self.unary()

        if self.match("POWER"):
            right = self.power()
            expression = Binary(expression, "^", right)

        return expression

    def unary(self):
        if self.match("PLUS", "MINUS"):
            return Unary(self.previous().value, self.unary())

        return self.primary()

    def primary(self):
        if self.match("NUMBER"):
            return Number(self.previous().value)

        if self.match("STRING"):
            return String(self.previous().value)

        if self.match("NAME"):
            name = self.previous().value

            if self.match("LEFT_PAREN"):
                arguments = []

                if not self.check("RIGHT_PAREN"):
                    arguments.append(self.expression())

                    while self.match("COMMA"):
                        arguments.append(self.expression())

                self.consume("RIGHT_PAREN", "Expected ')' after function arguments")
                return Call(name, arguments)

            return Name(name)

        if self.match("LEFT_PAREN"):
            expression = self.expression()
            self.consume("RIGHT_PAREN", "Expected ')'")
            return expression

        self.error("Expected an expression")

    def looks_like_function_definition(self):
        if not self.check("NAME"):
            return False

        if self.peek(1).type != "LEFT_PAREN":
            return False

        if self.peek(2).type != "NAME":
            return False

        if self.peek(3).type != "RIGHT_PAREN":
            return False

        return self.peek(4).type == "EQUALS"

    def starts_implicit_multiplication(self):
        token = self.current()

        if token.type == "NUMBER":
            return True

        if token.type == "LEFT_PAREN":
            return True

        if token.type == "NAME":
            return True

        return False

    def match(self, *types):
        if self.current().type not in types:
            return False

        self.position += 1
        return True

    def consume(self, type, message):
        if self.check(type):
            token = self.current()
            self.position += 1
            return token

        self.error(message)

    def check(self, type):
        return self.current().type == type

    def current(self):
        return self.tokens[self.position]

    def previous(self):
        return self.tokens[self.position - 1]

    def peek(self, distance):
        position = self.position + distance

        if position >= len(self.tokens):
            return self.tokens[-1]

        return self.tokens[position]

    def skip_newlines(self):
        while self.match("NEWLINE"):
            pass

    def is_at_end(self):
        return self.check("EOF")

    def error(self, message):
        token = self.current()
        raise SyntaxError(
            f"{message} at line {token.line}, column {token.column}"
        )
