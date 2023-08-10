import mvtask
#from apiEnv import getEnvKey
from wxtask import mvAlertToWX, eventToWx


##Handler for 3 main events: mvMotionAlert, sensorAutomation, webhookEvent

def eventhandler(dictWhPayload):
    print("MV Motion Alert\n---------------")
    ##idea: add payload modifiers here?

    if dictWhPayload['alertTypeId'] == 'motion_alert':
        ##define mvMotionAlert process

        try:
            dictResp = mvtask.getSnap(dictWhPayload, isRecap="y")
        except Exception as err:
            print("Snapshot processing error:\n", str(err))
            return (err), 404
        
        dictResp = mvAlertToWX(dictWhPayload, isRecap="y")
        return (dictResp)
        
 
    #elif dictWhPayload['alertTypeId'] == 'sensor_automation':
    #    print("Sensor Automation\n---------------")
    #    pass ##define sensorAutomation process

    ## Default webhook payload handler for all other events
    else:
        print("Webhook Handler\n---------------")
        dictResp = eventToWx(dictWhPayload)
        return (dictResp)