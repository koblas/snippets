from ..models import Snippet, Vote
import tornado.web
from addons import route
from apps.base import BaseHandler

@route('/snippets/vote/(?P<guid>[^/]+)')
class SnippetVoteHandler(BaseHandler):
    def get(self, guid=None):
        if not self.current_user:
            raise tornado.web.HTTPError(404)

        vote = self.get_argument('vote', 0)

        snippet = Snippet.objects.get(guid=guid)
        obj, created = Vote.objects.get_or_create(snippet=snippet, user=self.current_user)
        if not created:
            obj.value = vote
            obj.save()

        self.finish({'count': obj.snippet.vote_count });
