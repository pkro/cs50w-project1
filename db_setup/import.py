import os
import csv
import create_tables

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create tables if they don't exist
create_tables.create_tables(db)

# read and insert lines from CSV
csv_file = "books.csv"

with open(csv_file) as fp:
    csv_reader = csv.DictReader(fp, delimiter=',')
    lines_processed = 0

    # skip header
    next(csv_reader)
    
    for row in csv_reader:
        author_id = db.execute("SELECT id FROM authors WHERE author = :author", 
                                {"author": row['author']}).fetchone()
        
        if author_id is None:
            author_id = db.execute("INSERT INTO authors (author) values(:author) RETURNING id", 
                                    {"author": row["author"]}).fetchone()

        author_id = author_id[0]

        db.execute('''  INSERT INTO books(isbn, title, year, author_id) 
                        VALUES(:isbn, :title, :year, :author_id) 
                        ON CONFLICT (isbn) DO NOTHING''', 
                        {   'isbn': row['isbn'], 
                            'title': row['title'],
                            'year': row['year'],
                            'author_id': author_id })
                        

        lines_processed += 1
    
book_count = db.execute("SELECT count(*) from books").fetchone()[0]
author_count = db.execute("SELECT count(*) from authors").fetchone()[0]

print(f"{lines_processed} lines processed. {book_count} books and {author_count} authors total to DB.")

db.commit()
            