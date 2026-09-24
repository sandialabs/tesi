import pandas as pd
import numpy as np
import sqlite3
import json
import re
import ast
import os


# ------------------ GLOBAL VARIABLES ------------------

# print("SANCTIONS QUERY OS DIRECTORY:", os.path.realpath(__file__))  # DELETE LATER
DIR = os.path.dirname(os.path.dirname(__file__))  # in 'tesi-kyc/back_end' directory


# ------------------ UTILITY HELPER FUNCTIONS ------------------

def upload_new_country_sanctions(input_filepath=None, output_filepath=None):
    """
    Function to upload a new country's sanctions into the sanctions database, for querying by the user 
    in the application.

    Inputs:
        - input_filepath (str): A required field - a string of the input filepath containing the new
            country sanctions being input into the sanctions database.
        - output_filepath (str): An optional field - a string of the output filepath at which the dataframe 
            should be exported for later querying in the application.
    Outputs:
        - updated_df or clean_df (pd.DataFrame): A Pandas DataFrame of the sanctions to be queried.
    """
    if not output_filepath:
        # The filepath for the newly cleaned data to be saved under. Default is: 'back_end/db/sanctions_data/all_sanctions_entities_cleaned.json'
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        output_filepath = os.path.join(DIR, 'db', 'sanctions_data', 'all_sanctions_entities_cleaned.json')
        #output_filepath = os.path.join(script_dir, 'sanctions_data', 'all_sanctions_entities_cleaned.json')
    else:
        if type(output_filepath) is not str:
            raise AssertionError(f"Input type of the output_filepath must be a string, but a {type(output_filepath)} was provided.")
    if not input_filepath:
        # The filepath where the data that needs to be cleaned is saved. Default is: 'back_end/db/sanctions_data/entities.ftm.json'
        # input_filepath = os.path.join(DIR, 'db', 'sanctions_data', 'entities.ftm.json')  # DELETE LATER (old)
        raise AssertionError(f"No input_filepath was provided. Please provide an input_filepath in order to insert new data into the sanctions database. The file should be under the directory 'tesi-kyc/back_end/db/sanctions_data/individual_countries/' and named with the 'entities.ftm(XX).json' format (replacing the 'XX' with the two-digit country code pertaining to the country's sanctions being input).")
    else:

        if type(input_filepath) is not str:
            raise AssertionError(f"Input type of the input_filepath must be a string, but a {type(input_filepath)} was provided.")
        try:
            country_of_input_file = input_filepath.split('/')[-1].split('.')[1].split('(')[1].split(')')[0]
        except IndexError as e:
            raise AssertionError(f"(Error: {str(e)}.)\nThe naming convention used for the input_filepath does not match the input requirement. The file should be under the directory 'tesi-kyc/back_end/db/sanctions_data/individual_countries/' and named with the 'entities.ftm(XX).json' format (replacing the 'XX' with the two-digit country code pertaining to the country's sanctions being input).")
        supported_countries_path = os.path.join(DIR, 'db', 'sanctions_data', 'supported_countries.csv')
        supported_countries = pd.read_csv(supported_countries_path)
        country_sanction_dir = os.path.join(DIR, 'db', 'sanctions_data', 'individual_countries')
        country_sanction_files = [os.path.join(country_sanction_dir, f) for f in os.listdir(country_sanction_dir) if os.path.isfile(os.path.join(country_sanction_dir, f))]
        if country_of_input_file in list(supported_countries['countries']):

            raise AssertionError(f"The sanction data corresponding to the country provided has already been added to the sanctions dataframe. If you are replacing the existing data for that country, please first delete the file from the {country_sanction_dir} directory, and delete the country row entry in the {supported_countries_path} file and try again.")
        if input_filepath not in set(country_sanction_files):
            raise AssertionError(f"Please make sure to add the new country's sanctions file to the {country_sanction_dir} directory first and try again.")
        #supported_countries = supported_countries.append({'countries': country_of_input_file}, ignore_index=True)
        supported_countries = pd.concat([supported_countries, pd.DataFrame([{'countries': country_of_input_file}])], ignore_index=True)
        supported_countries.to_csv(supported_countries_path, index=False)
    sanctions_raw_data = pd.read_json(input_filepath)  # defaults are: typ='frame', orient='columns'
    sanctions_raw_properties = pd.DataFrame.from_records(sanctions_raw_data["properties"])  # Flattened Properties Column
    raw_df = sanctions_raw_data.join(sanctions_raw_properties)
    clean_df = clean_data(raw_df)
    if os.path.isfile(output_filepath):
        updated_df = pd.read_json(output_filepath, orient="records")  # if the file exists, open and read it
        updated_df = pd.concat([updated_df, clean_df], ignore_index=True)  # append the newly cleaned data to it
        # updated_df.drop_duplicates(inplace=True)  # in case of adding too much unnecessery data (if needed)
        updated_df.to_json(output_filepath, orient="records")  # save it to json file in AppData.bin
        print("\n\nThe Cleaned Data has been saved to the following filepath: \n", 
              output_filepath, "\n\nHere is a summary of the data: \n")
        updated_df.info(verbose=True)
        return updated_df
    else:
        clean_df.to_json(output_filepath, orient="records")
        print("\n\nThe Cleaned Data has been saved to the following filepath: \n", 
              output_filepath, "\n\nHere is a summary of the data: \n")
        clean_df.info(verbose=True)
        return clean_df


def check_nan(val):
    """Convert NaN (aka: np.nan) values to strings and replace with empty string for data processing."""
    if val is np.nan:
        return str(val).replace(str(np.nan), '')
    else:
        return val


def lowercase_str(val):
    """
    Strip and convert all strings to lowercase for data processing. If they 
    are dicts or lists of strings, it lowercases them as well before turning 
    them back to their original type.
    """
    input_type = type(val)
    # print("Input Type: ", input_type)  # DELETE LATER
    if input_type is not str:
        val = str(val)
    val = val.lower().strip()
    # print("Lowercase Input: ", val)  # DELETE LATER
    if input_type is dict:
        val = ast.literal_eval(val)
        keys = [k.strip() for k in val.keys()]
        values = [v.strip() for v in val.values()]
        val = dict(zip(keys, values))
    if input_type is list:
        val = ast.literal_eval(val)
        val = [n.strip() for n in val]
    return val


def clean_data(df, columns_to_lowercase=[]):
    """
    Helper function to apply the check_nan() and lowercase_str() functions to the dataframe.
    """
    if str(type(df)) != "<class 'pandas.core.frame.DataFrame'>":
        raise AssertionError("If you are overriding the default dataframe value, this function only takes pd.DataFrame objects as the second argument.")
    if not columns_to_lowercase:
        columns_to_lowercase = [
            'caption', 'name', 'topics', 'country', 'alias', 'city', 'full', 'notes', 
            'postalCode', 'street', 'region', 'authority', 'provisions', 'entity', 
            'startDate', 'reason', 'sourceUrl', 'authorityId', 'endDate', 'program'
        ]
    else:
        if type(columns_to_lowercase) is not list:
            raise AssertionError(f"Input type of the columns_to_lowercase must be a list of strings, but a {type(columns_to_lowercase)} was provided.")
    # sanctions_raw_data = pd.read_json(os.path.join(DIR, 'db', 'sanctions_data', 'entities.ftm.json'))  # defaults are: typ='frame', orient='columns'
    # sanctions_raw_properties = pd.DataFrame.from_records(sanctions_raw_data["properties"])  # Flattened Properties Column
    # df = sanctions_raw_data.join(sanctions_raw_properties)
    for col in df.columns:

        df[col] = df[col].map(lambda x: check_nan(x))
    for col in columns_to_lowercase:
        if col in df.columns:

            df[col] = df[col].map(lambda x: lowercase_str(x))
    # TODO: Might want to clean the 'id' column as well.  Also, might want to save 'id' and 'caption' as their raw state and make a new column for those
    return df


def clean_input(search_input):
    """
    Strip and convert input to lowercase for data processing and string matching.
    """
    if search_input is None:
        return None
        #return ""
    if type(search_input) is not str:
        raise AssertionError(f"Input type must be a string, but a {type(search_input)} was provided.")
    return lowercase_str(search_input)


def find_matches(name_input, address_input, df):
    """
    Find matches in either the name or the address input by the user.
    """
    cleaned_name = clean_input(name_input)
    cleaned_address = clean_input(address_input)
    # attributes_to_search = ["caption", "name", "alias", "full", "street", "city", "postalCode"]
    # removed: "country", "addressEntity", "referents", "region","id", "authorityId", "sourceUrl", "entity", "authority", "reason", "provisions", "notes", "program", 
    potential_address_matches = {}
    info = []
    addresses = []

    # Finds matching names and then finds address associated with those names.
    # Need to eventually add addresses found not associated with those names (when names were found) - de-dupe will be required
    # Currently, if names are found, other addresses aren't included.
    for i, r in df.iterrows():
        check_indices_name = []
        check_indices_address = []

        if r["schema"] == "Person" or r["schema"] == "Organization" or r["schema"] == "Entity":
            if r["caption"]:
                if cleaned_name in r["caption"]:
                    if i not in check_indices_name:

                        check_indices_name.append(i)
                        info.append(dict(r))
            if r["name"]:
                for name in r["name"]:
                    if cleaned_name in name:
                        if i not in check_indices_name:

                            check_indices_name.append(i)
                            info.append(dict(r))
            if r["alias"]:
                for alias in r["alias"]:
                    if cleaned_name in alias:
                        if i not in check_indices_name:

                            check_indices_name.append(i)
                            info.append(dict(r))
        
        if cleaned_address:
            if r["schema"] == "Address":
                if r["full"]:
                    for full_addr in r["full"]:
                        if cleaned_address in full_addr:
                            if i not in check_indices_address:

                                check_indices_address.append(i)
                                potential_address_matches[r["id"]] = r
                                addresses.append(dict(r))
                if r["street"]:
                    for street in r["street"]:
                        if cleaned_address in street:
                            if i not in check_indices_address:

                                check_indices_address.append(i)
                                potential_address_matches[r["id"]] = r
                                addresses.append(dict(r))
                if r["city"]:
                    for city in r["city"]:
                        if cleaned_address in city:
                            if i not in check_indices_address:

                                check_indices_address.append(i)
                                potential_address_matches[r["id"]] = r
                                addresses.append(dict(r))
                if r["postalCode"]:
                    for postal_code in r["postalCode"]:
                        if cleaned_address in postal_code:
                            if i not in check_indices_address:

                                check_indices_address.append(i)
                                potential_address_matches[r["id"]] = r
                                addresses.append(dict(r))
                if r["region"]:
                    for region in r["region"]:
                        if cleaned_address in region:
                            if i not in check_indices_address:

                                check_indices_address.append(i)
                                potential_address_matches[r["id"]] = r
                                addresses.append(dict(r))
                if r["country"]:
                    for country in r["country"]:
                        if cleaned_address in country:
                            if i not in check_indices_address:

                                check_indices_address.append(i)
                                potential_address_matches[r["id"]] = r
                                addresses.append(dict(r))

    name_address_matches = []
    check_ids = []
    for name_match in info:
        if name_match["addressEntity"]:
            updated_addresses = []
            all_addresses = []
            for addr_entity in name_match["addressEntity"]:
                if potential_address_matches:
                    if addr_entity in potential_address_matches.keys():
                        address_match = potential_address_matches.get(addr_entity)
                        updated_addresses.extend(address_match["full"])
                        name_match["full"] = updated_addresses
                        if name_match["id"] not in check_ids:
                            check_ids.append(name_match["id"])
                            name_address_matches.append(dict(name_match))
                else:
                    address = df[df["id"] == addr_entity].iloc[0]
                    all_addresses.extend(address["full"])
                    name_match["full"] = all_addresses
                    if name_match["id"] not in check_ids:
                        check_ids.append(name_match["id"])
                        name_address_matches.append(dict(name_match))
    if name_address_matches:
        return name_address_matches
    # If no names were matched, return just the addresses found.
    sanction_data = info + addresses
    return sanction_data


def run_search(search_name, search_address=None, dataframe=None):
    if not dataframe:
        dataframe = pd.read_json(os.path.join(DIR, 'db', 'sanctions_data', 'all_sanctions_entities_cleaned.json'), typ='frame')
    else:
        if str(type(dataframe)) != "<class 'pandas.core.frame.DataFrame'>":
            raise AssertionError("If you are overriding the default dataframe value, this function only takes pd.DataFrame objects as the third argument.")
    search_results = find_matches(search_name, search_address, dataframe)
    return search_results
