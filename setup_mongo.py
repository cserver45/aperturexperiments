"""Setup_mongo.py - A script to initally setup the entries in mongodb."""
import configparser
import pymongo

# pymongo does not need to be added to requirements.txt, due to motor requiring it

# insert the default items
items = [
    {
        "name": "Watch", 
        "description": "Time (useless right now)",
        "price": 100
    },
    {
        "name": "Apple",
        "description": "It's an apple",
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
]

# init connection
config = configparser.ConfigParser()
config.read('config/bot.conf')
client = pymongo.MongoClient(str(config["mongodb"]["passwd"]))

# 
def create_items():
    """Function for creating all entires"""
    coll = client.aperturelabsbot.shop_data
    for item in items:
        # add them to the shop_data collection
        coll.insert_one(item)

create_items()