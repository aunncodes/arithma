import sympy


superscripts = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def pretty(value, parent_precedence=0):
    if value is True:
        return "true"

    if value is False:
        return "false"

    if value == sympy.pi:
        return "π"

    if value == sympy.E:
        return "e"

    if value == sympy.oo:
        return "∞"

    if value == -sympy.oo:
        return "-∞"

    if isinstance(value, sympy.Integer):
        return str(value)

    if isinstance(value, sympy.Float):
        return str(value)

    if isinstance(value, sympy.Rational):
        if value.q == 1:
            return str(value.p)

        text = f"{value.p}/{value.q}"
        return f"({text})" if parent_precedence > 2 else text

    if isinstance(value, sympy.Symbol):
        return value.name

    if isinstance(value, sympy.Add):
        terms = value.as_ordered_terms()
        text = pretty(terms[0], 1)

        for term in terms[1:]:
            if term.could_extract_minus_sign():
                text += " - " + pretty(-term, 1)
            else:
                text += " + " + pretty(term, 1)

        return f"({text})" if parent_precedence > 1 else text

    if isinstance(value, sympy.Mul):
        numerator, denominator = sympy.fraction(value)

        if denominator != 1:
            top = pretty(numerator, 2)
            bottom = pretty(denominator, 3)

            if isinstance(numerator, sympy.Add):
                top = f"({top})"

            if isinstance(denominator, (sympy.Add, sympy.Mul)):
                bottom = f"({bottom})"

            text = f"{top}/{bottom}"
            return f"({text})" if parent_precedence > 2 else text

        factors = value.as_ordered_factors()
        text = ""
        previous = None

        for factor in factors:
            current = pretty(factor, 2)

            if not text:
                text = current
            elif can_touch(previous, factor):
                text += current
            else:
                text += " · " + current

            previous = factor

        return f"({text})" if parent_precedence > 2 else text

    if isinstance(value, sympy.Pow):
        base, exponent = value.as_base_exp()

        if exponent == sympy.Rational(1, 2):
            inside = pretty(base)
            if isinstance(base, (sympy.Add, sympy.Mul)):
                inside = f"({inside})"
            return "√" + inside

        base_text = pretty(base, 3)
        if isinstance(base, (sympy.Add, sympy.Mul)):
            base_text = f"({pretty(base)})"

        if isinstance(exponent, sympy.Integer):
            return base_text + str(exponent).translate(superscripts)

        exponent_text = pretty(exponent)
        return f"{base_text}^({exponent_text})"

    if isinstance(value, sympy.Abs):
        return f"|{pretty(value.args[0])}|"

    if isinstance(value, sympy.Function):
        arguments = ", ".join(pretty(argument) for argument in value.args)
        return f"{value.func.__name__}({arguments})"

    return str(value)


def can_touch(left, right):
    if left is None:
        return True

    if left.is_number:
        return True

    if left == sympy.pi or left == sympy.E:
        return isinstance(right, sympy.Symbol) and len(right.name) == 1

    if isinstance(left, sympy.Symbol) and len(left.name) == 1:
        return isinstance(right, sympy.Symbol) and len(right.name) == 1

    return False
