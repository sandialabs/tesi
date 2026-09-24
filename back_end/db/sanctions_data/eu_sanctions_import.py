import xml.etree.ElementTree as ET
import pandas as pd
import json
import uuid
from datetime import datetime
import os

def convertExcelToPD (inputXMLPath):
    # Define file path
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    input_file_path = os.path.join(script_dir, inputXMLPath)

    # Parse the XML file
    tree = ET.parse(input_file_path)
    root = tree.getroot()

    # Define the namespace
    ns = {'ns': 'http://eu.europa.ec/fpi/fsd/export'}

    # Initialize lists to store data
    data = []

    # Iterate over each sanctionEntity
    for entity in root.findall('ns:sanctionEntity', ns):
        entity_data = {
            'designationDetails': entity.get('designationDetails'),
            'unitedNationId': entity.get('unitedNationId'),
            'euReferenceNumber': entity.get('euReferenceNumber'),
            'logicalId': entity.get('logicalId'),
            'remark': entity.find('ns:remark', ns).text if entity.find('ns:remark', ns) is not None else None,
            'properties': {"topics":["sanction"],"name":[]},
            'citizenship': entity.find('ns:citizenship', ns).get('countryDescription') if entity.find('ns:citizenship', ns) is not None else None,
            'addresses': []
        }
        
        for name_alias in entity.findall('ns:nameAlias', ns):
            name = name_alias.get('wholeName')
            entity_data.get('properties').get('name').append(name)

        for address in entity.findall('ns:address', ns):
            street = address.get('street') or ""
            city = address.get('city') or ""
            zipCode = address.get('zipCode') or ""
            country = address.get('countryDescription') or ""

            address_data = {
                'street': street,
                'city': city,
                'country': country,
                'zipCode': zipCode,
                'full': street + ' ' + city + ' ' + zipCode + ' ' + country
            }
            entity_data.get('addresses').append(address_data)
            
        data.append(entity_data)

    # Convert the list of dictionaries to a DataFrame
    # df = pd.DataFrame(data)

    # Display the DataFrame
    # print(df.head(8).to_json(orient="records"))
    #script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    # output_file_path = os.path.join(script_dir, "test_output.json")
    # print(output_file_path)
    # with open(output_file_path, 'w+') as f:
    #     json.dump(data, f, indent=4)

    return data

def transform_json(input_data, output_file):
    
    transformed_data = []
    address_entities = []

    for result in input_data:
        entity_id = str(uuid.uuid4())
        entity_name = result.get('properties').get("name", [])
        entity = {
            "id": entity_id,
            "caption": entity_name[0] or "",
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
            "nationality": result.get("Citizenship", ""),
            "passportNumber": result.get("Passport", "")
        }

        for address in result.get("addresses", []):
            address_id = "addr-" + str(uuid.uuid4()).replace("-", "")
            address_entity = {
                "id": address_id,
                "caption": address.get("address", ""),
                "schema": "Address",
                "properties": {
                    "full": [address.get("full", "")] if address.get("full") else [],
                    "country": [address.get("country", "").lower()] if address.get("country") else [],
                    "street": [address.get("street", "")] if address.get("address") else [],
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

    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    output_file_path = os.path.join(script_dir, output_file)
    print(output_file_path)
    with open(output_file_path, 'w') as f:
        json.dump(transformed_data, f, indent=4)

# Example usage
sanctions_json = convertExcelToPD("EU_20240905-FULL-1_1(xsd).xml")
transform_json(sanctions_json, 'individual_countries/entities.ftm(eu).json')
