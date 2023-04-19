from dataclasses import dataclass


class Node:
    pass


@dataclass
class Domain(Node):
    name: str

    def __str__(self):
        return self.name


@dataclass
class Hairpin(Node):
    pre: Domain
    inner: 'Chain'
    post: Domain

    def __str__(self):
        return f'{str(self.pre)}( {str(self.inner)} )'


@dataclass
class SplitComplex(Node):
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
class Chain(Node):
    within: list[Domain | Hairpin | SplitComplex]

    def __str__(self):
        return ' '.join(str(el) for el in self.within)


def create_complementary(domain: Domain) -> Domain:
    return Domain(domain.name + '*')
