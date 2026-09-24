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

# print("CUSTOMERS OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')

customers_blueprint = Blueprint('customers_blueprint', __name__, url_prefix='/customers', static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

@customers_blueprint.route('/customer_database', methods=['GET', 'POST', 'DELETE'])
def customer_database():
    """
    Customer Database Page
    """
    try:
        if request.method == 'GET':
            query = 'SELECT * FROM customers;'
            db_customers = query_db(query)
            if db_customers:
                address_proofs_query = 'SELECT address_proof_type_id, proof_type FROM address_proof_type;'
                db_address_proofs = query_db(address_proofs_query)
                payment_method_query = 'SELECT payment_method_id, payment_method_name FROM payment_methods;'
                db_payment_methods = query_db(payment_method_query)
                return render_with_error_handling('customers/customer_database.html', customers=db_customers, payment_methods=db_payment_methods, address_proofs=db_address_proofs)
            else:

                response = make_response({'error': 204, 'message': 'No customers to display because the database is empty.'})
                response.headers["Content-Type"] = "text/html"
                # return response, 204
                # return {'error': 'Problem getting customers or no customers to show.'}, 204
                return render_with_error_handling('customers/customer_database.html', 
                                                  customers={"customer_name": None, 
                                                            "phone_number": None, 
                                                            "poc_name": None, 
                                                            "poc_email": None,
                                                            "hq_country": None,
                                                            "address_proof_type_id": None,
                                                            "address_proof_accept": None,
                                                            "poc_dob": None,
                                                            "poc_nationality": None,
                                                            "poc_parent_name": None,
                                                            "business_num": None,
                                                            "business_type": None,
                                                            "third_party_ref_name": None,
                                                            "third_party_contact_info": None,
                                                            "payment_method_id": None,
                                                            "order_frequency": None,
                                                            "sanctioned": None,
                                                            "trusted_customer": None,
                                                            "verification_date": None,
                                                            "facility_customer_id": None})

        if request.method == 'POST':


            customer = dict(request.form)
            if customer.get("customer_id"):
                if customer.get("customer_name"):
                    query = 'UPDATE customers SET customer_name = ?, phone_number = ?, poc_name = ?, poc_email = ?, \
                            hq_country = ?, address_proof_type_id = ?, address_proof_accept = ?, poc_dob = ?, \
                            poc_nationality = ?, poc_parent_name = ?, business_num = ?, business_type = ?, \
                            third_party_ref_name = ?, third_party_contact_info = ?, payment_method_id = ?, \
                            order_frequency = ?, sanctioned = ?, trusted_customer = ?, verification_date = ?, facility_customer_id = ?  WHERE customer_id = ?;'
                    unsuccessful_update = query_db(query, [
                        customer.get("customer_name"),
                        customer.get("phone_number"),
                        customer.get("poc_name"),
                        customer.get("poc_email"),
                        customer.get("hq_country"),
                        customer.get("address_proof_type_id") or None,
                        customer.get("address_proof_accept"),
                        customer.get("poc_dob"),
                        customer.get("poc_nationality"),
                        customer.get("poc_parent_name"),
                        customer.get("business_num"),
                        customer.get("business_type"),
                        customer.get("third_party_ref_name"),
                        customer.get("third_party_contact_info"),
                        customer.get("payment_method_id"),
                        customer.get("order_frequency"),
                        customer.get("sanctioned"),
                        customer.get("trusted_customer"),
                        customer.get("verification_date"),
                        customer.get("facility_customer_id"),
                        customer.get("customer_id")
                        ])
                    if not unsuccessful_update:

                        return jsonify({"customer_id": customer.get("customer_id")}), 200
                    else:

                        response = make_response({'error': 406, 'message': 'The customer ID provided for updating does not exist.'})
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                else:

                    response = make_response({'error': 400, 'message': 'You did not provide any of the required parameters (ie, customer ID, required update fields, etc) for this HTTP Method.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 400
            else:
                if customer.get("customer_name"):
                    customer_object = Customer()  # Instantiate the customer object
                    query = customer_object.insert_query()
                    # customers = query_db(query, [customer.name, customer.cas, customer.packaging, customer.size, customer.hazard_codes, customer.concerns])  # can also add parameter:  one=True
                    new_id = query_db(query, customer_object.get_attributes(), one=True, want_id=True)
                    print("~~~ New Customer ID ~~~", new_id)
                    customer_object.set_id(new_id)

                    bank_query = 'INSERT INTO customer_banks (bank_name, bank_address, customer_id, sanctioned) VALUES (?, ?, ?, ?) RETURNING customer_bank_id;'
                    new_bank_id = query_db(bank_query, [customer_object.get_bank_info()[0],
                                                        customer_object.get_bank_info()[1],
                                                        new_id,
                                                        customer_object.get_bank_info()[2]], one=True, want_id=True)
                    
                    address_query = 'INSERT INTO customer_addresses (customer_address, customer_id, sanctioned) VALUES (?, ?, ?) RETURNING customer_address_id;'
                    # new_address_id = query_db(address_query, [customer.get_address_info()[0],
                    #                                           new_id,
                    #                                           customer.get_address_info()[1]], one=True, want_id=True)



                    # return redirect('/customers/customer_database')
                    return jsonify({"customer_address_id": new_id,
                    "customer_sanction_results": run_search(customer.get("customer_name"),
                                                            customer_object.get_address_info()[0]),
                                                            "bank_sanction_results": run_search(customer_object.get_bank_info()[0],
                                                                                                customer_object.get_bank_info()[1])}), 201
                else:

                    response = make_response({'error': 204, 'message': 'No Customer ID provided for updating.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
        if request.method == 'DELETE':
            query = 'DELETE FROM customers WHERE customer_id = ?;'
            customer = dict(request.form)

            cust_id = customer.get("customer_id")
            unsuccessful_removal = query_db(query, [customer.get("customer_id")])

            if not unsuccessful_removal:

                return jsonify({"Deleted ID:": cust_id}), 201
            else:

                response = make_response({'error': 406, 'message': 'The Customer ID provided for removal does not exist.'})
                response.headers["Content-Type"] = "application/json"
                return response, 406
    except Exception as e:

        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400


@customers_blueprint.route('/customer_details/<customer_id>', methods=['GET', 'POST'])
def customer_details(customer_id=None, customer_name=None, phone_number=None, 
                    poc_name=None, poc_email=None, hq_country=None,
                    address_proof_type_id=None, address_proof_accept=None,
                    poc_dob=None, poc_nationality=None, poc_parent_name=None,
                    business_num=None, business_type=None, third_party_ref_name=None,
                    third_party_contact_info=None, payment_method_id=None,
                    order_frequency=None, sanctioned=None, trusted_customer=None,
                    verification_date=None, facility_customer_id=None):

    """
    Details of a Single customer Object Page

    Source: Serialization of a pandas DataFrame
        https://stackoverflow.com/questions/16936608/storing-bools-in-sqlite-database
        https://stackoverflow.com/questions/16971803/serialization-of-a-pandas-dataframe
    """
    # https://www.geeksforgeeks.org/flask-http-method/

    try:
        if request.method == 'GET':
            query = 'SELECT customer_id, customer_name, phone_number, poc_name, poc_email, hq_country, address_proof_type_id, address_proof_accept, poc_dob, poc_nationality, poc_parent_name, business_num, business_type, third_party_ref_name, third_party_contact_info, payment_method_id, order_frequency, sanctioned, trusted_customer, verification_date, facility_customer_id FROM customers WHERE customer_id = ?;'
            db_customer = query_db(query, [customer_id], one=True)
                        
            # flash("Power has been turned ON")
            if db_customer:
                return jsonify(dict(db_customer)), 201
            else:
                response = make_response({'error': 204, 'message': 'No Customer ID provided for retrieval, or that customer ID does not exist.'})
                response.headers["Content-Type"] = "application/json"
                return response, 204
    except:    
        response = make_response({'error': 400, 'message': 'Sorry! This endpoint */customers/customer_details* has only been developed for GET requests.'})
        response.headers["Content-Type"] = "application/json"
        return response, 400
