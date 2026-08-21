import matplotlib.pyplot as plt
import numpy
import sympy


def output(value):
    if hasattr(value, "arithma_function"):
        output_function(value)
        return

    print(sympy.sstr(value))


def output_function(function):
    x_values = numpy.linspace(-10, 10, 500)
    python_function = sympy.lambdify(
        function.symbol,
        function.body,
        modules=["numpy"],
    )

    try:
        y_values = python_function(x_values)
    except Exception as error:
        raise ValueError(
            f"Could not graph {function.name}: {error}"
        )

    if numpy.isscalar(y_values):
        y_values = numpy.full_like(x_values, y_values, dtype=float)

    plt.figure()
    plt.plot(x_values, y_values)
    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)
    plt.title(f"{function.name}({function.parameter}) = {sympy.sstr(function.body)}")
    plt.xlabel(function.parameter)
    plt.ylabel(function.name)
    plt.grid(True)
    plt.show()
