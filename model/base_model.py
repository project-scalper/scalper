#!/usr/bin/python3

# import json
import uuid
import model
from datetime import datetime

time = "%b %d %Y, %I:%M:%S %p"

class BaseModel:
    """class definition"""

    def __init__(self, *args, **kwargs):
        """class initialization"""
        if kwargs:
            for key, value in kwargs.items():
                if key != "__class__":
                    setattr(self, key, value)
            if kwargs.get("created_at", None) and type(self.created_at) is str:
                self.created_at = datetime.strptime(kwargs["created_at"], time)
            else:
                self.created_at = datetime.utcnow()
            if kwargs.get("updated_at", None) and type(self.updated_at) is str:
                self.updated_at = datetime.strptime(kwargs["updated_at"], time)
            else:
                self.updated_at = datetime.utcnow()
            if kwargs.get("id", None) is None:
                self.id = str(uuid.uuid4())
        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = self.created_at

    def to_dict(self):
        """This returns a dict representation of the object"""
        dictionary = self.__dict__.copy()
        if 'created_at' in dictionary:
            dictionary['created_at'] = self.created_at.strftime(time)
        if 'updated_at' in dictionary:
            dictionary['updated_at'] = self.updated_at.strftime(time)
        dictionary.pop('_sa_instance_state', None)
        dictionary['__class__'] = self.__class__.__name__
        return dictionary

    def __str__(self):
        """Called when print function is used"""
        return "[{}] ({}) {}".format(self.__class__.__name__,
                                     self.id, self.to_dict())

    def save(self):
        """This save the object to storage"""
        self.updated_at = datetime.utcnow()
        model.storage.new(self)
        model.storage.save()

    def update(self, **kwargs):
        """This updates some attribute in storage"""
        try:
            for key, val in kwargs.items():
                if key == "password":
                    if self.reset_code == "Valid":
                        setattr(self, key, val)
                    else:
                        pass
                else:
                    setattr(self, key, val)
                model.storage.save()
        except Exception:
            pass

    def delete(self):
        """This removes an object from storage"""
        model.storage.delete(self)
        model.storage.save()
