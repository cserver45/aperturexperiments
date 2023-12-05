"""Setup_mongo.py - A script to initally setup the entries in mongodb."""
import pymongo

# pymongo does not need to be added to requirements.txt, due to motor requiring it

# insert the default items
items = {
    {
        "name": "Watch", 
        "description": "Time (useless right now)",
        "price": 100
    },
    {
        "name": "Apple",
        "descirption": "It's an apple",
        "price": 10
    },
    {
        "name": "Laptop",
        "description": "Work",
        "price": 1000
    },
    {
        "name": "Mask",
        "description": "Used for diving",
        "price": 350
    }
}


# 
def create_items():
    """Function for creating all entires"""
    for item in items:
        # add them to the shop_data collection
        pass