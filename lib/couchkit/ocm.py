import time
from dbwrapper import Server, ServerError

class Index(object):
    def __init__(self, model, field):
        self.db_name = 'idx--%s--%s' % (model.db_name, field.fieldname)
        server = Server()
        if not server[self.db_name]:
            server.create_db(self.db_name)

    def db(self):
        server = Server()
        return server[self.db_name]

    def get_ids(self, v):
        model_ids = self.db()["%s" % v]['store_ids']
        return model_ids

    def set(self, v, model_id):
        db = self.db()
        try:
            db.create_doc({'store_ids': [model_id], '_id': v})
        except ServerError, e:
            print e.status, e.msg
            # Already exits
            model_ids = set(db.fetch(v, [])['store_ids'])
            model_ids.add(model_id)
            db[v] = {'store_ids': list(model_ids)}

    def delete(self, v, model_id):
        model_ids = set(self.get_ids(v))
        if model_id in model_ids:
            model_ids.remove(model_id)
            self.db()[v] = {'store_ids': list(model_ids)}

    def change(self, old_v, new_v, model_id):
        if old_v:
            self.delete(old_v, model_id)
        if new_v:
            self.set(new_v, model_id)        

class Field(object):
    def __init__(self, null=True):
        self.null = null # Seems null is not used currently
        self._fieldname = None
        self.index = None
        self.enable_index = False
        
    def _get_fieldname(self):
        return self._fieldname
    def _set_fieldname(self, v):
        self._fieldname = v
    fieldname = property(_get_fieldname, _set_fieldname)

    def probe_index(self, model):
        if self.enable_index:
            self.index = Index(model, self)
            
    def default_value(self):
        return None

    def __get__(self, obj, type=None):
        return getattr(obj, 'proxied_%s' % self.fieldname)
    
    def __set__(self, obj, value):
        obj.tainted = True
        if self.index:
            old_value = getattr(obj, 'proxied_%s' % self.fieldname, None)
            obj.changed_indices.append((self.index, old_value, value))
        setattr(obj, 'proxied_%s' % self.fieldname, value)

    def __del__(self, obj):
        pass

class ScalaField(Field):
    def __init__(self, default=None, null=True, index=False):
        super(ScalaField, self).__init__(null)
        self.default = default
        self.enable_index = index
        
    def default_value(self):
        return self.default

class ListField(Field):
    def default_value(self):
        return []

class DateTimeField(Field):
    def default_value(self):
        return time.time()

        
class ModelMeta(type):
    def __new__(meta, clsname, bases, classdict):
        cls = type.__new__(meta, clsname, bases, classdict)
        if clsname == 'Model':
            return cls
        cls.initialize()
        return cls

class Model(object):
    __metaclass__ = ModelMeta

    @classmethod
    def indices(cls):
        for field in cls.fields.itervalues():
            if field.index:
                yield field, field.index

    @classmethod
    def initialize(cls):
        cls.db_name = cls.__name__.lower()
        cls.fields = []
        for fieldname, v in vars(cls).items():
            if isinstance(v, Field):
                v.fieldname = fieldname
                cls.fields.append(v)
                v.probe_index(cls)
        server = Server()
        if not server[cls.db_name]:
            server.create_db(cls.db_name)
    
    @classmethod
    def create(cls, **kwargs):
        model_obj = cls(**kwargs)
        return model_obj
    @classmethod
    def db(cls):
        server = Server()
        return server[cls.db_name]

    @classmethod
    def all(cls):
        db = cls.db()
        return [cls.get(item['id']) for item in db.docs()['rows']]

    @classmethod
    def get(cls, id, exc_class=None):
        db = cls.db()
        try:
            user_dict = db[id]
        except ServerError:
            if exc_class:
                raise exc_class()
            raise
        obj = cls(**user_dict)
        return obj

    @classmethod
    def get_by_ids(cls, *ids):
        db = cls.db()
        for id in ids:
            try:
                user_dict = db[id]
                yield cls(**user_dict)
            except ServerError:
                pass

    def __eq__(self, other):
        return self.__class__ == other.__class__ and \
               hasattr(self, 'id') and hasattr(other, 'id')  and \
               self.id == other.id
    def __hash__(self):
        return hash(getattr(self, 'id', None))
    
    def save(self):
        if not self.tainted:
            # TODO: things should be reconsidered when foreign key added in
            return
        db = self.db()
        if hasattr(self, 'id'):
            db[self.id] = self.get_dict()
        else:
            res = db.create_doc(self.get_dict())
            self.id = res['id']

        for index, old_value, new_value in self.changed_indices:
            index.change(old_value, new_value, self.id)
        self.changed_indices = []
        self.tainted = False

    def delete(self):
        if hasattr(self, 'id'):
            del self.db()[self.id]

        for field, index in self.indices():
            v = getattr(self, field.fieldname)
            if v:
                index.delete(v, self.id)
        
    def get_dict(self):
        info_dict = {}
        for field in self.fields:
            info_dict[field.fieldname] = getattr(self, field.fieldname)
        if hasattr(self, 'id'):
            info_dict['id'] = self.id
        return info_dict

    def __init__(self, **kwargs):
        self.changed_indices = []
        for field in self.fields:
            setattr(self,
                    field.fieldname,
                    kwargs.get(field.fieldname,
                               field.default_value()))
        if '_id' in kwargs:
            self.id = kwargs['_id']
            self.tainted = False
        else:
            self.tainted = True
