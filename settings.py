# URLs currently provided 
URLMAP = (
    (r'^/user/signup', 'Signup'),
    (r'^/timeline/((?P<user_id>[0-9a-zA-Zu]+)/)?', 'Timeline'),
    (r'^/user/timeline/((?P<user_id>[0-9a-zA-Zu]+)/)?', 'UserTimeline'),
    (r'^/user/((?P<user_id>[0-9a-zA-Zu]+)/)?', 'UserInfo'),
    (r'^/update/', 'Update'),
    (r'^/entry/(?P<entry_id>[0-9a-zA-Z]+)/delete', 'EntryDelete'),
    (r'^/entry/(?P<entry_id>[0-9a-zA-Z]+)', 'EntryInfo'), 
    (r'^/$', 'Hello'),
    )

# UTF-8 by default
ENCODING = 'utf8'

# Connection url for the back end
COUCHDB_SERVER = 'http://localhost:5984'

# The port server daemon listening on
SERVER_PORT = 8001

# Realm token used in Basic HTTP Authentication
APP_REALM = 'RainyAPI'
