class AuthMixin(object):
    def login(self, user, remember=True):
        if not user:
            self.clear_cookie('user')
        else:
            if remember:
                self.set_secure_cookie('user', str(user.guid), expires_days=100)
            else:
                self.set_secure_cookie('user', str(user.guid), expires_days=None)
