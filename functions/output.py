import matplotlib.pyplot as plt
import numpy
import sympy

from .pretty import pretty


def output(values, use_pretty=True):
    text = []

    for value in values:
        if hasattr(value, "arithma_function"):
            if text:
                print(" ".join(text))
                text = []

            output_function(value, use_pretty)
            continue

        if isinstance(value, str):
            text.append(value)
        elif use_pretty:
            text.append(pretty(value))
        else:
            text.append(sympy.sstr(value))

    if text:
        print(" ".join(text))


def output_function(function, use_pretty=True):
    x_values = numpy.linspace(-10, 10, 500)
    python_function = sympy.lambdify(
        function.symbol,
        function.body,
        modules=["numpy"],
    )

    try:
        y_values = python_function(x_values)
    except Exception as error:
        raise ValueError(f"Could not graph {function.name}: {error}")

    if numpy.isscalar(y_values):
        y_values = numpy.full_like(x_values, y_values, dtype=float)

    body = pretty(function.body) if use_pretty else sympy.sstr(function.body)

    plt.figure()
    plt.plot(x_values, y_values)
    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)
    plt.title(f"{function.name}({function.parameter}) = {body}")
    plt.xlabel(function.parameter)
    plt.ylabel(function.name)
    plt.grid(True)
    plt.show()
