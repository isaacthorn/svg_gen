from ply import yacc
from lex import tokens

import complex


def p_chain_begin(p):
    '''chain : domain
             | hairpin
             | splitcomplex'''
    p[0] = complex.Chain([p[1]])


def p_chain_extend_domain(p):
    'chain : chain domain'
    p[0] = complex.Chain(p[1].within + [p[2]])


def p_chain_extend_hairpin(p):
    'chain : chain hairpin'
    p[0] = complex.Chain(p[1].within + [p[2]])


def p_chain_extend_splitcomplex(p):
    'chain : chain splitcomplex'
    p[0] = complex.Chain(p[1].within + [p[2]])


def p_hairpin(p):
    'hairpin : domainopen chain RPAREN'
    p[0] = complex.Hairpin(p[1], p[2], complex.create_complementary(p[1]))


def p_splitcomplex_l_r(p):
    'splitcomplex : domainopen chain PLUS chain RPAREN'
    p[0] = complex.SplitComplex(p[1], p[2], p[4], complex.create_complementary(p[1]))


def p_splitcomplex_l(p):
    'splitcomplex : domainopen chain PLUS RPAREN'
    p[0] = complex.SplitComplex(p[1], p[2], None, complex.create_complementary(p[1]))


def p_splitcomplex_r(p):
    'splitcomplex : domainopen PLUS chain RPAREN'
    p[0] = complex.SplitComplex(p[1], None, p[3], complex.create_complementary(p[1]))


def p_splitcomplex_neither(p):
    'splitcomplex : domainopen PLUS RPAREN'
    p[0] = complex.SplitComplex(p[1], None, None, complex.create_complementary(p[1]))


def p_domain(p):
    'domain : LABEL'
    p[0] = complex.Domain(p[1])

def p_domainopen(p):
    'domainopen : LABEL_OPEN'
    p[0] = complex.Domain(p[1][:-1])
    

parser = yacc.yacc()


def parse(data: str):
    return parser.parse(data)


if __name__ == '__main__':
    from sys import argv
    if len(argv) > 1:
        string = argv[1]
    else:
        string = input('>>> ')
    ast = parse(string)
    print(repr(ast))
    print(f'After parsing, {string} = {str(ast)}')

