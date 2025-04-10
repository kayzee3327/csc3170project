import mysql.connector
import os

import click
from flask import current_app, g

def get_db(config=None):
    if 'db' not in g:
        if config is not None:
            g.db = mysql.connector.connect(**config)
        else:
            c = {
                "host": os.getenv("DB_HOST", "localhost"), 
                "user": os.getenv("DB_USER", "root"),
                "password": os.getenv("DB_PASSWORD", ""),
                "database": os.getenv("DB_NAME", "library_management")
            }

            g.db = mysql.connector.connect(**c)
    
    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def execute_sql_file(cursor, filename):
    """Execute SQL file to create tables or insert data."""
    with current_app.open_resource(filename) as f:
        sql = f.read().decode('utf8')
        for statement in sql.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
                print(f"Executed: {statement[:30]}...")  # Print first 30 characters of the SQL statement for logging


def init_db():
    db = get_db()
    c = db.cursor()
    execute_sql_file(c, 'sql/schema.sql')
    execute_sql_file(c, 'sql/users.sql')
    execute_sql_file(c, 'sql/books.sql')
    execute_sql_file(c, 'sql/borrows.sql')
    execute_sql_file(c, 'sql/complaints.sql')
    db.commit()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized database')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
