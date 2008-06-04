from lib.httputil import require_login, AppError, Forbidden
from lib.couchkit import ServerError
from lib.util import require_login, force_unicode, ok
from models import User, Entry

class EntryInfo:
    @require_login
    def handle_GET(self, reactor, entry_id):
        return Entry.get(entry_id).get_dict()

class EntryDelete:
    @require_login
    def handle_POST(self, reactor, entry_id):
        entry = Entry.get(entry_id)
        if entry.owner_id != reactor.user.id:
            raise Forbidden()
        entry.delete()
        return ok("Delete OK")
