#!/usr/bin/env python

import settings
from application import Reactor

def eventlet_server():
    from eventlet import wsgi, api
    wsgi.server(api.tcp_listener(('', settings.SERVER_PORT)), Reactor)

if __name__ == '__main__':
    eventlet_server()
