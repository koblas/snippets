from ..models import User
from addons import route
from apps.base import BaseHandler
from collections import defaultdict
from .auth_mixin import AuthMixin

@route('/auth/register')
class RegisterHandler(BaseHandler, AuthMixin):
    def get(self):
        self.render("auth/register.html")

    def post(self):
        form = {}
        for field in ['firstname', 'lastname', 'email', 'password', 'next']:
            form[field] = self.get_argument(field, '')

        if form['next'].startswith('/auth/'):
            form['next'] = '/'

        errors = defaultdict(list)

        if not form['firstname']:
            errors['firstname'].append('Please enter your first name')
        if not form['lastname']:
            errors['lastname'].append('Please enter your last name')
        if not form['email']:
            errors['email'].append('Please enter your email address')
        if not form['password']:
            errors['password'].append('Please enter provide a password')

        # TODO - Verify it's a valid email

        if User.objects.filter(email=form['email']).count():
            errors['email'].append('Email already in use')

        if errors:
            return self.render("auth/register.html", errors=errors, **form)

        user = User()
        user.email = form['email']
        user.set_password(form['password'])
        user.first_name = form['firstname']
        user.last_name = form['lastname']
        user.save()

        self.login(user)

        self.redirect(form['next'])
