from flask import Flask, request
import sys


app = Flask(__name__)

@app.route('/whtest', methods=['POST'])
def test_only():
    from apiConn import envTest
    whPayload = request.get_json()  # Get the JSON payload from the request

    print ("Testing Connection...")
    envTest()
    return (whPayload), 200


@app.route('/mvmotionalert', methods=['POST'])
def mv_task():
    
    import mvtask
    from wxtask import sendToWX
    from dtConvert import epochToAest
    
    whPayload = request.get_json()  # Get the JSON payload from the request
    strTimeISO = str(epochToAest(whPayload["alertData"]["timestamp"]))
    print("Webhook received: ",strTimeISO,"\nStart process.")


    ##Process the payload and perform necessary actions

    try:
        urlSnap = mvtask.getSnap(whPayload)
    except Exception as err:
        print("Snapshot processing error:\n", str(err))
        sys.exit(400)
    print (urlSnap)

    sendToWX(whPayload)
    return "OK", 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)