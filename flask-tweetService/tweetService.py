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
# app.config.from_envvar('APP_CONFIG')
FLASK_APP = 'api'
FLASK_ENV = 'development'
APP_CONFIG = 'api.cfg'
DATABASE = '../flask-sqlite3/test.db'
SQL_FILEPATH = '../flask-sqlite3/users.sql'


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
        with app.open_resource(SQL_FILEPATH, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def checkUserExist(userId):
    userId = userId.strip()
    sql = """select * from users where id=?"""
    data = (userId,)
    result = query_db_check(sql, data)
    if result is None:
        return False
    else:
        return True


@app.route('/tweetService/v1/<user_id>/postTweet', methods=['PUT'])
def postTweet(user_id):
    # ideally one should take sessionId in the request and validate the session and proceed
    # check if use exists
    tweet_text = request.json.get("tweetText")
    if None in (user_id, tweet_text):
        make_error(400, 'One or many required parameters are missing')
    user_id = user_id.strip()
    twid = uuid.uuid4()
    tweet_id = "twid-" + str(twid)
    date_of_creation = datetime.utcnow()
    checkUserQuery = """INSERT INTO tweets (userid,tweet_id,tweet_text,date_of_creation) VALUES (?,?,?,?)"""
    userExistData = (user_id, tweet_id, tweet_text, date_of_creation)

    query_db(checkUserQuery, userExistData)
    return jsonify({"statusCode": "200", "status": "ok"})


@app.route('/tweetService/v1/<user_id>/userTweets', methods=['GET'])
def getUserTimeline(user_id):
    # ideally one should take sessionId in the request and validate the session and proceed
    if not user_id:
        make_error(400, "Required parameter 'userId' is missing")
        user_id = user_id.strip()
    checkUserQuery = """SELECT tweet_text, date_of_creation FROM tweets WHERE userId=? LIMIT 25"""
    userExistData = (user_id,)
    result = query_db(checkUserQuery, userExistData)
    print(result)
    return jsonify(result)


@app.route('/tweetService/v1/publicTweets', methods=['GET'])
def getPublicTimeline():
    checkUserQuery = """SELECT userid, tweet_text, date_of_creation FROM tweets LIMIT 25"""
    # userExistData = ()
    result = plain_query_db(checkUserQuery)
    print(result)
    # tweets = jsonify(result)
    # response = jsonify({"userId": user_id, "tweets": tweets})
    return jsonify(result)


@app.route('/tweetService/v1/<user_id>/tweetsFromFollowings', methods=['GET'])
def getHomeTimeline(user_id):
    user_id = user_id.strip()
    # ideally one should take sessionId in the request and validate the session and proceed
    if not user_id:
        make_error(400, "Required parameter 'userId' is missing")
    checkUserQuery = """SELECT following FROM followers WHERE userid=? LIMIT 25"""
    userExistData = (user_id,)
    resultForFollowing = query_db(checkUserQuery, userExistData)
    print(resultForFollowing)
    results = []
    for row in resultForFollowing:
        print(row)
        followingUserId = row.get('following')
        checkUserQuery1 = """SELECT userid,tweet_text, date_of_creation FROM tweets WHERE userid=? LIMIT 1"""
        userExistData1 = (followingUserId,)
        result = query_db(checkUserQuery1, userExistData1)
        results.append(result)
    return jsonify(results)


if __name__ == "__main__":
    app.run()
