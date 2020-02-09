import json
import sqlite3
import numpy as np
import database_manager
import grequests
import os

"""
Module for communication among raspberry units
"""

config = json.load(open("config.json"))

def ping_to_children(protocol="http://"):
    """
    A get gate suffices to check the connection.
    url -> index 1
    id  -> index 0
    """
    children = database_manager.fetch_all_children()
    id_children = list(map(lambda x: x[0], children))
    to_ping = grequests.map([grequests.get(x[1]) for x in children])
    online = dict(filter(lambda x: x[1].ok,zip(id_children,to_ping)))
    return online

def create_new_batch(X):
    """
    X: numpy.array
        Chomossome population matrix where lines are chromossomes.
    """
    online_devices = ping_to_children()
    splits = np.array_split(X,len(online_devices))
    #Creating assignment
    batch_id = database_manager.get_new_batch_id()
    for id,batch in zip(online_devices.keys(), splits):
        for data in batch:
            database_manager.create_assignment(id,sqlite3.Binary(data),batch_id)
    return batch_id
    #This should already return a list of json elements or tuple

def check_exsiting_batch():
    """
    If an assignment already exists, returns batch_id. Otherwise returns False.
    Never allow batch_id to be zero.
    """
    return database_manager.check_exsiting_batch()
    #This should already return a list of json elements or tuple

def update_assignment(request_id, fitness):
    """
    request_id is automatic on table assignment.
    """
    database_manager.update_assignment(request_id,fitness)
