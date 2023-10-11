# app.py
from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def instance_id():
    try:
        # AWS provides the instance metadata at this URL
        response = requests.get('http://169.254.169.254/latest/meta-data/instance-id', timeout=1)
        return response.text
    except requests.RequestException:
        return "Not running on an EC2 instance"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
