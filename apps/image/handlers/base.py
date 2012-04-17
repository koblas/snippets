from cStringIO import StringIO
from addons import route
from apps.base import BaseHandler
from hashlib import sha1
import settings
from datetime import datetime, timedelta
from ..identicon import render_identicon
from tornado.util import import_object

PATH_BASE = '/img/'

@route(r'%s(?P<mod>[^/]+)/(?P<uid>[^_]+)_(?P<size>\d+x\d+).(?P<fmt>\w+)' % PATH_BASE)
class ImageViewHandler(BaseHandler):
    CLASSES = {}

    def get(self, mod=None, uid=None, size="32x32", fmt="PNG") :
        if mod in self.CLASSES:
            cls = self.CLASSES[mod]
        else:
            cls = import_object(mod)
            self.CLASSES[mod] = cls

        rawimage = None
        if cls and hasattr(cls, 'icon_image'):
            rawimage = cls.icon_image(uid)

        if fmt  : fmt = fmt.lower()
        if size : 
            w, h = size.split('x')
            w = int(w)
            h = int(h)
        else :
            w, h = 32, 32

        if rawimage :
            from PIL import Image

            thumb = Image.open(StringIO(rawimage))
            image = Image.new("RGB", (w, h), (255,255,255))

            if False :
                if thumb.size[0] > thumb.size[1] :
                    scale = w / float(thumb.size[0])
                else :
                    scale = h / float(thumb.size[1]) 
            else :  
                if thumb.size[0] < thumb.size[1] :
                    scale = w / float(thumb.size[0])
                else :
                    scale = h / float(thumb.size[1]) 

            thumb = thumb.resize((int(thumb.size[0] * scale), int(thumb.size[1] * scale)), Image.ANTIALIAS)
            dw = (w - thumb.size[0]) / 2
            dh = (h - thumb.size[1]) / 2
            image.paste(thumb, (dw, dh))

            fout = StringIO()
        else :
            s = sha1()
            s.update(settings.SECRET_KEY)

            s.update(mod)
            s.update(uid)

            v = s.hexdigest()

            image = render_identicon(int(v[0:16], 16), w / 3)

        ofd = StringIO()
        if fmt == 'gif' :
            mimetype = "image/gif"
            image.save(ofd, "GIF")
        elif fmt == 'jpg' :
            mimetype = "image/jpeg"
            image.save(ofd, "JPG")
        else :
            mimetype = "image/png"
            image.save(ofd, "PNG")

        tnow = datetime.now()
        data = ofd.getvalue()

        self.set_header('Content-Length', len(data))
        self.set_header('Content-Type',  mimetype)
        self.set_header('Cache-Control', 'public')
        self.set_header('Expires', tnow + timedelta(days=30))

        #self.set_header('Expires',        format_date_time(mktime(nowtuple) + 30 * 24*60*60))

        ##  TODO - Should get the last-modified working again...
        ## # match the code in http.last_modified -- since it does an "==" on the timestamps
        ## from calendar import timegm
        ## from email.Utils import formatdate
        ## self.set_header('Last-Modified',  formatdate(timegm(MIN_DATE.utctimetuple()))[:26] + 'GMT')

        self.write(data)
        self.finish()
