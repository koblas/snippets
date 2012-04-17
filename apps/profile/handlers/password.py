import tornado.web
from addons import route
from apps.base import BaseHandler

@route('/profile/password')
class ProfilePasswordHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("profile/password.html")

    @tornado.web.authenticated
    def post(self):
        old         = self.get_argument('password_old', '').strip()
        pw1         = self.get_argument('password', '').strip()
        pw2         = self.get_argument('password_again', '').strip()

        errors = {}

        user = self.current_user
        if not user.check_password(old):
            errors['password_old'] = ["old password doesn't match"]
        elif not pw1 or not pw2:
            errors['password'] = ["Missing new password"]
        elif pw1 != pw2:
            errors['password'] = ["Passwords don\'t match"]
        
        if not errors:
            user.set_password(pw1)
            user.save()

            self.set_message('Password updated', kind='success')

        self.render("profile/password.html", errors=errors)
