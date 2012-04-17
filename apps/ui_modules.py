
import tornado.web

class messages(tornado.web.UIModule):
    def render(self, *args, **kwargs):
        return self.handler.get_message()
