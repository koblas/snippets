from datetime import datetime, timedelta
from ..pager import Paginator
from ..models import Snippet, User
from addons import route
from apps.base import BaseHandler

@route('/$')
class HomeViewHandler(BaseHandler):
    PER_PAGE = 10

    def get(self, guid=None):
        snippets = Snippet.objects()

        self.render('homepage.html', snippet_list=snippets)
