# Science Fiction Novel API from "Creating Web APIs with Python and Flask"
# <https://programminghistorian.org/en/lessons/creating-apis-with-python-and-flask>.
#
# What's new:
#
#  * Database specified in app config file
#
#  * Includes features from "Using SQLite 3 with Flask"
#    <https://flask.palletsprojects.com/en/1.1.x/patterns/sqlite3/>
#

import flask
from flask import request, jsonify, g, abort, make_response
import sqlite3


app = flask.Flask(__name__)
app.config.from_envvar('APP_CONFIG')


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def query_db_check(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchone()
    # db.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def make_error(status_code, message):
    abort(make_response(jsonify(message=message, stausCode=status_code), status_code))


@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('users.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    firstName = request.json.get("firstName")
    lastName = request.json.get("lastName")
    userName = request.json.get("userName")
    email = request.json.get("email")
    password = request.json.get("password")
    if None in (firstName, lastName, userName, email, password):
        make_error(400, 'Required parameter is missing')

    checkUserQuery = """SELECT email
                          , username
                   FROM user
                   WHERE email=?
                       OR username=?"""
    userExistData = (email, userName)
    result = query_db_check(checkUserQuery, userExistData)
    if result:
        make_error(400, 'user exists already')
    else:
        sql = """INSERT INTO user(firstName, lastName, userName, email, password)
                          VALUES(?, ?, ?, ?, ?)"""
        data_tuple = (firstName, lastName, userName, email, password)
        result = query_db(sql, data_tuple)
        print('result is', result)
    return {'message': 'User Created', 'statusCode': 201}


@app.errorhandler(404)
def page_not_found(e):
    return make_error(404, 'No Url Found')

@app.route('/api/v1/resources/books', methods=['GET'])
def api_filter():
    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM users WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    results = query_db(query, to_filter)

    return jsonify(results)
