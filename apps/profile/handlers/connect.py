import logging
import tornado.web
#from ..models import User
from addons import route
from apps.base import BaseHandler

@route('/profile/connect')
class ProfileConnectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("profile/connect.html")
