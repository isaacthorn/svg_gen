"""
Tests for lex.py
"""

import lex

import pytest


@pytest.mark.parametrize(('input_str', 'expected_tokens'), [
    ('a', ['LABEL']),
    ('a b c d', ['LABEL', 'LABEL', 'LABEL', 'LABEL']),
    ('a( b )', ['LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a( b c )', ['LABEL_OPEN', 'LABEL', 'LABEL', 'RPAREN']),
    ('a( b c( d ) )', ['LABEL_OPEN', 'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'RPAREN']),
    ('a( b c( d ) e f( g ) h )', ['LABEL_OPEN', 'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN',
                                  'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL', 'RPAREN']),
    ('a( b ) c', ['LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a b( c )', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a b( c ) d', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a( b ) c( d )', ['LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a( b c( d ) e( f ) g )', ['LABEL_OPEN', 'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN',
                                'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL', 'RPAREN']),
    ('a( b ) c( d ) e', ['LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a b( c ) d( e )', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a b( c ) d( e ) f', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a( + )', ['LABEL_OPEN', 'PLUS', 'RPAREN']),
    ('a( b + )', ['LABEL_OPEN', 'LABEL', 'PLUS', 'RPAREN']),
    ('a( + b )', ['LABEL_OPEN', 'PLUS', 'LABEL', 'RPAREN']),
    ('a( b + c )', ['LABEL_OPEN', 'LABEL', 'PLUS', 'LABEL', 'RPAREN']),
    ('a( + b( + ) )', ['LABEL_OPEN', 'PLUS', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'RPAREN']),
    ('a( b( + ) + )', ['LABEL_OPEN', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'PLUS', 'RPAREN']),
    ('a( b + c( + ) )', ['LABEL_OPEN', 'LABEL', 'PLUS', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'RPAREN']),
    ('a( b( + ) + c )', ['LABEL_OPEN', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'PLUS', 'LABEL', 'RPAREN']),
    ('a( b + c d( + ) )', ['LABEL_OPEN', 'LABEL', 'PLUS', 'LABEL', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'RPAREN']),
    ('a( b( + ) c + d )', ['LABEL_OPEN', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'LABEL', 'PLUS', 'LABEL', 'RPAREN'])
])
def test_token_types(input_str: str, expected_tokens: list[str]):
    parsed = lex.tokenise(input_str)

    assert len(parsed) == len(expected_tokens)
    assert all(token.type == expected for token, expected in zip(parsed, expected_tokens))


@pytest.mark.parametrize(('input_str', 'expected_tokens'), [
    ('a', ['LABEL']),
    ('a b c d', ['LABEL', 'LABEL', 'LABEL', 'LABEL']),
    ('a(b )', ['LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a( b c)', ['LABEL_OPEN', 'LABEL', 'LABEL', 'RPAREN']),
    ('a( b c(d ) )', ['LABEL_OPEN', 'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'RPAREN']),
    ('a(b c( d) e f( g) h )', ['LABEL_OPEN', 'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN',
                               'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL', 'RPAREN']),
    ('a(b ) c', ['LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a b( c)', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a b( c ) d', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a( b ) c(d)', ['LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a(b c( d) e(f ) g )', ['LABEL_OPEN', 'LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN',
                             'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL', 'RPAREN']),
    ('a( b) c(d ) e', ['LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a b(c ) d( e )', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN']),
    ('a b( c) d( e ) f', ['LABEL', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL_OPEN', 'LABEL', 'RPAREN', 'LABEL']),
    ('a(+)', ['LABEL_OPEN', 'PLUS', 'RPAREN']),
    ('a( b+ )', ['LABEL_OPEN', 'LABEL', 'PLUS', 'RPAREN']),
    ('a(+b )', ['LABEL_OPEN', 'PLUS', 'LABEL', 'RPAREN']),
    ('a(b+c)', ['LABEL_OPEN', 'LABEL', 'PLUS', 'LABEL', 'RPAREN']),
    ('a( +b(+ ) )', ['LABEL_OPEN', 'PLUS', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'RPAREN']),
    ('a( b( +) + )', ['LABEL_OPEN', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'PLUS', 'RPAREN']),
    ('a( b +c( + ))', ['LABEL_OPEN', 'LABEL', 'PLUS', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'RPAREN']),
    ('a( b( +) + c)', ['LABEL_OPEN', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'PLUS', 'LABEL', 'RPAREN']),
    ('a( b +c d( +) )', ['LABEL_OPEN', 'LABEL', 'PLUS', 'LABEL', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'RPAREN']),
    ('a(b( +) c + d )', ['LABEL_OPEN', 'LABEL_OPEN', 'PLUS', 'RPAREN', 'LABEL', 'PLUS', 'LABEL', 'RPAREN'])
])
def test_erratic_whitespace(input_str: str, expected_tokens: list[str]):
    """
    Same as previous test except that random spaces have been removed (in locations which shouldn't affect the lexing)
    """
    parsed = lex.tokenise(input_str)

    assert len(parsed) == len(expected_tokens)
    assert all(token.type == expected for token, expected in zip(parsed, expected_tokens))


@pytest.mark.parametrize(('input_str', 'expected_names'), [
    ('a', ['a']),
    ('a b c d', ['a', 'b', 'c', 'd']),
    ('a( b', ['a(', 'b']),
    ('a( b c', ['a(', 'b', 'c']),
    ('a( b c( d', ['a(', 'b', 'c(', 'd']),
    ('a( b c( d e f( g h ', ['a(', 'b', 'c(', 'd', 'e', 'f(', 'g', 'h']),
])
def test_label_names(input_str: str, expected_names: list[str]):
    """
    Test that token.value is correct for all token types

    RPAREN and PLUS tokens don't have a value that means anything, so they are omitted. This makes the test inputs
    invalid notation, but the tokeniser does not check validity, so this doesn't matter.
    """
    parsed = lex.tokenise(input_str)

    assert len(parsed) == len(expected_names)
    assert all(token.value == expected for token, expected in zip(parsed, expected_names))


@pytest.mark.parametrize('input_str', [
    '*',
    'a b *',
    'a( * )',
    'a( + * )'
])
def test_raises_illegal_char(input_str: str):
    with pytest.raises(ValueError) as e:
        lex.tokenise(input_str)
    assert 'Illegal character' in str(e.value)
