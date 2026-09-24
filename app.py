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
from back_end.endpoint_blueprints.general import general_blueprint
from back_end.endpoint_blueprints.customer import customer_blueprint
from back_end.endpoint_blueprints.customers import customers_blueprint
from back_end.endpoint_blueprints.orders import orders_blueprint
from back_end.endpoint_blueprints.products import products_blueprint
from back_end.endpoint_blueprints.facility_overview import facility_blueprint
from back_end.endpoint_blueprints.manage_data import data_blueprint
from back_end.utils.util import init_db, get_db, query_db, render_with_error_handling, polling
import webbrowser as wb
import sys
from threading import Thread, Timer
import time
from datetime import timedelta
from werkzeug.serving import make_server
import requests


# ------------------ GLOBAL VARIABLES ------------------

DIR = os.path.dirname(__file__)
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')
RUNNING = True
WINDOW_OPEN_TIMESTAMP = time.time()  # Check every 4 minutes
SERVER = None


# ------------------ GENERAL FLASK APPLICATION SET-UP ------------------

class ServerThread(Thread):
    """
    Inherited Thread Object for Managing Flask Application.
    """
    def __init__(self, app):
        Thread.__init__(self)
        self.server = make_server('127.0.0.1', 5000, app)
        self.ctx = app.app_context()
        self.ctx.push()
    def run(self):

        self.server.serve_forever()
    def shutdown(self):
        self.server.shutdown()


def create_app():
    """
    Transaction Evaluation for Suspicious Indicators (TESI) Know-Your-Customer (KYC) Tool

    Source:
        https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c
    """
    global SERVER, RUNNING, WINDOW_OPEN_TIMESTAMP

    # App configuration defined here:
    app = Flask(__name__, static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)
    app.config["SECRET_KEY"] = "\xbaN\x1b\x9c\xfaB\xf4u\xdc\x11?%\xec[\x872a\xa1\x93M\x7f\x0fC\xba"
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.config["TEMPLATES_AUTO_RELOAD"] = True  # DELETE LATER - should be None by default.
    app.config["DEBUG"] = True  # DELETE LATER - should be False by default.  Can also run "export FLASK_DEBUG=True" or "export FLASK_DEBUG=False" from terminal.
    # app.config["ENV"] = 'development'  # DELETE LATER - should be 'production' by default.  Can also run "export FLASK_ENV=development" or "export FLASK_ENV=production" from terminal.
    # app.config.update(
    # TESTING=True,
    # SECRET_KEY=b'_5#y2L"F4Q8z\n\xec]/'
    # )
    
    app.register_blueprint(general_blueprint)
    app.register_blueprint(customer_blueprint)
    app.register_blueprint(customers_blueprint)
    app.register_blueprint(orders_blueprint)
    app.register_blueprint(products_blueprint)
    app.register_blueprint(facility_blueprint)
    app.register_blueprint(data_blueprint)
    bootstrap = Bootstrap5(app)

    @app.route('/')
    def splash():
        return render_template('splash.html')

    @app.route('/shutdown')
    def shutdown_app():
        """Shutdown the TESI Tool flask application from Flask Endpoint."""

        global RUNNING
        RUNNING = False
        return render_with_error_handling('shutdown.html')
    
    def browser_timeout():
        """Browser window timeout due to inactivity, so shutdown app."""

        global RUNNING
        RUNNING = False
        return render_with_error_handling('timeout.html')
    
    @app.route('/is_open', methods=['GET', 'POST'])
    def is_open():
        """Check if the user's browser window is still open."""

        global WINDOW_OPEN_TIMESTAMP
        if request.method == 'POST':
            try:
                window_open = request.form["is-window-open"]  # returns the string: "Window Open"

                if window_open:

                    WINDOW_OPEN_TIMESTAMP = time.time()
                    return make_response({'error': 201, 'message': 'CONFIRMED - The user still has the window open.'}), 201
                else:

                    return redirect("/shutdown")
            except:

                response = {'error': 404, 'message': 'No is-window-open variable was found from the webform.'}
                return render_with_error_handling("error.html", args=response)
        if request.method == 'GET':

            response = make_response({'error': 405, 'message': 'The GET HTTP Method for /is_open failed because it has not been set up. This endpoint is only meant to be used for POST Methods.'})
            response.headers["Content-Type"] = "application/json"
            return response, 405

    # App run code defined here
    interval = 0
    time_count = 1  # in seconds
    try:
        SERVER = ServerThread(app)
        SERVER.start()
        while True:
            response = requests.get('http://127.0.0.1:5000/')
            if response.ok:
                # source at: https://linuxhint.com/python-requests-ok/

                break

            time.sleep(1)
        time.sleep(2)
        wb.open('http://127.0.0.1:5000/', new=1)

    except Exception as e:

        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400
    heartbeat = 60 * 4  # 4minutes = (60seconds * 4)
    while RUNNING:
        interval, time_count, browser_open = polling(interval, time_count, WINDOW_OPEN_TIMESTAMP, heartbeat)
        if not browser_open:
            # browser_timeout()  # add this in case the browser window was not closed, but after a certain amount of inactivity
            RUNNING = False
        time.sleep(1)
    time.sleep(1)
    SERVER.shutdown()
    SERVER.join()



def shutdown_server():
    """
    Shutdown Server from Python Side (rather than Flask).
    """
    global SERVER
    SERVER.shutdown()


if __name__ == "__main__":
    # Documentation for Dev/Debug Mode:
    # https://flask.palletsprojects.com/en/3.0.x/quickstart/#debug-mode
    
    # app.run(debug=True)

    # export FLASK_APP="app:create_app()"  # run this from terminal (if on Windows, use 'set' instead of 'export')
    create_app()
