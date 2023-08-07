from flask import Flask, request
import sys
sys.path.append('modules')


app = Flask(__name__)

##Setting environment parameters
from apiEnv import envTest
envTest()


@app.route("/")
def hello():
    return "Hello, webhook user."


@app.route('/whtest', methods=['POST'])
def test_only():
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    return (dictWhPayload), 200


@app.route('/mvmotionalert', methods=['POST'])
def mvmotionalert():
    
    import mvtask
    from wxtask import mvAlertToWX
    from dtConvert import epochToAest
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    strTimestampAEST = str(epochToAest(dictWhPayload["alertData"]["timestamp"]))
    print("##########\nWebhook timestamp: ",strTimestampAEST,"\nStarting process...\n##########")


    ##Process the payload and perform necessary actions

    try:
        mvtask.getSnap(dictWhPayload, isRecap="y")
    except Exception as err:
        print("Snapshot processing error:\n", str(err))
        sys.exit(500)
    
    ## Assign response string to dictResp and use as response (json) body to webhook request
    dictResp = mvAlertToWX(dictWhPayload, isRecap="y")
    return (dictResp), 200

@app.route('/alerttowx', methods=['POST'])  ###development process 26/07/23
def alertToWx():

    #from wxtask import eventToWx
    from dtConvert import epochToAest
    from wxtask import eventToWX
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    strTimestampAEST = str(epochToAest(dictWhPayload["alertData"]["timestamp"]))
    print("##########\nStarting webhook event handler\nEvent timestamp: ",strTimestampAEST,"\n##########")


    ## Send payload to eventToWx script and   
    ## return response body to webhook sender
    dictResp = eventToWX(dictWhPayload)
    return (dictResp), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)