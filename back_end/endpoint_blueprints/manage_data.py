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
from pathlib import Path


# ------------------ GLOBAL VARIABLES ------------------

# print("MANAGE DATA OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
STATIC_FILEPATH = os.path.join(DIR, 'front_end', 'static')
TEMPLATE_FILEPATH = os.path.join(DIR, 'front_end', 'templates')

data_blueprint = Blueprint('data_blueprint', __name__, url_prefix='/manage_data', static_folder=STATIC_FILEPATH, template_folder=TEMPLATE_FILEPATH)


# ------------------ ENDPOINTS ------------------

@data_blueprint.route('/data_landing_page', methods=['GET', 'POST'])
def data_landing_page():
    """
    Main Data Management Landing Page
    """
    return render_with_error_handling('manage_data/data_landing_page.html')


@data_blueprint.route('/import_landing', methods=['GET', 'POST'])
def import_landing():
    """
    Landing page for importing data from the user. This endpoint asks the user what 
    data they are importing (Products, Customers, or Orders), and asks them to upload 
    it from their computer.
    """
    if request.method == 'POST':
        if not request.form:

            return jsonify({'error': 406, 'message': 'Neither Import Data nor Export Data were selected, please go back and select the option you would like.'}), 406
        return render_with_error_handling('manage_data/import_landing.html')


@data_blueprint.route('/import_data', methods=['GET', 'POST'])
def import_data():
    """
    Import data from the user from an external source. The data can be imported from 
    either an xlsx, xls, xlsm, csv, or json format. This function supports the imports 
    of product data, customer data, or order data.
    """
    # TODO ("nice-to-haves")
    # Add functionality to check filesize, and add a flash for "This file is very large... this might take a moment." 
    # Add functionality for dealing with multiple sheets inside an excel or csv file (currently just pulls the first sheet)
    if request.method == 'POST':
        import_file = request.files["upload-file"]
        if not import_file:

            response = {'error': 406, 'message': 'No file was selected for upload, please go back and select a file.'}
            return render_with_error_handling("error.html", args=response)
        try:
            import_table_name = request.form["corresponding-table"]
        except:

            response = {'error': 406, 'message': 'No data table type was specified, please go back and select one of the three data import options.'}
            return render_with_error_handling("error.html", args=response)

        file_type = import_file.filename.split('.')[-1]
        if file_type == 'xlsx' or file_type == 'xls' or file_type == 'xlsm':
            import_data = pd.read_excel(import_file)
        elif file_type == 'csv':
            import_data = pd.read_csv(import_file)
        elif file_type == 'json':
            raw_data = pd.read_json(import_file, typ='series')
            json_import_type = str(type(raw_data.index))
            if json_import_type == "<class 'pandas.core.indexes.range.RangeIndex'>":
                import_data = pd.json_normalize(raw_data)
            elif json_import_type == "<class 'pandas.core.indexes.base.Index'>":
                import_data = pd.DataFrame(raw_data).transpose()
        else:
            import_data = None

            response = {'error': 415, 'message': 'The file type uploaded is not supported by this app, please convert it to Excel, CSV, or JSON, and try again.'}
            return render_with_error_handling("error.html", args=response)

        rv_dict = process_data(import_data, import_table_name)
        if rv_dict.get('error'):
            return render_with_error_handling("error.html", args=rv_dict)
        return render_with_error_handling('manage_data/import_data.html', data=import_data.to_html(classes="database-table th"))


@data_blueprint.route('/export_landing', methods=['GET', 'POST'])
def export_landing():
    """
    Landing page for exporting/downloading data from the databaser. This endpoint asks 
    the user what data they are exporting (Products, Customers, or Orders), and asks 
    them what data format they would like it to be in (Excel, CSV, or JSON).
    """
    if request.method == 'POST':
        if not request.form:

            return jsonify({'error': 406, 'message': 'Neither Import Data nor Export Data were selected, please go back and select the option you would like.'}), 406
        return render_with_error_handling('manage_data/export_landing.html')


@data_blueprint.route('/export_data', methods=['GET', 'POST'])
def export_data():
    """
    Export data from the TESI Database. The data can be exported
    as either an xlsx, csv, or json format.
    """
    if request.method == 'GET':

        response = {'error': 405, 'message': 'This endpoint /manage_data/export_data is not set up for a GET Method, please use the POST Method.'}
        return render_with_error_handling("error.html", args=response)
    if request.method == 'POST':
        try:
            export_table_name = request.form["corresponding-table"]
        except:

            response = {'error': 406, 'message': 'No data table type was specified, please go back and select one of the three data download options.'}
            return render_with_error_handling("error.html", args=response)
        try:
            export_data_format = request.form["data-format"]
        except:

            response = {'error': 406, 'message': 'No data format was specified, please go back and select one of the three data format options.'}
            return render_with_error_handling("error.html", args=response)
        connection = sqlite3.connect(os.path.join(DIR, 'back_end', 'db', 'tesi_tool.sqlite3'), 
                                     isolation_level=None, 
                                     detect_types=sqlite3.PARSE_COLNAMES)

        download_filepath = os.path.join(DIR, 'back_end', 'db', 'downloadable_files', f'{export_table_name}_database.{export_data_format}')
        if export_table_name == "orders":
            ### Need to include Order Items (the products and quantities) as well
            db1 = pd.read_sql_query(f"SELECT * FROM orders", connection)
            db2 = pd.read_sql_query(f"SELECT * FROM order_item", connection)    
            merged_1 = pd.merge(db1, db2, on='order_id', how='left')
            db3 = pd.read_sql_query(f"SELECT * FROM products", connection)      
            db = pd.merge(merged_1, db3, on='product_id', how='left')
            print("****  ", db.columns)
            db = db.drop(['order_id', 'order_item_id', 'product_id'], axis=1)
        else:
            db = pd.read_sql_query(f"SELECT * FROM {export_table_name}", connection)
        if export_data_format == 'xlsx':
            db.to_excel(download_filepath, index=False)
        elif export_data_format == 'csv':
            db.to_csv(download_filepath, index=False)
        elif export_data_format == 'json':
            db.to_json(download_filepath, orient="records")
        else:

            response = {'error': 415, 'message': 'The file type selected is not supported by this app, please go back and select one of the approved options: Excel, CSV, or JSON, and try again.'}
            return render_with_error_handling("error.html", args=response)

        return render_with_error_handling('manage_data/export_data.html', export_filepath=download_filepath, data=db.to_html(classes="database-table th"))


@data_blueprint.route('/download_file', methods=['GET', 'POST'])
def download_file():
    """
    Download the file to the client through the browser.
    """
    if request.method == 'GET':

        response = {'error': 405, 'message': 'This endpoint /manage_data/download_file is not set up for a GET Method, please use the POST Method.'}
        return render_with_error_handling("error.html", args=response)
    if request.method == 'POST':
        try:
            downloaded_filepath = request.form["downloadable-items-filepath"]
        except:

            response = {'error': 406, 'message': 'No filepath was specified for the downloaded file.'}
            return render_with_error_handling("error.html", args=response)
        try:
            return send_file(downloaded_filepath, as_attachment=True)
        except:

            response = {'error': 417, 'message': 'Sending the file failed when returning to client.'}
            return render_with_error_handling("error.html", args=response)


# ------------------ MANAGE DATA HELPER FUNCTIONS ------------------

def process_data(data, corresponding_table):
    """
    Helper function to import_data() that processes the data input by the user.
    
    Note: When the data structure of any of the import tables changes in the tesi_tool.sqlite3, 
    the new_columns variable to be updated here, in order for everything to function properly:
        new_columns (dict):
            keys: the columns that are expected in the user's input file.
            values: the corresponding columns that are associated with those 
                input columns in the database.

    Inputs:
        data (pandas DataFrame object): the user's input data that has been converted 
            into a pandas dataframe 
        corresponding_table (str): a string of one of three values (products, customers, 
            or orders), indicating the corresponding SQL Table in the tesi_tool.sqlite3 
            file to process the data inserts under.
    Outputs:
        (dict) a dictionary object containing the HTTP response status code and message 
            key-value pairs (the HTTP response status code is stored under the key 'error' 
            if it failed, or under the key 'code' if it was successful).
    """
    connection = sqlite3.connect(os.path.join(DIR, 'back_end', 'db', 'tesi_tool.sqlite3'))
    cursor = connection.cursor()  # DELETE LATER
    columns = data.columns
    
    print("*** Incoming Columns: ", columns)
    
    new_columns = {}
    if corresponding_table == "products":
        user_columns = ['Product Name', 'CAS Number', 'Physical State ID', 'Material Packaging ID', 'Size', 'Hazard Codes', 'Other Issues', 'Concerns', 'Facility Product ID']
        db_columns = ['name', 'cas_numbers', 'physical_state_id', 'packaging', 'size', 'hazard_codes', 'other_issues', 'concerns', 'facility_product_id']
    if corresponding_table == "customers":
        user_columns = ['Customer Name', 'Telephone', 'POC Name', 'POC Email', 'Country', 'Address Proof Type ID', 'Address Proof Accepted', 'POC Date of Birth', 'POC Nationality', 'POC Parent Name', 'Business Number', 'Business Type', 'Third Party Ref Name', 'Third Party Contact Information', 'Payment Method ID', 'Order Frequency', 'Sanctioned', 'Trusted Customer', 'Verification Date', 'Facility Customer ID', 'Customer Address', 'Bank Name', 'Bank Address']
        db_columns = ['customer_name', 'phone_number', 'poc_name', 'poc_email', 'hq_country', 'address_proof_type_id', 'address_proof_accept', 'poc_dob', 'poc_nationality', 'poc_parent_name', 'business_num', 'business_type', 'third_party_ref_name', 'third_party_contact_info', 'payment_method_id', 'order_frequency', 'sanctioned', 'trusted_customer', 'verification_date', 'facility_customer_id', 'customer_address', 'bank_name', 'bank_address']
    if corresponding_table == "orders":
        # CSV Columns (orders and products): # Order Date,Delivery Date,Customer ID,POC Name,Address Different,Bank Name Different,Bank Address Different,Payment Different,Atypical Order,Larger Order,End Use Verified,Urgent Shipping,Immediate Custody,First Time Transporter,Shipment Verification,Unusual Routing,Unusual Labeling,Unusual Handling,PPE Concern,Route Safety Concern,Order Method,Transporter Name,Transporter Address,Transporter Phone,Facility Order ID,Product Name,CAS Number,Physical State ID,Material Packaging ID,Size,Hazard Codes,Other Issues,Concerns,Facility Product ID,Order Quantity
        # "customer_id" might need to be changed to "facility_customer_id", and the logic re-worked around using that as the UID in the DB
        user_product_columns = ['Product Name', 'CAS Number', 'Physical State ID', 'Material Packaging ID', 'Size', 'Hazard Codes', 'Other Issues', 'Concerns', 'Facility Product ID', 'Order Quantity']
        db_product_columns = ['name', 'cas_numbers', 'physical_state_id', 'packaging', 'size', 'hazard_codes', 'other_issues', 'concerns', 'facility_product_id', 'quantity']
        user_columns = ['Order Date', 'Delivery Date', 'Customer ID', 'POC Name', 'Address Different', 'Bank Name Different', 'Bank Address Different', 'Payment Different', 'Atypical Order', 'Larger Order', 'End Use Verified', 'Urgent Shipping', 'Immediate Custody', 'First Time Transporter', 'Shipment Verification', 'Unusual Routing', 'Unusual Labeling', 'Unusual Handling', 'PPE Concern', 'Route Safety Concern', 'Order Method', 'Transporter Name', 'Transporter Address', 'Transporter Phone', 'Facility Order ID', 'Order Bank', 'Payment Method ID', 'Shipping Address']
        db_columns = ['order_date', 'delivery_date', 'customer_id', 'poc_name', 'address_different', 'bank_name_different', 'bank_address_different', 'payment_different', 'atypical_order', 'larger_order', 'end_use_verified', 'urgent_shipping', 'immediate_custody', 'first_time_transporter', 'shipment_verification', 'unusual_routing', 'unusual_labeling', 'unusual_handling', 'ppe_concern', 'route_safety_concern', 'order_method', 'transporter_name', 'transporter_address', 'transporter_phone', 'facility_order_id', 'order_bank', 'payment_method_id', 'shipping_address']
        # user_columns = user_columns + user_product_columns
        user_columns = db_columns + db_product_columns
        db_columns = db_columns + db_product_columns
        columns_to_remove = ['order_id', 'order_item_id', 'product_id']
        columns = list(set(columns) - set(columns_to_remove))

    new_columns = dict(zip(user_columns, db_columns))
    print("*** New Columns: ", new_columns)
    is_formatting_incorrect = check_basic_data_formatting(columns, new_columns, corresponding_table)
    if is_formatting_incorrect:
        return is_formatting_incorrect
    
    data = data.rename(columns=new_columns)
    if corresponding_table == "customers":
        other_data = data[['sanctioned', 'customer_address', 'bank_name', 'bank_address']]  # sanctioned, customer_address, bank_name, bank_address
        data = data.drop(columns=['customer_address', 'bank_name', 'bank_address'], axis=1)
    if corresponding_table == "orders":
        product_data = data[['facility_order_id', 'name', 'cas_numbers', 'physical_state_id', 'packaging', 'size', 'hazard_codes', 'other_issues', 'concerns', 'facility_product_id', 'quantity']]
        data = data.drop(columns=['name', 'cas_numbers', 'physical_state_id', 'packaging', 'size', 'hazard_codes', 'other_issues', 'concerns', 'facility_product_id', 'quantity'], axis=1)
        data = data.drop_duplicates('facility_order_id', keep='first')
        # print("UPDATED product_data AFTER DROPS: \n", product_data)
        # print("UPDATED DATA AFTER DROPS: \n", data)
    try:
        data.to_sql(corresponding_table, connection, if_exists="append", index=False)
        num_new_rows = len(data.index)
        if corresponding_table == "customers":
            all_customers = query_db('SELECT * FROM customers;')
            new_rows = all_customers[-num_new_rows:]
            for i, row in enumerate(new_rows):
                # print("\n\n########################## NEW ROW IS: \n", dict(row))
                new_customer_id = dict(row).get('customer_id')
                other_data_row = dict(other_data.iloc[i])
                bank_query = 'INSERT INTO customer_banks (bank_name, bank_address, customer_id, sanctioned) VALUES (?, ?, ?, ?) RETURNING customer_bank_id;'
                new_bank_id = query_db(bank_query, [other_data_row.get('bank_name'), other_data_row.get('bank_address'), new_customer_id, other_data_row.get('sanctioned')], one=True, want_id=True)
                address_query = 'INSERT INTO customer_addresses (customer_address, customer_id, sanctioned) VALUES (?, ?, ?) RETURNING customer_address_id;'
                new_address_id = query_db(address_query, [other_data_row.get('customer_address'), new_customer_id, other_data_row.get('sanctioned')], one=True, want_id=True)
                # print(f"\n NEW CUSTOMER BANK (ID: {new_bank_id}) ADDED SUCCESSFULLY")  # DELETE LATER
                # print(f"\n NEW CUSTOMER ADDRESS (ID: {new_address_id}) ADDED SUCCESSFULLY")  # DELETE LATER
        if corresponding_table == "orders":
            all_orders = query_db('SELECT * FROM orders;')
            new_rows = all_orders[-num_new_rows:]
            for i, row in enumerate(new_rows):
                # print("\n\n########################## NEW ROW IS: \n", dict(row))
                new_order_id = dict(row).get('order_id')
                current_order_facility_id = dict(row).get('facility_order_id')
                current_order_products = product_data[product_data['facility_order_id']==current_order_facility_id]
                for _, product in current_order_products.iterrows():
                    print("############################ product: \n", type(product), product)
                    current_product = dict(product)

                    facility_product_id = current_product.get('facility_product_id')
                    check_existing_product = query_db('SELECT * FROM products WHERE facility_product_id = ?;', [facility_product_id], one=True)
                    
                    
                    print("############################ check existing product: \n", type(check_existing_product), check_existing_product)
                    if not check_existing_product:
                        product_query = 'INSERT INTO products (name, cas_numbers, physical_state_id, packaging, size, hazard_codes, other_issues, concerns, facility_product_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING product_id;'
                        new_product_id = query_db(product_query, [product['name'], product['cas_numbers'], product['physical_state_id'], product['packaging'], product['size'], product['hazard_codes'], product['other_issues'], product['concerns'], product['facility_product_id']], one=True, want_id=True)
                    # product_id = dict(check_existing_product).get('product_id') or new_product_id
                    product_id = dict(check_existing_product).get('product_id') or new_product_id


                    order_item_query = "INSERT INTO order_item (order_id, product_id, quantity) VALUES (?, ?, ?) RETURNING order_item_id;"
                    new_order_item_id = query_db(order_item_query, [new_order_id, product_id, product['quantity']], one=True, want_id=True)
                    # print(f"\n NEW PRODUCT (ID: {new_product_id}) ADDED SUCCESSFULLY")  # DELETE LATER
                    # print(f"\n NEW ORDER_ITEM (ID: {new_order_item_id}) ADDED SUCCESSFULLY")  # DELETE LATER

        return {'code': 201, "message:": f"Data was inserted into {corresponding_table} table of the database successfully!"}
    except Exception as e:

        response = {'error': 409, 'message': e}
        return response


def check_basic_data_formatting(cols, column_mapping, table_name):
    """
    Helper function to process_data() that verifies the input data is formatted properly 
    for import. It is mainly checking if the number of columns is correct and if the column
    names match up with those that are in the database.

    Inputs:
        cols (list): a list of the columns in the data provided by the user.
        column_mapping (dict): a dictionary with the keys mapped to the input columns that are 
            expected in the user's input file, and the values mapped to the corresponding 
            columns that are associated with those input columns in the database.
        table_name (str): a string of one of three values (products, customers, or orders), 
            indicating the corresponding SQL Table in the tesi_tool.sqlite3 file to process 
            the data inserts under.
    Outputs:
        (dict) a dictionary object representing what is wrong with the data formatting, which 
            contains the HTTP response status code and message key-value pairs.
        OR
        (None) a Nonetype object, indicating there was nothing wrong with the formatting.
    """
    if len(cols) != len(column_mapping):
        few_or_many = "few" if len(cols) < len(column_mapping) else "many"

        return {'error': 412, 'message': f'The data provided contains too {few_or_many} columns to insert into the {table_name} table.\n\nThere should be {len(column_mapping)} columns, but {len(cols)} were provided.\n\nPlease refer to the data import guidelines and adjust your data file accordingly before importing again.'}
    incorrect_column_names = [col for col in cols if str(col).strip() not in column_mapping.keys()]
    if incorrect_column_names != []:

        return {'error': 422, 'message': f'The data provided contains a column or columns that are not in our list of required column names for inserting data into the {table_name} table.\n\nThe incorrectly named column or columns are: {incorrect_column_names}.\nThe columns required to import the data are: {list(column_mapping.keys())}.\n\nPlease refer to the data import guidelines and adjust your column names accordingly before importing again.'}
    return None
