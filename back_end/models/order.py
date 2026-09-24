# Model View Controller (MVC) Architecture

from flask import * # Flask, g, redirect, render_template, request, url_for

class Order():
    def __init__(self):
        """Initialize an Order object."""
        # TODO
        pass
    def __repr__(self):
        """Repr Method"""
        # TODO
        s = f""
        return s


class Product():
    def __init__(self, other_issues=None, concerns=None):
        """
        Initialize a Product object.

        Inputs:
            None

        Attributes:
            name: (str) the Name of the product
            cas: (str) the CAS Number for the product
            packaging: (str) the type of Packaging used for the product
            size: (str) the Size of the product
            hazard_codes: (str) any GHS Hazard Codes associated with the product
            concerns: (bool) any Concerns associated with the product

        Work On / Still To-Do:
            Inserting into a BOOLEAN column (https://www.beekeeperstudio.io/blog/guide-to-boolean-columns-in-sqlite)
                https://stackoverflow.com/questions/7156147/inserting-boolean-value-into-mysql-with-python
                https://docs.python.org/3/library/sqlite3.html#sqlite3.Blob
            
            Possible Pagination:
                https://www.google.com/search?q=cursor+based+pagination+vs+offset+flask&rlz=1C1GCEU_enUS1075US1075&oq=cursor+based+pagination+vs+offset+flask&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQABiABDIICAIQABgWGB4yCggDEAAYhgMYigUyCggEEAAYhgMYigUyCggFEAAYhgMYigUyCggGEAAYhgMYigXSAQg3MDQ1ajBqN6gCALACAA&sourceid=chrome&ie=UTF-8
        """
        self.name = request.form['productName']
        self.cas = request.form['casNumber']
        self.packaging = request.form['materialPackaging']
        self.size = request.form['size']
        self.hazard_codes = request.form['ghsHazardCodes'] ## TODO This might need to be changed to hazard_code
        
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
        # self.insert_query = f"INSERT INTO products (name, cas, packaging, size, hazard_codes, concerns) VALUES (?, ?, ?, ?, ?, ?);"
        self.insert_query = f"INSERT INTO products (name, cas, packaging, size, hazard_codes) VALUES (?, ?, ?, ?, ?) RETURNING id;"
        # print("INSERT QUERY IS: ", self.insert_query)
        return self.insert_query

    def set_id(self, product_id):
        """
        Check if Product has been inserted into the Database yet, and if so, 
        get the Product's ID.
        """
        if self.insert_query:
            self.id = product_id
        else:
            print("***WARNING: PRODUCT HAS NOT YET BEEN INSERTED IN THE DATABASE!!!***")
        # self.id = product_id

    def get_attributes(self):
        """
        Get a list of the attributes from a Product object.
        """
        return [self.name, self.cas, self.packaging, self.size, self.hazard_codes]

    def __repr__(self):
        """
        Repr Method (for quick development printing).
        
        Accessed by:
            example_product = Product()
            print(repr(example_product))
        """
        if self.id:
            return f"Product({self.id}, {self.name}, {self.cas}, {self.packaging}, {self.size})"
        return f"Product({self.name}, {self.cas}, {self.packaging}, {self.size})"
    
    def __str__(self):
        """
        Str Method (for general string printing).
        
        Accessed by:
            example_product = Product()
            print(example_product)
        """
        if self.id:
            s = f"\nProduct ID: {self.id} \nProduct Name: {self.name} \
                  \nProduct CAS: {self.cas} \nProduct Packaging: {self.packaging} \
                  \nProduct Size: {self.size}"
            return s
        s = f"\nProduct Name: {self.name} \nProduct CAS: {self.cas} \
              \nProduct Packaging: {self.packaging} \nProduct Size: {self.size}"
        return s


class ProductDetails(Product):
    def __init__(self, other_issues=None, concerns=None):
        """
        Single-Item Product Details

        https://docs.python.org/3/tutorial/classes.html#inheritance
        https://www.youtube.com/watch?v=RSl87lqOXDE
        """
        super().__init__(other_issues, concerns)
        self.ghs_hazard_code = ghs_hazard_code
        self.ghs_hazard_statement = ghs_hazard_statement
        self.ghs_hazard_class = ghs_hazard_class
        # inherit Product()
        # TODO
        # MIGHT WANT TO DO MULTIPLE INHERITENCE HERE (WITH DIFFERENT SUBCLASSES FOR EACH SUB-TABLE).
        # bring in IngredientCAS, PhysicalState, PackagingTypes, MaterialQuantities, ProductGHSHazards, GHSHazards
        pass
    def __repr__(self):
        """Repr Method"""
        s = f""
        return s

