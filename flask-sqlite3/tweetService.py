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
import sys
# import logging
import flask
from flask import request, jsonify, g, abort, make_response
import sqlite3
import uuid
from datetime import datetime

app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('APP_CONFIG')
# FLASK_APP = 'api'
# FLASK_ENV = 'development'
# APP_CONFIG = 'api.cfg'
# DATABASE = 'test.db'
# SQL_FILEPATH = 'users.sql'


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


def plain_query_db(query):
    db = get_db()
    cur = db.cursor()
    cur.execute(query)
    db.commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if False else rv


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


def checkUserExists(user_name):
    user_name = user_name.strip()
    sql = """select userName from users where userName=?"""
    data = (user_name,)
    result = query_db_check(sql, data)
    if result is None:
        return False
    else:
        return True


def getUserId(user_name):
    user_name = user_name.strip()
    sql = """select id from users where userName=?"""
    data = (user_name,)
    result = query_db(sql, data)
    if not result:
        make_error(400, "user:'" + user_name + "' does not exist")
    else:
        return result[0].get('id')

@app.route('/', methods=['GET'])
def helloMethod():
    return "this is tweet api"

@app.route('/tweetService/v1/postTweet', methods=['POST'])
def postTweet():
    print("hr")
    user_name = request.json.get("userName")
    tweet_text = request.json.get("tweetText")
    if None in (user_name, tweet_text):
        make_error(400, 'One or many required parameters are missing')
    user_name = user_name.strip()
    user_id = getUserId(user_name)
    date_of_creation = datetime.utcnow()
    checkUserQuery = """INSERT INTO tweets (userid,tweet_text,date_of_creation) VALUES (?,?,?)"""
    userExistData = (user_id, tweet_text, date_of_creation)
    query_db(checkUserQuery, userExistData)
    return jsonify({"statusCode": "200", "status": "ok"})

@app.route('/tweetService/v1/userTweets', methods=['GET'])
def getUserTimeline():
    user_name = request.json.get("userName")
    if user_name is None:
        make_error(400, "Required parameter 'userName' is missing")
    user_name = user_name.strip()
    user_id = getUserId(user_name)  # this does user validation also
    checkUserQuery = """SELECT tweet_text, date_of_creation FROM tweets WHERE userid=? ORDER BY date_of_creation DESC LIMIT 25"""
    userExistData = (user_id,)
    result = query_db(checkUserQuery, userExistData)
    return jsonify(result)


@app.route('/tweetService/v1/publicTweets', methods=['GET'])
def getPublicTimeline():

    checkUserQuery = """SELECT u.userName, t.tweet_text, t.date_of_creation FROM users u, tweets t where u.id == t.userid ORDER BY date_of_creation DESC LIMIT 25"""
    result = plain_query_db(checkUserQuery)
    return jsonify(result)


@app.route('/tweetService/v1/tweetsFromFollowings', methods=['GET'])
def getHomeTimeline():
    user_name = request.args.get("userName")
    if not user_name:
        make_error(400, "Required parameter 'userId' is missing")
    user_name = user_name.strip()
    user_id = getUserId(user_name)  # this does user validation also
    checkUserQuery = """SELECT following FROM followers WHERE userid=? LIMIT 25"""
    userExistData = (user_id,)
    resultForFollowing = query_db(checkUserQuery, userExistData)
    print(resultForFollowing)
    results = []
    for row in resultForFollowing:
        print(row)
        followingUserId = row.get('following')
        checkUserQuery1 = """SELECT userid,tweet_text, date_of_creation FROM tweets WHERE userid=? ORDER BY date_of_creation DESC LIMIT 1"""
        userExistData1 = (followingUserId,)
        result = query_db(checkUserQuery1, userExistData1)
        results.append(result[0])
    return jsonify(results)


if __name__ == "__main__":
    app.run()
