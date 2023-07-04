from flask import Flask, request
import mvtask

app = Flask(__name__)

@app.route('/whtest', methods=['POST'])
def test_only():
    payload = request.get_json()  # Get the JSON payload from the request
    # Process the payload and perform necessary actions
    print(payload)
    return "200OK \n", 200


@app.route('/mvmotionalert', methods=['POST'])
def mv_task():
    objPayload = request.get_json()  # Get the JSON payload from the request
    # Process the payload and perform necessary actions
    #print(objPayload)
    urlSnap = mvtask.getsnapshot(objPayload)
    print (urlSnap.text)
    return "200OK \n", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)