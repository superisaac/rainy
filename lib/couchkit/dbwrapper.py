import httpc as http
from urllib import quote, urlencode
import simplejson
import settings

class ServerError(Exception):
    def __init__(self, status, msg):
        self.status = status
        self.msg = msg
        
    def __str__(self):
        return "Server Error: %s %s" % (self.status, self.msg)

class ServerConnectionError(ServerError):
    def __init__(self, cerror):
        response = cerror.params.response
        super(ServerConnectionError, self).__init__(response.status,
                                                    response.reason + '|')

class Server(object):
    servers = {}
    def __new__(cls, server_url=settings.COUCHDB_SERVER):
        if server_url not in cls.servers:
            obj = object.__new__(cls)
            obj.initialize(server_url)
            cls.servers[server_url] = obj            
        return cls.servers[server_url]        
        
    def initialize(self, server_url):
        self.server_url = server_url
        if self.server_url[-1:] == '/':
            self.server_url = self.server_url[:-1]

        self.opened_dbs = {}

    def handle_response(self, status, msg, body):
        if status >= 200 and status < 300:
            return simplejson.loads(body)
        else:
            raise ServerError(status, msg)

    def dumps(self, obj):
        if obj is None:
            return ''
        else:
            return simplejson.dumps(obj)
        
    def get(self, url='/', **params):
        param_str = urlencode(params)
        url = quote(url)
        if param_str:
            url += '?' + param_str
        try:
            t = http.get_(self.server_url + url,
                           headers={'Accept':'Application/json'},
                           )
        except http.ConnectionError, e:
            raise ServerConnectionError(e)
        obj = self.handle_response(*t)
        if isinstance(obj, dict):
            obj = dict((k.encode(settings.ENCODING), v) for k, v in obj.iteritems())
        return obj

    def delete(self, url='/', **params):
        param_str = urlencode(params)
        url = quote(url)
        if param_str:
            url += '?' + param_str
        try:
            t = http.delete_(self.server_url + url)
        except http.ConnectionError, e:
            raise ServerConnectionError(e)

        return self.handle_response(*t)

    def post(self, url, obj):
        url = quote(url)
        data = self.dumps(obj)
        try:
            t = http.post_(self.server_url + url,
                            data=data,
                            headers={'content-type': 'application/json',
                                     'accept':'application/json'
                                     },
                            )
        except http.ConnectionError, e:
            raise ServerConnectionError(e)
        return self.handle_response(*t)

    def put(self, url, obj):
        url = quote(url)
        data = self.dumps(obj)
        try:
            t = http.put_(self.server_url + url,
                           data=data,
                           headers={'conent-type': 'application/json',
                                    'accept':'Application/json'},
                           )
        except http.ConnectionError, e:
            raise ServerConnectionError(e)
        return self.handle_response(*t)

    def __getitem__(self, dbname):
        if dbname in self.opened_dbs:
            return self.opened_dbs[dbname]
        dbs = self.dbs()
        if dbname in dbs:
            db = Database(self, dbname)
            self.opened_dbs[dbname] = db
            return db
        else:
            #raise KeyError(dbname)
            return None
    
    def __delitem__(self, dbname):
        if dbname in self.opened_dbs:
            del self.opened_dbs[dbname]
        return self.delete('/%s/' % dbname)
    
    def dbs(self):
        return self.get('/_all_dbs')
    
    def create_db(self, dbname):
        return self.put('/%s/' % dbname, None)

class Database:
    def __init__(self, server, dbname):
        self.server = server
        self.dbname = dbname
        self._cache = {}
        self.enable_cache = False
        
    def del_cache(self, docid):
        if self.enable_cache:
            if docid in self._cache:
                del self._cache[docid]
    def get_cache(self, docid):
        if self.enable_cache:
            if docid in self._cache:
                return self._cache[docid]
    def set_cache(self, docid, obj):
        if self.enable_cache:
            self._cache[docid] = obj
            
    def clean_cache(self):
        self._cache = {}
        
    def info(self):
        return self.server.get('/%s/' % self.dbname)

    def docs(self):
        return self.server.get('/%s/_all_docs' % self.dbname)

    def get(self, docid, rev=None):
        params = rev and dict(rev=rev) or {}
        obj = self.server.get('/%s/%s' % (self.dbname, docid), **params)
        self.set_cache(docid, obj)
        return obj

    def revs(self, docid):
        obj = self.server.get('/%s/%s' % (self.dbname, docid), revs='true')
        return obj['_revs']
        
    def fetch(self, docid, absent=None):
        try:
            obj = self.server.get('/%s/%s/' % (self.dbname, docid))
        except ServerError:
            return absent
        self.set_cache(docid, obj)
        return obj
        
    def __getitem__(self, docid):
        obj = self.get_cache(docid)
        return obj or self.get(docid)

    def __setitem__(self, docid, obj):
        try:
            #self.server.put('/%s/%s' % (self.dbname, docid), obj)
            self.set(docid, obj)
        except ServerError:
            doc = self.get(docid)
            rev = doc['_rev']
            obj['_rev'] = rev
            self.server.put('/%s/%s' % (self.dbname, docid), obj)
        self.del_cache(docid)

    def set(self, docid, obj):
        self.server.put('/%s/%s' % (self.dbname, docid), obj)

    def create_doc(self, obj):
        """ Create a new document with the id and rev generated by server
        :returns
        {"ok":true, "id":"123BAC", "rev":"946B7D1C"}
        """
        return self.server.post('/%s/' % self.dbname, obj)

    def __delitem__(self, docid):
        doc = self.get(docid)
        rev = doc['_rev']
        self.del_cache(docid)
        return self.server.delete('/%s/%s' % (self.dbname, docid), rev=rev)

    def query(self, map_func, reduce_func=""):
        "query temporary view"
        view = View(map_func, reduce_func)
        return self.server.post('/%s/_temp_view' % (self.dbname), view.query_dict())
    
    def query_view(self, design_name, view_name):
        return self.server.get('/%s/_view/%s' % (self.dbname,
                                              design_name
                                              ))
    
    def create_or_replace_design(self, name, design):
        self[name] = design.query_dict(name)

class View:
    def __init__(self, map_func='', reduce_func=''):
        self.map_func = map_func
        self.reduce_func = reduce_func

    def query_dict(self):
        query = {}
        if self.map_func:
            query['map'] = self.map_func
        if self.reduce_func:
            query['reduce'] = self.reduce_func
        return query
    
class Design:
    def __init__(self, **views):
        self.views = {}
        self.views.update(views)
        
    def query_dict(self, name):
        query = {
            '_id': '_design/%s' % name,
            'language': 'javascript',
            'views': {},
            }
        
        for name, view in self.views.iteritems():
            query['views'][name] = view.query_dict()
        return query
        
        
