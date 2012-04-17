from datetime import datetime
import tornado.web
from ..models import Snippet, Tag
from addons import route
from apps.base import BaseHandler

@route('/snippets/(?P<guid>[^/]*)(?:add|/edit)/')
class SnippetEditHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, guid=None):
        user = self.current_user

        template_name = 'snippet/edit.html'
        if guid:
            try:
                snippet = Snippet.objects.get(guid=guid)
            except Snippet.DoesNotExist:
                pass

            if user.guid != snippet.author.guid:
                # TODO - FIXME
                return HttpResponseForbidden()
        else:
            snippet = Snippet(author=user)
            snippet.tags = []
            snippet.title = ''
            snippet.description = ''
            snippet.code = ''

        self.render(template_name, snippet=snippet)

    @tornado.web.authenticated
    def post(self, guid=None):
        user = self.current_user

        form = {}
        for field in ['title', 'language', 'tags', 'code', 'description']:
            form[field] = self.get_argument(field, '')

        errors = {}

        if form['title'] == '':
            errors['title'] = ['Please provide a title']
        if form['description'] == '':
            errors['description'] = ['Please provide a description']
        if form['code'] == '':
            errors['code'] = ['Please provide a some code']

        if errors:
            template_name = 'snippet/edit.html'
            self.render(template_name, errors=errors)
            return

        tags = []
        for tag in form['tags'].split(','):
            tag = tag.strip()
            if tag:
                t, created = Tag.objects.get_or_create(lc_name=tag.lower(), defaults={ 'name' : tag })
                tags.append(t)

        if guid:
            try:
                snippet = Snippet.objects.get(guid=guid)
            except Snippet.DoesNotExist:
                pass

            if user.guid != snippet.author.guid:
                # TODO - FIXME
                return HttpResponseForbidden()
        else:
            snippet = Snippet(author=user)

        snippet.title = form['title']
        snippet.code = form['code']
        snippet.description = form['description']
        snippet.updated_date = datetime.now()
        # snippet.language = language
        snippet.tags = tags
        snippet.save()

        self.set_message("Updated", 'success')
        
        # TODO - Message "Your snippet has been saved"
        self.redirect(snippet.get_absolute_url())
