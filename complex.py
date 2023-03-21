from dataclasses import dataclass
from types import NoneType
from typing import Sequence


class Domain:
    def __init__(self, name: str, bond: 'Domain' = None):
        self.name = name
        self.bond = bond

    def __repr__(self):
        if self.bond:
            return f'<Domain name={self.name}, bond={self.bond.name}>'
        return f'<Domain name={self.name}>'


class Strand:
    def __init__(self, name: str):
        self.name = name
        self.domains: list[Domain] = []
    
    def __str__(self):
        domain_str = ' '.join(repr(domain) for domain in self.domains)
        return f'Strand({self.name}) {{{domain_str}}}'

    def add_domain(self, **kwargs) -> Domain:
        self.domains.append(Domain(**kwargs))
        return self.domains[-1]


@dataclass
class Complex:
    strands: list[Strand]
