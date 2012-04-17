import logging
import tornado.web
import tornado.auth
from addons import route
from apps.base import BaseHandler, TornadoContext
from .auth_mixin import AuthMixin

from ..models import User, OpenUser

class CommonMixer(AuthMixin):
    def _find_user(self, oid, email='', first_name='', last_name=''):
        user = None

        try:
            ouser = OpenUser.objects.get(openid=oid)
            user = ouser.user
        except OpenUser.DoesNotExist:
            user = User()
            user.email      = email
            user.first_name = first_name
            user.last_name  = last_name
            user.save()

            ouser = OpenUser(user_guid=user.guid, openid=oid)
            ouser.save()

        self.login(user)

        return user

@route('/auth/oa/facebook')
class FacebookHandler(tornado.web.RequestHandler, tornado.auth.FacebookMixin, CommonMixer):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("session", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, odata):
        if not odata:
            raise tornado.web.HTTPError(500, "Facebook auth failed")

        oid = 'facebook:%s' % odata['uid']

        user = self._find_user(oid, first_name=odata['first_name'], last_name=odata['last_name'])

        self.redirect('/')

@route('/auth/oa/google')
class GoogleHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin, CommonMixer):
    @tornado.web.asynchronous
    def get(self):
        if self.get_argument("openid.mode", None):
            self.get_authenticated_user(self.async_callback(self._on_auth))
            return
        self.authenticate_redirect()

    def _on_auth(self, odata):
        if not odata:
            raise tornado.web.HTTPError(500, "Google auth failed")

        oid = 'google:%s' % odata['email']

        user = self._find_user(oid, email=odata['email'], first_name=odata['first_name'], last_name=odata['last_name'])

        self.redirect('/')
