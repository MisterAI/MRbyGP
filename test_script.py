import sympy
from sympy.core.compatibility import exec_

namespc = {}
exec_('from sympy.abc import x\nfrom sympy import Rational', namespc)

expr = sympy.sympify('sin(0)', locals=namespc)
print(expr)
print(type(expr.func))
