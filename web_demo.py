from flask import Flask, jsonify, render_template, request
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run')
def run():
    def create_result(message, tokenised, ast, image):
        return jsonify({
            'message': message,
            'tokens': [{'type': token.type, 'value': token.value} for token in tokens] if tokenised else None,
            'ast': ast,
            'svg': image
        })

    input_text = request.args.get('input', '')

    import lex
    try:
        tokens = lex.tokenise(input_text)
    except ValueError:
        return create_result('Error while tokenising input', None, None, None)

    import parse
    try:
        parsed = parse.parse(input_text)
    except ValueError:
        return create_result('Error while parsing input', tokens, None, None)

    import geometry
    import renderer

    svg = StringIO()

    geom = geometry.layout_geometry(parsed)
    renderer.SVGRenderer(svg, geom).render()

    print(svg.getvalue())
    return create_result('Successfully created diagram', tokens, parsed, svg.getvalue())


if __name__ == '__main__':
    app.run(host='localhost', port=80, debug=True)
