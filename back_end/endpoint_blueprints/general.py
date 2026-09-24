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
from back_end.utils.util import get_db, query_db, render_with_error_handling
from back_end.utils.sanctions_query import run_search
import webbrowser
import sys


# ------------------ GLOBAL VARIABLES ------------------

# print("GENERAL OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')
# SERVER = app.SERVER
# RUNNING = app.RUNNING

general_blueprint = Blueprint('general_blueprint', __name__, static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

# @general_blueprint.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()


# DELETE LATER
# @general_blueprint.before_request
# def before_request():
#     """
    
#     Source:
#         https://mulgrew.me/posts/session-timeout-flask.html
#     """
#     session.permanent = False
#     app.permanent_session_lifetime = timedelta(minutes=0.5)
#     session.modified = True


@general_blueprint.route('/index')
def home():
    """
    Landing/Home Page
    """
    # TODO
    # return render_with_error_handling('home.html')
    return render_template('home.html')


@general_blueprint.route('/about_tesi', methods=['GET'])
def about_tesi():
    """
    About TESI Page
    """
    return render_template('about_tesi.html')


@general_blueprint.route('/licenses', methods=['GET'])
def licenses():
    """
    TESI Licenses Page
    """
    return render_template('licenses.html')


# @general_blueprint.route('/quit', methods=['GET'])
# @general_blueprint.route('/exit', methods=['GET'])
# @general_blueprint.route('/shutdown', methods=['GET'])
# def shutdown_app():
#     """
#     Shutdown the TESI Tool flask application.
#     """
#     print("~~~ Commencing Server Shutdown ~~~")

#     # global SERVER, RUNNING
#     # SERVER.shutdown()
#     # SERVER.join()
#     # exit(0)
#     app.RUNNING = False
#     # print("Running switched to False")
#     return "<h1>DISCONNECTED</h1> <h2>You may now close this window.</h2>"


@general_blueprint.route('/sanctions_query', methods=['POST'])
def query_sanctions():
    """
    query sanctions
    """
    if request.method == 'POST':
        try:
            form = dict(request.form)
            if form.get("search_name") is None:

                response = make_response({'status': 400})
                response.headers["Content-Type"] = "application/json"
                return response, 400
            results = run_search(form.get("search_name"), form.get("search_address"))
            return jsonify(results), 200
        except Exception as e:

            response = make_response({'status': 400, 'error': e})
            response.headers["Content-Type"] = "application/json"
            return response, 400
