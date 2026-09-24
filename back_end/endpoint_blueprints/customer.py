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

# print("CUSTOMER OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')

customer_blueprint = Blueprint('customer_blueprint', __name__, url_prefix='/customer', static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

@customer_blueprint.route('/banks/<customer_id>', methods=['GET', 'POST', 'PATCH'])
def customer_banks(customer_id=None):
    """
    Customer Banks View/Update Page
    """
    # EXAMPLE FIELDS:
    # order_form = {"bank_name": "Bank B", "bank_address": "100 Money Drive", "customer_id": 5}
    # order_form = {"bank_name": "US Bank", "bank_address": "456 Middle St", "customer_id": 5}
    # order_form = {"bank_name": "Chase Bank", "bank_address": "123 Main St", "customer_id": 3}
    bank_form = dict(request.form)
    try:
        if customer_id:
            if request.method == 'GET':
                query = 'SELECT customer_bank_id, bank_name, bank_address, sanctioned FROM customer_banks WHERE customer_id = ?;'
                db_banks = query_db(query, [customer_id])
                if db_banks:
                    banks = [dict(row) for row in db_banks]
                    return jsonify(banks), 201
                else:
                    response = make_response({'error': 204, 'message': 'No Banks registered with that Customer.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
            if request.method == 'POST':
                if bank_form.get("customer_bank_id"):
                    query = 'UPDATE customer_banks SET bank_name = ?, bank_address = ?, sanctioned = ? WHERE customer_bank_id = ? RETURNING customer_bank_id;'
                    new_id = query_db(query, [bank_form.get("bank_name"),
                                            bank_form.get("bank_address"),
                                            bank_form.get("sanctioned"),
                                            bank_form.get("customer_bank_id")], one=True, want_id=True)
                    if new_id:
                        return jsonify({"customer_bank_id": new_id,
                                        "bank_name": bank_form.get("bank_name"),
                                        "bank_address": bank_form.get("bank_address"),
                                        "sanctioned": bank_form.get("sanctioned"),
                                        "sanction_results": run_search(bank_form.get("bank_name"), 
                                                                       bank_form.get("bank_address"))}), 201
                    else:
                        print("The Post HTTP Method for /customer/banks failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/banks failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                elif bank_form.get("bank_name"):
                    query = 'INSERT INTO customer_banks (bank_name, bank_address, customer_id, sanctioned) VALUES (?, ?, ?, ?) RETURNING customer_bank_id;'
                    new_id = query_db(query, [bank_form.get("bank_name"),
                                              bank_form.get("bank_address") or None,
                                              customer_id,
                                              bank_form.get("sanctioned") or None], one=True, want_id=True)
                    if new_id:
                        print("Address information updated successfully!")
                        return jsonify({"customer_bank_id": new_id,
                                        "bank_address": bank_form.get("bank_address"),
                                        "sanctioned": bank_form.get("sanctioned"),
                                        "sanction_results": run_search(bank_form.get("bank_name"), 
                                                                       bank_form.get("bank_address"))}), 201
                    else:
                        print("The Post HTTP Method for /customer/banks update failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                else:
                    print("The Post HTTP Method for /customer/addresses failed.")
                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
            if request.method == 'PATCH':
                if bank_form.get("customer_bank_id"):
                    query = 'UPDATE customer_banks SET sanctioned = ? WHERE customer_bank_id = ? RETURNING customer_bank_id;'
                    new_id = query_db(query, [True, bank_form.get("customer_bank_id")], one=True, want_id=True)
                    if new_id:
                        print("Bank information updated successfully!")
                        return jsonify({"customer_bank_id": new_id,
                                        "bank_name": bank_form.get("bank_name"),
                                        "bank_address": bank_form.get("bank_address")}), 201
                    else:
                        print("The Post HTTP Method for /customer/banks failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/banks failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                else:
                    print("The Post HTTP Method for /customer/addresses failed.")
                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
        else:
            response = make_response({'error': 204, 'message': 'No Customer provided for retrieval of Bank Details.'})
            response.headers["Content-Type"] = "application/json"
            return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /customer/banks.")
        response = make_response({'error': 400, 'error': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400

    
@customer_blueprint.route('/addresses/<customer_id>', methods=['GET', 'POST', 'PATCH'])
def customer_addresses(customer_id=None):
    """
    Customer Addresses View/Update Page
    """
    # EXAMPLE FIELDS:
    # order_form = {"customer_address": "54 Purple Street, Moscow", "customer_id": 4}
    # order_form = {"customer_address": "123 Main St", "customer_id": 4}
    
    address_form = dict(request.form)
    try:
        #if order_form.get("customer_id"):
        if customer_id:
            if request.method == 'GET':
                query = 'SELECT customer_address_id, customer_address, sanctioned FROM customer_addresses WHERE customer_id = ?;'
                db_addresses = query_db(query, [customer_id])
                if db_addresses:
                    addresses = [dict(row) for row in db_addresses]
                    return jsonify(addresses), 201
                else:
                    response = make_response({'error': 204, 'message': 'No Addresses registered with that Customer.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
            if request.method == 'POST':
                print("Incoming address: ", address_form.get("new_address"))
                if address_form.get("customer_address_id"):
                    query = 'UPDATE customer_addresses SET customer_address = ?, sanctioned = ? WHERE customer_address_id = ? RETURNING customer_address_id;'
                    new_id = query_db(query, [address_form.get("new_address"),
                                              address_form.get("sanctioned"),
                                            address_form.get("customer_address_id")], one=True, want_id=True)
                    if new_id:
                        print("Address information updated successfully!")
                        search_address = address_form.get("customer_address") or None
                        return jsonify({"customer_address_id": new_id,
                                         "customer_address": search_address,
                                        "sanctioned": address_form.get("sanctioned"),
                                        "sanction_results": run_search(address_form.get("search_name"), 
                                                                       address_form.get("customer_address"))}), 201
                    else:
                        print("The Post HTTP Method for /customer/addresses failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                elif address_form.get("new_address"):
                    query = 'INSERT INTO customer_addresses (customer_address, customer_id, sanctioned) VALUES (?, ?, ?) RETURNING customer_address_id;'
                    new_id = query_db(query, [address_form.get("new_address"),
                                              customer_id,
                                              address_form.get("sanctioned")], one=True, want_id=True)
                    if new_id:
                        print("Address information updated successfully!")
                        return jsonify({"customer_address_id": new_id,
                                        "customer_address": address_form.get("new_address"),
                                        "sanctioned": address_form.get("sanctioned"),
                                        "sanction_results": run_search(address_form.get("search_name"), 
                                                                       address_form.get("new_address"))}), 201
                    else:
                        print("The Post HTTP Method for /customer/addresses failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                else:
                    print("The Post HTTP Method for /customer/addresses failed.")
                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
            if request.method == 'PATCH':
                if address_form.get("customer_address_id"):
                    query = 'UPDATE customer_addresses SET sanctioned = ? WHERE customer_address_id = ? RETURNING customer_address_id;'
                    new_id = query_db(query, [True, address_form.get("customer_address_id")], one=True, want_id=True)
                    if new_id:
                        print("Address information updated successfully!")
                        return jsonify({"customer_address_id": new_id,
                                        "customer_address": address_form.get("customer_address")}), 201
                    else:
                        print("The Post HTTP Method for /customer/addresses failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                else:
                    print("The Post HTTP Method for /customer/addresses failed.")
                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
        else:
            response = make_response({'error': 204, 'message': 'No Customer provided for retrieval of Address Details.'})
            response.headers["Content-Type"] = "application/json"
            return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /customer/addresses.")
        response = make_response({'error': 400, 'error': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400

    """
    Customer Addresses View/Update Page
    """
    # EXAMPLE FIELDS:
    # order_form = {"customer_address": "54 Purple Street, Moscow", "customer_id": 4}
    # order_form = {"customer_address": "123 Main St", "customer_id": 4}
    order_form = dict(request.form)
    try:
        if order_form.get("customer_id"):
            if request.method == 'GET':
                query = 'SELECT customer_address_id, customer_address, sanctioned FROM customer_addresses WHERE customer_id = ?;'
                db_addresses = query_db(query, [order_form.get("customer_id")])
                if db_addresses:
                    addresses = [dict(row) for row in db_addresses]
                    return jsonify(addresses), 201
                else:
                    response = make_response({'error': 204, 'message': 'No Addresses registered with that Customer.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
            if request.method == 'POST':
                query = 'UPDATE customer_addresses SET customer_address = ?, sanctioned = ? WHERE customer_id = ? RETURNING customer_address_id;'
                new_id = query_db(query, [order_form.get("customer_address"),
                                          order_form.get("sanctioned"),
                                          order_form.get("customer_id")], one=True, want_id=True)
                if new_id:
                    print("Address information updated successfully!")
                    return jsonify({"customer_address_id": new_id,
                                    "customer_address": order_form.get("customer_address"),
                                    "sanctioned": order_form.get("sanctioned")}), 201
                else:
                    print("The Post HTTP Method for /customer/addresses failed.")
                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/addresses failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
        else:
            response = make_response({'error': 204, 'message': 'No Customer provided for retrieval of Address Details.'})
            response.headers["Content-Type"] = "application/json"
            return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /customer/addresses.")
        response = make_response({'error': 400, 'error': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400

@customer_blueprint.route('/flag_addresses/<entity_id>', methods=['POST'])
def flag_addresses(entity_id=None):
    """
    Customer Addresses View/Update Page
    """    
    #address_form = dict(request.form)
    try:
        if entity_id:
            if request.method == 'POST':
                query = 'UPDATE customer_addresses SET sanctioned = ? WHERE customer_address_id = ? RETURNING customer_address_id;'
                new_id = query_db(query, [True, entity_id], one=True, want_id=True)
                if new_id:
                    print("Address information updated successfully!")
                    return jsonify({"customer_address_id": new_id}), 201
                else:
                    print("The Post HTTP Method for /customer/flag_addresses failed.")
                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/flag_addresses failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
        else:
            response = make_response({'error': 204, 'message': 'No address ID provided for retrieval of Address Details.'})
            response.headers["Content-Type"] = "application/json"
            return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /customer/flag_addresses.")
        response = make_response({'error': 400, 'error': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400
    

@customer_blueprint.route('/flag_bank/<entity_id>', methods=['POST'])
def flag_bank(entity_id=None):
    """
    Customer Addresses View/Update Page
    """    
    try:
        if entity_id:
            if request.method == 'POST':
                    query = 'UPDATE customer_banks SET sanctioned = ? WHERE customer_bank_id = ? RETURNING customer_bank_id;'
                    new_id = query_db(query, [True, entity_id], one=True, want_id=True)
                    if new_id:
                        print("Bank information updated successfully!")
                        return jsonify({"customer_bank_id": new_id}), 201
                    else:
                        print("The Post HTTP Method for /customer/flag_bank failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /customer/flag_bank failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
        else:
            response = make_response({'error': 204, 'message': 'No bank ID provided for retrieval of bank Details.'})
            response.headers["Content-Type"] = "application/json"
            return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /customer/flag_addresses.")
        response = make_response({'error': 400, 'error': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400