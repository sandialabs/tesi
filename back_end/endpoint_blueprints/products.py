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

# print("PRODUCTS OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')

products_blueprint = Blueprint('products_blueprint', __name__, url_prefix='/products', static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

@products_blueprint.route('/product_form', methods=['GET', 'POST'])
def product_form(product_id=None):
    """
    Product Risk Assessment Page
    """
    # TODO
    if product_id:
        return render_with_error_handling('products/productForm.html', product_id=product_id)
    return render_with_error_handling('products/productForm.html', product_id=None)


# def product_database(prod_id=45, **kwargs):
@products_blueprint.route('/product_database', methods=['GET', 'POST', 'DELETE'])
def product_database():
    """
    Product Database Page
    """
    try:
        if request.method == 'GET':
            # TODO
            # products = [] of Product class objects
            query = 'SELECT product_id, name, cas_numbers, physical_state_id, packaging_types.packaging_type_name AS packaging, size, hazard_codes, other_issues, concerns, facility_product_id FROM products LEFT JOIN packaging_types ON products.packaging = packaging_types.packaging_type_id;'
            db_products = query_db(query)
            # if db_products:
            packaging_query = 'SELECT packaging_type_id, packaging_type_name FROM packaging_types;'
            db_packaging = query_db(packaging_query)

            return render_with_error_handling('products/product_database.html', products=db_products or [], packaging_types=db_packaging)
            # else:
            #     print("The GET HTTP Method for /products/product_database failed because there are no products in the database to display.")
            #     response = make_response({'error': 204, 'message': 'No products to display because the database is empty.'})
            #     response.headers["Content-Type"] = "text/html"
            #     # return response, 204
            #     # return {'error': 'Problem getting products or no products to show.'}, 204
            #     return render_with_error_handling('products/product_database.html', 
            #                                       products={"name": None, 
            #                                                 "cas_numbers": None, 
            #                                                 "packaging": None, 
            #                                                 "size": None,
            #                                                 "other_issues": None,
            #                                                 "concerns": None,
            #                                                 "facility_product_id": None},
            #                                                 packaging_types=db_packaging)
        if request.method == 'POST':


            product = dict(request.form)
            if request.form.get("concerns") != None:
                product["concerns"] = True



            if product.get("productID"):
                if product.get("productName") and product.get("cas_numbers"):


                    query = 'UPDATE products SET name = ?, cas_numbers = ?, physical_state_id = ?, packaging = ?, size = ?, \
                            hazard_codes = ?, other_issues = ?, concerns = ?, facility_product_id = ? WHERE product_id = ?;'
                    unsuccessful_update = query_db(query, [product.get("productName"), product.get("cas_numbers"), product.get("physical_state_id"), 
                                                           product.get("packaging"), product.get("size"),
                                                           product.get("hazard_code"), product.get("other_issues"),
                                                           product.get("concerns"), product.get("facility_product_id"),
                                                           product.get("productID")])
                    if not unsuccessful_update:

                        return redirect('/products/product_database')
                    else:

                        response = make_response({'error': 406, 'message': 'The Product ID provided for updating does not exist.'})
                        response.headers["Content-Type"] = "application/json"
                        return response, 406
                else:

                    response = make_response({'error': 400, 'message': 'You did not provide any of the required parameters (ie, Product ID, required update fields, etc) for this HTTP Method.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 400
            else:
                if product.get("productName") and product.get("cas_numbers"):
                    product = Product()  # Instantiate the Product object
                    query = product.insert_query()
                    # products = query_db(query, [product.name, product.cas_numbers, product.packaging, product.size, product.hazard_codes, product.concerns])  # can also add parameter:  one=True
                    new_id = query_db(query, product.get_attributes(), one=True, want_id=True)
                    product.set_id(new_id)

                    return redirect('/products/product_database')
                else:

                    response = make_response({'error': 204, 'message': 'No Product ID provided for updating.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
        if request.method == 'DELETE':
            query = 'DELETE FROM products WHERE product_id = ?;'
            product = dict(request.form)

            prod_id = product.get("productID")
            unsuccessful_removal = query_db(query, [product.get("productID")])

            if not unsuccessful_removal:

                # return redirect('/products/product_database')
                return jsonify({"Deleted ID:": prod_id}), 201
            else:

                response = make_response({'error': 406, 'message': 'The Product ID provided for removal does not exist.'})
                response.headers["Content-Type"] = "application/json"
                return response, 406
    except Exception as e:

        response = make_response({'error': 400, 'message': e})
        response.headers["Content-Type"] = "application/json"
        return response, 400


# def product_details(prod_id):
@products_blueprint.route('/product_details/<prod_id>', methods=['GET', 'POST'])
def product_details(prod_id=None, prod_name=None, prod_cas=None, 
                    prod_packaging=None, prod_size=None, prod_hazard_codes=None, 
                    prod_other_issues=None, prod_concerns=False, facility_product_id=None):
    """
    Details of a Single Product Object Page

    Source: Serialization of a pandas DataFrame
        https://stackoverflow.com/questions/16936608/storing-bools-in-sqlite-database
        https://stackoverflow.com/questions/16971803/serialization-of-a-pandas-dataframe
    """
    # https://www.geeksforgeeks.org/flask-http-method/

    try:
        if request.method == 'GET':
            query = 'SELECT product_id, name, cas_numbers, physical_state_id, packaging, size, hazard_codes, other_issues, concerns, facility_product_id FROM products WHERE product_id = ?;'
            db_product = query_db(query, [prod_id], one=True)
            # flash("Power has been turned ON")
            if db_product:
                return jsonify(dict(db_product)), 201
            else:
                response = make_response({'error': 204, 'message': 'No Product ID provided for retrieval, or that Product ID does not exist.'})
                response.headers["Content-Type"] = "application/json"
                return response, 204
    except:    
        response = make_response({'error': 400, 'message': 'Sorry! This endpoint */products/product_details* has only been developed for GET requests.'})
        response.headers["Content-Type"] = "application/json"
        return response, 400
    

@products_blueprint.route('/products_by_name/<prod_name>', methods=['GET'])
def products_by_name(prod_id=None, prod_name=None, prod_cas=None, 
                    prod_packaging=None, prod_size=None, prod_hazard_codes=None, 
                    prod_other_issues=None, prod_concerns=False, facility_product_id=None):
    """
    Details of a Single Product Object Page

    """
    # try:
    if request.method == 'GET':

        products = []
        query = 'SELECT product_id, name, cas_numbers, physical_state_id, packaging_types.packaging_type_name AS packaging, size, other_issues, hazard_codes, concerns FROM products LEFT JOIN packaging_types ON products.packaging = packaging_types.packaging_type_id WHERE name = ?;'
        db_products = query_db(query, [prod_name])

        if db_products:
            for row in db_products:
                products.append(dict(row)) # or simply data.append(list(row))
            return jsonify(products), 201
        else:
            response = make_response({'error': 204, 'message': 'No Product Name provided for retrieval, or that Product Name does not exist.'})
            response.headers["Content-Type"] = "application/json"
            return response, 204
    # except:    
    #     response = make_response({'error': 400, 'message': 'Sorry! This endpoint */products/products_by_name* has only been developed for GET requests.'})
    #     response.headers["Content-Type"] = "application/json"
    #     return response, 400


@products_blueprint.route('/cas_hazards/<cas>', methods=['GET'])
def cas_hazards(cas=None):

    """
    Query db for existing CAS number and return if found

    """
    
    casList = cas.split(",")
    cleanedCasList = [item.strip(' ') for item in casList]

    if cas:
        try:
            if request.method == 'GET':
                qs = ", ".join("?" * len(cleanedCasList))
                #query = f"SELECT cas_ghs_hazards_join_id, cas_number, ghs_hazard_code FROM cas_ghs_hazards_join WHERE cas_number IN ({qs})"
                query = f"SELECT c.cas_hazards_id, c.cas_number, g.hazard_code FROM cas_hazards c \
                    LEFT JOIN cas_ghs_hazards j ON c.cas_hazards_id = j.cas_hazards_id \
                    LEFT JOIN ghs_hazards g ON j.ghs_hazards_id = g.ghs_hazards_id WHERE c.cas_number IN ({qs})"
                db_hazard = query_db(query, cleanedCasList, one=True)
                if db_hazard:
                    return jsonify(dict(db_hazard)), 201
                else:
                    response = make_response({'error': 204, 'message': 'No CAS number provided for retrieval, or that CAS number does not exist in the database.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
        except:    
            response = make_response({'error': 400, 'message': 'Sorry! This endpoint */products/cas_hazards* has only been developed for GET requests.'})
            response.headers["Content-Type"] = "application/json"
            return response, 400
        

@products_blueprint.route('/ghs_hazards/<ghs>', methods=['GET'])
def ghs_hazards(ghs=None):

    """
    Query db for existing GHS code and return if found

    """
    
    ghsList = ghs.upper().split(",")
    cleanedGhsList = [item.strip(' ') for item in ghsList]

    if ghs:
        try:
            if request.method == 'GET':
                qs = ", ".join("?" * len(cleanedGhsList))
                query = f"SELECT ghs_hazards_id, hazard_code FROM ghs_hazards WHERE hazard_code IN ({qs})"
                db_hazard = query_db(query, cleanedGhsList, one=True)
                if db_hazard:
                    return jsonify(dict(db_hazard)), 201
                else:
                    response = make_response({'error': 204, 'message': 'No GHS code provided for retrieval, or that GHS code does not exist in the database.'})
                    response.headers["Content-Type"] = "application/json"
                    return response, 204
        except:    
            response = make_response({'error': 400, 'message': 'Sorry! This endpoint */products/ghs_hazards* has only been developed for GET requests.'})
            response.headers["Content-Type"] = "application/json"
            return response, 400
