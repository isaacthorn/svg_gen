import math

import complex
import parse
import geometry

import svgwrite


class Renderer:
    def __init__(self, root: geometry.Node):
        self.root = root

    def render(self):
        raise NotImplementedError()


class SVGRenderer(Renderer):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.svg = svgwrite.Drawing(filename)

        self.offset = (350.0, 50.0)

    def render(self):
        self.root.local_transform = geometry.Transformation(geometry.Position(*self.offset), -0.5 * math.pi)
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
    print(repr(layout))

    renderer = SVGRenderer('out.svg', root=layout)
    renderer.render()
