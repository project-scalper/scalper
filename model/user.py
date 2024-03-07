#!/usr/bin/python3

from model.base_model import BaseModel

class User(BaseModel):
    username = ""
    email = ""
    password = ""
    keys = {}
    exchange = ""
    capital = 0
    has_bot = False
    bot_id = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)