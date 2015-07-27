__author__ = 'Piellia Vasyl'

from app import db, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
import flask.ext.whooshalchemy as whooshalchemy

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

    @staticmethod
    def make_unique_username(username):
        if User.query.filter_by(username = username).first() is None:
            return username
        version = 2
        while True:
            new_username = username + str(version)
            if User.query.filter_by(username = new_username).first() == None:
                break
            version += 1
        return new_username

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
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)


class Book(db.Model):
    __tablename__ = 'books'
    __searchable__ = ['book_title']
    book_title = db.Column(db.String(60), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    authors = db.relationship('Author',
                              secondary=association_table,
                              backref='books',
                              lazy='dynamic')


class Author(db.Model):
    __tablename__ = 'authors'
    __searchable__ = ['name']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))


whooshalchemy.whoosh_index(app, Book)
whooshalchemy.whoosh_index(app, Author)
