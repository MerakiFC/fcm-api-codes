from flask import Flask, request
import sys
sys.path.append('modules')


app = Flask(__name__)

global tzOffset
##Setting environment parameters
from apiEnv import envTest, getEnvKey

envTest()
tzOffset = int(getEnvKey("TZ_OFFSET"))

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
    from dtConvert import utc_iso_to_tz_offset
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    strTimestampAEST = utc_iso_to_tz_offset(dictWhPayload["sentAt"], tzOffset)
    print("---------------\nStarting mvAlert. Webhook sent: ",strTimestampAEST,"\n---------------")


    ##Process the payload and perform necessary actions

    try:
        mvtask.getSnap(dictWhPayload, isRecap="y")
    except Exception as err:
        print("Snapshot processing error:\n", str(err))
        sys.exit(500)
    
    ## Assign response string to dictResp and use as response (json) body to webhook request
    dictResp = mvAlertToWX(dictWhPayload, isRecap="y")
    return (dictResp), 200

@app.route('/alerttowx', methods=['POST']) 
def alertToWx():

    #from wxtask import eventToWx
    from dtConvert import utc_iso_to_tz_offset
    from wxtask import eventToWx
    from wh_handler import eventhandler
    
    dictWhPayload = request.get_json()  # Get the JSON payload from the request
    strTimestampAEST = utc_iso_to_tz_offset(dictWhPayload["sentAt"], tzOffset)
    print("---------------\nEvent received. Webhook sent: ",strTimestampAEST,"\n---------------")

    dictResp = eventhandler(dictWhPayload)


    ## Send payload to eventToWx script and   
    ## return response body to webhook sender
    
    #dictResp = eventToWx(dictWhPayload)
    return (dictResp), 200
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8116, debug=True)