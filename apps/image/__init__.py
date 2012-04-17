
from .handlers.base import PATH_BASE

def url(obj, id, width=64, height=64, fmt='png', modtime=None) :
    u = "%s%s.%s/%s_%dx%d.%s" % (PATH_BASE, obj.__class__.__module__, obj.__class__.__name__, id, width, height, fmt)
    if modtime :
        return u + '?_=%d' % modtime
    return u
