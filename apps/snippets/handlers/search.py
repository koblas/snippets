from ..pager import Paginator
from ..models import Snippet
from addons import route
from apps.base import BaseHandler

@route('/search/')
class SearchViewHandler(BaseHandler):
    def get(self):
        term = self.get_argument('q')

        try:
            months = int(self.get_argument('months', 0))
        except:
            months = None

        try:
            page_num = int(self.get_argument('page', 0))
            if page_num < 1:
                page_num = 1
        except:
            page_num = 1

        results = []
        for snippet in Snippet.objects.all():
            results.append(snippet)

        page = Paginator(results).page(page_num)

        self.render('snippet/search.html', page=page, hits=page.paginator.count, months=months)
