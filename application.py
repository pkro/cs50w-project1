import os
import datetime
import json

import requests

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

goodreads_key = 'UJohDpcwYqZUnxbdgXOUGg'
# login form
@app.route("/", methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        sql = 'select id, name, password from users where username=:username'
        row = db.execute(sql, {'username': username}).fetchone()
        if row is not None and check_password_hash(row[2], password):
            session['user_id'] = row[0]
            session['user_name'] = row[1]
            session['logged_in'] = True
            return redirect(url_for('search'))
        else:
            error = 'Username not found or password incorrect'

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# registration form
@app.route("/registration", methods=['POST', 'GET'])
def registration():
    errors = []
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        password_repeat = request.form.get('password_repeat')

        if password != password_repeat:
            errors.append('Passwords do not match.')
        
        sql = 'select id, name from users where username=:username'
        row = db.execute(sql, {'username': username}).fetchone()
        if row is not None:
            errors.append('A user with that name already exists.')

        if len(errors) == 0:
            password_hash = generate_password_hash(password)
            sql = '''   insert into users (name, username, password) 
                        values(:name, :username, :password_hash)
                        RETURNING id'''
            row = db.execute(sql, {'name': name, 'username': username, 'password_hash': password_hash}).fetchone()
            db.commit()

            session['user_id'] = row[0]
            session['user_name'] = username
            session['logged_in'] = True
            
            return redirect(url_for('search'))

    return render_template("registration.html", errors=errors)
        
        

# Search form
@app.route("/search")
def search():
    return render_template("search.html")

# Book results
# ToDo: save last search in session and prefill form
#       add this sites avg rating / nr of reviews and goodreads avg rating / reviews to result
@app.route("/results", methods=["POST"])
def results():
    use_strict = True if request.form.get('use_strict') == '1' else False
    sql_comparison = '=' if use_strict else 'like'

    # build the where clause depending on what was filled in and fill variables for execute
    cols = dict()
    where_clause = []
    for col in ['title', 'author', 'isbn']:
        cols[col] = request.form.get(col).lower()
        if cols[col] != '':
            where_clause.append(f"LOWER({col}) {sql_comparison} :{col}")
            if not use_strict: 
                cols[col] = f"%{cols[col]}%"

    year = request.form.get('year')
    # prefill or db.execute will complain aout unbound variables
    year_from, year_to = 0, 0
    
    if year != '':
        years = year.split('-')
        year_from = years[0].strip()
        year_to = years[1].strip() if len(years)>1 else year_from
        
        where_clause.append("books.year >= :year_from AND books.year <= :year_to")
    
    if len(where_clause) == 0:
        errors = ["Please fill at least one search field."]
        return render_template('search.html', errors=errors)

    where_clause = ' AND '.join(where_clause)
    sql = '''   SELECT books.id, title, year, authors.author, isbn, 
                ROUND(ROUND(AVG(rating)*2, 0)/2, 0) as rating, 
                count(rating) as rating_count
                FROM books 
                INNER JOIN authors ON books.author_id = authors.id
                LEFT JOIN reviews ON books.id = reviews.book_id
                WHERE ''' + where_clause + ''' 
                GROUP BY books.id, title, author
                ORDER BY title ASC '''

    books = db.execute(sql, {'title':   cols['title'], 
                            'author':   cols['author'], 
                            'isbn':     cols['isbn'],
                            'year_from':year_from, 
                            'year_to':  year_to}).fetchall()
    if len(books) == 0:
        errors = ["No books found."]
        return render_template('search.html', errors=errors)
    else:
        return render_template('book_results.html', books=books, test=str(books))
    

# Book details, reviews + write own review on one page for (mostly my) convenience
@app.route("/book/<int:book_id>", methods=['GET', 'POST'])
def book(book_id):
    sql = '''   SELECT books.id, title, year, authors.author, isbn, 
                ROUND(ROUND(AVG(rating)*2, 0)/2, 0) as rating,
                count(rating) as rating_count
                FROM books 
                INNER JOIN authors ON books.author_id = authors.id
                LEFT JOIN reviews ON books.id = reviews.book_id
                WHERE books.id=:id 
                GROUP BY books.id, title, author'''
    book = db.execute(sql, {'id': book_id}).fetchone()

    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", 
                        params={"key": goodreads_key,
                        "isbns": '978'+book.isbn})
    res = res.json()
    
    gr_rating = res['books'][0]['average_rating']
    gr_numratings = res['books'][0]['work_ratings_count']
    
    return render_template('book_details.html', book=book, 
                                                gr_rating=gr_rating, 
                                                gr_numratings=gr_numratings)
    

