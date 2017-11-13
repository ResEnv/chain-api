DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

ADMINS = (
    ('Joe Admin', 'joe@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'chain',
        'USER': 'yoda',
        'PASSWORD': '123',
        'HOST': 'localhost',  # use domain socket (127.0.0.1 for TCP)
        'PORT': '',
        'CONN_MAX_AGE': 600, # keep connections open up to 10 minutes
    }
}

# these will be used by the collector scripts and should match the username and
# password provided in the .htpasswd file that nginx is looking at
COLLECTOR_AUTH = ('yoda', '123')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'jakd82l?las{19ka0n%laoeb*klanql0?kdj01kdnc1(n=lbac'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

ZMQ_PASSTHROUGH_URL_PULL = 'tcp://127.0.0.1:31416'
ZMQ_PASSTHROUGH_URL_PUB = 'tcp://127.0.0.1:31417'

# leave the websocket host as None if it is the same as the Django host
WEBSOCKET_HOST = None

# this is the path the user will see in stream links, so it needs to match your
# front end webserver (e.g. nginx) configuration. Note this configuration has
# the trailing but not leading slash
WEBSOCKET_PATH = 'ws/'

INFLUX_HOST = 'localhost'
# default influx port
INFLUX_PORT = '8086'
INFLUX_DATABASE = 'chain'
# the measurement (like a table) where the scalar sensor data will be stored
INFLUX_MEASUREMENT = 'sensordata'
