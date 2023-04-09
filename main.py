import os
import quart
import quart_cors
from quart import request
from bs4 import BeautifulSoup, Comment

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")
_SERVICE_AUTH_KEY = os.environ.get("_SERVICE_AUTH_KEY")

def assert_auth_header(req):
    assert req.headers.get("Authorization", None) == f"Bearer {_SERVICE_AUTH_KEY}"


@app.route('/executeCode', methods=['POST'])
async def executeCode():
    assert_auth_header(request)

    input_data = await request.get_json()

    if not input_data or not input_data.get('code'):
        return quart.Response(response='Missing input data', status=400)

    
    code_string = input_data('code')
    print(code_string)
    try:
        # Use eval to execute the string as an expression
        result = eval(code_string)
    except SyntaxError:
        try:
            # Use exec to execute the string as a statement
            exec(code_string)
            result = None
        except Exception as e:
            result = f"Error: {str(e)}"
    return result



@app.get("/logo.png")
async def plugin_logo():
    filename = 'logo.png'
    return await quart.send_file(filename, mimetype='image/png')

@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers['Host']
    with open("ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")

@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers['Host']
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")

def main():
    app.run(debug=True, host="0.0.0.0", port=5002)

if __name__ == "__main__":
   main()