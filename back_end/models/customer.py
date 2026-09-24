# Model View Controller (MVC) Architecture

from flask import * # Flask, g, redirect, render_template, request, url_for


### CLASSES ###

class Customer():
    def __init__(self):
        """
        Initialize a customer object.

        Inputs:
            None

        Attributes:
            name: (str) the Name of the customer
            cas: (str) the CAS Number for the customer
            packaging: (str) the type of Packaging used for the customer
            size: (str) the Size of the customer
            hazard_codes: (str) any GHS Hazard Codes associated with the customer
            concerns: (bool) any Concerns associated with the customer

        Work On / Still To-Do:
            Inserting into a BOOLEAN column (https://www.beekeeperstudio.io/blog/guide-to-boolean-columns-in-sqlite)
                https://stackoverflow.com/questions/7156147/inserting-boolean-value-into-mysql-with-python
                https://docs.python.org/3/library/sqlite3.html#sqlite3.Blob
            
            Possible Pagination:
                https://www.google.com/search?q=cursor+based+pagination+vs+offset+flask&rlz=1C1GCEU_enUS1075US1075&oq=cursor+based+pagination+vs+offset+flask&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQABiABDIICAIQABgWGB4yCggDEAAYhgMYigUyCggEEAAYhgMYigUyCggFEAAYhgMYigUyCggGEAAYhgMYigXSAQg3MDQ1ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8
        """
        
        self.customer_name = request.form['customer_name']
        self.phone_number = request.form['phone_number']
        self.poc_name = request.form['poc_name']
        self.poc_email = request.form['poc_email']
        self.hq_country = request.form['hq_country']
        # print("#################### address_proof_type_id VARIABLE IS: ", type(request.form.get('address_proof_type_id')), request.form.get('address_proof_type_id'))
        self.address_proof_type_id = request.form.get('address_proof_type_id')
        self.address_proof_accept = True if request.form.get("address_proof_accept") != None else False
        self.poc_dob = request.form['poc_dob']
        self.poc_nationality = request.form['poc_nationality']
        self.poc_parent_name = request.form['poc_parent_name']
        self.business_num = request.form['business_num']
        self.business_type = request.form['business_type']
        self.third_party_ref_name = request.form['third_party_ref_name']
        self.third_party_contact_info = request.form['third_party_contact_info']
        self.payment_method_id = request.form['payment_method_id']
        self.order_frequency = True if request.form.get("order_frequency") != None else False
        self.sanctioned = True if request.form.get('sanctioned') == "1" else False
        self.trusted_customer = True if request.form.get("trusted_customer") != None else False
        self.verification_date = request.form['verification_date']
        self.facility_customer_id = request.form['facility_customer_id']

        self.bank_name = request.form['bank_name']
        self.bank_address = request.form['bank_address'] or None
        
        self.customer_address = request.form['customer_address_1']

        # self.other_issues = other_issues
        # if request.form['otherIssues']:
        #     self.other_issues = request.form['otherIssues']
        
        # self.concerns = concerns
        # if request.form['hazardous']:
        #     self.concerns = request.form['hazardous']
        # print('~~~~~~~~~~~~~~~~~CONCERNS/HAZARDOUS', self.concerns, type(self.concerns))

    def insert_query(self):
        """
        Create SQL Query to be Executed on the Flask App side.
        """
        self.insert_query = f"INSERT INTO customers (customer_name, phone_number, poc_name, poc_email, hq_country, address_proof_type_id, address_proof_accept, poc_dob, poc_nationality, poc_parent_name, business_num, business_type, third_party_ref_name, third_party_contact_info, payment_method_id, order_frequency, sanctioned, trusted_customer, verification_date, facility_customer_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING customer_id;"
        # print("INSERT QUERY IS: ", self.insert_query)
        return self.insert_query

    def set_id(self, customer_id):
        """
        Check if customer has been inserted into the Database yet, and if so, 
        get the customer's ID.
        """
        if self.insert_query:
            self.customer_id = customer_id
        else:
            print("***WARNING: customer HAS NOT YET BEEN INSERTED IN THE DATABASE!!!***")
        # self.customer_id = customer_id

    def get_attributes(self):
        """
        Get a list of the attributes from a customer object.
        """
        return [self.customer_name, self.phone_number, self.poc_name, self.poc_email, self.hq_country, self.address_proof_type_id, self.address_proof_accept, self.poc_dob, self.poc_nationality, self.poc_parent_name, self.business_num, self.business_type, self.third_party_ref_name, self.third_party_contact_info, self.payment_method_id, self.order_frequency, self.sanctioned, self.trusted_customer, self.verification_date, self.facility_customer_id]
        #return [self.customer_name, self.phone_number, self.poc_name, self.poc_email, self.hq_country]
    
    def get_bank_info(self):
        """
        Get a list of the attributes related to a customer's bank information.
        """
        return [self.bank_name, self.bank_address, self.sanctioned]
    
    def get_address_info(self):
        """
        Get a list of the attributes related to a customer's address information.
        """
        return [self.customer_address, self.sanctioned]

    def __repr__(self):
        """
        Repr Method (for quick development printing).
        
        Accessed by:
            example_customer = customer()
            print(repr(example_customer))
        """
        if self.customer_id:
            return f"customer({self.customer_id}, {self.customer_name}, {self.phone_number}, {self.poc_name}, {self.poc_email}, {self.hq_country}, {self.address_proof_type_id}, {self.address_proof_accept}, {self.poc_dob}, {self.poc_nationality}, {self.poc_parent_name}, {self.business_num}, {self.business_type}, {self.third_party_ref_name}, {self.third_party_contact_info}, {self.payment_method_id}, {self.order_frequency}, {self.sanctioned}, {self.trusted_customer}, {self.verification_date}, {self.facility_customer_id})"
        return f"customer({self.customer_name}, {self.phone_number}, {self.poc_name}, {self.poc_email}, {self.hq_country}, {self.address_proof_type_id}, {self.address_proof_accept}, {self.poc_dob}, {self.poc_nationality}, {self.poc_parent_name}, {self.business_num}, {self.business_type}, {self.third_party_ref_name}, {self.third_party_contact_info}, {self.payment_method_id}, {self.order_frequency}, {self.sanctioned}, {self.trusted_customer}, {self.verification_date}, {self.facility_customer_id})"
        #     return f"customer({self.customer_id}, {self.customer_name}, {self.phone_number}, {self.poc_name}, {self.poc_email})"
        # return f"customer({self.customer_name}, {self.phone_number}, {self.poc_name}, {self.poc_email})"
    
    def __str__(self):
        """
        Str Method (for general string printing).
        
        Accessed by:
            example_customer = customer()
            print(example_customer)
        """
        if self.customer_id:
            s = f"\ncustomer ID: {self.customer_id} \ncustomer Name: {self.customer_name} \
                  \ncustomer CAS: {self.phone_number} \ncustomer Packaging: {self.poc_name} \
                  \ncustomer Size: {self.poc_email} \ncustomer Payment: {self.payment_method_id}"
            return s
        s = f"\ncustomer Name: {self.customer_name} \ncustomer CAS: {self.phone_number} \
              \ncustomer Packaging: {self.poc_name} \ncustomer Size: {self.poc_email}"
        return s


class customerDetails(Customer):
    def __init__(self):
        """
        Single-Item customer Details

        https://docs.python.org/3/tutorial/classes.html#inheritance
        https://www.youtube.com/watch?v=RSl87lqOXDE
        """
        super().__init__()
        # self.ghs_hazard_code = ghs_hazard_code
        # self.ghs_hazard_statement = ghs_hazard_statement
        # self.ghs_hazard_class = ghs_hazard_class
        # inherit customer()
        # TODO
        # MIGHT WANT TO DO MULTIPLE INHERITENCE HERE (WITH DIFFERENT SUBCLASSES FOR EACH SUB-TABLE).
        # bring in IngredientCAS, PhysicalState, PackagingTypes, MaterialQuantities, customerGHSHazards, GHSHazards
        pass
    def __repr__(self):
        """Repr Method"""
        s = f""
        return s

