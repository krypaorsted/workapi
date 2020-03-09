import amq
import json
import sys
import time
import os
import uuid
import getopt
from pathlib import Path

def jsonLoad(file):
    with open(file) as f:
        data = json.load(f)
    return data

def jsonDumps(file):
    data = jsonLoad(file)
    return json.dumps(data)

def printHelp():
    """ Outputs list of possile options """
    print("amqWorkApiMass.py -n <msgcnt> -b <body> -m <headers> -s <path/to/bodyandheaders>")


def main(argv):
    #Load connection file
    connCfg = jsonLoad('config/conn.json') 
    #Get body and header
    body = {}
    headerCfg = {}
    path = ''
    cnt = 1
    error = False
    try:
        opts, args = getopt.getopt(argv,"hn:b:m:s:",["cnt=", "body=","headerCfg=", "path="])
    except getopt.GetoptError:
        printHelp()
        return
    for opt, arg in  opts:
        if opt == "-h":
            printHelp()
            return
        elif opt in ("-b", "--body"):
            body = jsonDumps(Path(arg))
        elif opt in ("-m", "--headerCfg"):
            headerCfg = jsonLoad(Path(arg))
        elif opt in ("-s", "--path"):
            path = Path(arg)
        elif opt in ("-n", "--cnt"):
            try:
                cnt = int(arg)
            except:
                print("Message counter must be numerical")
                error = True
    if error == True:
        return
    if not path and (not body or not headerCfg):
        print("Incorrect input") 
        return
    elif path and (body or headerCfg):
        print("Both path and files location given. Path will be used")
    if path:
        body = jsonDumps(path / 'body.json')
        headerCfg = jsonLoad(path / 'header.json')
    #body = jsonDumps('config/body.json')
    #headerCfg = jsonLoad('config/header.json')

    try:
        conn = amq.amqConn(connCfg)
        conn.open()
    except Exception as e:
        print(e)
        return
    while cnt > 0:
        try:
            cnt = cnt - 1
           
            header = headerCfg
            header['JMSCorrelationID'] = str(uuid.uuid4())  #generate random uuid
            print("Send request with correlation id:"+str(header['JMSCorrelationID']))
            conn.sendRequest(header, body)
        except Exception as e:
            print(e)
            

    conn.close()



if __name__ == "__main__":
    main(sys.argv[1:])
