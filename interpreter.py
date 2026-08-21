import sympy

from functions import constants, functions, output
from parser import Binary, Call, ExpressionStatement, FunctionDefinition, Let, Name, Number, Unary


class ArithmaFunction:
    arithma_function = True

    def __init__(self, name, parameter, body, symbol):
        self.name = name
        self.parameter = parameter
        self.body = body
        self.symbol = symbol

    def call(self, value):
        return self.body.subs(self.symbol, value)


class Interpreter:
    def __init__(self):
        self.variables = {}
        self.user_functions = {}

    def run(self, statements):
        for statement in statements:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, Let):
            self.variables[statement.name] = self.evaluate(statement.value)
            return

        if isinstance(statement, FunctionDefinition):
            symbol = sympy.Symbol(statement.parameter)

            old_value = self.variables.get(statement.parameter)
            self.variables[statement.parameter] = symbol

            body = self.evaluate(statement.body)

            if old_value is None:
                del self.variables[statement.parameter]
            else:
                self.variables[statement.parameter] = old_value

            self.user_functions[statement.name] = ArithmaFunction(
                statement.name,
                statement.parameter,
                body,
                symbol,
            )
            return

        if isinstance(statement, ExpressionStatement):
            self.evaluate(statement.expression)
            return

        raise TypeError(f"Unknown statement type: {type(statement).__name__}")

    def evaluate(self, expression):
        if isinstance(expression, Number):
            if "." in expression.value:
                return sympy.Float(expression.value)

            return sympy.Integer(expression.value)

        if isinstance(expression, Name):
            if expression.value in self.variables:
                return self.variables[expression.value]

            if expression.value in self.user_functions:
                return self.user_functions[expression.value]

            if expression.value in constants:
                return constants[expression.value]

            return sympy.Symbol(expression.value)

        if isinstance(expression, Unary):
            value = self.evaluate(expression.value)

            if expression.operator == "+":
                return value

            if expression.operator == "-":
                return -value

        if isinstance(expression, Binary):
            left = self.evaluate(expression.left)
            right = self.evaluate(expression.right)

            if expression.operator == "+":
                return left + right

            if expression.operator == "-":
                return left - right

            if expression.operator == "*":
                return left * right

            if expression.operator == "/":
                return left / right

            if expression.operator == "^":
                return left ** right

        if isinstance(expression, Call):
            arguments = [self.evaluate(argument) for argument in expression.arguments]

            if expression.name == "output":
                if len(arguments) != 1:
                    raise TypeError("output() expects exactly one value")

                output(arguments[0])
                return arguments[0]

            if expression.name in functions:
                return functions[expression.name](*arguments)

            if expression.name in self.user_functions:
                function = self.user_functions[expression.name]

                if len(arguments) != 1:
                    raise TypeError(
                        f"{expression.name}() expects exactly one value"
                    )

                return function.call(arguments[0])

            raise NameError(f"Unknown function '{expression.name}'")

        raise TypeError(f"Unknown expression type: {type(expression).__name__}")
