from dataclasses import dataclass
from types import NoneType
from typing import Sequence



@dataclass
class Domain:
    name: str

    def __str__(self):
        return self.name


@dataclass
class Hairpin:
    pre: Domain
    inner: 'Chain'
    post: Domain

    def __str__(self):
        return f'{str(self.pre)}( {str(self.inner)} )'


@dataclass
class SplitComplex:
    pre: Domain
    left: 'Chain | NoneType'
    right: 'Chain | NoneType'
    post: Domain

    def __str__(self):
        if self.left and self.right:
            return f'{str(self.pre)}( {str(self.left)} + {str(self.right)} )'
        elif self.left:
            return f'{str(self.pre)}( {str(self.left)} + )'
        elif self.right:
            return f'{str(self.pre)}( + {str(self.right)} )'
        else:
            return f'{str(self.pre)}( + )'


@dataclass
class Clover:
    within: list[Hairpin | SplitComplex]

    def __str__(self):
        return ' '.join(str(el) for el in self.within)


@dataclass
class Chain:
    within: list[Clover | Domain]

    def __str__(self):
        return ' '.join(str(el) for el in self.within)


def create_complementary(domain: Domain) -> Domain:
    return Domain(domain.name + '*')
