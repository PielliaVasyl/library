__author__ = 'Piellia Vasyl'

from app import app
from flask import render_template, url_for


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Vasyl'}  # fake user
    return render_template("index.html",
                           title='Home',
                           user=user)


#@app.route('/books')
#def show_books():
#    books = db.session.query(Book)
#    return render_template('books.html', books=books)


#@app.route('/authors')
#def show_authros():
#    authors = db.session.query(Author)
#    return render_template('authors.html', authors=authors)
