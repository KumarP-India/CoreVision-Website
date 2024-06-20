'''
# @author: OpenAI ChatGPT 4o
$ @Assistant: Prabhas Kumar

# @Created: June 20'24
# @Updated: None

# @Project: CoreVision Website Version 1
# @File: app [python script]
'''

from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'CoreVision-Website-Form-data.json'

def save_data(data):
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)
    with open(DATA_FILE, 'r+') as f:
        current_data = json.load(f)
        current_data.append(data)
        f.seek(0)
        json.dump(current_data, f)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.get_json()
    save_data(data)
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
