tables = dict()

tables['authors'] = '''   
            CREATE TABLE IF NOT EXISTS authors (
                id SERIAL PRIMARY KEY,
                author VARCHAR
            )'''

tables['users'] = '''   
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR,
                username VARCHAR NOT NULL,
                password VARCHAR NOT NULL
            )'''            

tables['books'] = '''   
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                isbn char (10) UNIQUE,
                title VARCHAR,
                year SMALLINT,
                author_id INTEGER REFERENCES authors(id)
                
            )'''


tables['reviews'] = '''   
            CREATE TABLE IF NOT EXISTS reviews (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                book_id INTEGER REFERENCES books(id),
                rating SMALLINT,
                title VARCHAR,
                review TEXT
            )'''

def create_tables(db):
    try:
        for table in tables:
            db.execute(tables[table])
    except Exception as ex:
        print(ex)
        return ex
    
    db.commit()
