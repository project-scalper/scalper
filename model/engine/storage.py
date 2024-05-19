#!/usr/bin/python3

import json
from json import JSONDecodeError
from model.user import User
from model.usersession import UserSession
from model.bot import Bot
from datetime import datetime, timedelta
from typing import Union, Dict, List
# from model.engine import 

classes = {"Bot": Bot, "User": User, "UserSession": UserSession}


class Storage:
    fileName = 'data.json'

    def __init__(self) -> None:
        self.__objects = {}
        
    def all(self, cls=None) -> Dict:
        """returns the dictionary __objects"""
        if cls is not None:
            new_dict = {}
            if isinstance(cls, str):
                cls = classes[cls]
            for key, value in self.__objects.items():
                if cls == value.__class__ or cls == value.__class__.__name__:
                    new_dict[key] = value
            return new_dict
        return self.__objects
    
    def get(self, cls:str, id:str) -> Union[Bot | User | UserSession]:
        key = f"{cls}.{id}"
        obj = self.__objects.get(key, None)
        if obj and cls == "UserSession":
            if datetime.now() > obj.created_at + timedelta(hours=72):
                self.delete(obj)
                return None
        return obj
    
    def new(self, obj):
        key = f"{obj.__class__.__name__}.{obj.id}"
        self.__objects[key] = obj

    def save(self):
        json_objs = {}
        for key, obj in self.__objects.items():
            json_objs[key] = obj.to_dict()

        try:
            with open(self.fileName, 'w', encoding='utf-8') as f:
                json.dump(json_objs, f)
        except FileNotFoundError as e:
            pass

    def reload(self):
        try:
            with open(self.fileName) as f:
                objs = json.load(f)

            for key, obj in objs.items():
                cls = key.split(".")[0]
                if cls in classes:
                    model = classes[cls](**obj)
                    model.save()
        except FileNotFoundError:
            pass
        except JSONDecodeError:
            pass

    def search(self, cls, *args, **kwargs) -> List:
        matched_obj = []
        for key, obj in self.all(cls).items():
            flag = 1
            for key, val in kwargs.items():
                if getattr(obj, key) != val:
                    flag = 0
                    break
            if flag == 1:
                matched_obj.append(obj)
            
        return matched_obj
    
    def close(self):
        self.reload()

    def delete(self, obj):
        """delete obj from __objects if its inside"""
        if obj is not None:
            key = obj.__class__.__name__ + '.' + obj.id
            if key in self.__objects:
                del self.__objects[key]
                self.save()
