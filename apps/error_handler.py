from .base import BaseHandler
import tornado.web

class Handle404(BaseHandler):
    def initialize(self, status_code):
            self.set_status(status_code)

    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)

tornado.web.ErrorHandler = Handle404
