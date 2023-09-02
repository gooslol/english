"""
SimpleEval - (C) 2013-2023 Daniel Fairhead

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import ast
import operator as op

MAX_STRING_LENGTH = 100000
MAX_POWER = 4000000

class InvalidExpression(Exception):
    pass

class NameNotDefined(InvalidExpression):
    def __init__(self, name, expression):
        self.name = name
        self.message = f"'{name}' is not defined for expression '{expression}'"
        self.expression = expression
        super(InvalidExpression, self).__init__(self.message)

class OperatorNotDefined(InvalidExpression):
    def __init__(self, attr, expression):
        self.message = f"Operator '{attr}' does not exist in expression '{expression}'"
        self.attr = attr
        self.expression = expression
        super(InvalidExpression, self).__init__(self.message)

class FeatureNotAvailable(InvalidExpression):
    pass

class NumberTooHigh(InvalidExpression):
    pass

class IterableTooLong(InvalidExpression):
    pass

def safe_power(a, b):
    if abs(a) > MAX_POWER or abs(b) > MAX_POWER:
        raise NumberTooHigh("Sorry! I don't want to evaluate {0} ** {1}".format(a, b))
    return a**b

def safe_mult(a, b):
    if hasattr(a, "__len__") and b * len(a) > MAX_STRING_LENGTH:
        raise IterableTooLong("Sorry, I will not evalute something that long.")
    if hasattr(b, "__len__") and a * len(b) > MAX_STRING_LENGTH:
        raise IterableTooLong("Sorry, I will not evalute something that long.")

    return a * b

def safe_add(a, b):
    if hasattr(a, "__len__") and hasattr(b, "__len__"):
        if len(a) + len(b) > MAX_STRING_LENGTH:
            raise IterableTooLong(
                "Sorry, adding those two together would" " make something too long."
            )

    return a + b

class SimpleEval(object):
    expr = ""

    def __init__(self):
        self.operators = {
            ast.Add: safe_add,          # Support a + b
            ast.Sub: op.sub,            # Support a - b
            ast.Mult: safe_mult,        # Support a * b
            ast.Div: op.truediv,        # Support a / b
            ast.FloorDiv: op.floordiv,  # Support a // b
            ast.Pow: safe_power,        # Support a ** b
            ast.UAdd: op.pos,           # Support +a
            ast.USub: op.neg            # Support -a
        }
        self.names = {}
        self.nodes = {
            ast.Expr: self._eval_expr,
            ast.Name: self._eval_name,
            ast.BinOp: self._eval_binop,
            ast.UnaryOp: self._eval_unaryop,
            ast.Constant: self._eval_constant
        }

    def __del__(self):
        self.nodes = None

    @staticmethod
    def parse(expr):
        parsed = ast.parse(expr.strip())
        if not parsed.body:
            raise InvalidExpression("Sorry, cannot evaluate empty string")

        return parsed.body[0]

    def eval(self, expr, names={}, previously_parsed=None):
        self.names = names
        self.expr = expr
        return self._eval(previously_parsed or self.parse(expr))

    def _eval(self, node):
        try:
            return self.nodes[type(node)](node)

        except KeyError:
            raise FeatureNotAvailable

    def _eval_expr(self, node):
        return self._eval(node.value)

    @staticmethod
    def _eval_constant(node):
        if hasattr(node.value, "__len__") and len(node.value) > MAX_STRING_LENGTH:
            raise IterableTooLong(
                "Literal in statement is too long!"
                " ({0}, when {1} is max)".format(len(node.value), MAX_STRING_LENGTH)
            )
        return node.value

    def _eval_unaryop(self, node):
        try:
            operator = self.operators[type(node.op)]
        except KeyError:
            raise OperatorNotDefined(node.op, self.expr)
        return operator(self._eval(node.operand))

    def _eval_binop(self, node):
        try:
            operator = self.operators[type(node.op)]
        except KeyError:
            raise OperatorNotDefined(node.op, self.expr)
        return operator(self._eval(node.left), self._eval(node.right))

    def _eval_name(self, node):
        try:
            if hasattr(self.names, "__getitem__"):
                return self.names[node.id]
            if callable(self.names):
                return self.names(node)
            raise InvalidExpression(
                'Trying to use name (variable) "{0}"'
                ' when no "names" defined for'
                " evaluator".format(node.id)
            )

        except KeyError:
            raise NameNotDefined(node.id, self.expr)
