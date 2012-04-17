import tornado.web
from addons import route
from apps.base import BaseHandler

@route('/profile/')
class ProfileHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user

        self.render("profile/profile.html", first_name=user.first_name, last_name=user.last_name)

    @tornado.web.authenticated
    def post(self):
        firstname  = self.get_argument('first_name', '').strip()
        lastname   = self.get_argument('last_name', '').strip()

        errors   = {}
        if not firstname:
            errors['first_name'] = ["Please provide a first name"]
        if not lastname:
            errors['last_name'] = ["Please provide a last name"]

        if not errors:
            user = self.current_user

            user.first_name = firstname
            user.last_name  = lastname

            self.set_message('Updated', kind='success')

            user.save()

        self.render("profile/profile.html", errors=errors, first_name=firstname, last_name=lastname)
