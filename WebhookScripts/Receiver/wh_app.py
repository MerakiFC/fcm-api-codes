from flask import Flask, request
import sys
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
    from wxtask import sendToWX
    from dtConvert import epochToAest
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    strTimestampAEST = str(epochToAest(dictWhPayload["alertData"]["timestamp"]))
    print("---\n---\nWebhook timestamp: ",strTimestampAEST,"\nStarting process...\n---\n---")


    ##Process the payload and perform necessary actions

    try:
        mvtask.getSnap(dictWhPayload, isRecap="y")
    except Exception as err:
        print("Snapshot processing error:\n", str(err))
        sys.exit(500)
    

    sendToWX(dictWhPayload, isRecap="y")
    return "OK", 200



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)