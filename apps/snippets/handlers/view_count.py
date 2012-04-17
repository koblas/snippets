import logging
import tornado.web
from ..models import Snippet
from addons import route
from apps.base import BaseHandler

@route('/snippets/view/(?P<guid>[^/]+)')
class SnippetViewCountHandler(BaseHandler):
    def get(self, guid=None):
        snippet = Snippet.objects.get(guid=guid)

        snippet.increment_views();

        self.finish({'status': 1});
