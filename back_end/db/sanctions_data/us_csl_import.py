import json
import uuid
from datetime import datetime
import os

def transform_json(input_file, output_file):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    input_file_path = os.path.join(script_dir, input_file)
    with open(input_file_path, 'r') as f:
        data = json.load(f)
    
    transformed_data = []
    address_entities = []

    for result in data['results']:
        entity_id = str(uuid.uuid4())
        entity = {
            "id": entity_id,
            "caption": result.get("name", ""),
            "schema": "Entity",
            "properties": {
                "name": result.get("name", []),
                "topics": ["sanction"]
            },
            "referents": [result.get("entity_number", "")],
            "datasets": ["us_trade_csl"],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "last_change": datetime.now().isoformat(),
            "target": True,
            "name": result.get("alt_names", []),
            "topics": ["sanction"],
            "addressEntity": [],
            "country": "",
            "alias": "",
            "city": "",
            "full": "",
            "notes": result.get("remarks", ""),
            "postalCode": "",
            "street": "",
            "region": "",
            "authority": "",
            "provisions": "",
            "entity": "",
            "startDate": "",
            "reason": "",
            "sourceUrl": result.get("source_information_url", ""),
            "authorityId": "",
            "endDate": "",
            "program": result.get("programs", []),
            "postOfficeBox": None,
            "createdAt": None,
            "birthDate": None,
            "position": None,
            "gender": None,
            "birthPlace": None,
            "nationality": None,
            "taxNumber": None,
            "registrationNumber": None,
            "idNumber": None,
            "email": None,
            "website": None,
            "lastName": None,
            "firstName": None,
            "title": None,
            #"swiftBic": result.get("ids", [{}])[0].get("number", None),
            "phone": None,
            "listingDate": None,
            "holder": None,
            "number": None,
            "type": result.get("type", None),
            "summary": None,
            "unscId": None,
            "previousName": None,
            "weakAlias": None,
            "passportNumber": None
        }

        for address in result.get("addresses", []):
            address_id = "addr-" + str(uuid.uuid4()).replace("-", "")
            address_entity = {
                "id": address_id,
                "caption": address.get("address", ""),
                "schema": "Address",
                "properties": {
                    "full": [address.get("address", "")] if address.get("address") else [],
                    "country": [address.get("country", "").lower()] if address.get("country") else [],
                    "street": [address.get("address", "")] if address.get("address") else [],
                    "city": [address.get("city", "")] if address.get("city") else []
                },
                "referents": [],
                "datasets": ["us_trade_csl"],
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "last_change": datetime.now().isoformat(),
                "target": False
            }
            address_entities.append(address_entity)
            entity["addressEntity"].append(address_id)
        
        transformed_data.append(entity)
    
    transformed_data.extend(address_entities)

    #output_file_path = os.path.join(script_dir, output_file)
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    output_file_path = os.path.join(script_dir, output_file)
    with open(output_file_path, 'w') as f:
        json.dump(transformed_data, f, indent=4)

# Example usage
transform_json('input.json', 'individual_countries/entities.ftm(us).json')
