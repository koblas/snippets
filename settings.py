import os
ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *a: os.path.join(ROOT,*a)

SECRET_KEY = 'justarandomstring'

TITLE = u"Snaplabs"
APPS = (
  'main',
  'info',
  'image',
  'profile',
  'snippets',
  'auth',
)

DATABASE_NAME = "sniptest"

LOGIN_URL = "/auth/login"

STATIC_URL_BASE = '/static/'

#REDIS_HOST = 'localhost'
#REDIS_PORT = 6379

COOKIE_SECRET = "11o3tZkSXqagayDKL5GMgejJFu4h7EQnp1XdTP10/"

WEBMASTER = 'noreply@snaplabs.com'
ADMIN_EMAILS = ['david@koblas.com']

#EMAIL_REMINDER_SENDER = 'reminder+%(id)s@snaplabs.com'
#EMAIL_REMINDER_NOREPLY = 'noreplyplease@snaplabs.com'

FACEBOOK_SECRET  = 'xxx'
FACEBOOK_API_KEY = 'xxx'

# commented out because it's on by default but driven by dont_embed_static_url option instead
## if you do this, for the static files, instead of getting something like
## '/static/foo.png?v=123556' we get '/static/v-123556/foo.png'
#EMBED_STATIC_URL_TIMESTAMP = True

try:
    from local_settings import *
except ImportError:
    pass
