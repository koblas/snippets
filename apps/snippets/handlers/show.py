import logging
import tornado.web
from ..models import Snippet
from addons import route
from apps.base import BaseHandler

@route('/snippets/(?P<guid>[^/]+)')
class SnippetViewHandler(BaseHandler):
    def get(self, guid=None):
        snippet = Snippet.objects.get(guid=guid)

        self.render('snippet/show.html', snippet=snippet)
