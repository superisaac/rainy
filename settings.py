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

ENCODING = 'utf8'
COUCHDB_SERVER = 'http://localhost:5984'
SERVER_PORT = 8001

APP_REALM = 'RainyAPI'
