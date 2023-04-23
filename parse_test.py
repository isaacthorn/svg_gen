"""
Tests for parse.py
"""
from complex import Domain, Hairpin, SplitComplex, Chain
import parse

import pytest


def ast_equiv(a, b) -> bool:
    """
    Check if the structure of a and b matches
    """
    if not type(a) is type(b):
        return False
    if isinstance(a, Domain):
        return a.name == b.name
    elif isinstance(a, Hairpin):
        return ast_equiv(a.pre, b.pre) and ast_equiv(a.post, b.post) and ast_equiv(a.inner, b.inner)
    elif isinstance(a, SplitComplex):
        return ast_equiv(a.pre, b.pre) and ast_equiv(a.post, b.post) \
            and ast_equiv(a.left, b.left) and ast_equiv(a.right, b.right)
    elif isinstance(a, Chain):
        return all(ast_equiv(a_child, b_child) for a_child, b_child in zip(a.within, b.within))
    elif a is None:
        # 2 Nones are equivalent (SplitComplex without overhang, for example)
        return True
    raise NotImplementedError


@pytest.mark.parametrize(('input_str', 'expected_structure'), [
    ('a',
     Domain('a')),
    ('a b c d',
     Chain([
         Domain('a'), Domain('b'), Domain('c'), Domain('d')
     ])),
    ('a( b )',
     Hairpin(Domain('a'),
             Chain([
                 Domain('b')
             ]),
             Domain('a*'))),
    ('a( b c )',
     Hairpin(Domain('a'),
             Chain([
                 Domain('b'), Domain('c')
             ]),
             Domain('a*'))),
    ('a( b c( d ) )',
     Hairpin(Domain('a'),
             Chain([
                 Domain('b'),
                 Hairpin(
                     Domain('c'),
                     Chain([
                         Domain('d')
                     ]),
                     Domain('c*'))
             ]),
             Domain('a*'))),
    ('a( b c( d ) e f( g ) h )',
     Hairpin(Domain('a'),
             Chain([
                 Domain('b'),
                 Hairpin(Domain('c'),
                         Chain([
                             Domain('d')
                         ]),
                         Domain('c*')),
                 Domain('e'),
                 Hairpin(Domain('f'),
                         Chain([
                             Domain('g')
                         ]),
                         Domain('f*')),
                 Domain('h')
             ]),
             Domain('a*'))),
    ('a( b ) c',
     Chain([
         Hairpin(Domain('a'),
                 Chain([
                     Domain('b')
                 ]),
                 Domain('a*')),
         Domain('c')
     ])),
    ('a b( c )',
     Chain([
         Domain('a'),
         Hairpin(Domain('b'),
                 Chain([
                     Domain('c')
                 ]),
                 Domain('b*'))
     ])),
    ('a b( c ) d',
     Chain([
         Domain('a'),
         Hairpin(Domain('b'),
                 Chain([
                     Domain('c')
                 ]),
                 Domain('b*')),
         Domain('d')
     ])),
    ('a( b ) c( d )',
     Chain([
         Hairpin(Domain('a'),
                 Chain([
                     Domain('b')
                 ]),
                 Domain('a*')),
         Hairpin(Domain('c'),
                 Chain([
                     Domain('d')
                 ]),
                 Domain('c*'))
     ])),
    ('a( b c( d ) e( f ) g )',
     Hairpin(Domain('a'),
             Chain([
                 Domain('b'),
                 Hairpin(Domain('c'),
                         Chain([
                             Domain('d')
                         ]),
                         Domain('c*')),
                 Hairpin(Domain('e'),
                         Chain([
                             Domain('f')
                         ]),
                         Domain('e*')),
                 Domain('g')
             ]),
             Domain('a*'))),
    ('a( b ) c( d ) e',
     Chain([
         Hairpin(Domain('a'),
                 Chain([
                     Domain('b')
                 ]),
                 Domain('a*')),
         Hairpin(Domain('c'),
                 Chain([
                     Domain('d')
                 ]),
                 Domain('c*')),
         Domain('e')
     ])),
    ('a b( c ) d( e )',
     Chain([
         Domain('a'),
         Hairpin(Domain('b'),
                 Chain([
                     Domain('c')
                 ]),
                 Domain('b*')),
         Hairpin(Domain('d'),
                 Chain([
                     Domain('e')
                 ]),
                 Domain('d*'))
     ])),
    ('a b( c ) d( e ) f',
     Chain([
         Domain('a'),
         Hairpin(Domain('b'),
                 Chain([
                     Domain('c')
                 ]),
                 Domain('b*')),
         Hairpin(Domain('d'),
                 Chain([
                     Domain('e')
                 ]),
                 Domain('d*')),
         Domain('f')
     ])),
    ('a( + )',
     SplitComplex(Domain('a'),
                  None,
                  None,
                  Domain('a*'))),
    ('a( b + )',
     SplitComplex(Domain('a'),
                  Chain([
                      Domain('b')
                  ]),
                  None,
                  Domain('a*'))),
    ('a( + b )',
     SplitComplex(Domain('a'),
                  None,
                  Chain([
                      Domain('b')
                  ]),
                  Domain('a*'))),
    ('a( b + c )',
     SplitComplex(Domain('a'),
                  Chain([
                      Domain('b')
                  ]),
                  Chain([
                      Domain('c')
                  ]),
                  Domain('a*'))),
    ('a( + b( + ) )',
     SplitComplex(Domain('a'),
                  None,
                  Chain([
                      SplitComplex(Domain('b'),
                                   None,
                                   None,
                                   Domain('b*'))
                  ]),
                  Domain('a*'))),
    ('a( b( + ) + )',
     SplitComplex(Domain('a'),
                  Chain([
                      SplitComplex(Domain('b'),
                                   None,
                                   None,
                                   Domain('b*'))
                  ]),
                  None,
                  Domain('a*'))),
    ('a( b + c( + ) )',
     SplitComplex(Domain('a'),
                  Chain([
                      Domain('b')
                  ]),
                  Chain([
                      SplitComplex(Domain('c'),
                                   None,
                                   None,
                                   Domain('c*'))
                  ]),
                  Domain('a*'))),
    ('a( b( + ) + c )',
     SplitComplex(Domain('a'),
                  Chain([
                      SplitComplex(Domain('b'),
                                   None,
                                   None,
                                   Domain('b*'))
                  ]),
                  Chain([
                      Domain('c')
                  ]),
                  Domain('a*'))),
    ('a( b + c d( + ) )',
     SplitComplex(Domain('a'),
                  Chain([
                      Domain('b')
                  ]),
                  Chain([
                      Domain('c'),
                      SplitComplex(Domain('d'),
                                   None,
                                   None,
                                   Domain('d*'))
                  ]),
                  Domain('a*'))),
    ('a( b( + ) c + d )',
     SplitComplex(Domain('a'),
                  Chain([
                      SplitComplex(Domain('b'),
                                   None,
                                   None,
                                   Domain('b*')),
                      Domain('c')
                  ]),
                  Chain([
                      Domain('d')
                  ]),
                  Domain('a*')))
])
def test_parse_structure(input_str, expected_structure):
    ast = parse.parse(input_str)

    assert ast_equiv(ast, expected_structure)


@pytest.mark.parametrize('input_str', [
    'a(',
    'a( b',
    '+',
    'a + b',
    'a + b )',
    'a( b + c + d )'
])
def test_parse_raises(input_str):
    with pytest.raises(ValueError):
        parse.parse(input_str)
