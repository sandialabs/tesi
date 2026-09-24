import logging
import string
import traceback
import random
import sqlite3
from datetime import datetime
from flask import * # Flask, g, redirect, render_template, request, url_for, make_response, jsonify
from functools import wraps
from flask_bootstrap import Bootstrap5
import json
import pandas as pd
import numpy as np
import os
from back_end.models.product import Product
from back_end.models.customer import Customer
from back_end.models.order import Order
import webbrowser
import sys
import time


# ------------------ GLOBAL VARIABLES ------------------

# print("UTIL OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(__file__))  # DELETE LATER (fix DIR variable)


# ------------------ UTILITY HELPER FUNCTIONS ------------------

def init_db():
    """
    Initialize the Database Tables.
    """
    connection = sqlite3.connect('database.db')
    filepath = os.path.join(DIR, 'db', 'create_tables.sql')  # DELETE LATER (fix DIR variable)
    print("OS FILEPATH", filepath)
    with open(filepath) as f:
        connection.executescript(f.read())
    # cur = connection.cursor()
    # cur.execute("INSERT INTO products (name, description) VALUES (?, ?)",
    #             ('bleach', 'chemical for cleaning'))
    connection.commit()
    connection.close()


# def get_db(db=None):
def get_db():
    """
    Connect to Database

    https://flask.palletsprojects.com/en/3.0.x/tutorial/database/
    """
    # init_db()

    db = getattr(g, '_database', None)
    if db is None:
        filepath = os.path.join(DIR, 'db', 'tesi_tool.sqlite3')  # DELETE LATER (fix DIR variable)
        # Connects to the SQLite3 database and returns the connection
        db = g._database = sqlite3.connect(filepath)
        # https://docs.python.org/3/library/sqlite3.html
        sqlite3.register_adapter(bool, int)
        sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
        db.row_factory = sqlite3.Row
        setattr(g, '_database', db) 
    return db


def query_db(query, args=(), one=False, want_id=False):
    '''Takes a query and optional parameters to execute a query on
       the database and return the result'''
    
    #  Get the home directory of the user in order to persistently save database updates there.
    # home_dir = os.path.expanduser("~")

    db = get_db()
    db_cursor = db.cursor()
    cursor = db.execute(query, args)
    if one:
        single_row = cursor.fetchone()
        db.commit()
        cursor.close()
        if want_id:
            (inserted_id, ) = single_row if single_row else None
            return inserted_id
        return single_row
    db_cursor.close()
    
    rows = cursor.fetchall()
    #for row in rows[-5:]:
        #print(dict(row))
    db.commit()
    cursor.close()
    if rows:
        return rows
    return None


def render_with_error_handling(template, **kwargs):
    """
    Tries to render a template and returns a 500 error page if an exception occurs.
    """
    try:
        return render_template(template, **kwargs), 201
    except:
        t = traceback.format_exc()
        return render_template('error.html', args={'trace': t}), 500


def polling(num, second_cnt, global_window_open_timestamp, heartbeat, dev_mode=False):
    """
    Polling Helper Function for Back-End Server.
    """
    if dev_mode:
        if num == 0:
            if second_cnt == 1:
                print(f"Polling    ({second_cnt} second)")    
            else:
                print(f"Polling    ({second_cnt} seconds)")
        if num == 1:
            print(f"Polling.   ({second_cnt} seconds)")
        if num == 2:
            print(f"Polling..  ({second_cnt} seconds)")
        if num == 3:
            print(f"Polling... ({second_cnt} seconds)")
        num += 1
        second_cnt += 1
        if num < 0 or num > 3:
            num = 0

    threshold = global_window_open_timestamp + (2*heartbeat)
    if time.time() >= threshold:  # if current time is greater than timestamp + double heartbeat
        return num, second_cnt, False
    return num, second_cnt, True
