from itertools import pairwise
from typing import Optional

import complex
import math

import abc

DEFAULT_DOMAIN_LENGTH = 50
DEFAULT_BOUND_GAP = 5
DEFAULT_SPACING_GAP = 5


class Position:
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.val = (x, y)

    def __repr__(self):
        return f'({self.val[0]:.2f}, {self.val[1]:.2f})'

    @property
    def x(self):
        return self.val[0]

    @property
    def y(self):
        return self.val[1]

    def norm(self) -> float:
        """
        Get the length of the vector from (0, 0) to this position
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def angle(self) -> float:
        """
        Get the angle of the vector from (0, 0) to this position, where 0 rad is x-positive
        """
        return math.atan2(self.y, self.x)

    def translate(self, translation: 'Position') -> 'Position':
        """
        Apply the translation to this Position and return the new value
        """
        return Position(self.x + translation.x,
                        self.y + translation.y)

    def rotate(self, theta: float):
        """
        Rotate this position around the point (0, 0)
        """
        return Position(self.x * math.cos(theta) - self.y * math.sin(theta),
                        self.x * math.sin(theta) + self.y * math.cos(theta))

    def __neg__(self) -> 'Position':
        return Position(-self.x, -self.y)

    def __mul__(self, other: float):
        return Position(self.x * other, self.y * other)

    def __truediv__(self, other: float):
        return Position(self.x / other, self.y / other)


class Transformation:
    """
    A 2D transformation (translation and rotation only)

    rotation is in radians, clockwise
    """

    def __init__(self, translation: Position = Position(), rotation: float = 0.0):
        self.translation = translation
        self.rotation = rotation

    def __repr__(self):
        return f'{self.translation}, {self.rotation:.2f} rad'

    def inverse(self):
        return Transformation((-self.translation).rotate(-self.rotation), -self.rotation)

    def __add__(self, other: 'Transformation'):
        """
        Combine self and other as transformations

        Should be equivalent to first taking self as a transformation on a point, and then other.

        First rotate the other translation around its origin by OUR rotation, since our rotation is applied after our
        translation. Then add our (unrotated) translation to other's rotated translation, and add the 2 rotations.

        :param other: Second addend.
        """
        return Transformation(self.translation.translate(other.translation.rotate(self.rotation)),
                              self.rotation + other.rotation)

    def __mul__(self, other: float):
        return Transformation(self.translation * other, self.rotation)

    def __truediv__(self, other: float):
        return Transformation(self.translation / other, self.rotation)


class Node(metaclass=abc.ABCMeta):
    """
    Base class for all nodes within the geometry tree

    Within this class, an end transformation is stored, which represents the translation and rotation used to reach the
    end position from the start position.

    This transformation should consider positive-x as forwards. Positive-y is down, as in SVG.
    """

    def __init__(self, parent: Optional['Node'], source: Optional[complex.Node]):
        """
        Initialise the node with a parent and source

        :param parent: The parent node of this node. Can be None if this is the root of its tree
        :param source: The equivalent Node from complex.py, from which this Node was created
        """
        self.parent = parent
        self.source = source

        self.end_transform = None
        self.local_transform = Transformation()

        self.is_start = False
        self.is_end = False

    def get_parent_root(self) -> Transformation:
        return self.parent.get_root() if self.parent else Transformation()

    def get_root(self) -> Transformation:
        return self.get_parent_root() + self.local_transform

    @abc.abstractmethod
    def start_to_end(self) -> float:
        """
        Get the length from the start to the end of this node

        Used for laying things out on a circle. For example, a domain would return its length, which would then become
        the ARC length of the domain on its circle, whereas a hairpin would return the gap between start and end domains
        since this is also the length it will take up on a circle, if it were to be lain out onto one.
        """
        pass

    @abc.abstractmethod
    def set_as_start(self):
        """
        Assign or delegate to children to assign the strand start
        """

    @abc.abstractmethod
    def set_as_end(self):
        """
        Assign or delegate to children to assign the strand end
        """

    @abc.abstractmethod
    def needs_circle_fix(self) -> bool:
        """
        Check whether this type needs the 'circle fix'

        For Node types which lay themselves out on a circle properly (Domain and Gap), the chain doesn't have to rotate
        them, but types which can only lay themselves out in a straight line, the chain has to compensate for their
        angle in their local_transform. This applies only to Hairpins and SplitComplexes, since chains themselves are
        never placed directly as part of a circle
        """
        pass

    @abc.abstractmethod
    def layout(self, circle_radius: Optional[float], **kwargs):
        """
        Calculate internal layout (end position)

        :param circle_radius: If not None, this is the radius of the circle on which this Node is to be lain out
        """
        pass


def calculate_end_on_circle(radius: float, theta: float) -> Transformation:
    return Transformation(Position(radius * math.sin(theta), radius * (1 - math.cos(theta))), theta)


class Gap(Node):
    """
    Pseudo-node type used to represent a spacing component within the geometry

    For example, between 2 parts of a circular chain which are both not domain elements, a small gap should be placed
    """

    def __init__(self, parent: Optional[Node]):
        super().__init__(parent, None)

        self.circle_radius = None
        self.circle_theta = None

        self.length = DEFAULT_SPACING_GAP

    def __repr__(self):
        return f'Gap({"" if self.is_start else ">"}{self.length}{"" if self.is_end else ">"})'

    def start_to_end(self) -> float:
        return self.length

    def set_as_start(self):
        self.is_start = True

    def set_as_end(self):
        self.is_end = True

    def needs_circle_fix(self) -> bool:
        return False

    def layout(self, circle_radius: Optional[float], **kwargs):
        self.circle_radius = circle_radius
        if self.circle_radius:
            # Calculate end transform as if we're on a circle
            self.circle_theta = self.length / self.circle_radius
            self.end_transform = calculate_end_on_circle(self.circle_radius, self.circle_theta)
        else:
            # We're running in a straight line
            self.end_transform = Transformation(Position(0.0, -self.length), -0.5 * math.pi)


class Domain(Node):
    def __init__(self, parent: Optional[Node], source: complex.Domain):
        super().__init__(parent, source)

        self.circle_radius = None
        self.circle_theta = None

        # TODO: Configurable length
        self.length = DEFAULT_DOMAIN_LENGTH

    def __repr__(self):
        return f'Domain({"" if self.is_start else ">"}{self.source.name}{"" if self.is_end else ">"})'

    def start_to_end(self) -> float:
        return self.length

    def set_as_start(self):
        self.is_start = True

    def set_as_end(self):
        self.is_end = True

    def needs_circle_fix(self) -> bool:
        return False

    def layout(self, circle_radius: Optional[float], **kwargs):
        self.circle_radius = circle_radius
        if self.circle_radius:
            # Calculate end transform as if we're on a circle
            self.circle_theta = self.length / self.circle_radius
            self.end_transform = calculate_end_on_circle(self.circle_radius, self.circle_theta)
        else:
            # We're running in a straight line
            self.end_transform = Transformation(Position(0.0, -self.length), -0.5 * math.pi)


class Hairpin(Node):
    def __init__(self, parent: Optional[Node], source: complex.Hairpin):
        super().__init__(parent, source)

        # NB: The first parameter in these calls is the child's parent, not the self parameter to their __init__
        self.pre = Domain(self, source.pre)
        self.post = Domain(self, source.post)
        self.inner = Chain(self, source.inner)

        self.gap = DEFAULT_BOUND_GAP

    def __repr__(self):
        return f'Hairpin({self.pre.source.name}){repr(self.inner)}'

    def start_to_end(self) -> float:
        return self.gap

    def set_as_start(self):
        self.pre.set_as_start()

    def set_as_end(self):
        self.post.set_as_end()

    def needs_circle_fix(self) -> bool:
        return True

    def layout(self, circle_radius: Optional[float], **kwargs):
        self.pre.layout(None)
        self.pre.local_transform = Transformation(Position(), 0.0)

        self.post.layout(None)
        self.post.local_transform = Transformation(Position(self.gap, -self.post.length), math.pi)

        self.inner.layout(None, layout_circular=True)

        inner_angle_error = math.pi - self.inner.end_transform.translation.angle()
        self.inner.local_transform = Transformation(Position(0.0, -self.pre.length), math.pi + inner_angle_error)

        if circle_radius:
            # Inverse crd(theta) (\theta = 2 \cdot arcsin(\dfrac{c}{2r}))
            theta = 2.0 * math.asin(self.gap / (2.0 * circle_radius))
            self.end_transform = calculate_end_on_circle(circle_radius, theta)
        else:
            self.end_transform = Transformation(Position(self.gap, 0.0))


class SplitComplex(Node):
    def __init__(self, parent: Optional[Node], source: complex.SplitComplex):
        super().__init__(parent, source)

        self.pre = Domain(self, source.pre)
        self.post = Domain(self, source.post)
        self.left = Chain(self, source.left) if source.left else None
        self.right = Chain(self, source.right) if source.right else None

        self.gap = DEFAULT_BOUND_GAP

    def __repr__(self):
        return f'SplitComplex({self.pre.source.name})<{repr(self.left)},{repr(self.right)}>'

    def start_to_end(self) -> float:
        return self.gap

    def set_as_start(self):
        self.pre.set_as_start()

    def set_as_end(self):
        self.post.set_as_end()

    def needs_circle_fix(self) -> bool:
        return True

    def layout(self, circle_radius: Optional[float], **kwargs):
        self.pre.layout(None)
        self.pre.local_transform = Transformation(Position(), 0.0)

        self.post.layout(None)
        self.post.local_transform = Transformation(Position(self.gap, -self.post.length), math.pi)

        angle_from_forward = (0.25 * math.pi if self.left and self.right else 0.0)
        if self.left:
            self.left.layout(None, layout_circular=False)
            self.left.local_transform = Transformation(Position(0.0, -self.pre.length), -angle_from_forward)

            self.left.set_as_end()
        else:
            self.pre.set_as_end()

        if self.right:
            self.right.layout(None, layout_circular=False)
            # TODO: If the right hand chain is a [Domain], its final angle is off by -pi/2, possible the end_transform
            # of the Chain is wrong also
            self.right.local_transform = Transformation(Position(self.gap, -self.post.length), angle_from_forward) \
                + self.right.end_transform.inverse()

            self.right.set_as_start()
        else:
            self.post.set_as_start()

        if circle_radius:
            # Inverse crd(theta) (\theta = 2 \cdot arcsin(\dfrac{c}{2r}))
            theta = 2.0 * math.asin(self.gap / (2.0 * circle_radius))
            self.end_transform = calculate_end_on_circle(circle_radius, theta)
        else:
            self.end_transform = Transformation(Position(self.gap, 0.0))


class Chain(Node):
    def __init__(self, parent: Optional[Node], source: complex.Chain):
        super().__init__(parent, source)

        self.within = [create_geometry(self, node) for node in source.within]

    def __repr__(self):
        within_str = ', '.join(repr(node) for node in self.within)
        return f'[{within_str}]'

    def start_to_end(self) -> float:
        # Chains are never laid out as components of circles, so this works. Probably a better way to do it though
        return DEFAULT_BOUND_GAP

    def set_as_start(self):
        self.within[0].set_as_start()

    def set_as_end(self):
        self.within[-1].set_as_end()

    def needs_circle_fix(self) -> bool:
        return False

    def calculate_inner_radius(self, hidden_gap: float = DEFAULT_BOUND_GAP) -> float:
        """
        Work out how big the circle should be for the inner chain
        """

        """
        This is close enough iff the gap distance is substantially smaller than the domain lengths

        The problem here is mathematical, not practical.
        Domains report their arc length, whereas other node types cannot calculate their arc length, they know the
        straight-line distance between their start and end.

        An equation which represents the problem is \pi - \dfrac{l_c}{2r} = arcsin(\dfrac{l_s}{2r}) in TeX format.
        Solving this equation for r, where l_c is the arc length of all domains summed, and l_s is the straight-line
        length of the gap, will give you the radius. The problem is the presence of arcsin on one side, and no trig
        function on the other, making this equation not solvable numerically. Eventually I might implement some form
        of iterative solution (e.g. Newton-Raphson) to approximate the radius more precisely, but just summing all 
        distances equally will work well enough for now.
        """
        circumference = sum(node.start_to_end() for node in self.within) + hidden_gap
        return circumference / (2.0 * math.pi)

    def check_needs_gap(self, i: int, omit_end_gap: bool = False) -> bool:
        """
        Should we insert a Gap element between within[i] and within[i + 1]
        (The final element of within precedes a Domain, since it comes before self.post)
        A gap needs to be inserted between any pair of children which are BOTH NOT domains (e.g hairpin -> hairpin)
        """
        if i == -1:
            return not isinstance(self.within[0], Domain)
        if i + 1 == len(self.within):
            return not isinstance(self.within[i], Domain) and not omit_end_gap
        return not isinstance(self.within[i], Domain) and not isinstance(self.within[i + 1], Domain)

    def layout(self,
               circle_radius: Optional[float],
               layout_circular: bool = True,
               hidden_gap: float = DEFAULT_BOUND_GAP,
               omit_end_gap: bool = False,
               **kwargs):
        """
        :param layout_circular: Only valid for chains, determines whether the chain should be laid out in a circle or
        just end-to-end
        """

        # If we only have one child, and it isn't curvable, we don't NEED to layout on a circle (we can't)
        if len(self.within) == 1 and self.within[0].needs_circle_fix():
            layout_circular = False

        # If we're on a circle with len() > 1, insert gaps between pairs of non-domain children
        # Can't modify the list while iterating
        if layout_circular and len(self.within) > 1:
            new_within = []
            if self.check_needs_gap(-1):
                new_within.append(Gap(self))
            for i in range(len(self.within)):
                new_within.append(self.within[i])
                if self.check_needs_gap(i, omit_end_gap):
                    new_within.append(Gap(self))
            self.within = new_within

        # Calculate the radius of the circle
        inner_radius = None if not layout_circular else self.calculate_inner_radius(hidden_gap=hidden_gap)

        # The transform which will be given to the current node
        cur_transform = Transformation()

        for node in self.within:
            node.layout(inner_radius)

            angle_adjustment = node.end_transform.translation.angle() if node.needs_circle_fix() else 0.0
            node.local_transform = Transformation(cur_transform.translation, cur_transform.rotation + angle_adjustment)

            cur_transform = cur_transform + node.end_transform

        self.end_transform = cur_transform


def create_geometry(parent: Optional[Node], node: complex.Node) -> Node:
    """
    Create the geometry tree from node and return it. node can be any type from complex.
    Parent can be None if this is the root node of its tree.
    """
    if isinstance(node, complex.Domain):
        return Domain(parent, node)
    elif isinstance(node, complex.Hairpin):
        return Hairpin(parent, node)
    elif isinstance(node, complex.Chain):
        return Chain(parent, node)
    elif isinstance(node, complex.SplitComplex):
        return SplitComplex(parent, node)
    else:
        raise NotImplementedError(f'Unsupported geometry operation {type(node).__qualname__}')


def layout_geometry(root: complex.Node) -> Node:
    layout = create_geometry(None, root)
    layout.layout(None, omit_end_gap=True, hidden_gap=2 * DEFAULT_BOUND_GAP)
    layout.set_as_start()
    layout.set_as_end()
    return layout


if __name__ == '__main__':
    from sys import argv

    if len(argv) > 1:
        string = argv[1]
    else:
        string = input('>>> ')

    from parse import parse

    parsed = parse(string)
    geometry = create_geometry(None, parsed)
    print(repr(geometry))

    geometry.layout(None)
    print(repr(geometry))
