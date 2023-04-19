import complex
import parse
import geometry

import svgwrite


class Renderer:
    def __init__(self, root: geometry.GeometryNode):
        self.root = root

    def render(self):
        raise NotImplementedError()


class SVGRenderer(Renderer):
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.svg = svgwrite.Drawing(filename)

    def render(self):
        self.visit_node(self.root, geometry.Transformation(geometry.Position(100.0, 100.0)))
        self.svg.save()

    def visit_node(self, node: geometry.GeometryNode, transformation: geometry.Transformation):
        if isinstance(node, geometry.Chain):
            for child in node.within:
                self.visit_node(child, transformation + child.parent_to_local)
        elif isinstance(node, geometry.Hairpin):
            self.visit_node(node.pre, transformation + node.pre.parent_to_local)
            self.visit_node(node.post, transformation + node.post.parent_to_local)
            self.visit_node(node.inner, transformation + node.inner.parent_to_local)
        elif isinstance(node, geometry.Domain):
            start = node.start.transform(transformation)
            end = node.end.transform(transformation)
            new_path = self.svg.line((start.x, start.y), (end.x, end.y), stroke='red')
            self.svg.add(new_path)
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

    layout = geometry.layout(ast)
    print(repr(layout))

    renderer = SVGRenderer('out.svg', root=layout)
    renderer.render()
