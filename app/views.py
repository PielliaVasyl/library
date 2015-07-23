from app.forms import LoginForm, RegisterForm

__author__ = 'Piellia Vasyl'

from app import app
from flask import render_template, url_for, flash, redirect, request


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Vasyl'}  # fake user
    return render_template("index.html",
                           title='Home',
                           user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for "' + form.username.data + '", remember_me=' + str(form.remember_me.data))
        return redirect('/index')
    return render_template('login.html',
                           title='Sign In',
                           form=form)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    return render_template('register.html',
                           title='Sign In',
                           form=form)



#@app.route('/books')
#def show_books():
#    books = db.session.query(Book)
#    return render_template('books.html', books=books)


#@app.route('/authors')
#def show_authros():
#    authors = db.session.query(Author)
#    return render_template('authors.html', authors=authors)