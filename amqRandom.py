import amq    #custom classes for work api active MQ handling
import json
import sys
import time
import os
import uuid
import random
import getopt
from pathlib import Path
import time

def jsonLoad(file):
    with open(file) as f:
        data = json.load(f)
    return data

def jsonDumps(file):
    data = jsonLoad(file)
    return json.dumps(data)

def printHelp():
    """ Outputs list of possile options """
    print("amqRandom.py -n <msgcnt> -c <path/to/config>")


def main(argv):
    """ Main function 
        Read args, create connection, select random messages, send requests, close connection
    """
    path = ''
    cnt = 1
    error = False
    try:
        opts, args = getopt.getopt(argv,"hn:c:",["cnt=", "path="])
    except getopt.GetoptError:
        printHelp()
        return
    for opt, arg in  opts:
        if opt == "-h":
            printHelp()
            return
        elif opt in ("-c", "--path"):
            path = Path(arg)
        elif opt in ("-n", "--cnt"):
            try:
                cnt = int(arg)
            except:
                print("Message counter must be numerical")
                error = True
    if error == True:
        return

    """ Setup and open connection """
    if path:
        connCfg = jsonLoad(path / 'conn.json') 
    else:
        print("Default connection setup used")
        connCfg = jsonLoad('config/conn.json') 
    try:
        conn = amq.amqConn(connCfg)
        conn.open()
    except Exception as e:
        print(e)
        cnt = 0
    
    bodyFile = 'body.json'
    headerFile = 'header.json'
    body = {}
    header = {}
    choices = ["mobileNotificationUpdate", "workOrderHeader", "assetFL", "mobileNotificationCreate"]
    pathToFile = Path('..')
    while cnt > 0:
        cnt = cnt - 1
        choice = random.choice(choices)
        pathToFile = pathToFile.cwd() / choice
        body = jsonDumps(pathToFile / bodyFile)
        header = jsonLoad(pathToFile / headerFile)
        try:
            header['JMSCorrelationID'] = str(uuid.uuid4())  #generate random uuid
            print(choice+": "+str(header['JMSCorrelationID']))
            conn.sendRequest(header, body)
        except Exception as e:
            print(e)
    
    time.sleep(10)

    """ Close the connection """
    conn.close()




if __name__ == "__main__":
    main(sys.argv[1:])
