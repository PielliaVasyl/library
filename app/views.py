from datetime import datetime
from app.forms import LoginForm, RegisterForm, EditUserForm, NewBookForm, EditBookForm
from app.models import User, Book, Author
from flask.ext.login import login_user, logout_user, current_user, login_required

__author__ = 'Piellia Vasyl'

from app import app, db, lm
from flask import render_template, url_for, flash, redirect, request, g


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = g.user
    return render_template("index.html",
                           title='Home',
                           user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        flash('You are already logged in.')
        return redirect(request.args.get('next') or url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        remember_me = form.remember_me.data
        username = form.username.data
        password = form.password.data
        user_to_reg = db.session.query(User).filter_by(username=username, password=password).first()
        if user_to_reg is None:
            flash('Username or Password is invalid', 'error')
            return redirect(url_for('login'))
        login_user(user_to_reg, remember=remember_me)
        flash('Logged in successfully')
        return redirect(request.args.get('next') or url_for('index'))
    return render_template('login.html',
                           title='Sign In',
                           form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user is not None and g.user.is_authenticated():
        flash('You are already logged in.')
        return redirect(request.args.get('next') or url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User(username=username, password=password, email=email)
        if user.username in db.session.query(User.username).all():
            flash('This user name already exists.')
            return redirect(url_for('register'))
        if user.email in db.session.query(User.email).all():
            flash('This email already exists.')
            return redirect(url_for('register'))
        db.session.add(user)
        db.session.commit()
        flash('User successfully registered')
        return redirect(url_for('login'))
    return render_template('register.html',
                           title='Sign In',
                           form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have successfully logged out!")
    return redirect(url_for('index'))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@lm.user_loader
def load_user(id):
    return db.session.query(User).get(int(id))


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User ' + username + ' not found.')
        return redirect(url_for('index'))
    books = user.books
    authors = user.authors
    return render_template('user.html',
                           user=user,
                           books=books,
                           authors=authors)


@app.route('/user/edit', methods=['GET', 'POST'])
@login_required
def user_edit():
    form = EditUserForm(g.user.username)
    if form.validate_on_submit():
        g.user.username = form.username.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user_edit'))
    else:
        form.username.data = g.user.username
        form.about_me.data = g.user.about_me
    return render_template('user_edit.html',
                           form=form)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/books')
def show_books():
    books = db.session.query(Book)
    return render_template('books.html', books=books)


@app.route('/book/new/', methods=['GET', 'POST'])
@login_required
def new_book():
    form = NewBookForm()
    if form.validate_on_submit():
        if form.book_title.data is None:
            flash("Fill in a book title to create a book!")
            return redirect(url_for('show_books'))
        book = Book(book_title=form.book_title.data)
        book.user = g.user
        if book.book_title in db.session.query(Book.book_title).all():
            flash('This book title already exists.')
            return redirect(url_for('new_book'))
        db.session.add(book)
        db.session.commit()
        flash('Book successfully added.')
        return redirect(url_for('show_books'))
    return render_template('newbook.html', form=form)


@app.route('/book/<int:book_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = db.session.query(Book).filter_by(id=book_id).one()
    form = EditBookForm(book)
    if form.validate_on_submit():
        if book.user.id == g.user.id:
            book.book_title = form.book_title.data
            db.session.add(book)
            db.session.commit()
            flash("Book edited!")
            return redirect(url_for('edit_book', book_id=book_id, form=form))
        else:
            flash('You are not authorized to edit this book','error')
            return redirect(url_for('edit_book', book_id=book_id))
    else:
        form.book_title.data = book.book_title
    return render_template('book_edit.html', book=book, form=form)


@app.route('/book/<int:book_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    book = db.session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        if book:
            if book.user.id == g.user.id:
                db.session.delete(book)
                db.session.commit()
                flash("Book deleted!")
                return redirect(url_for('show_books'))
            else:
                flash('You are not authorized to delete this book','error')
                return redirect(url_for('edit_book', book_id=book_id))
        return redirect(url_for('show_books'))
    else:
        return render_template('book_delete.html', book_id=book_id, book=book)



@app.route('/authors')
def show_authors():
    authors = db.session.query(Author)
    return render_template('authors.html', authors=authors)


