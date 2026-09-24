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
import webbrowser
import sys


# ------------------ GLOBAL VARIABLES ------------------

# print("FACILITY OVERVIEW OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')

facility_blueprint = Blueprint('facility_blueprint', __name__, static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

@facility_blueprint.route('/facility_overview', methods=['GET', 'POST'])
def facility_overview():
    """
    Facility Overview Page
    """
    try:
        if request.method == 'GET':
            facility_query = 'SELECT * FROM facility_overview;'
            db_facility = query_db(facility_query)

            if db_facility:
                payment_query = 'SELECT * FROM payment_methods;'
                db_payments = query_db(payment_query)

                return render_with_error_handling('facility_overview.html', facility=db_facility, payments=db_payments)
            else:

                # response = make_response({'error': 204, 'message': 'No customers to display because the database is empty.'})
                # response.headers["Content-Type"] = "text/html"
                return render_with_error_handling('facility_overview.html', facility=None)
            
        if request.method == 'POST':
            facility = request.form

            
            facility.company_type = ';'.join(request.form.getlist("company_type"))

            facility.sales_tracking = True if request.form.get("sales_tracking") != None else False

            if request.form.get("facility_id"):
                query = 'UPDATE facility_overview SET facility_name = ?, facility_country = ?, company_type = ?, \
                        types_of_customers = ?, facility_address = ?, facility_phone_number = ?, facility_email = ?, transportation = ?, \
                        shipping_coordinator = ?, sales_tracking = ?, shipment_verification = ?, permits_required = ?, \
                        preparation_procedures = ?, payment_types = ?, order_methods = ?, payment_timing = ? WHERE facility_id = ?;'
                unsuccessful_update = query_db(query, [facility.get("facility_name"), facility.get("facility_country"), 
                                                        ';'.join(request.form.getlist("company_type")), ';'.join(request.form.getlist("types_of_customers")),
                                                        facility.get("facility_address"), facility.get("facility_phone_number"),
                                                        facility.get("facility_email"), ';'.join(request.form.getlist("transportation")),
                                                        ';'.join(request.form.getlist("shipping_coordinator")), facility.get("sales_tracking"), 
                                                        facility.get("shipment_verification"), facility.get("permits_required"), 
                                                        facility.get("preparation_procedures"), ';'.join(request.form.getlist("payment_types")), 
                                                        facility.get("order_methods"), ';'.join(request.form.getlist("payment_timing")),
                                                        facility.get("facility_id")])
                if not unsuccessful_update:

                    return redirect('/facility_overview')
                else:

                    response = make_response({'error': 406, 'message': 'The Product ID provided for updating does not exist.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
            else:
                facility_query = "INSERT INTO facility_overview (facility_name, facility_country, company_type, \
                        types_of_customers, facility_address, facility_phone_number, facility_email, transportation, \
                        shipping_coordinator, sales_tracking, shipment_verification, permits_required, \
                        preparation_procedures, payment_types, order_methods, payment_timing) VALUES \
                        (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING facility_id;"
                facility_id = query_db(facility_query, [
                    facility.get("facility_name"),
                    facility.get("facility_country"),
                    ';'.join(request.form.getlist("company_type")),
                    ';'.join(request.form.getlist("types_of_customers")),
                    facility.get("facility_address"),
                    facility.get("facility_phone_number"),
                    facility.get("facility_email"),
                    ';'.join(request.form.getlist("transportation")), 
                    ';'.join(request.form.getlist("shipping_coordinator")), 
                    facility.get("sales_tracking"), 
                    facility.get("shipment_verification"), 
                    facility.get("permits_required"), 
                    facility.get("preparation_procedures"), 
                    ';'.join(request.form.getlist("payment_types")), 
                    facility.get("order_methods"), 
                    ';'.join(request.form.getlist("payment_timing"))
                    ], one=True, want_id=True)
                if facility_id:

                    return redirect('facility_overview')
                else:

                    response = make_response({'error': 406, 'message': 'The Post HTTP Method for /orders/customer_order failed.'})                    
                    response.headers["Content-Type"] = "application/json"
                    return response, 406
            


        # if request.method == 'DELETE':
        #     query = 'DELETE FROM orders WHERE order_id = ?;'
        #     order = dict(request.form)
        #     print("\n\nOrder ID to DELETE: ", order)
        #     order_id = order.get("order_id")
        #     unsuccessful_removal = query_db(query, [order.get("order_id")])
        #     print("unsuccessful_removal variable is: ", unsuccessful_removal)
        #     if not unsuccessful_removal:
        #         print("Order removed successfully!")
        #         return jsonify({"Deleted ID:": order_id}), 201
        #     else:
        #         print("The DELETE HTTP Method for /orders/customer_order failed because the Order ID provided does not exist.")
        #         response = make_response({'error': 406, 'message': 'The Order ID provided for removal does not exist.'})
        #         response.headers["Content-Type"] = "application/json"
        #         return response, 406
    except Exception as e:

        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400

    return render_with_error_handling('facility_overview.html')