from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain_groq import ChatGroq
import sys
from io import StringIO
import os
csv_path = os.path.join('tech_dojo_backend-1', 'backend', 'cyberbullying_tweets.csv')

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    message = data['message']
    
    llm = ChatGroq(model = "llama-3.1-8b-instant",api_key="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")
    messages = [
        (
            "system",
            "The users message is supposed to send prompts. Respond with approved or not approved and why(very short) based on how good the users prompt is. Be lenient.",
        ),
        ("human", message),
        ]
    ai_msg = llm.invoke(messages)
    
    return jsonify({'response': ai_msg.content})


@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    message = data['message']
    
    llm = ChatGroq(model = "llama-3.1-8b-instant",api_key="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")
    messages = [("system","The users message will send you a python code for a very basic task. Respond with approved or not approved and why(very short) based on how good the users prompt is. Be very lenient, only disapprove if there are obvious errors in order of execution.",),
        ("human", message),]
    ai_msg = llm.invoke(messages)
    
    return jsonify({'response': ai_msg.content})

def execute_python_code(code):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import io
    import base64
    
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    csv_path = os.path.join('tech-dojo', 'backend', 'cyberbullying_tweets.csv')
    try:
        # Execute the code
        local_vars = {'csv_path': csv_path}
        
        # Execute the code with the local namespace
        exec(code, globals(), local_vars)
        
        # If there's an active plot, save it to base64
        if plt.get_fignums():
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close('all')  # Close all figures
            
            # Get any print output
            output = sys.stdout.getvalue()
            
            # Return both the plot and any print output
            return {'output': output, 'plot': plot_data}
        else:
            # Return just the print output if no plot
            return {'output': sys.stdout.getvalue()}
            
    except Exception as e:
        return {'output': str(e)}
    finally:
        sys.stdout = old_stdout





@app.route('/run_code', methods=['POST', 'OPTIONS'])
def run_code():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    code = request.json.get('code')
    if not code:
        return jsonify({"error": "No code provided"}), 400
    output = execute_python_code(code)
    return jsonify({"output": output})

@app.route('/api/moderate', methods=['POST'])
def moderate():
    data = request.json
    message = data['message']
    
    llm = ChatGroq(model = "llama-3.1-8b-instant",api_key="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")
    messages = [("system","The users message will be a message that will be posted on a forum. Respond in only one word either true or false, do not say anything else no matter what. If the message doesn't constitute cyber bullying respond with true if it does respond with false",),
        ("human", message),]
    ai_msg = llm.invoke(messages)
    
    return jsonify({'response': ai_msg.content.lower()})

@app.route('/')
def home():
    return 'Welcome to the Tech Dojo Backend API!'

if __name__ == '__main__':
    app.run(port=5000)