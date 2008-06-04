from lib.httputil import require_login, AppError, HttpNotFound
from lib.couchkit import ServerError
from lib.util import require_login, force_unicode, ok
from models import User

class Signup:
    def handle_POST(self, reactor):
        info = reactor.input_data
        try:
            user = User.signup(info['username'], info['password'], info['email'])
        except ServerError, e:
            raise AppError(1001, e.msg)
        return {'id': user.id,
                'message': 'Welcome',
                'username': user.username}
    
class UserInfo:
    @require_login
    def handle_GET(self, reactor, user_id=None):
        if user_id:
            user = User.get(user_id, exc_class=HttpNotFound)
        else:
            user = reactor.user
        return {'id': user.id,
                'username': user.username,
                'follows': user.follows,
                'followed_by': user.followed_by
                }

class Timeline:
    @require_login
    def handle_GET(self, reactor, user_id=None):
        if user_id:
            user = User.get(user_id, exc_class=HttpNotFound)
        else:
            user = reactor.user
        return [timeline.get_dict() for timeline, user in user.follow_timeline()]
class UserTimeline:
    @require_login
    def handle_GET(self, reactor, user_id=None):
        if user_id:
            user = User.get(user_id, exc_class=HttpNotFound)
        else:
            user = reactor.user
        return [timeline.get_dict() for timeline, user in user.user_timeline()]

class Update:
    @require_login
    def handle_POST(self, reactor):
        content = force_unicode(reactor.input_data['content'])
        content = content[:140]
        reactor.user.update(content)
        return ok("Updated")
