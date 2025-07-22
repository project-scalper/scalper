#!/usr/bin/python3

from model.engine.storage import Storage
# from model.engine.mongo_storage import Database

storage = Storage()
# storage = Database()
storage.reload()