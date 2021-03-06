import json
import sqlite3
import numpy as np
import database_manager
#import grequests
import os
import logging
import asyncio
import random
import requests
import time as time_
from experiment import f_set, f_read
from sync import sync_send
logging.basicConfig(filename="hanashi.log", level=logging.DEBUG)

"""
Module for communication among raspberry units
"""

dir_name = os.path.dirname(__file__)

config = json.load(open(os.path.join(dir_name,"config.json")))


def ping_to_children():
    """
    A get gate suffices to check the connection.
    url -> index 1
    id  -> index 0
    """
    children = database_manager.fetch_all_children()
    id_children = list(map(lambda x: x["id"], children))
    #to_ping = grequests.map([grequests.get(x[1]) for x in children])
    to_ping = [requests.get(x["url"]) for x in children]
    online = dict(filter(lambda x: x[1]!=None and x[1].ok,zip(id_children,to_ping)))
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
    database_manager.create_assignments(zip(online_devices.keys(), splits),batch_id)
    return database_manager.get_exsiting_batch()


def check_exsiting_batch():
    """
    If an assignment already exists, returns tuple of remaining items. Otherwise returns False.
    Never allow batch_id to be zero.
    """
    return database_manager.get_exsiting_batch()
    #This should already return a list of json elements or tuple

def update_assignment(request_id, fitness, sync=0):
    """
    request_id is automatic on table assignment.
    """
    database_manager.update_assignment(request_id,fitness, sync=0)

def step():
    """
    Used on push
    """
    unresolved = check_exsiting_batch()
    data = unresolved
    data["time"] = config["time"]
    #requests = [grequests.post(columns[4], data = data) for x in unresolved]
    Requests = [requests.post(data["url"], data = data) for x in unresolved]
    #gmap = grequests.map(requests)
    gmap = Requests
    """
    The output will be another dictionary whse values will be used to update the database. The result is caught by a get in Flask.
    """
    success = list(filter(lambda x: x!=None and x.ok,gmap))
    notification = f"Executed batch post, {len(success)} out of {len(requests)} returned 200."
    logging.info(notification)
    return notification


async def set(data):
    """
    DEPRECATED
    Set to experiment.
    When done, sends a request back to the main server.
    """
    chromossome = batch["chromossome_data"]
    if isinstance(chromossome, str):
        chromossome = eval(chromossome)
    id = batch["id"]
    request_id = batch_id["request_id"]
    batch_id = batch_id["batch_id"]
    time = batch_id["time"]

    #Set value to experiment
    time_.sleep(time)
    #Get value from experiment
    f = random.random()
    database_manager.update_assignment(f,request_id)

    #Posting back to main server
    data["fitness"] = f
    url = data["server_addr"]
    requests.post(url,data=data)

def static_set(assignment_tuple):
    #order: assignment.id,batch_id,request_id,fitness,url,IP,chromossome_data
    data = assignment_tuple

    chromossome = data["chromossome_data"]
    if isinstance(chromossome, str):
        chromossome = eval(chromossome)
    id = assignment_tuple["id"]
    request_id = assignment_tuple["request_id"]
    batch_id = assignment_tuple["batch_id"]
    time = config["time"]

    logging.info(f"Working on {assignment_tuple}.")

    #Set value to experiment
    f_set(chromossome)
    time_.sleep(time)
    #Get value from experiment
    y = f_read()
    if request_id != None:
        database_manager.update_assignment(y,request_id)
        sync_send()




if __name__=="__main__":
    a = np.random.randint(0,10,(5,3))
    print(a)
    print(create_new_batch(a))
