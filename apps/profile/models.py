import uuid
from ..auth.models import User
from mongoengine import *
from apps.image import url as image_url

class ProfileImage(Document):
    user     = ReferenceField(User)
    guid     = StringField(required=True, default=lambda:str(uuid.uuid4()))
    data     = BinaryField()

class UserProfile(object):
    def __init__(self, user):
        self.user = user

    def _icon(self, size):
        try:
            img = ProfileImage.objects(user=self.user).get()
        except ProfileImage.DoesNotExist:
            return None
        return image_url(self, img.guid, size, size)

    def icon30(self):
        return self._icon(30)

    def icon128(self):
        return self._icon(128)

    def icon70(self):
        return self._icon(70)

    @classmethod
    def icon_image(self, guid):
        try:
            obj = ProfileImage.objects(guid=guid).get()
        except ProfileImage.DoesNotExist:
            return None
        return obj.data

    def has_image(self):
        return ProfileImage.objects(user=self.user).count() != 0

    def url(self):
        return "/users/%s" % self.user.guid
    
User.profile = property(lambda u: UserProfile(user=u))
