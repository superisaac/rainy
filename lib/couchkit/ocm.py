import time
from dbwrapper import Server, ServerError

class Field(object):
    def __init__(self, null=True):
        self.null = null # Seems null is not used currently
        
    def default_value(self):
        return None

    def __get__(self, obj, type=None):
        return getattr(obj, 'proxied_%s' % self.fieldname)
    
    def __set__(self, obj, value):
        obj.tainted = True
        setattr(obj, 'proxied_%s' % self.fieldname, value)

    def __del__(self, obj):
        pass

class ScalaField(Field):
    def __init__(self, default=None, null=True):
        super(ScalaField, self).__init__(null)
        self.default = default
    def default_value(self):
        return self.default

class ListField(Field):
    def default_value(self):
        return []

class DateTimeField(Field):
    def default_value(self):
        return time.time()
    
class Model(object):
    @classmethod
    def create(cls, **kwargs):
        model_obj = cls(**kwargs)
        return model_obj

    @classmethod
    def all(cls):
        server = Server()
        db = server[cls.db_name]
        return [cls.get(item['id']) for item in db.docs()['rows']]

    @classmethod
    def get(cls, id, exc_class=None):
        server = Server()
        db = server[cls.db_name]
        try:
            user_dict = db[id]
        except ServerError:
            if exc_class:
                raise exc_class()
            raise
        obj = cls(**user_dict)
        return obj
    
    @classmethod
    def initialize(cls):
        cls.db_name = cls.__name__.lower()
        cls.fields = []
        for field, v in vars(cls).items():
            if isinstance(v, Field):
                v.fieldname = field
                cls.fields.append(v)
        server = Server()
        if not server[cls.db_name]:
            server.create_db(cls.db_name)

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
        server = Server()
        db = server[self.db_name]
        if hasattr(self, 'id'):
            db[self.id] = self.get_dict()
        else:
            res = db.create_doc(self.get_dict())
            self.id = res['id']

    def delete(self):
        if hasattr(self, 'id'):
            server = Server()
            db = server[self.db_name]
            del db[self.id]
        
    def get_dict(self):
        info_dict = {}
        for field in self.fields:
            info_dict[field.fieldname] = getattr(self, field.fieldname)
        if hasattr(self, 'id'):
            info_dict['id'] = self.id
        return info_dict

    def __init__(self, **kwargs):
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
