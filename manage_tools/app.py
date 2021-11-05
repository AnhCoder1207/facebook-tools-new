import json
import uuid

import pymongo
from flask import Flask
from flask import jsonify
from flask import request

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from flask_jwt_extended import create_access_token, create_refresh_token, set_access_cookies, unset_jwt_cookies, get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow


from flask_pymongo import PyMongo, DESCENDING
from marshmallow import ValidationError

from validator import ViaShareSchema, CookiesSchema, SchedulerSchema

app = Flask(__name__)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "89dfkj3478@123!!**(#"  # Change this!
# app.config["MONGO_URI"] = "mongodb://localhost:27017/test"
app.config["MONGO_URI"] = "mongodb+srv://facebook:auft.baff1vawn*WEC@cluster0.dtlfk.mongodb.net/test?retryWrites=true&w=majority&ssl=true&ssl_cert_reqs=CERT_NONE"
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_COOKIE_CSRF_PROTECT"] = False
jwt = JWTManager(app)
mongo = PyMongo(app)
ma = Marshmallow(app)


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = mongo.db.users.find({'username': username, 'password': password})
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401

    response = jsonify({"msg": "login successful"})
    access_token = create_access_token(identity="example_user")
    set_access_cookies(response, access_token)
    return response


# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@app.route("/via", methods=["GET"])
@jwt_required()
def get_all_via():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    fb_id = request.args.get('fb_id', '')
    email = request.args.get('email', '')
    phone_number = request.args.get('phone_number', '')
    cookies = request.args.get('cookies', '')
    finder = {
        "fb_id": {"$regex": fb_id},
        "email": {"$regex": email},
        "phone_number": {"$regex": phone_number},
        "cookies": {"$regex": cookies}
    }

    data = mongo.db.via_share.find(finder).sort([('_id', DESCENDING)]).skip(page_size * (page - 1)).limit(page_size)
    return jsonify(data=list(data))


@app.route("/cookies", methods=["GET"])
@jwt_required()
def get_cookies():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    cookie = request.args.get('cookie', '')
    finder = {
        "cookie": {"$regex": cookie}
    }

    data = mongo.db.cookies.find(finder).sort([('_id', DESCENDING)]).skip(page_size * (page - 1)).limit(page_size)
    return jsonify(data=list(data))


@app.route("/via/<via_id>", methods=["PUT"])
@jwt_required()
def update_via(via_id):
    finder = {
        "_id": via_id
    }
    try:
        content = request.get_json(silent=True)
        content = ViaShareSchema().load(content)
    except ValidationError as error:
        return jsonify(msg='failed', error=error.messages)

    new_values = {"$set": content}
    result = mongo.db.via_share.update_one(finder, new_values)
    return jsonify(msg='success', update_count=result.matched_count)


@app.route("/cookies/<cookie_id>", methods=["PUT"])
@jwt_required()
def update_cookies(cookie_id):

    try:
        content = request.get_json(silent=True)
        content = CookiesSchema().load(content)
    except ValidationError as error:
        return jsonify(msg='failed', error=error.messages)

    finder = {
        "_id": cookie_id
    }

    new_values = {"$set": content}
    result = mongo.db.cookies.update_one(finder, new_values)
    return jsonify(msg='success', update_count=result.matched_count)


@app.route("/scheduler", methods=["POST"])
# @jwt_required()
def scheduler_share():
    try:
        content = request.get_json()
        content = SchedulerSchema().load(content)
    except ValidationError as error:
        return jsonify(msg='failed', error=error.messages)

    date_time_obj = datetime.strptime(content.get('scheduler_date'), "%d/%m/%Y %H:%M")
    # if date_time_obj < datetime.now():
    #     return jsonify(msg='failed check datetime')
    exist_scheduler = mongo.db.scheduler.find_one({"video_id": content.get('video_id')})
    if exist_scheduler:
        mongo.db.scheduler.update_one({"_id": exist_scheduler['_id']}, {"$set": {"shared": False, "share_number": int(content.get("number"))}})
        return jsonify(msg='updated')

    new_scheduler = {
        "_id": str(uuid.uuid4()),
        "video_id": content.get('video_id'),
        "title": content.get('title'),
        "scheduler_time": datetime.now().timestamp(),
        "create_date": datetime.now().timestamp(),
        "shared": False,
        "share_number": int(content.get("number"))
    }

    result = mongo.db.scheduler.insert_one(new_scheduler)
    return jsonify(msg='success')


@app.route("/scheduler", methods=["GET"])
# @jwt_required()
def get_scheduler():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    video_id = request.args.get('video_id', '')
    shared = request.args.get('shared', '')
    finder = {
        "video_id": {"$regex": video_id},
        "shared": True if shared == "1" else False,
        "share_number": {"$ne": 0}
    }

    data = mongo.db.scheduler.find(finder).sort("create_date", pymongo.ASCENDING).skip(page).limit(page_size)
    return jsonify(data=list(data))


if __name__ == "__main__":
    app.run()
