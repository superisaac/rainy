#!/usr/bin/env python
import sys, os
sys.path.insert(0, '.')
from lib.couchkit import Server

server = Server()
def reset_db(db_name):
    if server[db_name]:
        del server[db_name]
        server.create_db(db_name)
reset_db('user')
reset_db('user-name')
reset_db('entry')
reset_db('idx--user--email')

    


