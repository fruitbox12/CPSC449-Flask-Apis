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
import hashlib, binascii, os


app = flask.Flask(__name__)
# app.config.from_envvar('APP_CONFIG')
FLASK_APP = 'api'
FLASK_ENV = 'development'
APP_CONFIG = 'api.cfg'
DATABASE = 'test.db'


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
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


def check_parameters(*params):
    for param in params:
        if param is None:
            make_error(400, 'Required parameter is missing')

def hash_password(password):
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    hashedPassword =  hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), 
                                salt, 100000)
    hashedPassword= binascii.hexlify(hashedPassword)
    return (salt + hashedPassword).decode('ascii')

@app.before_first_request
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
    hashedPassword = hash_password(password)
    check_parameters(firstName, lastName, userName, email, password)

    checkUserQuery = """SELECT email
                          , username
                   FROM users
                   WHERE email=?
                       OR username=?"""
    userExistData = (email, userName)
    result = query_db_check(checkUserQuery, userExistData)
    if result:
        make_error(400, 'user exists already')
    else:
        sql = """INSERT INTO users(firstName, lastName, userName, email, password)
                          VALUES(?, ?, ?, ?, ?)"""
        data_tuple = (firstName, lastName, userName, email, hashedPassword)
        result = query_db(sql, data_tuple)
        print('result is', result)
    return {'message': 'User Created', 'statusCode': 201}


@app.route('/app/v1/<userId>/checkUserExist',methods=['GET','POST'])
def checkUserExist(userId):
    sql = """select * from users where id=?"""
    data = (userId,)
    result = query_db_check(sql, data)
    if result is None:
        make_error(400, 'user does not exists')
    else:
        return {'message': 'true', 'statusCode': 201}
    


@app.route('/authenticate', methods = ['GET','POST'])
def authenticate():
    
    

@app.route('/addFollower', methods=['GET', 'POST'])
def addFollower():
    userName = request.json.get("userName")
    usernameToFollow = request.json.get("usernameToFollow")
    check_parameters(userName, usernameToFollow)

    checkUserQuery = """SELECT id
                          , username
                   FROM users
                   WHERE username=?"""

    userExistData = (userName)

    user_result = query_db_check(checkUserQuery, userExistData)

    userExistData = (usernameToFollow)
    follow_user_result = query_db_check(checkUserQuery, userExistData)

    if user_result or follow_user_result:
        sql = """Select id from users where userName = ?"""
        data = (usernameToFollow)
        result = query_db(sql, data)
        sql = """INSERT INTO userFollower(id, userName, follower)
                          VALUES(?, ?, ?)"""

        values = (result, usernameToFollow, userName)
        result = query_db(sql, values)
        return {'message': 'Follower added', 'statueCode': 201}

    else:
        make_error(400, 'user Or UserToFollow Does Not Exists')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
