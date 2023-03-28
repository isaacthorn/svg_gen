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
    print(f'Illegal character {t.value[0]}')
    t.lexer.skip(1)


lexer = lex.lex()
