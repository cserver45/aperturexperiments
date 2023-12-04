"""Setup_mongo.py - A script to initally setup the entries in mongodb."""
import pymongo

# pymongo does not need to be added to requirements.txt, due to motor requiring it

# insert the default items
items = {}


# 
def create_items():
    """Function for creating all entires"""
    for item in items:
        # add them to the shop_data collection
        pass