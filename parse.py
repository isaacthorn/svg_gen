import complex
from types import NoneType
from typing import Tuple
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    DOMAIN_UNBOUND = 0
    DOMAIN_OPEN = 1
    DOMAIN_CLOSE = 2
    NEW_STRAND = 3


class Token:
    def __init__(self, type: TokenType, **kwargs):
        self.type = type
        self.__dict__.update(kwargs)


def parse_token(token: str) -> Token:
    if token == ')':
        return Token(TokenType.DOMAIN_CLOSE)
    elif token == '+':
        return Token(TokenType.NEW_STRAND)
    elif token[-1] == '(':
        return Token(TokenType.DOMAIN_OPEN, name=token[0: -1])
    else:
        return Token(TokenType.DOMAIN_UNBOUND, name=token)


def parse(notation: str) -> complex.Complex:
    
    bonding_stack: list[complex.Domain] = []

    result = complex.Complex([])

    cur_strand_i = 0
    cur_strand = complex.Strand(f's{cur_strand_i}')

    for token_str in notation.split(' '):
        token = parse_token(token_str)
        match token.type:
            case TokenType.DOMAIN_OPEN:
                new_domain = cur_strand.add_domain(name=token.name)
                bonding_stack.append(new_domain)
            case TokenType.DOMAIN_CLOSE:
                bonded = bonding_stack.pop()
                new_domain = cur_strand.add_domain(name=bonded.name + '*', bond=bonded)
                bonded.bond = new_domain
            case TokenType.DOMAIN_UNBOUND:
                cur_strand.add_domain(name=token.name)
            case TokenType.NEW_STRAND:
                result.strands.append(cur_strand)
                cur_strand_i += 1
                cur_strand = complex.Strand(f's{cur_strand_i}')
            case _:
                raise NotImplementedError()
    result.strands.append(cur_strand)
    
    return result


if __name__ == '__main__':
    structure = parse('a b( c ) d( e f( g h( + ) ) i j( k l( + ) m ) n o( p + q( + ) ) r )')
    for strand in structure.strands:
        print(str(strand))
