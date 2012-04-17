import logging
import tornado.web
from addons import route
from apps.base import BaseHandler, TornadoContext
import thistle 

#logger = logging.getLogger('boilerplate.' + __name__)

@route('/mail')
class MailHandler(BaseHandler):
    def get(self):
        from addons.smtp import SMTPClient

        body = """
To: John Smith <john@example.com>
Subject: test message

Testing, testing...
"""
        x += 1

        smtp = SMTPClient('localhost', 25)
        client=smtp.send(sender='nobody@nowhere.net', rcpt=['david@koblas.com'], body=body)
        client=smtp.send(sender='nobody@nowhere.net', rcpt=['david@koblas.com'], body=body)

        self.finish(thistle.render_to_string("dashboard.html", {
                            }, context_instance=TornadoContext(self)))
