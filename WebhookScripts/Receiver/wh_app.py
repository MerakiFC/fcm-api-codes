from flask import Flask, request, Response
import sys,json
sys.path.append('modules')


app = Flask(__name__)

@app.route('/whtest', methods=['POST'])
def test_only():
    from apiEnv import envTest
    dictWhPayload = request.get_json()  # Get the JSON payload from the request

    print ("Testing Connection...")
    envTest()
    return (dictWhPayload), 200


@app.route('/mvmotionalert', methods=['POST'])
def mv_task():
    
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

@app.route('/plhandler', methods=['POST'])  ###development process 26/07/23
def plhandler():

    #from wxtask import sendToWX
    from dtConvert import epochToAest
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    strTimestampAEST = str(epochToAest(dictWhPayload["alertData"]["timestamp"]))
    print("##########\nStarting plhandler process\n##########")


    ##Process the payload and perform necessary actions
    pass
    
    ## Assign response string to strResp and use as the final response string to webhook request

    return (dictWhPayload), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)