from datetime import datetime
import tornado.web
from ..models import Snippet, Comment
from addons import route
from apps.base import BaseHandler

@route('/snippets/(?P<guid>[^/]*)/comment')
class SnippetCommentHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self, guid=None):
        user = self.current_user

        comment = self.get_argument('comment')
        snippet = Snippet.objects.get(guid=guid)

        errors = {}

        if comment == '':
            errors['comment'] = ['Please provide a title']

        if not errors:
            obj = Comment(author=user, content=comment)
            Snippet.objects(guid=guid).update_one(push__comments=obj)

            self.set_message('Your comment has been added', kind='success')
            self.redirect(snippet.get_absolute_url())

        return self.render('snippet/show.html', errors=errors, snippet=snippet)
