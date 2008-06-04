from lib.couchkit import Server, ServerError
from lib.couchkit.ocm import Model, ScalaField, ListField
from entry import Entry

class UserSignupException(Exception):
    pass

class UserLoginException(Exception):
    pass

class User(Model):
    email = ScalaField(null=False)
    username = ScalaField()
    follows = ListField()
    followed_by  = ListField()
    timeline = ListField()
    
    @classmethod
    def signup(cls, username, password, email):
        server = Server()
        namedb = server['user-name']
        try:
            namedb.set(username, {'password': password})
        except ServerError:
            raise UserSignupException('User %s already exists' %
                                        username)
        user = cls.create(username=username, email=email)
        user.save()
        namedb[username] = dict(password=password,
                                user_id=user.id)
        return user

    @classmethod
    def login(cls, username, password):
        server = Server()
        namedb = server['user-name']
        try:
            login_info = namedb[username]
            if login_info['password']  == password:
                return cls.get(login_info['user_id'])
        except ServerError, e:
            return None
        return None

    def delete(self):
        server = Server()
        db = server['user-name']
        del db[self.username]
        super(User, self).delete()

    def follow(self, other):
        other.followed_by.append(self.id)
        self.follows.append(other.id)
        other.save()
        self.save()

    def iter_follows(self):
        yield self
        for user_id in self.follows:
            yield User.get(user_id)
        
    def update(self, text):
        entry = Entry.create(owner_id=self.id,
                             content=text)
        entry.save()
        self.timeline.insert(0, (entry.id,
                                 entry.created_time))
        self.save()

    def user_timeline(self, time_limit=0):
        for entry_id, created_time in self.timeline:
            if created_time < time_limit:
                break
            entry = Entry.get(entry_id)
            yield entry

    def follow_timeline(self, time_limit=0):
        timeline = []
        for user in self.iter_follows():
            for entry_id, created_time in user.timeline:
                if created_time < time_limit:
                    break
                timeline.append((-created_time, entry_id, user))
        timeline.sort()

        for _, entry_id, user in timeline:
            entry = Entry.get(entry_id)
            yield entry, user

    def __str__(self):
        return self.username
