from collections import defaultdict
from .auth_mixin import AuthMixin
import urlparse
import tornado.web
from addons import route, mail
from apps.base import BaseHandler, TornadoContext
from ..models import User, PasswordRecovery

#logger = logging.getLogger('boilerplate.' + __name__)

@route('/auth/recover')
class RecoverHandler(BaseHandler):
    def get(self):
        self.render("auth/recover.html")

    def post(self):
        email = self.get_argument('email', '').strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return self.render("auth/recover_sent.html")

        try:
            obj = PasswordRecovery.objects.get(user_guid=user.guid)
            obj.delete()
        except PasswordRecovery.DoesNotExist:
            pass

        obj = PasswordRecovery(user=user)
        obj.save()

        rurl = urlparse.urljoin("http://%s%s" % (self.request.host, self.request.uri), 
                                      self.reverse_url('recovery_click', obj.token))

        from thistle import Context

        mail.send_template(subject="Password Recovery", 
                           html="auth/email_recovery.html", 
                           text=None, 
                           rcpt=[email], 
                           sender=self.application.settings['webmaster'], 
                           context_instance=Context({
                                'recovery' : obj,
                                'recovery_url' : rurl,
                           }),
                           fail_silently=True)

        """
        send_email(self.application.settings['email_backend'],
                   subject,
                   out.getvalue(),
                   self.application.settings['webmaster'],
                   self.application.settings['admin_emails'],
        """

        self.render("auth/recover_sent.html", email=email)

@route('/auth/reclick/(.*)', name="recovery_click")
class RecoverHandler(BaseHandler, AuthMixin):
    def get(self, token):
        try:
            obj = PasswordRecovery.objects.get(token=token)
        except PasswordRecovery.DoesNotExist:
            return self.render("auth/recover_notoken.html")

        self.render("auth/recover_click.html")

    def post(self, token):
        try:
            obj = PasswordRecovery.objects.get(token=token)
        except PasswordRecovery.DoesNotExist:
            return self.render("auth/recover_notoken.html")

        pw1 = self.get_argument('password', '').strip()
        pw2 = self.get_argument('password_again', '').strip()

        errors = defaultdict(list)
        if pw1 != pw2:
            errors['password'].append('Passwords don\'t match')
        elif not pw1 or not pw2:
            errors['password'].append('Please enter a password')

        if errors:
            return self.render("auth/recover_click.html", errors=errors)

        obj.user.set_password(pw1)
        obj.delete()

        self.login(obj.user, True)

        # TODO - We need to add messaging

        self.redirect("/")

@route('/auth/reset')
class ResetHandler(BaseHandler):
    def get(self):
        email = self.get_argument('email', '')

        self.render("auth/recover_reset.html", email=email)
