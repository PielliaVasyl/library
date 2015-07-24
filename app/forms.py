__author__ = 'Piellia Vasyl'
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length
from app import db
from app.models import User, Author, Book
from wtforms.fields.html5 import EmailField

authors = [(author.id, author.name) for author in db.session.query(Author)]
if not authors:
    author=Author(name='Unknown author')
    db.session.add(author)
    db.session.commit()
    authors = [(author.id, author.name) for author in db.session.query(Author)]
books = [(book.id, book.book_title) for book in db.session.query(Book)]


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class RegisterForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    email = EmailField('Email address', [DataRequired(), Email()])


class EditUserForm(Form):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_username, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_username = original_username

    def validate(self):
        if not Form.validate(self):
            return False
        if self.username.data == self.original_username:
            return True
        user = User.query.filter_by(username=self.username.data).first()
        if user is not None:
            self.username.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True


class NewBookForm(Form):
    book_title = StringField('Book title', validators=[DataRequired()])
    #author = SelectField(choices=authors)

    def validate(self):
        if not Form.validate(self):
            return False
        book = Book.query.filter_by(book_title=self.book_title.data).first()
        if book is not None:
            self.book_title.errors.append('This book title is already in use. Please choose another one.')
            return False
        return True

class EditBookForm(Form):
    book_title = StringField('Book title', validators=[DataRequired()])

    def __init__(self, original_book_title, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_book_title = original_book_title

    def validate(self):
        if not Form.validate(self):
            return False
        if self.book_title.data == self.original_book_title:
            return True
        book = Book.query.filter_by(book_title=self.book_title.data).first()
        if book is not None:
            self.book_title.errors.append('This book title is already in use. Please choose another one.')
            return False
        return True


class NewAuthorForm(Form):
    name = StringField('Author`s name', validators=[DataRequired()])

    def validate(self):
        if not Form.validate(self):
            return False
        author = Author.query.filter_by(name=self.name.data).first()
        if author is not None:
            self.author.errors.append('This author`s name is already in use. Please choose another one.')
            return False
        return True


class EditAuthorForm(Form):
    name = StringField('Author`s name', validators=[DataRequired()])

    def __init__(self, original_name, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_name = original_name

    def validate(self):
        if not Form.validate(self):
            return False
        if self.name.data == self.original_name:
            return True
        author = Author.query.filter_by(name=self.name.data).first()
        if author is not None:
            self.name.errors.append('This author`s name is already in use. Please choose another one.')
            return False
        return True
