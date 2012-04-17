import subprocess
import email.utils
import os
import re
import time
import logging
import tornado.web
import datetime
from addons import route
import thistle 
from settings import path

#logger = logging.getLogger('boilerplate.' + __name__)

@route("/dynamic/.*\.css", )
class ScssFileHandler(tornado.web.RequestHandler):
    DEP_RE  = re.compile(r'filename\{font-family:(?P<filename>.*?)}')
    CSS_DIR = ["static", "css"]
    watchers = {}
    depend = {}
    cache = {}

    @classmethod
    def sassRun(cls, dst_file):
        if dst_file in cls.watchers:
            return

        import os
        ofd = open(os.devnull, 'w')

        orig_file = dst_file.replace('.css', '.scss')
        pobj = subprocess.Popen(['sass', '--watch', '%s:%s' % (orig_file, dst_file)], stderr=ofd, cwd=path(*cls.CSS_DIR))
        time.sleep(0.1)     # There has to be something better than a sleep
        cls.watchers[dst_file] = pobj

    def sassData(cls, dst_file):
        if dst_file in cls.depend and dst_file in cls.cache:
            data = cls.cache[dst_file]
            modified = 0
            for filename, lastmod in cls.depend[dst_file].items():
                modified = max(lastmod, modified)
                if os.stat(filename)[8] != lastmod:
                    data = None
                    break

            if data:
                return (data, modified)

        orig_file = dst_file.replace('.css', '.scss')
        p = subprocess.Popen(['sass', '-g', '%s' % (orig_file)], stdout=subprocess.PIPE, cwd=path(*cls.CSS_DIR))
        data = p.stdout.read()

        deps = {}
        for line in data.split("\n"):
            if line.startswith('@media -sass-debug-info{filename{'):
                m = cls.DEP_RE.search(line)
                if m:
                    filename = m.group('filename')
                    filename = filename.replace('\\', '')[7:]
                    if filename not in deps:
                        deps[filename] = os.stat(filename)[8]

        cls.depend[dst_file] = deps
        cls.cache[dst_file] = data

        modified = max(deps.values())

        return (data, modified)

    def get(self):
        file = self.request.path.split('/')[-1]

        try :
            # self.runSass(file)
            # with open(path('static', 'css', file)) as fd:
            #    data = fd.read()
            data, modified = self.sassData(file)
        except Exception as e:
            data = None
            modified = 0
            print e
        
        self.set_header('Content-Type', 'text/css')
        if modified:
            modts = datetime.datetime.fromtimestamp(modified)
            self.set_header("Last-Modified", modts)

        ims_value = self.request.headers.get("If-Modified-Since")
        if ims_value and modified:
            date_tuple = email.utils.parsedate(ims_value)
            if_since = datetime.datetime.fromtimestamp(time.mktime(date_tuple))
            if if_since >= modts:
                self.set_status(304)
                return

        self.finish(data)
