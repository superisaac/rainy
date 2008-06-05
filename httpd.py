#!/usr/bin/env python

import settings
from application import Reactor

def eventlet_server():
    "Run as standalone wsgi server"
    from eventlet import wsgi, api
    wsgi.server(api.tcp_listener(('', settings.SERVER_PORT)), Reactor)

def flup_server():
    """Run as fast cgi
    don't make it a standalone program
    """
    from flup.server.fcgi import WSGIServer
    WSGIServer(Reactor).run()

if __name__ == '__main__':
    eventlet_server()
    #flup_server()
