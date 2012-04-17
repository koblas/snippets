from datetime import datetime, timedelta
from ..pager import Paginator
from ..models import Snippet, User
from addons import route
from apps.base import BaseHandler

@route('/users/(?P<guid>[^/]*)/?')
class UserViewHandler(BaseHandler):
    PER_PAGE = 10

    def get(self, guid=None):
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

        if guid:
            user = User.objects.get(guid=guid)

            all_snippets = Snippet.objects(author=user)
            if not months:
                snippets = all_snippets
            else:
                tval = datetime.now() - timedelta(days=months*30)
                snippets = Snippet.objects(author=user, updated_date__gt=tval)

            count = snippets.count()
            page = Paginator(snippets).page(page_num)

            self.render('snippet/by_user.html', 
                            author=user, 
                            author_count=count, 
                            months=months, 
                            page=page)
        else:
            self.render('snippet/all_users.html', users=User.objects)
