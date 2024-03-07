#!/usr/bin/python3

from flask import Blueprint
from model import storage
from model.usersession import UserSession
from flask_httpauth import HTTPTokenAuth

app_views = Blueprint('app_views', __name__, url_prefix='/bot')
auth = HTTPTokenAuth(scheme='scalper')
# sessions = UserSession()

@auth.verify_token
def verify_token(token):
    """This validates the token presented by the user"""
    sess = storage.get("UserSession", token)
    if not sess:
        print("No user found")
        return None
    else:
        user = storage.get("User", sess.user_id)
        return user
    

from api.blueprint.users import *
from api.blueprint.bot import *