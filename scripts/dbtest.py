#!/usr/bin/env python
import sys
sys.path.insert(0, '.')
from models import User, Entry
from lib.couchkit import Server

user1 = User.signup('zk', 'passwd', 'zk@hihi.com')
user2 = User.signup('mj', 'passwd1', 'mj@whihi.com')

user1.follow(user2)
user1.update('haha, I am here')
user2.update('yes, you got it')
user2.update('good so good')

for status, user in  user1.follow_timeline():
    print user, 'says:', status.content, status.created_time
server = Server()
print server['idx--user--email']['zk@hihi.com']

    
