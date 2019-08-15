from django.utils.log import AdminEmailHandler
from django.core.cache import get_cache

class ThrottledAdminEmailHandler(AdminEmailHandler):
    # as of August 15, 2019 we're using the in-memory cache, which means that
    # each worker (currently 4) has its own copy of this variable, so we'll
    # actually send 4x as many errors as MAX_EMAILS_IN_PERIOD
    PERIOD_LENGTH_IN_SECONDS = 60*60*24
    MAX_EMAILS_IN_PERIOD = 20
    COUNTER_CACHE_KEY = "email_admins_counter"

    def increment_counter(self):
        cache = get_cache('default')
        try:
            cache.incr(self.COUNTER_CACHE_KEY)
        except ValueError:
            cache.set(self.COUNTER_CACHE_KEY, 1, self.PERIOD_LENGTH_IN_SECONDS)
        return cache.get(self.COUNTER_CACHE_KEY)

    def emit(self, record):
        try:
            counter = self.increment_counter()
        except Exception:
            pass
        else:
            if counter > self.MAX_EMAILS_IN_PERIOD:
                return
        super(ThrottledAdminEmailHandler, self).emit(record)
