import math

import parse
import geometry

import svgwrite


DEFAULT_ARROWHEAD_BODY_LEN = 5
DEFAULT_ARROWHEAD_HEAD_LEN = 4


class Renderer:
    def __init__(self,
                 root: geometry.Node,
                 root_transform: geometry.Transformation = geometry.Transformation()):
        self.root = root
        self.root.local_transform = root_transform

    def render(self):
        raise NotImplementedError()


class GeometryRenderer(Renderer):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(root_transform=geometry.Transformation(geometry.Position(350.0, 350.0)), *args, **kwargs)

        self.svg = svgwrite.Drawing(filename)

    def render(self):
        self.visit_node(self.root)
        self.svg.save()

    def visit_node(self, node: geometry.Node, colour: str = 'red'):
        if not node:
            return
        if isinstance(node, geometry.Chain):
            for child in node.within:
                self.visit_node(child, colour)
        elif isinstance(node, geometry.SplitComplex):
            self.visit_node(node.pre, colour='orange')
            self.visit_node(node.post, colour='red')
            self.visit_node(node.left, colour='purple')
            self.visit_node(node.right, colour='green')
        elif isinstance(node, geometry.Hairpin):
            self.visit_node(node.pre)
            self.visit_node(node.post)
            self.visit_node(node.inner)
        elif isinstance(node, geometry.Domain):
            start = node.get_root()
            end = start + node.end_transform

            if not node.circle_radius:
                # Straight domain
                domain_line = self.svg.line((start.translation.x, start.translation.y),
                                            (end.translation.x, end.translation.y),
                                            stroke=colour)
                self.svg.add(domain_line)
            else:
                # Curved domain
                domain_line = self.svg.path(f'M{start.translation.x},{start.translation.y}', fill='none', stroke=colour)
                domain_line.push_arc(target=(end.translation.x, end.translation.y),
                                     rotation=0.0,
                                     r=node.circle_radius,
                                     large_arc=(node.circle_theta > math.pi),
                                     absolute=True)
                self.svg.add(domain_line)

            angle_line_end = end.translation.translate(geometry.Position(4.0, 0.0)
                                                       .rotate(end.rotation - (math.pi * 0.75)))
            angle_line = self.svg.line((end.translation.x, end.translation.y),
                                       (angle_line_end.x, angle_line_end.y),
                                       stroke='black')
            self.svg.add(angle_line)
        elif isinstance(node, geometry.Gap):
            start = node.get_root()
            end = start + node.end_transform

            if not node.circle_radius:
                # Straight gap
                domain_line = self.svg.line((start.translation.x, start.translation.y),
                                            (end.translation.x, end.translation.y),
                                            stroke=colour)
                self.svg.add(domain_line)
            else:
                # Curved gap
                domain_line = self.svg.path(f'M{start.translation.x},{start.translation.y}', fill='none', stroke=colour)
                domain_line.push_arc(target=(end.translation.x, end.translation.y),
                                     rotation=0.0,
                                     r=node.circle_radius,
                                     large_arc=(node.circle_theta > math.pi),
                                     absolute=True)
                self.svg.add(domain_line)
        else:
            raise NotImplementedError()


class SVGRenderer(Renderer):
    class Strand:
        def __init__(self, svg: svgwrite.Drawing, start_pos: tuple[float, float], colour: tuple[int, int, int]):
            self.colour = colour
            self.position = start_pos

            self.path = svg.path(f'M{self.position[0]},{self.position[1]}',
                                 fill='none',
                                 stroke=self.get_colour(),
                                 stroke_linecap='round')

        def get_colour(self) -> str:
            return f'rgb({self.colour[0]}, {self.colour[1]}, {self.colour[2]})'

        def add_straight_line(self, end_pos: tuple[float, float]):
            self.path.push(f'L {end_pos[0]} {end_pos[1]}')

        def add_curved_line(self, end_pos: tuple[float, float], radius: float, theta: float):
            self.path.push_arc(target=end_pos,
                               rotation=0.0,
                               r=radius,
                               large_arc=(theta > math.pi),
                               absolute=True)

    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.svg = svgwrite.Drawing(filename)

        self.cur_strand = None
        self.colour_stack = [(220,  35,  32),
                             ( 68, 114, 189),
                             ( 77, 173,  63),
                             (149,  52, 168),
                             (246, 111,  21)]
        self.colour_stack.reverse()

    def render(self):
        self.root.local_transform = geometry.Transformation(geometry.Position(250.0, 250.0), -0.5 * math.pi)
        self.visit_node(self.root)
        self.svg.save()

    def draw_bond_lines(self, left: geometry.Node, right: geometry.Node):
        lines_count = 8

        left_step = left.end_transform / lines_count
        right_step = right.end_transform / lines_count

        lines_path = self.svg.path(fill='none', stroke='rgb(200, 200, 200)')
        for i in range(lines_count + 1):
            left_pos = left.get_root() + (left_step * i)
            right_pos = right.get_root() + (right_step * (lines_count - i))
            lines_path.push(f'M{left_pos.translation.x},{left_pos.translation.y}')
            lines_path.push(f'L{right_pos.translation.x},{right_pos.translation.y}')

        self.svg.add(lines_path)

    def visit_node(self, node: geometry.Node):
        if not node:
            return
        if isinstance(node, geometry.Chain):
            for child in node.within:
                self.visit_node(child)
        elif isinstance(node, geometry.SplitComplex):
            self.draw_bond_lines(node.pre, node.post)
            self.visit_node(node.pre)
            self.visit_node(node.left)
            self.visit_node(node.right)
            self.visit_node(node.post)
        elif isinstance(node, geometry.Hairpin):
            self.draw_bond_lines(node.pre, node.post)
            self.visit_node(node.pre)
            self.visit_node(node.inner)
            self.visit_node(node.post)
        elif isinstance(node, (geometry.Domain, geometry.Gap)):
            start = node.get_root()
            end = start + node.end_transform

            if node.is_start:
                self.cur_strand = SVGRenderer.Strand(self.svg,
                                                     (start.translation.x, start.translation.y),
                                                     self.colour_stack.pop())

            if not self.cur_strand:
                raise ValueError(f'Domain tried to render without a strand! ({repr(node)})')

            if not node.circle_radius:
                self.cur_strand.add_straight_line((end.translation.x, end.translation.y))
            else:
                self.cur_strand.add_curved_line((end.translation.x, end.translation.y),
                                                node.circle_radius,
                                                node.circle_theta)
            if node.is_end:
                # Add 3' end arrowhead
                arrow_body = geometry.Transformation(geometry.Position(DEFAULT_ARROWHEAD_BODY_LEN, 0.0),
                                                     -0.75 * math.pi)
                arrow_head = geometry.Transformation(geometry.Position(DEFAULT_ARROWHEAD_HEAD_LEN, 0.0))

                arrow_body_end = end + arrow_body
                arrow_head_end = arrow_body_end + arrow_head

                self.cur_strand.add_straight_line((arrow_body_end.translation.x, arrow_body_end.translation.y))
                self.cur_strand.add_straight_line((arrow_head_end.translation.x, arrow_head_end.translation.y))

                self.svg.add(self.cur_strand.path)
                self.cur_strand = None
        else:
            raise NotImplementedError()


if __name__ == '__main__':
    from sys import argv

    if len(argv) > 1:
        string = argv[1]
    else:
        string = input('>>> ')
    ast = parse.parse(string)
    print(repr(ast))

    layout = geometry.create_geometry(None, ast)

    print(repr(layout))
    layout.layout(None)
    layout.set_as_start()
    layout.set_as_end()
    print(repr(layout))

    renderer = SVGRenderer('out.svg', root=layout)
    renderer.render()
