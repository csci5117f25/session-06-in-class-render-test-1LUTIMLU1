from flask import Flask, render_template, request, url_for, redirect
import psycopg2

from contextlib import contextmanager
import logging
import os
from flask import current_app, get_flashed_messages

from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')
    

@contextmanager
def get_db_connection():
    try:
        connection = pool.geconn()
        yield connection
    finally:
        pool.putconn(connection)

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

def add_registration(name, address, phone):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding registration for %s", name)
        cur.execute(
            "INSERT INTO registrations (name, address, phone) VALUES (%s, %s, %s)",
            (name, address, phone)
        )
def get_registrations(page=0, per_page=10):
    limit = per_page
    offset = page * per_page
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT * FROM registrations ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset)
        )
        return cur.fetchall()


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/<name>')
def hello(name=None):
    if request.method == 'POST':
        name = request.form.get('name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        # You'd typically save this data to the database here
        return redirect(url_for('submit'))

    return render_template('hello.html', name=name)


@app.route('/submit')
def submit():
    return render_template('submit.html')


if __name__ == '__main__':
    app.run(debug = True)

