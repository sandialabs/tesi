# Transaction Evaluation for Suspicious Indicators (TESI) Know-Your-Customer (KYC) Tool

## Description
Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Installation
Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

## License
For open source projects, say how it is licensed.

## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.


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