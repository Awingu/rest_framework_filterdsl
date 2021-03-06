# encoding: utf8

from pyparsing import CaselessKeyword, Combine, Group, Keyword, \
         Literal, nums, Optional, Or, QuotedString, \
         Word, ZeroOrMore, Forward, alphanums

from .exceptions import BadQuery
from .base import BOOLEAN_TRUE_VALUES, BOOLEAN_FALSE_VALUES

import itertools
try:
    from functools import lru_cache
except ImportError:
    # python <= 3.2
    try:
        from functools32 import lru_cache
    except:
        # no caching
        def lru_cache():
            '''do-nothing lru_cache implementation'''
            def decorator(fn):
                def wrapper(*a, **kw):
                    return fn(*a, **kw)
                return wrapper
            return decorator


def fail(msg):
    raise BadQuery(msg)

class Token(object):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, self.value)

    @property
    def value(self):
        return self._value

class GroupToken(Token):
    tokens = []

    def __init__(self, tokens):
        self.tokens = list(itertools.chain(*tokens))

    def _filter_class(self, token_class):
        return [t for t in self.tokens if isinstance(t, token_class)]

    def _filter_class_first(self, token_class):
        for t in self.tokens:
            if isinstance(t, token_class):
                return t

    def __repr__(self):
        return "{0}({1})".format(
                self.__class__.__name__,
                ' '.join([repr(t) for t in self.tokens])
        )


class Field(Token):
    @property
    def name(self):
        return self.value.lower()

class Negation(Token):
    pass

class Operator(GroupToken):
    @property
    def op(self):
        for t in self.tokens:
            if not isinstance(t, Negation):
                return t.lower()

    @property
    def negate(self):
        return self._filter_class_first(Negation) is not None


class Value(Token):
    def __repr__(self):
        return self.value

class String(Value):
    pass

class Integer(Value):
    pass

class Float(Value):
    pass

class Boolean(Value):
    @property
    def value(self):
        value = self._value.lower()
        if value in BOOLEAN_TRUE_VALUES:
            return True
        if value in BOOLEAN_FALSE_VALUES:
            return False
        return value

class LogicalOp(Token):
    @property
    def op(self):
        return self.value.lower()

class Comparison(GroupToken):

    @property
    def fields(self):
        return self._filter_class(Field)

    @property
    def operator(self):
        return self._filter_class_first(Operator)

    @property
    def values(self):
        return self._filter_class(Value)

class Statement(Token):
    pass

class SortDirection(Token):
    pass

class SortDirective(GroupToken):
    @property
    def field(self):
        return self._filter_class_first(Field)

    @property
    def direction(self):
        return self._filter_class_first(SortDirection) or SortDirection('+')

def _build_field_expr():
    field = Word(alphanums+'_')
    field.setParseAction(lambda x: Field(x[0]))
    return field

def build_filter_parser():
    return _build_filter_parser()

@lru_cache()
def _build_filter_parser():
    field = _build_field_expr()

    negation = CaselessKeyword('not')
    negation.setParseAction(lambda x: Negation(x[0]))

    comparison_operator = Group(
            Keyword('=')
            ^ Keyword('!=')
            ^ Keyword('>=')
            ^ Keyword('<=')
            ^ Keyword('<')
            ^ Keyword('>')
            ^ Keyword('lte') # match before lt
            ^ Keyword('lt')
            ^ Keyword('gte') # match before gt
            ^ Keyword('gt')
            ^ (Optional(negation) + (
                    CaselessKeyword('contains')
                    ^ CaselessKeyword('icontains')
                    ^ CaselessKeyword('startswith')
                    ^ CaselessKeyword('istartswith')
                    ^ CaselessKeyword('endswith')
                    ^ CaselessKeyword('iendswith')
                    ^ CaselessKeyword('eq')
                    )
             )
        )
    comparison_operator.setParseAction(lambda x: Operator(x))

    single_value_operator = Group(
            CaselessKeyword('isnull')
            ^  (Optional(negation) + CaselessKeyword('isnull'))
    )
    single_value_operator.setParseAction(lambda x: Operator(x))

    plusorminus = Literal('+') | Literal('-')

    num_integer = Combine(
            Optional(plusorminus) + Word(nums)
    )
    num_integer.setParseAction(lambda x: Integer(x[0]))

    num_float = Combine(
            Optional(plusorminus) + Word(nums) + '.' + Word(nums)
    )
    num_float.setParseAction(lambda x: Float(x[0]))

    quoted_string = (
            QuotedString("'")
            ^ QuotedString('"')
    )
    quoted_string.setParseAction(lambda x: String(x[0]))

    boolean = Or(
            [CaselessKeyword(v) for v in BOOLEAN_TRUE_VALUES+BOOLEAN_FALSE_VALUES]
        )
    boolean.setParseAction(lambda x: Boolean(x[0]))

    value = (
            quoted_string
            ^ num_integer
            ^ num_float
            ^ boolean
    )

    comparison = Group(
            (field + comparison_operator + value)
            ^ (value + comparison_operator + field)
            ^ (field + comparison_operator + field)
            ^ (field + single_value_operator)
    )
    comparison.setParseAction(lambda x: Comparison(x))

    invalid_comparison = Group(
            (
                value
                + comparison_operator 
                + value
            ).setParseAction(lambda x: fail("Value may not be compared with values: {0}".format(' '.join(x))))
    )

    logical_op = Group(
            CaselessKeyword("and") | CaselessKeyword("or")
    )
    logical_op.setParseAction(lambda x: LogicalOp(x[0][0]))

    expr = Forward()
    statement = (
            comparison
            | invalid_comparison
            | (Literal('(').suppress() + expr + Literal(')').suppress())
    )
    statement.setParseAction(lambda x: Statement(x))

    expr << statement + ZeroOrMore(logical_op + statement)

    return expr


def build_sort_parser():
    return _build_sort_parser()

@lru_cache()
def _build_sort_parser():
    field = _build_field_expr()

    plusorminus = Literal('+') | Literal('-')
    plusorminus.setParseAction(lambda x: SortDirection(x[0]))

    sort_directive = Group(
                Optional(plusorminus) + field
    ).setParseAction(lambda x: SortDirective(x))

    statement = Optional(sort_directive) + ZeroOrMore(
            Literal(',') + sort_directive
    )
    return statement
