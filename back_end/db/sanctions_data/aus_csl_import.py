
import pandas as pd
import json
import uuid
from datetime import datetime
import os

def convertExcelToJson (inputExcelPath):
    # Convert Excel To Json With Python
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    input_file_path = os.path.join(script_dir, inputExcelPath)

    data = pd.read_excel(input_file_path, sheet_name="Sheet1")
    #print(data)
    #json_data = data.head(5).to_json(orient="records")
    
    # Print the JSON data
    #print(json_data)

    return data

def transform_json(input_data, output_file):
    #script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    # input_file_path = os.path.join(script_dir, input_file)
    # with open(input_file_path, 'r') as f:
    #     data = json.load(f)
    
    transformed_data = []
    address_entities = []

    for index, result in input_data.iterrows():
        entity_id = str(uuid.uuid4())
        entity_name = result.get("Name of Individual or Entity", "")
        entity = {
            "id": entity_id,
            "caption": entity_name,
            "schema": "Entity",
            "properties": {
                "name": entity_name,
                "topics": ["sanction"]
            },
            "referents": [result.get("Reference", "")],
            "datasets": ["aus_csl"],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "last_change": datetime.now().isoformat(),
            "target": True,
            "addressEntity": [],
            "alias": "",
            "notes": result.get("Additional Information", ""),
            "postalCode": "",
            "region": "",
            "authority": "",
            "provisions": "",
            "entity": "",
            "startDate": "",
            "nationality": result.get("Citizenship", ""),
            #"swiftBic": result.get("ids", [{}])[0].get("number", None),
            "passportNumber": result.get("Passport", "")
        }

        address_id = "addr-" + str(uuid.uuid4()).replace("-", "")
        address_entity = {
            "id": address_id,
            "caption": result.get("Address", ""),
            "schema": "Address",
            "properties": {
                "full": result.get("Address", ""),
                "country": "",
                "street": "",
                "city": ""
            },
            "referents": [],
            "datasets": ["aus_csl"],
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "last_change": datetime.now().isoformat(),
            "target": False
        }
        #address_entities.append(address_entity)
        entity["addressEntity"].append(address_id)
        
        transformed_data.append(entity)
    
        transformed_data.append(address_entity)

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    output_file_path = os.path.join(script_dir, output_file)
    print(output_file_path)
    with open(output_file_path, 'w+') as f:
        json.dump(transformed_data, f, indent=4)

# Example usage
sanctions_json = convertExcelToJson ("aus_regulation8_consolidated.xlsx")
transform_json(sanctions_json, 'individual_countries/entities.ftm(au).json')
