import amq    #custom classes for work api active MQ handling
import json
import sys
import time
import os
import uuid
import getopt

def jsonLoad(file):
    with open(file) as f:
        data = json.load(f)
    return data

def jsonDumps(file):
    data = jsonLoad(file)
    return json.dumps(data)

def printHelp():
    """ Outputs list of possile options """
    print("amqListener.py -t <timeout>")

def main(argv):

    sleep = 30
    error = False
    try:
        opts, args = getopt.getopt(argv,"ht:",["sleep="])
    except getopt.GetoptError:
        printHelp()
        return
    for opt, arg in  opts:
        if opt == "-h":
            printHelp()
            return
        elif opt in ("-t", "--sleep"):
            try:
                sleep = int(arg)
            except:
                print("timeout must be integer")
                error = True

    if error:
        return

    connCfg = jsonLoad('config/conn.json')
    
    try:
        conn = amq.amqConn(connCfg)
        conn.open()
        conn.subscribe("WP.OM.WorkOrderUpdate.saptest.Response")
        conn.subscribe("WP.OM.Notification.saptest.Response")
        conn.subscribe("WP.OM.AssetService.saptest.Response")
        print("Connection open")
    except Exception as e:
        print(e)
        return

    print('Waiting for responses ...')
    """timeout = time.time() + sleep
    while time.time() < timeout :
        time.sleep(1)"""
    time.sleep(sleep)

    conn.close()
    print("Connection closed")



if __name__ == "__main__":
    main(sys.argv[1:])
