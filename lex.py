from ply import lex


tokens = (
    'LABEL',
    'LABEL_OPEN',
    'RPAREN',
    'PLUS'
)

t_LABEL = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_LABEL_OPEN = r'[a-zA-Z_][a-zA-Z_0-9]*\('
t_RPAREN = r'\)'
t_PLUS = r'\+'

t_ignore = ' \t'


def t_error(t):
    raise ValueError(f'Illegal character {t.value[0]}')


lexer = lex.lex()


def tokenise(data: str):
    lexer.input(data)
    return list(lexer)


if __name__ == '__main__':
    from sys import argv
    if len(argv) > 1:
        tokens = tokenise(argv[1])
        print(tokens)
