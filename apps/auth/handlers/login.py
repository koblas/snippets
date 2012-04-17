from addons import route
from apps.base import BaseHandler
from .auth_mixin import AuthMixin

from ..models import User

@route('/auth/login')
class LoginHandler(BaseHandler, AuthMixin):
    def get(self):
        self.render("auth/login.html", nexturl=self.get_argument('next','').strip())

    def post(self):
        email            = self.get_argument('email', '')
        password         = self.get_argument('password', '')
        remember         = self.get_argument('remember', False)
        nexturl          = self.get_argument('next', '/')

        if nexturl in ('/auth/login', '/auth/logout'):
            nexturl = '/'

        form = dict(email=email, remember=remember, nexturl=nexturl)

        errors = {}

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            errors['email'] = ["User doesn't exist"]

        if not errors and not user.check_password(password):
            errors['password'] = ["Password incorrect"]

        if errors:
            return self.render("auth/login.html", errors=errors, **form)

        self.login(user, remember)
        self.redirect(nexturl)
