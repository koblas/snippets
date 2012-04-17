import tornado.web
from addons import route
from apps.base import BaseHandler
from ..models import ProfileImage

@route('/profile/image')
class ProfileImageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user

        self.render("profile/image.html")

    @tornado.web.authenticated
    def post(self):
        # body, content_type, filename
        file_data = self.request.files.get('image',None)
        if file_data:
            data = file_data[0]['body']

        errors   = {}
        if not data:
            errors['image'] = ["No Image Provided"]

        if not errors:
            user = self.current_user

            ProfileImage.objects(user=user).delete()
            ProfileImage(user=user, data=data).save()

            self.set_message('Updated', kind='success')

            user.save()

        self.render("profile/image.html", errors=errors)
