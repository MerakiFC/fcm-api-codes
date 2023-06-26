from flask import Flask, request

app = Flask(__name__)

@app.route('/whtest', methods=['POST'])
def handle_webhook():
    payload = request.get_json()  # Get the JSON payload from the request
    # Process the payload and perform necessary actions
    print(payload)
    return 'OK ', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)