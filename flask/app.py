from flask import Flask, jsonify
import requests

app = Flask(__name__)


@app.route('/')
def get_instance_id():
    # Get instance metadata
    response = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
    instance_id = response.text
    return jsonify(instance_id=instance_id)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
