import base64
import re

class HttpAuthentication(Exception):
    pass

class HttpNotFound(Exception):
    pass

class Forbidden(Exception):
    pass

class AppError(Exception):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message
        
def require_login(func):
    def __decorator(self, reactor, *args, **kwargs):
        from models import User
        auth_str = reactor.environ.get('HTTP_AUTHORIZATION')
        if auth_str:
            m = re.match(r'[Bb]asic (.+)', auth_str)
            if m:
                try:
                    username, password = base64.decodestring(m.group(1)).split(':', 1)
                    reactor.user = User.login(username, password)
                except:
                    raise HttpAuthentication()
                if reactor.user:
                    return func(self, reactor, *args, **kwargs)
        raise HttpAuthentication()
    return __decorator
