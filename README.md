# Transaction Evaluation for Suspicious Indicators (TESI) Know-Your-Customer (KYC) Tool

## Description
Transaction Evaluation for Suspicious Indicators (TESI©) is a simple tool developed by Sandia National Laboratories (SNL) to help chemical distributors, suppliers, and retailers implement Know Your Customer (KYC) best practices for dual-use chemicals.  In the scope of this tool, dual-use chemicals include chemicals defined by the Organisation for the Prohibition of Chemical Weapons (OPCW), Wassenaar Arrangement, or Australia Group, as well as toxic industrial chemicals that pose a risk if used in a malicious scenario.

The tool is designed around a framework that integrates an organization’s products, customers, sales, and shipping databases. This integrated database approach helps the facility to identify any abnormalities (or suspicious indicators) during the sale of their products which may be a security concern. The goal of TESI is to identify high-risk product sales by showing the seller suspicious indicators or “red flags” prior to the product being sold or otherwise provided to a customer.  

The KYC tool looks at a number of suspicious indicators, including validation of the customer (ensuring they are who they claim to be), scrutinizing unusual orders (may include orders outside the normal activity of a customer), changes in order placement or funding source, requesting unusual shipping routes or packaging, or asking unusual questions during the placement of the order which may raise suspicion about the intended use of the chemicals. The scope of the tool is for small-to-medium companies, but the underlying methodology can be applied across any organization selling products that may contain dual-use chemicals.  

*NOTE: The TESI software is only one example of sales management or Customer Relationship Management (CRM) software that can be used. There are others in forms in varying complexity. We encourage further investigation into available software to best fit your management system needs.*

A proper sales management system will ultimately lead to better data integration, automation, and data reporting capabilities for both the identification of suspicious indicators as well as sales management. These benefits not only reduce time and resource costs but also improve recordkeeping, which supports historical data analysis. The TESI software is easy to use and implements a chemical sales database system that supports broader sales operations. 

## License
Copyright 2026 National Technology & Engineering Solutions of Sandia, LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S. Government retains certain rights in this software.


## APP USAGE:

To install requirements so far, run:
    `$ pip install -r requirements.txt`

To run the Flask Application, run:
    `$ flask run` 

To run the Flask Application on Development/Debugging Mode, run:
    `$ flask run --debug`
    OR
    `$ flask run --reload`

On Windows machines, if flask is not registered in the system path and the above commands do not work, try:
    `$ python -m flask run --reload`

## Database Access
To open the internal SQLite3 database, download the SQLite Tools bundle (https://www.sqlite.org/download.html), unzip them, and then open the database file in the project db directory with the .open command like this:
    `.open C:/Sites/TESI2/tesi-kyc/back_end/db/tesi_tool.sqlite3`

## Packaging the Application

Based on your operating system, run the following python command to package the app with the console hidden.

Windows:
    `python -m PyInstaller -D --add-data "back_end:back_end" --add-data "front_end:front_end" --noconsole app.py`

Linux/Mac:
    `pyinstaller -w -D --add-data "back_end:back_end" --add-data` `"front_end:front_end" app.py --hidden-import=sqlite3`

## Updating the Sanctions Query Database (Developers Only):
    Sanctions data which has been loaded:
    - United States (US): https://www.trade.gov/consolidated-screening-list (API Source: https://api.trade.gov/static/consolidated_screening_list/consolidated.json)
    - Australia (AU): https://www.dfat.gov.au/international-relations/security/sanctions/consolidated-list (File Source: https://www.dfat.gov.au/sites/default/files/regulation8_consolidated.xlsx)
    - Singapore (SG): https://sso.agc.gov.sg/Act/TSFA2002?ProvIds=Sc1-#Sc1- (File Source: https://sso.agc.gov.sg/Act/TSFA2002?ProvIds=Sc1-#Sc1-)
    - EU Financial Sanctions Files (EU): https://www.eeas.europa.eu/eeas/european-union-sanctions_en#10710 (File Source: https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/content?token=dG9rZW4tMjAxNw)

    Import the United States (US) CSL list by saving it as input.json in the '/tesi-kyc/back_end/db/sanctions_data' directory and running the us_csl_import.py script. This converts the data into a format which is compatible with data from OpenSanctions.org. From there, follow the instructions below for importing data using the OpenSanctions.org style formats. The following scripts may be tailored to import sanctions data:
    - aus_csl_import.py (imports Excel .xlsx files)
    - eu_sanctions_import.py (imports XML files)
    - us_csl_import.py (imports JSON files)

# Importing data with OpenSanction.org format
    Sanctions data can be downloaded from Open Sanctions (https://www.opensanctions.org/datasets/).

    Tested Sanctions Sources (from the files entitled: entities.ftm.json):
        - United States (US): https://www.opensanctions.org/datasets/us_trade_csl/
        - European Union (EU): https://www.opensanctions.org/datasets/eu_fsf/
        - Australia (AU): https://www.opensanctions.org/datasets/au_dfat_sanctions/
        - Japan (JP): https://www.opensanctions.org/datasets/jp_mof_sanctions/
        - Singapore (SG): https://www.opensanctions.org/datasets/sg_terrorists/

All of the relevant code and data are housed in the `/tesi-kyc/back_end/db/sanctions_data/` directory.

To upload a new country's sanctions into the sanctions database, for querying later by the user in the application, follow the below steps:

- In a new terminal, navigate to the `tesi-kyc/` home directory. 

- Make sure to save the new sanctions data file you are uploading into the `/tesi-kyc/back_end/db/sanctions_data/individual_countries/` directory. This needs to be saved with the format `entities.ftm(XX).json` (replacing the 'XX' with the two-digit country code pertaining to the country's sanctions being input). For example, `entities.ftm(us).json` would contain all of the sanctions for the United States (US).

- With your relevant environment activated, activate your python interpreter:
    `$ ipython`
    OR
    `$ ipython3`

- Import the upload_new_country_sanctions() function into your python interpreter:
    `from back_end.utils.sanctions_query import upload_new_country_sanctions`

- Execute the below command to incorporate the new country's sanctions data into the database. Make sure to include the entire filepath of the document, for example: '/tesi-kyc/back_end/db/sanctions_data/individual_countries/entities.ftm(us).json'. 
    `upload_new_country_sanctions(input_filepath='/tesi-kyc/back_end/db/sanctions_data/individual_countries/entities.ftm(sg).json')`
    or for Windows machines:
    `upload_new_country_sanctions(input_filepath='C:\\Sites\\TESI2\\tesi-kyc\\back_end\\db\\sanctions_data\\individual_countries\\entities.ftm(au).json')`

- You have now uploaded your new sanctions data to the database.

## Deleteing Old Sanctions Data
If there is ever a need to delete old data (for example, if there is a new year of sanctions data, and you are replacing the existing data for a particular country), go into the `/tesi-kyc/back_end/db/sanctions_data/individual_countries/` directory and delete the relevant country's file. Then, delete the country row entry in the `/tesi-kyc/back_end/db/sanctions_data/supported_countries.csv` file. Finally, delete the `/tesi-kyc/back_end/db/sanctions_data/all_sanctions_entities_cleaned.json` file, and re-run the `upload_new_country_sanctions()` function with all of the relevant country's files (whether they were updated or not).