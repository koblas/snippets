import logging
import tornado.web
from addons import route
from apps.base import BaseHandler, TornadoContext

from ..models import User
from .auth_mixin import AuthMixin

@route('/auth/logout')
class LogoutHandler(BaseHandler, AuthMixin):
    def get(self):
        self.login(None)

        self.render("auth/logout.html", current_user=None)
