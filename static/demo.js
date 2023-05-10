function OnLoad()
{
    SubmitNewInput();
}

function UpdateTokens(tokens)
{
    let tokens_area = document.getElementById('tokens-area');
    tokens_area.innerText = JSON.stringify(tokens, null, 2);
}

function UpdateAST(ast)
{
    let ast_area = document.getElementById('ast-area');
    ast_area.innerText = JSON.stringify(ast, null, 2);
}

function UpdateSVG(svg)
{
    let svg_area = document.getElementById('svg-container')
    let existing_svgs = document.getElementsByClassName('result-image')
    for(let i = 0; i < existing_svgs.length; i++)
    {
        svg_area.removeChild(existing_svgs[i]);
    }
    let svg_element = document.createElement('svg');
    svg_element.innerHTML = svg
    svg_element.className = 'result-image'
    svg_area.appendChild(svg_element)
}

let current_text = null;
function SubmitNewInput()
{
    let input_text = document.getElementById('run-input').value;
    if(input_text && input_text === current_text)
        return;

    let fetch_url = '/run?' + new URLSearchParams({
        input: input_text,
    });
    fetch(fetch_url)
        .then((response) => response.json())
        .then((result) => {
            UpdateTokens(result.tokens);
            UpdateAST(result.ast);
            UpdateSVG(result.svg);
            current_text = input_text;
        })
        .catch((error) => {
            console.log(error);
        });
}
