from datetime import datetime
from app.forms import LoginForm, RegisterForm, EditUserForm, NewBookForm, EditBookForm, NewAuthorForm, EditAuthorForm, \
    AddAuthorToBookForm, AddBookToAuthorForm
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
        author = db.session.query(Author).filter_by(id=form.author.data).first()
        book.authors.append(author)
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
        authors = book.authors
        add_author_form = AddAuthorToBookForm()
    return render_template('book_edit.html', book=book, form=form, authors=authors, add_author_form=add_author_form)


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


@app.route('/book/authors/<int:book_id>/add', methods=['GET', 'POST'])
@login_required
def add_author_to_book(book_id):
    book = db.session.query(Book).filter_by(id=book_id).one()
    add_author_form = AddAuthorToBookForm()
    form = EditBookForm(book)
    if add_author_form.validate_on_submit():
        author_id = add_author_form.author.data
        if book.user.id == g.user.id:
            author_to_add = db.session.query(Author).filter_by(id=author_id).one()
            book.authors.append(author_to_add)
            db.session.add(book)
            db.session.commit()
            flash("Author added to book!")
            return redirect(url_for('edit_book', book_id=book_id, form=form))
        else:
            flash('You are not authorized to edit this book','error')
            return redirect(url_for('edit_book', book_id=book_id, form=form))
    else:
        form.book_title.data = book.book_title
        authors = book.authors
    return render_template('book_edit.html', book_id=book_id, add_author_form=add_author_form, form=form, book=book, authors=authors)


@app.route('/book/authors/<int:book_id>/<int:author_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_author_from_book(book_id, author_id):
    book = db.session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        if book.user.id == g.user.id:
            author_to_delete = db.session.query(Author).filter_by(id=author_id).one()
            book.authors.remove(author_to_delete)
            db.session.add(book)
            db.session.commit()
            flash("Author deleted form the book!")
            return redirect(url_for('edit_book', book_id=book_id, form=form))
        else:
            flash('You are not authorized to edit this book', 'error')
            return redirect(url_for('edit_book', book_id=book_id, form=form))
    else:
        return render_template('book_edit.html', book_id=book_id)

@app.route('/authors')
def show_authors():
    authors = db.session.query(Author)
    return render_template('authors.html', authors=authors)


@app.route('/author/new/', methods=['GET', 'POST'])
@login_required
def new_author():
    form = NewAuthorForm()
    if form.validate_on_submit():
        if form.name.data is None:
            flash("Fill in a author`s name to create an author!")
            return redirect(url_for('show_authors'))
        author = Author(name=form.name.data)
        author.user = g.user
        if author.name in db.session.query(Author.name).all():
            flash('This author already exists.')
            return redirect(url_for('new_author'))
        db.session.add(author)
        db.session.commit()
        flash('Author successfully added.')
        return redirect(url_for('show_authors'))
    return render_template('author_new.html', form=form)


@app.route('/author/<int:author_id>/edit/', methods=['GET', 'POST'])
@login_required
def edit_author(author_id):
    author = db.session.query(Author).filter_by(id=author_id).one()
    form = EditAuthorForm(author)
    if form.validate_on_submit():
        if author.user.id == g.user.id:
            author.name = form.name.data
            db.session.add(author)
            db.session.commit()
            flash("Author edited!")
            return redirect(url_for('edit_author', author_id=author_id, form=form))
        else:
            flash('You are not authorized to edit this author','error')
            return redirect(url_for('edit_author', author_id=author_id, form=form))
    else:
        form.name.data = author.name
        books = author.books
        add_book_form = AddBookToAuthorForm()
    return render_template('author_edit.html', author=author, form=form, books=books, add_book_form=add_book_form)


@app.route('/author/<int:author_id>/delete/', methods=['GET', 'POST'])
@login_required
def delete_author(author_id):
    author = db.session.query(Author).filter_by(id=author_id).one()
    if request.method == 'POST':
        if author:
            if author.user.id == g.user.id:
                db.session.delete(author)
                db.session.commit()
                flash("Author deleted!")
                return redirect(url_for('show_authors'))
            else:
                flash('You are not authorized to delete this author','error')
                return redirect(url_for('edit_author', author_id=author_id))
        return redirect(url_for('show_authors'))
    else:
        return render_template('author_delete.html', author_id=author_id, author=author)


@app.route('/author/books/<int:author_id>/add', methods=['GET', 'POST'])
@login_required
def add_book_to_author(author_id):
    author = db.session.query(Author).filter_by(id=author_id).one()
    add_book_form = AddBookToAuthorForm()
    form = EditAuthorForm(author)
    if add_book_form.validate_on_submit():
        book_id = add_book_form.book.data
        if author.user.id == g.user.id:
            book_to_add = db.session.query(Book).filter_by(id=book_id).one()
            author.books.append(book_to_add)
            db.session.add(author)
            db.session.commit()
            flash("Book added to author!")
            return redirect(url_for('edit_author', author_id=author_id, form=form))
        else:
            flash('You are not authorized to edit this author','error')
            return redirect(url_for('edit_author', author_id=author_id, form=form))
    else:
        form.name.data = author.name
        books = author.books
    return render_template('author_edit.html', author_id=author_id, add_book_form=add_book_form, form=form, author=author, books=books)


@app.route('/author/books/<int:author_id>/<int:book_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_book_from_author(book_id, author_id):
    author = db.session.query(Author).filter_by(id=author_id).one()
    if request.method == 'POST':
        if author.user.id == g.user.id:
            book_to_delete = db.session.query(Book).filter_by(id=book_id).one()
            author.books.remove(book_to_delete)
            db.session.add(author)
            db.session.commit()
            flash("Book deleted form the author!")
            return redirect(url_for('edit_author', author_id=author_id, form=form))
        else:
            flash('You are not authorized to edit this author', 'error')
            return redirect(url_for('edit_author', author_id=author_id, form=form))
    else:
        return render_template('author_edit.html', author_id=author_id)
