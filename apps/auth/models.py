import uuid
import password
from datetime import datetime
from mongoengine import *
from mongoengine.queryset import QuerySet

class UserQuerySet(QuerySet):
    def get(self, *args, **kwargs):
        if 'email' in kwargs:
            kwargs['email_lc'] = kwargs.pop('email').lower()
        return super(UserQuerySet, self).get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        if 'email' in kwargs:
            kwargs['email_lc'] = kwargs.pop('email').lower()
        return super(UserQuerySet, self).filter(*args, **kwargs)

class User(Document):
    meta = {
        'queryset_class' : UserQuerySet,
        'collection'     : 'auth_user',
        'indexes'        : ['guid', 'email', 'email_lc'],
    }

    email      = StringField(required=True)
    email_lc   = StringField(required=True)
    email_secondary = StringField()
    first_name = StringField()
    last_name  = StringField()
    password   = StringField(required=True, default=password.UNUSABLE_PASSWORD)
    guid       = StringField(required=True, default=lambda:str(uuid.uuid4()))
    created_at = DateTimeField(required=True, default=datetime.now)

    def check_password(self, raw_password):
        return password.check_password(raw_password, self.password)

    def set_password(self, raw_password):
        self.password = password.make_password(raw_password)

    def save(self, *args, **kwargs):
        lc_email = self.email.lower()
        if lc_email != self.email_lc:
            self.email_lc = lc_email

        super(User, self).save(*args, **kwargs)

    def name(self):
        return "%s %s" % (self.first_name , self.last_name)

#
#
#
class UserModelMixin(Document):
    meta = {
            'abstract' : True,
            'index_background'  : ['user_guid'],
    }

    user_guid  = StringField(required=True)

    def __init__(self, user=None, *args, **kwargs):
        super(UserModelMixin, self).__init__(*args, **kwargs)

        if user:
            self.user_guid = user.guid
            self._user_cache = user

    @property
    def user(self):
        if not hasattr(self, '_user_cache'):
            self._user_cache = User.objects.get(guid=self.user_guid)
        return self._user_cache

#
#
#
class OpenUser(UserModelMixin):
    meta = {
        'collection'     : 'auth_open_user',
    }

    guid       = StringField(required=True, default=lambda:str(uuid.uuid4()))
    openid     = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.now)

class PasswordRecovery(UserModelMixin):
    meta = {
        'collection'     : 'auth_password_recovery',
        'indexes'        : ['token'],
    }

    token      = StringField(required=True)
    created_at = DateTimeField(required=True, default=datetime.now)

    def __init__(self, **kwargs):
        super(PasswordRecovery, self).__init__(**kwargs)

        import uuid
        import base64

        self.token = base64.urlsafe_b64encode(uuid.uuid1().bytes).rstrip('=')
