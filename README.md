# Project 1
#
Author: Peerky (edx username)

Web Programming with Python and JavaScript

This is an implementation of project 1 of the 2018 CS50W edx/harvard course
following the specifications layed out here:
https://docs.cs50.net/web/2018/x/projects/1/project1.html

Minor additions to the requirements:
- Optional strict search, for example to find books with short titles without a result mess ("it")
- Optional year range search by using a dash (e.g. 1972-1974)
- Star-display of averaged local reviews
- Review of logged in user can be submitted / edited on book details page

The goodreads API key must be stored in a shell variable:
export GOODREADS_API_KEY=xxx

Video:
https://youtu.be/2sP4hvINlkQ

Wrong colors recorded by OBS studio. 
Strict search at the end used incorrectly (didn't re-check the checkbox,
"Christie" shouldn't have been found with strict search, but "Agatha Christie" 
should have.)
Didn't show json api functionality (but is implemented)

Files:
.
├── application.py -> the flask app containing all routes
├── db_setup
│   ├── create_tables.py -> table definitions and function to create tables
│   └── import.py -> create tables and import books.csv (should be located in same directory)
├── README.md -> this file
├── requirements.txt -> requests module added
├── static
│   ├── css
│   │   ├── style.css -> SASS-generated CSS
│   │   └── style.scss -> SASS file
│   └── images -> book image used in app
│       ├── favicon.ico
│       ├── icon.png
│       └── license.txt -> Spoiler: free
├── templates -> mostly self explanatory if not otherwise noted
│   ├── 404.html
│   ├── book_details.html -> single book details with reviews and review form
│   ├── book_results.html -> list of search results
│   ├── footer.html
│   ├── header.html -> Generic header with navigation / logout / search
│   ├── layout.html
│   ├── login.html
│   ├── registration.html
│   └── search.html



