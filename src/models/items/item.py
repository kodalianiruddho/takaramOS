import uuid

import datetime

import pymongo

import src.models.items.constants as ItemConstants
from src.common.database import Database

__author__ = 'ibininja'


class Item(object):
    def __init__(self, title, description, image_url, contact, user_id, category = None, approved=False, _id=None,
                 date_posted=datetime.datetime.utcnow()):
        self.title = title
        self.description = description
        self.image_url = image_url
        self.date_posted = date_posted
        self.contact = contact
        self.user_id = user_id
        self.category = category
        self.approved = approved
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            "title": self.title,
            "description": self.description,
            "image_url": self.image_url,
            "date_posted": self.date_posted,
            "contact": self.contact,
            "user_id": self.user_id,
            "category": self.category,
            "approved": self.approved,
            "_id": self._id,

        }

    def save_to_mongo(self):
        Database.insert(ItemConstants.COLLECTION, self.json())

    @classmethod
    def get_items_by_user_id(cls, user_id):
        items = Database.find(ItemConstants.COLLECTION, {"user_id": user_id})
        if items is not None:
            return [cls(**item) for item in items]

    @classmethod
    def get_item_by_id(cls, item_id):
        item = Database.find_one(ItemConstants.COLLECTION, {"_id": item_id})
        if item is not None:
            return cls(**item)

    @classmethod
    def get_user_id(cls, item_id):
        user_id = Database.find_one(ItemConstants.COLLECTION, {"_id":item_id},{"_id":0, "user_id":1})
        if user_id is not None:
            return user_id

    @classmethod
    def get_all_items(cls):
        items = Database.find(ItemConstants.COLLECTION, {})
        if items is not None:
            return [cls(**item) for item in items]

    @classmethod
    def get_all_approved_items(cls):
        items = Database.find(ItemConstants.COLLECTION, {"approved": True})
        if items is not None:
            return [cls(**item) for item in items]

    @classmethod
    def get_pending_items(cls):
        items = Database.find(ItemConstants.COLLECTION, {"approved": False})
        if items is not None:
            return [cls(**item) for item in items]

    def remove_item(self):
        Database.remove(ItemConstants.COLLECTION, {"_id": self._id})

    def update_item(self, attribute_name, attribute_value):
        Database.update_one(ItemConstants.COLLECTION, {"_id": self._id}, {"$set": {attribute_name: attribute_value}})

    @classmethod
    def search_items(cls, words):
        #"$caseSensitive": True for mongodb version 3.2
        results = Database.find(ItemConstants.COLLECTION,
                                {"approved": True, "$text": {"$search": words}})
        if results is not None:
            return [cls(**result) for result in results]

    @classmethod
    def get_posted_items_count(cls):
        items = Database.aggregate(ItemConstants.COLLECTION, [{"$group":{"_id":"$date_posted", "count":{"$sum":1}}}, {"$sort":{"_id":1}}])
        return items
