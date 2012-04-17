import logging
import tornado.web
#from ..models import User
from addons import route
from apps.base import BaseHandler

@route('/profile/settings')
class ProfileSettingsHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user

        email2 = user.email_secondary if user.email_secondary else ""

        self.render("profile/settings.html", email=user.email, email2=email2)

    @tornado.web.authenticated
    def post(self):
        email      = self.get_argument('email', '').strip()

        errors = {}
        if not email:
            messages += ["Please provide an email address"]

        if not errors:
            user = self.current_user

            user.email           = email

            user.save()

            self.set_message("Email Address Updated", kind='success')

        self.render("profile/settings.html", errors=errors, email=email)
