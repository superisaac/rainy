from lib.httputil import require_login

class Hello:
    @require_login
    def handle_GET(self, reactor):
        return 'Hello World'
