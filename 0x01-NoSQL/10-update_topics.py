#!/usr/bin/env python3
""" MongoDB Operations with Python using pymongo """


def update_topics(mongo_collection, name, topics):
    """ Changes all topics of a school document based on the name """
    toUpdate = {"name": name}
    new_values = {"$set": {"topics": topics}}

    mongo_collection.update_many(toUpdate, new_values)
