import os
import quart
import quart_cors
from quart import request
from bs4 import BeautifulSoup, Comment
import sys
from io import StringIO

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")
_SERVICE_AUTH_KEY = os.environ.get("_SERVICE_AUTH_KEY")

def assert_auth_header(req):
    assert req.headers.get("Authorization", None) == f"Bearer {_SERVICE_AUTH_KEY}"

def execute_code(code_string):

    # Redirect stdout to a string buffer
    original_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        # Execute the code string
        exec(code_string)
        # Get the output from the string buffer
        result = sys.stdout.getvalue()
    except Exception as e:
        result = str(e)
    finally:
        # Restore the original stdout
        sys.stdout = original_stdout

    return result

# Example usage
code_string = '''
import math
print(math.sqrt(16))
'''
result = execute_code(code_string)
print("Result:", result)
  
@app.route('/getCodeExecutionResults', methods=['POST'])
async def getCodeExecutionResults():
    assert_auth_header(request)

    input_data = await request.get_json()

    if not input_data or not input_data.get('code'):
        return quart.Response(response='Missing input data', status=400)

    print(input_data)
    code_string = input_data['code']
    print(code_string)
    result = execute_code(code_string)
    print("Result:", result)

    
    return quart.Response(response=result, status=200)



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