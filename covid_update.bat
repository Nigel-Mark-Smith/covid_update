@echo off
rem This batch file generates all my derived Pillar 1, Pillar 2 and COVID-19
rem (England only) data files.
erase log\log.txt
erase data\pillar*.csv
erase data\trust*.csv
erase data\*.xlsx
pillar1_covid_update.py nation.csv
pillar1_covid_update.py region.csv
pillar1_covid_update.py upper.csv
rem Introduced a pause as there seems to be some gapping
rem applied to requests for this data file.
timeout 2 /nobreak
pillar1_covid_update.py lower.csv
rem CSV files for Pillar testing and death data no longer updated 
rem pillar2_covid_update.py
nhs_trust_deaths.py
rem Display any areas with no Pillar1 infectious cases
findstr /C:"No infectious" log\log.txt