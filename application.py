#!/usr/bin/env python
import re
import urllib
import traceback
from cStringIO import StringIO
from simplejson import loads, dumps
import settings
from lib.httputil import HttpAuthentication, HttpNotFound, AppError, Forbidden
import app

RESPONSE_CONTENT_TYPE = 'application/json'
class Reactor:
    def __init__(self, env, start_response):
        self.environ = env
        self.start = start_response
        self.status = '200 OK'
        self.response_headers = [('Content-Type', RESPONSE_CONTENT_TYPE)]
        self.handleRequest()
        
    def handleRequest(self):
        self.params = {}
        for k, v in  re.findall(r'([^&#=]+)=([^&#=]*)', self.environ['QUERY_STRING']):
            #self.params.setdefault(k, []).append(urllib.unquote(v))
            self.params[k] = urllib.unquote(v)

    def notfound(self):
        self.start('404 Not Found', [('Content-Type', RESPONSE_CONTENT_TYPE)])
        return dumps({'error_code': 404, 'message': '404 Not Found'})
    
    def authentication(self, realm=settings.APP_REALM):
        self.start('401 Unauthorized', [('Content-Type', RESPONSE_CONTENT_TYPE),
                                        ('WWW-Authenticate', 'Basic realm="%s"' % realm)])
        return dumps({'error_code': 401, 'message': '401 Unauthorized'})

    def servererror(self, trace_info):
        self.start('500 Server Error', [('Content-Type', 'text/plain'),])
        return trace_info

    def apperror(self, error_code, message):
        self.start('500 Server Error', [('Content-Type', RESPONSE_CONTENT_TYPE),])
        return dumps({'error_code': error_code, 'message': message})

    def forbidden(self):
        self.start('403 Forbidden', [('Content-Type', RESPONSE_CONTENT_TYPE),])
        return dumps({'error_code': 403, 'message': 'Permission Denied'})

    def __iter__(self):
        yield self.one_request()

    def one_request(self):
        path = self.environ['PATH_INFO']
        method = self.environ['REQUEST_METHOD']
        if method in ('POST', 'PUT'):
            content_length = int(self.environ['CONTENT_LENGTH'])
            data = self.environ['wsgi.input'].read(content_length)
            self.input_data = loads(data)
        else:
            self.input_data = None
        try:
            for pattern, handler_name in settings.URLMAP:
                m = re.search(pattern, path)
                if m:
                    handler = getattr(app, handler_name)()
                    obj = getattr(handler, 'handle_%s' % method)(self, **m.groupdict())
                    response = dumps(obj)
                    self.start(self.status, self.response_headers)
                    return response
            raise HttpNotFound()
        except HttpAuthentication:
            return self.authentication()
        except HttpNotFound:
            return self.notfound()
        except AppError, e:
            return self.apperror(e.error_code, e.message)
        except Forbidden:
            return self.forbidden()
        except:
            buf = StringIO()
            traceback.print_exc(file=buf)
            return self.servererror(buf.getvalue())
