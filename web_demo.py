from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run')
def run():
    input_text = request.args.get('input', '')

    import lex
    tokens = lex.tokenise(input_text)

    import parse
    parsed = parse.parse(input_text)

    result = jsonify({
        'tokens': [{'type': token.type, 'value': token.value} for token in tokens],
        'ast': parsed,
        'svg': None,
    })

    return result


if __name__ == '__main__':
    app.run(host='192.168.0.16', port=80, debug=True)
