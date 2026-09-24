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
import datetime


# ------------------ GLOBAL VARIABLES ------------------

# print("ORDERS OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')

orders_blueprint = Blueprint('orders_blueprint', __name__, url_prefix='/orders', static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

@orders_blueprint.route('/customer_order', methods=['GET', 'POST', 'DELETE'])
def customer_order():
    """
    Customer Order Page
    """
    try:
        if request.method == 'GET':
            orders_query = 'SELECT c.customer_name, c.phone_number, o.*, m.order_method_name, (SELECT sum(quantity) FROM order_item i WHERE i.order_id = o.order_id) AS num_units, \
                julianday(o.delivery_date) - julianday("now") AS active_order \
                FROM orders o \
                LEFT JOIN customers c ON o.customer_id = c.customer_id \
                LEFT JOIN order_methods m ON o.order_method = m.order_method_id;'
            db_orders = query_db(orders_query)

            customer_query = 'SELECT customer_id, customer_name, phone_number, poc_name, poc_email, hq_country, address_proof_type_id FROM customers;'
            db_customers = query_db(customer_query)

            if db_customers:
                #product_list_query = 'SELECT product_id, name, cas, packaging_types.packaging_type_name AS packaging, size, other_issues, concerns FROM products LEFT JOIN packaging_types ON products.packaging = packaging_types.packaging_type_id;'
                product_list_query = 'SELECT DISTINCT name FROM products;'
                db_products = query_db(product_list_query)
                # if db_products is None:
                #     print("The PUT HTTP Method for /orders/customer_order failed because the no products exist in the database.")
                #     response = make_response({'error': 406, 'message': 'No products exist in the database. Please visit the Product tab to enter a product for sale.'})
                #     response.headers["Content-Type"] = "text/html"
                #     return response, 406

                payment_query = 'SELECT * FROM payment_methods;'
                db_payments = query_db(payment_query)

                return render_with_error_handling('orders/orderForm.html', customers=db_customers or [], orders=db_orders, products=db_products or [], payments=db_payments)
            else:
                print("The GET HTTP Method for /orders/customer_order failed because there are no customers in the database to display.")
                response = make_response({'error': 204, 'message': 'No customers to display because the database is empty.'})
                response.headers["Content-Type"] = "text/html"
                # return response, 204
                # return {'error': 'Problem getting customers or no customers to show.'}, 204
                return render_with_error_handling('orders/orderForm.html', customers={"customer_name": None, 
                                                        "phone_number": None, 
                                                        "poc_name": None, 
                                                        "poc_email": None,
                                                        "hq_country": None,
                                                        "address_proof_type_id": None}, orders=order)
        if request.method == 'POST':
            # print("~~~~~~~~~~path is:", os.path.join(DIR, 'back_end', 'db', 'order_example.json'))
            # f = open(os.path.join(DIR, 'back_end', 'db', 'order_example.json'))  # comment/delete out when using real form (and not the order_example.json)
            # order = json.load(f)  # comment/delete out when using real form (and not the order_example.json)
            
            # order = dict(request.form)  # uncomment out when using real form (and not the order_example.json)
            order = request.form
            print("~~~~~~~ORDER IS: ", order)

            # products_string = request.form.get("products")
            # products = json.loads(products_string)
            # print("~~~~~~~PRODUCT ITEMS ARE: ", products)
            # response = make_response({'error': 400, 'message': "Bad Request"})
            # response.headers["Content-Type"] = "application/json"
            # return response, 400

            if request.form.get("order_id"):
                #orders_query = 'UPDATE orders SET order_date = ?, customer_id = ? WHERE customer_id = ? RETURNING order_id;'
                orders_query = "UPDATE orders SET order_date = ?, delivery_date = ?, customer_id = ?, poc_name = ?, address_different = ?, \
                    bank_name_different = ?, bank_address_different = ?, payment_different = ?, atypical_order = ?, larger_order = ?, \
                    end_use_verified = ?, urgent_shipping = ?, immediate_custody = ?, first_time_transporter = ?, \
                    shipment_verification = ?, unusual_routing = ?, unusual_labeling = ?, unusual_handling = ?, ppe_concern = ?, \
                    route_safety_concern = ?, order_method = ?, transporter_name = ?, transporter_address = ?, transporter_phone = ?, facility_order_id = ?, \
                        shipping_address = ?, order_bank = ?, payment_method_id = ? WHERE order_id = ? RETURNING order_id;"
                updated_order_id = query_db(orders_query, [
                    order.get("order_date"), order.get("delivery_date"), order.get("customer_id"), order.get("poc_name"), order.get("address_different"), 
                    order.get("bank_name_different"), order.get("bank_address_different") or False, order.get("payment_different"), 
                    order.get("atypical_order"), order.get("larger_order"), order.get("end_use_verified"), order.get("urgent_shipping"), 
                    order.get("immediate_custody"), order.get("first_time_transporter"), order.get("shipment_verification"), 
                    order.get("unusual_routing"), order.get("unusual_labeling"), order.get("unusual_handling"), 
                    order.get("ppe_concern"), order.get("route_safety_concern") or False, order.get("order_method"), order.get("transporter_name"),
                    order.get("transporter_address"), order.get("transporter_phone"), order.get("facility_order_id"), order.get("shipping_address"),
                    order.get("order_bank"), order.get("payment_method_id"), order.get("order_id")
                    ], one=True, want_id=True)
                if updated_order_id > 0:
                    # products = list(order.get("products"))
                    products_string = request.form.get("products")
                    products = json.loads(products_string)
                    product_ids = []
                    for product in products:
                        product_dict = dict(product)
                        print("Updated Product ID",product_dict.get("product_id"))
                        product_ids.append(product_dict.get("product_id"))
                        order_item_query = "INSERT OR REPLACE INTO order_item (order_item_id, order_id, product_id, quantity) VALUES (?, ?, ?, ?) RETURNING order_item_id;"
                        order_item_id = query_db(order_item_query, [product_dict.get("order_item_id"), updated_order_id, product_dict.get("product_id"), product_dict.get("quantity")], one=True, want_id=True)
                        
                        print("Updated Order Item ID",order_item_id)
                        if order_item_id:
                            print("Product added to order successfully!")
                        else:
                            print("The Post HTTP Method for /orders/customer_order of adding a product to the order failed.")
                            response = make_response({'error': 406, 'message': 'The Post HTTP Method for /orders/customer_order of adding a product to the order failed.'})                    
                            response.headers["Content-Type"] = "application/json"
                            return response, 406
                    return jsonify({"new_order_id": updated_order_id, "product_ids": product_ids}), 201
                else:
                    print("The PUT HTTP Method for /orders/customer_order failed because the Order ID provided does not exist.")
                    response = make_response({'error': 406, 'message': 'The Order ID provided for updating does not exist.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 406

            if not request.form.get("customer_id") or not request.form.get("products"):
                response = make_response({'error': 400, 'message': "Bad Request"})
                response.headers["Content-Type"] = "application/json"
                return response, 400
            # add UPDATE query
            # query = 'UPDATE orders SET order_date = ?, customer_id = ? WHERE customer_id = ? RETURNING order_id;'
            orders_query = "INSERT INTO orders (order_date, delivery_date, customer_id, poc_name, address_different, \
                     bank_name_different, bank_address_different, payment_different, atypical_order, larger_order, \
                     end_use_verified, urgent_shipping, immediate_custody, first_time_transporter, \
                     shipment_verification, unusual_routing, unusual_labeling, unusual_handling, ppe_concern, \
                     route_safety_concern, order_method, transporter_name, transporter_address, transporter_phone, facility_order_id, shipping_address, \
                        payment_method_id, order_bank) VALUES \
                     (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING order_id;"
            new_order_id = query_db(orders_query, [
                order.get("order_date"), order.get("delivery_date"), order.get("customer_id"), order.get("poc_name"), order.get("address_different"), 
                order.get("bank_name_different"), order.get("bank_address_different") or False, order.get("payment_different"), 
                order.get("atypical_order"), order.get("larger_order"), order.get("end_use_verified"), order.get("urgent_shipping"), 
                order.get("immediate_custody"), order.get("first_time_transporter"), order.get("shipment_verification"), 
                order.get("unusual_routing"), order.get("unusual_labeling"), order.get("unusual_handling"), 
                order.get("ppe_concern"), order.get("route_safety_concern") or False, order.get("order_method"), order.get("transporter_name"),
                order.get("transporter_address"), order.get("transporter_phone"), order.get("facility_order_id"),
                order.get("shipping_address"), order.get("payment_method_id"), order.get("order_bank")
                ], one=True, want_id=True)
            
            if new_order_id:
                print("Order updated successfully!")
                # products = list(order.get("products"))
                products_string = request.form.get("products")
                products = json.loads(products_string)

                print("~~~~~~~PRODUCT ITEMS ARE: ", products)
                product_ids = []
                for product in products:
                    product_dict = dict(product)
                    product_ids.append(product_dict.get("product_id"))
                    order_item_query = "INSERT INTO order_item (order_id, product_id, quantity) VALUES (?, ?, ?) RETURNING order_item_id;"
                    order_item_id = query_db(order_item_query, [new_order_id, product_dict.get("product_id"), product_dict.get("quantity")], one=True, want_id=True)
                    if order_item_id:
                        print("Product added to order successfully!")
                    else:
                        print("The Post HTTP Method for /orders/customer_order of adding a product to the order failed.")
                        response = make_response({'error': 406, 'message': 'The Post HTTP Method for /orders/customer_order of adding a product to the order failed.'})                    
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                return jsonify({"new_order_id": new_order_id, "product_ids": product_ids}), 201
            else:
                print("The Post HTTP Method for /orders/customer_order failed.")
                response = make_response({'error': 406, 'message': 'The Post HTTP Method for /orders/customer_order failed.'})                    
                response.headers["Content-Type"] = "application/json"
                return response, 406
        if request.method == 'DELETE':
            query = 'DELETE FROM orders WHERE order_id = ?;'
            order = dict(request.form)
            print("\n\nOrder ID to DELETE: ", order)
            order_id = order.get("order_id")
            unsuccessful_removal = query_db(query, [order.get("order_id")])
            print("unsuccessful_removal variable is: ", unsuccessful_removal)
            if not unsuccessful_removal:
                print("Order removed successfully!")
                items_query = 'DELETE FROM order_item WHERE order_id = ?;'
                unsuccessful_items_removal = query_db(items_query, [order.get("order_id")])
                return jsonify({"Deleted ID:": order_id}), 201
            else:
                print("The DELETE HTTP Method for /orders/customer_order failed because the Order ID provided does not exist.")
                response = make_response({'error': 406, 'message': 'The Order ID provided for removal does not exist.'})
                response.headers["Content-Type"] = "application/json"
                return response, 406
    except Exception as e:
        print("The Connection failed for endpoint /orders/customer_order.")
        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400


@orders_blueprint.route('/customer_order/<order_id>', methods=['GET', 'POST', 'DELETE'])
def order_details(order_id=None):
    """
    Order Details View/Update Page
    """

    try:
        if request.method == 'GET':
            orders_query = 'SELECT c.customer_name, c.phone_number, o.*, m.order_method_name, (SELECT sum(quantity) FROM order_item i WHERE i.order_id = o.order_id) AS num_units \
                FROM orders o \
                LEFT JOIN customers c ON o.customer_id = c.customer_id \
                LEFT JOIN order_methods m ON o.order_method = m.order_method_id \
                    WHERE order_id = ?;'
            db_orders = query_db(orders_query, [order_id], True)

            if db_orders:
                products_query = 'SELECT p.name, o.* FROM order_item o LEFT JOIN products p ON o.product_id = p.product_id WHERE o.order_id = ?;'
                db_products = query_db(products_query, [order_id])

                orders = dict(db_orders)
                if db_products:
                    orders['products'] = [dict(row) for row in db_products]
                else: orders['products'] = []

                # Get history of past shipping addresses
                addresses_query = 'SELECT DISTINCT order_id, shipping_address FROM orders WHERE customer_id = ?;'
                db_addresses = query_db(addresses_query, [db_orders["customer_id"]])
                addresses = [dict(row) for row in db_addresses]

                # Get history of past banks
                banks_query = 'SELECT DISTINCT order_id, order_bank FROM orders WHERE customer_id = ?;'
                db_banks = query_db(banks_query, [db_orders["customer_id"]])
                banks = [dict(row) for row in db_banks]
                
                return jsonify({"orders": orders, "addresses": addresses, "banks": banks}), 200
            else:
                response = make_response({'error': 204, 'message': 'No order registered with that ID.'})
                response.headers["Content-Type"] = "application/json"
                return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /orders/customer_order.")
        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400
    
@orders_blueprint.route('/customer_order/shipping_history/<customer_id>', methods=['GET', 'POST', 'DELETE'])
def shipping_history(customer_id=None):
    """
    Customer details for new orders
    """

    print("~~~ Customer ID: ", customer_id)

    try:
        if request.method == 'GET':
            # Get history of past shipping addresses
            addresses_query = 'SELECT DISTINCT shipping_address FROM (SELECT shipping_address FROM orders WHERE customer_id = ? UNION SELECT customer_address FROM customer_addresses WHERE customer_id = ?);'
            db_addresses = query_db(addresses_query, [customer_id, customer_id])

            if db_addresses:
                addresses = [dict(row) for row in db_addresses]
                
                return jsonify(addresses), 200
            else:
                response = make_response({'error': 204, 'message': 'No shipping history from customer with that ID.'})
                response.headers["Content-Type"] = "application/json"
                return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /orders/customer_order/shipping_history/.")
        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400
    
@orders_blueprint.route('/customer_order/bank_history/<customer_id>', methods=['GET', 'POST', 'DELETE'])
def bank_history(customer_id=None):
    """
    Customer details for new orders
    """

    print("~~~ Customer ID: ", customer_id)

    try:
        if request.method == 'GET':
            # Get history of past shipping addresses
            banks_query = 'SELECT DISTINCT order_bank FROM (SELECT order_bank FROM orders WHERE customer_id = ? UNION SELECT concat(bank_name, " ",  bank_address) AS order_bank FROM customer_banks WHERE customer_id = ?);'
            db_banks = query_db(banks_query, [customer_id, customer_id])

            if db_banks:
                banks = [dict(row) for row in db_banks]
                
                return jsonify(banks), 200
            else:
                response = make_response({'error': 204, 'message': 'No bank history from customer with that ID.'})
                response.headers["Content-Type"] = "application/json"
                return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /orders/customer_order/bank_history/.")
        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400
    
@orders_blueprint.route('/customer_order/by_customer/<customer_id>', methods=['GET', 'POST', 'DELETE'])
def orders_by_customer(customer_id=None):
    """
    Order Details View/Update Page
    """

    try:
        if request.method == 'GET':
            orders_query = 'SELECT * FROM orders WHERE customer_id = ? ORDER BY order_date DESC, order_id DESC LIMIT 1;'
            db_orders = query_db(orders_query, [customer_id], True)

            if db_orders:
                orders = dict(db_orders)
                return jsonify(orders), 200
            else:
                response = make_response({'error': 204, 'message': 'No order registered with that ID.'})
                response.headers["Content-Type"] = "application/json"
                return response, 204
    except Exception as e:
        print("The Connection failed for endpoint /orders/customer_order.")
        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400