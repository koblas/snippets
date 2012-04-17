# python
import traceback
import stat
from cStringIO import StringIO
from urlparse import urlparse
from pprint import pprint
from time import mktime, sleep, time
import datetime
import os.path
import re
import logging

# tornado
import tornado.auth
import tornado.web
import settings

from addons.mail import send_mail

from thistle import Context
class TornadoContext(Context):
    def __init__(self, handler):
        data = {
            'xsrf_token' : handler.xsrf_token,
            'user'       : handler.user,
            'STATIC_URL' : settings.STATIC_URL_BASE,
        }
        super(TornadoContext, self).__init__(dict_=data)

class HTTPSMixin(object):

    def is_secure(self):
        # XXX is this really the best/only way?
        return self.request.headers.get('X-Scheme') == 'https'

    def httpify_url(self, url=None):
        url = url if url else self.request.full_url()
        if url.startswith('/'):
            parsed = urlparse(self.request.full_url())
            return 'http://%s%s' % (parsed.netloc, url)
        else:
            return url.replace('https://', 'http://')

    def httpsify_url(self, url=None):
        url = url if url else self.request.full_url()
        if url.startswith('/'):
            parsed = urlparse(self.request.full_url())
            return 'https://%s%s' % (parsed.netloc, url)
        else:
            return url.replace('http://', 'https://')


class BaseHandler(tornado.web.RequestHandler, HTTPSMixin):

    #def render(self, *args, **kwargs):
    #    super(BaseHandler, self).render(*args, **kwargs)
    #    print self.application.ui_modules

    def static_url(self, path):
        self.require_setting("static_path", "static_url")
        if not hasattr(BaseHandler, "_static_timestamps"):
            BaseHandler._static_timestamps = {}
        timestamps = BaseHandler._static_timestamps
        abs_path = os.path.join(self.application.settings["static_path"],
                                        path)
        if abs_path not in timestamps:
            try:
                timestamps[abs_path] = os.stat(abs_path)[stat.ST_MTIME]
            except OSError:
                logging.error("Could not open static file %r", path)
                timestamps[abs_path] = None
        base = self.request.protocol + "://" + self.request.host \
            if getattr(self, "include_host", False) else ""
        static_url_prefix = self.settings.get('static_url_prefix', '/static/')
        if timestamps.get(abs_path):
            if self.settings.get('embed_static_url_timestamp', False):
                return base + static_url_prefix + 'v-%d/' % timestamps[abs_path] + path
            else:
                return base + static_url_prefix + path + "?v=%d" % timestamps[abs_path]
        else:
            return base + static_url_prefix + path

    def _handle_request_exception(self, exception):
        if not isinstance(exception, tornado.web.HTTPError) and \
          not self.application.settings['debug']:
            # ie. a 500 error
            try:
                self._email_exception(exception)
            except:
                print "** Failing even to email exception **"

        if self.application.settings['debug']:
            # Because of
            # https://groups.google.com/d/msg/python-tornado/Zjv6_3OYaLs/CxkC7eLznv8J
            print exception
        super(BaseHandler, self)._handle_request_exception(exception)

    def x_log(self):
        """overwritten from tornado.web.RequestHandler because we want to put
        all requests as logging.debug and keep all normal logging.info()"""
        if self._status_code < 400:
            #log_method = logging.info
            log_method = logging.debug
        elif self._status_code < 500:
            log_method = logging.warning
        else:
            log_method = logging.error
        request_time = 1000.0 * self.request.request_time()
        log_method("%d %s %.2fms", self._status_code,
                   self._request_summary(), request_time)


    def _email_exception(self, exception): # pragma: no cover
        print "**** HERE"

        import sys
        err_type, err_val, err_traceback = sys.exc_info()
        error = u'%s: %s' % (err_type, err_val)
        out = StringIO()
        subject = "%r on %s" % (err_val, self.request.path)
        print >>out, "TRACEBACK:"
        traceback.print_exception(err_type, err_val, err_traceback, 500, out)
        traceback_formatted = out.getvalue()
        print traceback_formatted
        print >>out, "\nREQUEST ARGUMENTS:"
        arguments = self.request.arguments
        if arguments.get('password') and arguments['password'][0]:
            password = arguments['password'][0]
            arguments['password'] = password[:2] + '*' * (len(password) -2)
        pprint(arguments, out)

        print >>out, "\nCOOKIES:"
        for cookie in self.cookies:
            print >>out, "  %s:" % cookie,
            print >>out, repr(self.get_secure_cookie(cookie))

        print >>out, "\nREQUEST:"
        for key in ('full_url', 'protocol', 'query', 'remote_ip',
                    'request_time', 'uri', 'version'):
            print >>out, "  %s:" % key,
            value = getattr(self.request, key)
            if callable(value):
                try:
                    value = value()
                except:
                    pass
            print >>out, repr(value)

        print >>out, "\nGIT REVISION: ",
        print >>out, self.application.settings['git_revision']

        print >>out, "\nHEADERS:"
        pprint(dict(self.request.headers), out)

        send_mail(subject,
                  out.getvalue(),
                  self.application.settings['webmaster'],
                  self.application.settings['admin_emails'],
                  )

    @property
    def redis(self):
        return self.application.redis

    def get_cdn_prefix(self):
        """return something that can be put in front of the static filename
        E.g. if filename is '/static/image.png' and you return '//cloudfront.com'
        then final URL presented in the template becomes
        '//cloudfront.com/static/image.png'
        """
        return self.application.settings.get('cdn_prefix')
        # at the time of writing, I'm just going to use the CDN if you're running
        # a secure connection. This is because the secure connection is limited
        # to paying customers and they deserve it
        if self.is_secure():
            return self.application.settings.get('cdn_prefix')

    def write_json(self, struct, javascript=False):
        if javascript:
            self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(tornado.escape.json_encode(struct))

    def write_txt(self, str_):
        self.set_header("Content-Type", "text/plain; charset=UTF-8") # doesn;t seem to work
        self.write(str_)

    def get_current_user(self):
        """Implementation for current_user property"""
        from apps.auth.models import User

        guid = self.get_secure_cookie("user")
        if guid:
            return User.objects.get(guid=guid)
        return None

    def set_message(self, msg, kind='error'):
        """ Kind should be one of:  error, success, info """
        import json
        self.get_message()
        if not hasattr(self, '_new_message'):
            self._new_messages = []
        self._new_messages.append([kind, msg])
        self.set_secure_cookie("message", json.dumps(self._new_messages))

    def get_message(self):
        if not hasattr(self, '_messages'):
            msgs = self.get_secure_cookie("message")
            self.clear_cookie('message')
            if msgs:
                import json
                self._messages = [{'kind':v[0], 'message':v[1]} for v in json.loads(msgs)]
            else:
                self._messages = []
        return self._messages

    def get_error_html(self, status_code, **kwargs):
        try:
            import httplib
            return self.render_string("error.html", message=httplib.responses[status_code], status_code=status_code)
        except:
            if self.settings.get("debug") and "exc_info" in kwargs:
                # in debug mode, try to send a traceback
                self.set_header('Content-Type', 'text/plain')
                return "\n".join([line for line in traceback.format_exception(*kwargs["exc_info"])])
            else:
                return ("<html><title>%(code)d: %(message)s</title>"
                        "<body>%(code)d: %(message)s</body></html>") % {
                        "code": status_code,
                        "message": httplib.responses[status_code],
                        }
