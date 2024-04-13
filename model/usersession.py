#!/usr/bin/python3

import model
from model.base_model import BaseModel
from datetime import datetime, timedelta

class UserSession(BaseModel):
    __tablename__ = 'usersessions'
    user_id = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
