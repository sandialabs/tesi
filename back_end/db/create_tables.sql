CREATE TABLE address_proof_type AS CREATE TABLE address_proof_type (
    address_proof_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    proof_type VARCHAR(40)
);
CREATE TABLE payment_methods AS CREATE TABLE payment_methods (
    payment_method_id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_method_name VARCHAR(40)
);
CREATE TABLE physical_state AS CREATE TABLE physical_state (
    physical_state_id INTEGER PRIMARY KEY AUTOINCREMENT,
    physical_state_name VARCHAR(80)
);
CREATE TABLE packaging_types AS CREATE TABLE packaging_types (
    packaging_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
    packaging_type_name VARCHAR(80)
);
CREATE TABLE product_ghs_hazards AS CREATE TABLE product_ghs_hazards (
    product_ghs_hazards_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    ghs_hazards_id INTEGER,
    FOREIGN KEY(product_id) REFERENCES products(product_id)
    FOREIGN KEY(ghs_hazards_id) REFERENCES ghs_hazards(ghs_hazards_id)
);
CREATE TABLE customer_addresses AS CREATE TABLE customer_addresses (
    customer_address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_address VARCHAR(80),
    customer_id INTEGER, sanctioned BOOLEAN,
    FOREIGN KEY(customer_id) REFERENCES "old_table"(customer_id)
);
CREATE TABLE customer_banks AS CREATE TABLE customer_banks (
    customer_bank_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bank_name VARCHAR(40),
    bank_address VARCHAR(80),
    customer_id INTEGER, sanctioned BOOLEAN,
    FOREIGN KEY(customer_id) REFERENCES "old_table"(customer_id)
);
CREATE TABLE order_item AS CREATE TABLE order_item (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY(order_id) REFERENCES orders(order_id),
    FOREIGN KEY(product_id) REFERENCES products(product_id)
);
CREATE TABLE facility_overview AS CREATE TABLE facility_overview (
    facility_id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_name VARCHAR(80),
    facility_country VARCHAR(40),
    company_type VARCHAR(80),
    types_of_customers VARCHAR(80),
    facility_address VARCHAR(80),
    facility_phone_number VARCHAR(40),
    facility_email VARCHAR(80),
    transportation VARCHAR(80),
    shipping_coordinator VARCHAR(40),
    sales_tracking BOOLEAN,
    shipment_verification BOOLEAN,
    permits_required BOOLEAN,
    preparation_procedures BOOLEAN,
    payment_types VARCHAR(80),
    order_methods VARCHAR(40),
    payment_timing VARCHAR(80)
);
CREATE TABLE cas_ghs_hazards_join AS CREATE TABLE cas_ghs_hazards_join (
    cas_ghs_hazards_join_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ghs_hazard_code VARCHAR(80),
    cas_number VARCHAR(80),
    hazard_class TEXT,
    hazard_statement TEXT,
    cas_chemical_name TEXT,
    cas_pictograms TEXT
);
CREATE TABLE order_methods AS CREATE TABLE order_methods (
    order_method_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_method_name VARCHAR(40)
);
CREATE TABLE cas_product AS CREATE TABLE cas_product (
    cas_product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    cas_hazards_id INTEGER,
    FOREIGN KEY(product_id) REFERENCES products(product_id),
    FOREIGN KEY(cas_hazards_id) REFERENCES cas_hazards(cas_hazards_id)
);
CREATE TABLE cas_ghs_hazards AS CREATE TABLE cas_ghs_hazards (
    cas_ghs_hazards_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cas_hazards_id INTEGER,
    ghs_hazards_id INTEGER,
    FOREIGN KEY(cas_hazards_id) REFERENCES cas_hazards(cas_hazards_id),
    FOREIGN KEY(ghs_hazards_id) REFERENCES ghs_hazards(ghs_hazards_id)
);
CREATE TABLE cas_hazards AS CREATE TABLE cas_hazards (
    cas_hazards_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cas_number VARCHAR(80),
    cas_chemical_name TEXT,
    pictograms TEXT
);
CREATE TABLE ghs_hazards AS CREATE TABLE ghs_hazards (
    ghs_hazards_id INTEGER PRIMARY KEY AUTOINCREMENT,
    hazard_code VARCHAR(80),
    hazard_statement VARCHAR(80),
    hazard_class VARCHAR(80)
);
CREATE TABLE products AS CREATE TABLE products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(80),
    facility_product_id VARCHAR(40), /* New */
    cas_numbers VARCHAR(80),
    physical_state_id INTEGER,
    packaging INTEGER,
    size INTEGER,
    hazard_codes TEXT,
    other_issues TEXT,
    concerns BOOLEAN,
    FOREIGN KEY(physical_state_id) REFERENCES physical_state(physical_state_id),
    FOREIGN KEY(packaging) REFERENCES packaging_types(packaging_type_id)
);
CREATE TABLE orders AS CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    facility_order_id VARCHAR(40),
    order_date DATE,
    customer_id INTEGER,
    poc_name VARCHAR(80),
    address_different BOOLEAN,
    payment_method VARCHAR(40),
    bank_name_different BOOLEAN,
    bank_address_different BOOLEAN,
    payment_different BOOLEAN,
    atypical_order BOOLEAN,
    larger_order BOOLEAN,
    end_use_verified BOOLEAN,
    order_method INTEGER,
    urgent_shipping BOOLEAN,
    immediate_custody BOOLEAN,
    transporter_name VARCHAR(40),
    transporter_address VARCHAR(80),
    transporter_phone VARCHAR(40),
    first_time_transporter BOOLEAN,
    shipment_verification BOOLEAN,
    unusual_routing BOOLEAN,
    unusual_labeling BOOLEAN,
    unusual_handling BOOLEAN,
    ppe_concern BOOLEAN,
    route_safety_concern BOOLEAN,
    delivery_date DATE,
    shipping_address VARCHAR(80),
    order_bank VARCHAR(80),
    FOREIGN KEY(customer_id) REFERENCES "old_table"(customer_id),
    FOREIGN KEY(order_method) REFERENCES order_methods(order_method_id)
);
CREATE TABLE customers AS CREATE TABLE "customers" (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name VARCHAR(80),
    phone_number VARCHAR(40),
    poc_name VARCHAR(80),
    poc_email VARCHAR(80),
    hq_country VARCHAR(40),
    address_proof_type_id INTEGER,
    address_proof_type VARCHAR(80),
    address_proof_accept BOOLEAN,
    poc_dob DATE,
    poc_nationality VARCHAR(40),
    poc_parent_name VARCHAR(80),
    business_num VARCHAR(40),
    business_type VARCHAR(80),
    third_party_ref_name VARCHAR(40),
    third_party_contact_info VARCHAR(80),
    payment_method_id INTEGER,
    payment_method VARCHAR(40),
    order_frequency VARCHAR(40),
    sanctioned BOOLEAN,
    trusted_customer BOOLEAN,
    verification_date DATE, facility_customer_id VARCHAR(40),
    FOREIGN KEY(address_proof_type_id) REFERENCES address_proof_type(address_proof_type_id),
    FOREIGN KEY(payment_method_id) REFERENCES payment_methods(payment_method_id)
);