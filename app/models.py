__author__ = 'Piellia Vasyl'

from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    __tablename__ = "users"
    id = db.Column('user_id', db.Integer, primary_key=True)
    username = db.Column('username', db.String(20), unique=True, index=True)
    password = db.Column('password', db.String(10))
    email = db.Column('email', db.String(50), unique=True, index=True)
    registered_on = db.Column('registered_on', db.DateTime)
    books = db.relationship('Book', backref='user', lazy='dynamic')
    authors = db.relationship('Author', backref='user', lazy='dynamic')
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.registered_on = datetime.utcnow()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


association_table = db.Table('association', db.Model.metadata,
    db.Column('author_id', db.Integer, db.ForeignKey('authors.author_id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.book_id'))
)


class Book(db.Model):
    __tablename__ = 'books'

    book_title = db.Column(db.String(60), nullable=False)
    id = db.Column('book_id', db.Integer, primary_key=True)
    authors = db.relationship('Author', secondary=association_table, backref='books')
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column('author_id', db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
