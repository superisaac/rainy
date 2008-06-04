import base64
import re
from models import User

class HttpAuthentication(Exception):
    pass

class HttpNotFound(Exception):
    pass

def require_login(func):
    def __decorator(self, reactor, **kwargs):
        auth_str = reactor.environ.get('HTTP_AUTHORIZATION')
        if auth_str:
            m = re.match(r'Basic (\w+)', auth_str)
            if m:
                username, password = base64.decodestring(m.group(1)).split(':', 1)
                reactor.user = User.login(username, password)
                if reactor.user:
                    return func(self, reactor, **kwargs)
        raise HttpAuthentication
    return __decorator

def force_unicode(data):
    if isinstance(data, unicode):
        return data
    return unicode(data, 'utf8')

def ok(message):
    return {'result': 'ok',
            'message': message}
