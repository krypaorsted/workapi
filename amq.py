import stomp
import uuid

class amqListener(stomp.ConnectionListener):
    """ Basic listener to be extended """
    def __init__(self):
        self.msgs = {}
    def addMsg(self,correlationID, headers, body ):
        self.msgs[correlationID] = {'headers': headers, 'body': body, 'response': {}}
    def getResponse(self, correlationID):
        if correlationID in self.msgs:
            return self.msgs[correlationID]['response']
        else:
            return {}
    def setCorrelationID(self, correlationID):
        self.correlationID = correlationID
    def setDone(self, headers, message, error=False):
        #if headers['correlation-id'] == self.correlationID:
        if headers['correlation-id'] in self.msgs:
            self.msgs[headers['correlation-id']]['response'] = message
            """self.headers = headers
            self.message = message
            self.done = True"""

    def on_error(self, headers, message):
        #print('received an error "%s"' % message)
        self.setDone(headers, message, True)
    def on_message(self, headers, message):
        #print('received a message "%s"' % message)
        #print(str(headers))
        self.setDone(headers, message )


class amqConn():
    """ Active MQ connection class """
    steteClosed = 0
    stateOpen = 1
    stateError = 9

    def __init__(self,config):
        self.config = config
        self.conn   = ''
        self.state = amqConn.steteClosed

    def open(self):
        """ Open connection """
        host = self.config['host']
        port = int(self.config['port'])
        user = self.config['user']
        password = self.config['password']
        try:
            self.conn = stomp.Connection(host_and_ports=[(host, port)])
            self.listener = amqListener()
            self.conn.set_listener('', self.listener)
            self.conn.connect(user, password, wait=True)
            self.state = amqConn.stateOpen
        except:
            self.state = amqConn.stateError

    def close(self):
        """ Close connection """
        if self.conn and self.state == amqConn.stateOpen:
            self.conn.disconnect()
            self.state = amqConn.steteClosed

    def sendRequest(self, header, body):
        """ Send request 
            Subscribe for response if listener is instantiated and header contains JSMReplyTo
        """
        if self.state != amqConn.stateOpen:
            print(self.state)
            raise Exception('Connection not open')
        if not header['SendTo']:
            raise Exception('SendTo required in header')
        sendTo = header['SendTo']
        replyTo = header['JMSReplyTo']
        #self.listener.setCorrelationID(header['JMSCorrelationID'])
        if self.listener:
            self.listener.addMsg(header['JMSCorrelationID'], header, body)
            self.conn.subscribe(destination=replyTo, id=1, ack='auto', headers=header)
        self.conn.send(body=body, destination=sendTo, headers=header)
    
    def getResponse(self, correlationID):
        if self.listener:
            return self.listener.getResponse(correlationID)
        else:
            return {}



    
        