# covid_update

This repository delivers utility scripts 'pillar1_covid_update.py', 'pillar2_covid_update.py' 
'nhs_trust_deaths.py' and 'covid_update.bat' which support the processing of publicly available 
COVID-19 data and raise alerts to the user relating to negative trends in this data. The data is 
retrieved from a number of publically available files. The python utilities 'pillar1_covid_update.py',
'pillar2_covid_update.py' and 'nhs_trust_deaths.py' each have a configuration file which allows the 
criteria under which alerts are raised to be changed to increase or decrease 'sensitivity'. It 
is envisaged that script 'covid_update.bat' should be run daily to assist the user in being 'alert' 
to current COVID-19 trends.  As perparation for running script 'covid_update.bat'  the user should 
amend the following files to add the name(s) of the nhs nation, nhs regions, nhs upper tier local 
authrorities (utla's) nhs lower tier local authorities (ltla's) and nhs hospital trusts they wish 
to monitor.

- ./config/nation.csv
- ./config/region.csv
- ./config/upper.csv
- ./config/lower.csv
- ./config/trust_deaths.csv

At the time of writing the default configuration files delivered contain valid nhs organization names.  

Note
----
Since these scripts were originally written a number of download files are no longer available 
with the data access being migrated to the UK COVD-19 API. As a result the script 
'pillar2_covid_update.py' no longer works and script 'pillar1_covid_update.py' has been rewritten to 
use API calls. New utilties using the API are available in the 'covid_alerts' repository and the user 
is recommended to use these instead. 

Deliverables
------------
To implement the functionality discussed above the following scripts and configuration files are delivered:

File | File Contents
------------- | -------------
covid_update.bat | Runs all utiltity scripts to raise any and all alerts relating to current COVID_19 data
pillar1_covid_update.py | Script generating alerts and csv output files relating to current case rates.
pillar2_covid_update.py | Script generating alerts and csv output files relating to current testing and death rates.
nhs_trust_deaths.py | Script generating alerts and csv output files relating to current death rates for each monitored trust.
pillar1_configuration.csv | Default configuration file for pillar1_covid_update.py
nation.csv | Configuration file for pillar1_covid_update.py specifying nations to be monitored (England)
region.csv | Configuration file for pillar1_covid_update.py specifying regions to be monitored
upper.csv | Configuration file for pillar1_covid_update.py specifying utla's to be monitored
lower.csv | Configuration file for pillar1_covid_update.py specifying ltla's to be monitored
pillar2_configuration.csv | Default configuration file for pillar1_covid_update.py
convert_workbook.vbs | VBasic script used to extract nhs trust death data from Excel file
ExtractTrustDeaths.txt | Source for Excel macro ExtractTrustDeaths used by convert_workbook.vbs

As well as the above scripts and data files the following supporting documentation is also provided:

Document File | File Contents
------------- | -------------
covid_update_installation.txt | Installation instructions
covid_update.docx | User documentation.
covid_update_testing.txt | Script testing information
covid_update_api_requests.txt | curl commands for manual verification of data availability