from flask import Flask, request

app = Flask(__name__)

@app.route('/whtest', methods=['POST'])
    def handle_webhook():
        payload = request.get_json()  # Get the JSON payload from the request
        # Process the payload and perform necessary actions
        print(payload)
        return 'Webhook Received', 200

if __name__ == '__main__':
    app.run(debug=True)