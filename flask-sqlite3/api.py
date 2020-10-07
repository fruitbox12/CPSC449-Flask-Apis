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
import sqlite3, uuid
import hashlib, binascii, os

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG')
# FLASK_APP = 'api'
# FLASK_ENV = 'development'
# APP_CONFIG = 'api.cfg'
# DATABASE = 'test.db'


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


def check_parameters(*params):
    for param in params:
        if param is None:
            make_error(400, 'Required parameter is missing')



@app.before_first_request
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource(app.config['SQL_FILEPATH'], mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/', methods=['GET'])
def helloMethod():
    return "this is user api"

@app.route('/createUser', methods=['GET', 'POST'])
def createUser():
    if request.json is None:
    	make_error(400, 'No Data Provided')
    userName = request.json.get("userName")
    email = request.json.get("email")
    password = request.json.get("password")
    hashedPassword = str(hashlib.md5(password.encode()).hexdigest())
    check_parameters(userName, email, password)
    checkUserQuery = """SELECT username, email FROM users WHERE username=?"""
    userExistData = (userName,)
    result = query_db_check(checkUserQuery, userExistData)
    if result:
        make_error(400, 'user exists already')
    else:
        sql = """INSERT INTO users (userName, email, password) VALUES(?, ?, ?)"""
        data_tuple = (userName, email, hashedPassword)
        result = query_db(sql, data_tuple)
    return {'message': 'User Created', 'statusCode': 200}


@app.route('/authenticate', methods=['POST'])
def authenticate():
    if request.json is None:
    	make_error(400, 'No Data Provided')
    userName = request.json.get("userName")
    password = request.json.get("password")
    check_parameters(userName, password)
    sql = """select password from users where userName=?"""
    data = (userName,)
    storedPassword = query_db_check(sql, data).get("password")
    newPassword = str(hashlib.md5(password.encode()).hexdigest())
    if storedPassword == newPassword:
        return jsonify({"message": "user authenticated", "statusCode": "200", "status": "ok"})
    else:
        return jsonify(
            {"statusCode": "401", "status": "Unauthorized", "message:": "either username or password do not match"})


@app.route('/addFollower', methods=['POST'])
def addFollower():
    if request.json is None:
    	make_error(400, 'No Data Provided')
    userName = request.json.get("userName")
    usernameToFollow = request.json.get("usernameToFollow")
    check_parameters(userName, usernameToFollow)
    checkUserQuery = """SELECT id, username FROM users WHERE username=?"""
    userExistData = (userName,)
    user_result = query_db_check(checkUserQuery, userExistData)
    userExistData = (usernameToFollow,)
    follow_user_result = query_db_check(checkUserQuery, userExistData)
    if user_result and follow_user_result:
    	
        sql_select = """Select id from users where userName = ?"""
        data = (usernameToFollow,)
        idOfFollowing = query_db_check(sql_select, data).get("id")
        data = (userName,)
        idOfUser = query_db_check(sql_select, data).get("id")
        checkDuplicateSql = """SELECT * from followers where userid = ? and following=?"""
        duplicate_data=(idOfUser, idOfFollowing)
        sql_insert = """INSERT INTO followers(userid, following) VALUES(?, ?)"""
        values = (idOfUser, idOfFollowing)
        record = query_db_check(checkDuplicateSql,duplicate_data)
        if record is None:
        	query_db(sql_insert, values)
        	message = str(userName + ' has started following ' + usernameToFollow)
        	return {'message': message, 'statueCode': 201}
        else:
        	message = str(userName + ' already follows ' + usernameToFollow)
        	make_error(400, message)        
    else:
        make_error(400, 'user Or UserToFollow Does Not Exists')


@app.route('/removeFollower', methods=['POST'])
def removeFollower():
    if request.json is None:
    	make_error(400, 'No Data Provided')
    userName = request.json.get("userName")
    usernameToFollow = request.json.get("usernameToFollow")
    checkUserQuery = """SELECT id, username FROM users WHERE username=?"""
    userExistData = (userName,)
    user_result = query_db_check(checkUserQuery, userExistData)
    userExistData = (usernameToFollow,)
    follow_user_result = query_db_check(checkUserQuery, userExistData)
    if user_result and follow_user_result:
        sql_select = """Select id from users where userName = ?"""
        data = (usernameToFollow,)
        idOfFollowing = query_db_check(sql_select, data).get("id")
        data = (userName,)
        idOfUser = query_db_check(sql_select, data).get("id")
        sql_delete = """DELETE from followers where userId = ? and following = ?"""
        values = (idOfUser, idOfFollowing)
        query_db(sql_delete, values)
        message = str(userName + ' has stopped following ' + usernameToFollow)
        return {'message': message, 'statueCode': 201}
    else:
        make_error(400, 'user Or UserToFollow Does Not Exists')


if __name__ == "__main__":
    app.run()
