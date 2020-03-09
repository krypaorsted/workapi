import amq    #custom classes for work api active MQ handling
import json
import sys
import time
import os
import uuid

def jsonLoad(file):
    with open(file) as f:
        data = json.load(f)
    return data

def jsonDumps(file):
    data = jsonLoad(file)
    return json.dumps(data)


def main(argv):
    #TODO: add support of args
    connCfg = jsonLoad('config/conn.json')
    body = jsonDumps('config/body.json')
    headerCfg = jsonLoad('config/header.json')

    
    try:
        conn = amq.amqConn(connCfg)
        conn.open()
        header = headerCfg
        header['JMSCorrelationID'] = str(uuid.uuid4())  #generate random uuid
        print("Send request with correlation id:"+str(header['JMSCorrelationID']))
        conn.sendRequest(header, body)
    except Exception as e:
        print(e)
        return

    print('Waiting for response ...')
    loop  = 0
    response = ''
    while response == '' and loop < 10:
        loop += 1
        time.sleep(10)
        response = conn.getResponse(header['JMSCorrelationID'])

    #Output response message
    print(response)

    conn.close()



if __name__ == "__main__":
    main(sys.argv[1:])
