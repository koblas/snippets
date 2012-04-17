from ..models import Tag, Snippet
from ..pager import Paginator
from addons import route
from apps.base import BaseHandler

@route('/tags/(?P<tag>[^/]*)/?')
class ByTagViewHandler(BaseHandler):
    def get(self, tag=None):
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

        if tag:
            tobj = Tag.objects.get(lc_name=tag.lower())

            snippets = Snippet.objects(tags=tobj)
            count = snippets.count()
            page = Paginator(snippets).page(page_num)

            self.render('snippet/by_tag.html', page=page, tag=tobj, months=months)
        else:
            self.render('snippet/all_tags.html', tags=Tag.objects, months=months)
