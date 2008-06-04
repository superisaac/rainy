from lib.couchkit import Server, ServerError
from lib.couchkit.ocm import Model, ScalaField, ListField, DateTimeField

class Entry(Model):
    owner_id = ScalaField(null=False)
    content = ScalaField()
    created_time = DateTimeField()
    mimetype = ScalaField(default="text/plain")
