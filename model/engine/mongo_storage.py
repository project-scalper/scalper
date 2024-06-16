#!/usr/bin/python3

from pymongo.mongo_client import MongoClient
import pymongo
from os import getenv
from helper.loadenv import handleEnv
from model.bot import Bot
from model.user import User
from model.signal import Signal
from bson import ObjectId
from datetime import datetime, timedelta
from model.usersession import UserSession

classes = {"users": "User", "bots": "Bot", 'usersessions': "UserSession",
           "signals": "Signal"}
classes2 = {"Bot": Bot, "User": User, "UserSession": UserSession,
            "Signal": Signal}


class Database:
    __objects = {}

    def __init__(self):
        # db_name = getenv('DB_NAME', 'scalperdb')
        # url = getenv("HOST", 'localhost')
        url = handleEnv("DB_HOST")
        db_name = handleEnv("DB_NAME")
        # port = getenv("PORT", 27017)
        try:
            self.client = MongoClient(url)
            print("Client created")
            self.db = self.client[db_name]
        except Exception as e:
            print("Unable to connect to mongo server:", e)

    def all(self, cls=None):
        if cls and cls in classes:
            cls = classes[cls]
        # elif cls and cls in classes2:
        #     cls = classes2[cls]
        if cls:
            new_dict = {key: obj for key, obj in self.__objects.items() if obj.__class__ == cls}
            # for key, obj in self.__objects.items():
            #     if obj.__class__ == cls:
            #         new_dict[key] = obj
            return new_dict
        return self.__objects

    def new(self, obj):
        if obj is not None:
            key = obj.__class__.__name__ + "." + obj.id
            self.__objects[key] = obj

    def save(self, model=None):
        """
        Save a new document in the specified collection.
        Args:
            model (class): The model class representing the collection.
        """
        if not model:
            return
        query = {'id': model.id}
        vals = model.to_dict()
        if '_id' in vals and isinstance(vals['_id'], str):
            vals['_id'] = ObjectId(vals['_id'])
        new_attrs = {"$set": vals}
        self.db[model.__tablename__].update_one(query, new_attrs, upsert=True)
        # print("Document updated successfully")

    def delete(self, obj=None):
        """
        Remove a document from the specified collection based on a query.
        Args:
            obj (class): The instance representing the document.
        """
        try:
            key = f"{obj.__class__.__name__}.{obj.id}"
            self.db[obj.__tablename__].delete_one({'id': obj.id})
            self.__objects.pop(key)
        except pymongo.errors.PyMongoError as e:
            print(f'Error deleting document(s): {e}')

    def close(self):
        self.client.close()

    def reload(self):
        """This recreates all objects and save them to __objects"""
        try:
            for cls in classes:
                models = self.db[cls].find()
                # print(models, type(models))
                for obj in list(models):
                    model = classes2[obj['__class__']](**obj)
                    key = f"{model.__class__.__name__}.{model.id}"
                    self.__objects[key] = model
        except Exception as e:
            print(e)
            pass
        
    def get(self, cls, id):
        if cls in classes:
            cls = classes[cls]
        if cls in classes2.values():
            cls = cls.__class__
        key = f"{cls}.{id}"
        
        obj = self.__objects.get(key, None)
        if obj and obj.__class__ == 'UserSession':
            if datetime.now() > obj.created_at + timedelta(hours=72):
                self.delete(obj)
                return
        return obj

    def search(self, cls, **kwargs):
        """This filters the storage for objects matching kwargs
        Args:
            cls (str): The class to search for the documents
            kwargs (dict): filter parameters
        Return:
            A list of documents matching the description
        """
        if cls not in classes:
            for key, val in classes.items():
                if val == cls:
                    cls = key
                    break
        if cls not in classes:
            cls = cls.__tablename__

        result = []
        docs = self.db[cls].find( kwargs )
        if docs:
            for doc in docs:
                key = doc['__class__'] + "." + doc['id']
                model = self.__objects[key]
                result.append(model)
        return result
    
    def count(self, cls:str=None)->int:
        """This counts the number of documents in a cls,
            If key is provided, it sums all the values of that key in the collection
        Args:
            cls (str): the class name or class tablename
        Return:
            int: count of found documents
        """
        if cls not in classes:
            if cls in classes2:
                cls = classes2[cls].__tablename__
        return self.db[cls].count()
