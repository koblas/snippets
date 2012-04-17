from tornado import ioloop
from tornado import iostream
import socket

class SMTPClient(object):
    def __init__(self, host, port):
        self.host = 'localhost'
        self.port = 25
        self.msgs = []
        self.stream = None

    def send(self, sender=None, rcpt=[], body="", callback=None):
        self.msgs.append({
                'rcpt'     : rcpt[:],
                'body'     : body,
                'sender'   : sender,
                'callback' : callback,
            })

        if not self.stream:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.stream = iostream.IOStream(s)
            self.stream.connect((self.host, self.port), self.wait_greet)

    def wait_greet(self):
        self.stream.read_until('\r\n', self.send_ehlo)

    def send_ehlo(self, data):
        #print "send_ehlo", data,
        if data[0:3] != '220':
            # TODO - error on startup
            self.close()
            return
        self.stream.write('EHLO localhost\r\n')
        self.stream.read_until('\r\n', self.helo_response)

    def helo_response(self, data):
        #print "helo_response", data,
        if data[0:3] != '250':
            self.close()
            return
        if data[3] == '-':
            self.stream.read_until('\r\n', self.helo_response)
        else:
            self.stream.write('MAIL FROM: <%s>\r\n' % self.msgs[0]['sender']) 
            self.stream.read_until('\r\n', self.mail_response)

    def mail_response(self, data):
        #print "mail_response", data,
        if data[0:3] != '250':
            self.close()
            return

        if self.msgs[0]['rcpt']:
            self.stream.write('RCPT TO: <%s>\r\n' % self.msgs[0]['rcpt'].pop(0))
            self.stream.read_until('\r\n', self.rcpt_response)

    def rcpt_response(self, data):
        #print "rcpt_response", data,
        if data[0:3] not in ('250', '251'):
            self.close()
            return
            
        if self.msgs[0]['rcpt']:
            self.stream.write('RCPT TO: <%s>\r\n' % self.msgs[0]['rcpt'].pop(0))
            self.stream.read_until('\r\n', self.rcpt_response)
        else:
            self.stream.write('DATA\r\n') 
            self.stream.read_until('\r\n', self.data_response)

    def data_response(self, data):
        #print "data_response", data,
        if data[0:3] != '354':
            self.close()
            return
        self.stream.write(self.msgs[0]['body'])
        if self.msgs[0]['body'][-2:] == '\r\n':
            self.stream.write('.\r\n')
        else:
            self.stream.write("\r\n.\r\n")
        self.stream.read_until("\r\n", self.body_response)

    def body_response(self, data):
        #print "body_response", data,
        if data[0:3] != '250':
            self.close()
        if self.msgs[0]['callback']:
            self.msgs[0]['callback'](True)

        self.msgs.pop(0)
        if self.msgs:
            self.stream.write('MAIL FROM: <%s>' % self.msgs[0]['sender']) 
            self.stream.read_until('\r\n', self.mail_response)

    def close(self):
        for msg in self.msgs:
            if msg['callback']:
                msg['callback'](False)
        self.stream.close()
