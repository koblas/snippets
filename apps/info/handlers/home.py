import logging
import tornado.web
from addons import route
from apps.base import BaseHandler
from tornado.web import HTTPError

@route('/about/([^/]*)/?')
class InfoHandler(BaseHandler):
    def get(self, name):
        print name
        if not name:
            name = 'about'
        try:
            self.render("info/%s.html" % name)
        except:
            raise HTTPError(404)
