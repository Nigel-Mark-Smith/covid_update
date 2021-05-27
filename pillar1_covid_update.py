# pillar1_covid_update.py
#
# Description
# -----------
# This script will download the current English COVID-19 ( Pillar 1 ) csv data
# file and output a processed set of data for a sub-set of the NHS areas of
# the tier type specified. Included in this output is an estimate of the current 
# number of infectious people which is derived from the cumulative confirmed cases 
# data and a constant 'InfectiousPeriod' repesenting the number of days for which 
# a confirmed case remains infectious. Log messages indicating whether the rolling average 
# number of infectious people is increasing of decreasing are also generated. The rolling 
# average period is the same as 'InfectiousPeriod'. For further details on the data used see:
# 
# https://coronavirus.data.gov.uk/about-data
# 
# Usage
# -----
# This script requires no command line arguments but an optional configuration file
# name may be specified overriding the default name 'pillar1_configuration.csv'. 
# The script may then be run in the following ways:
#
# python pillar1_covid_update.py
# python pillar1_covid_update.py <configuration file name>
#
# The script will launch 'spreadsheet' to display the generated csv
# if the number of infectious people has just gone up in the last
# rolling average period.
#
# Statistics file
# ---------------
# This script will generate a statistics file containing extracted 
# data for the specified NHS tiers plus a derived column 'Contagious'.
# The name of the file is of the following format:
#
# Pillar1_<tier type string>_<YYYY><MM><DD>
#
# The first line of the file contains the following headers for the data
# columns:
#
# Area,Date,Daily,Infectious,Cumulative,Rate
# 
# Data and configuration files
# ----------------------------
# The following configuration file is required by
# this script:
#
# .\config\pillar1_configuration.csv               
#
# This csv file consists of one line with the following comma
# separated values:
#
# <url of download file>,<area tier type>,<infectious period in days>,<region 1>,<region 2>...<region x>
#
# Where:
# 
# - The area tier type must match one of the tier types found in the data i.e.
#
#   Nation
#   Region
#   Upper tier local authority
#   lower tier local authority
#
# If the users specifies an optional configuration file whilst running this script
# the file must have the the same format as .\config\pillar1_configuration.csv
#
# Logging
# -------
# This script logs error and status messages to the file .\log\log.txt
#

import re
import requests
from datetime import date,timedelta
import time
import os
import sys
import subprocess
import File.Operations as File
import Interface.Prompts as Interface

# This procedure will determine if 'string' is present
# at 'index' in 'list'
def IsPresent(string,index,list) :

    "This procedure will determine if 'string' is  present at 'index' in 'list'"
    
    result = False
    if ( re.match(string,list[index]) ) : result = True
    
    return result
 
# This procedure will return a string containing the
# elements of list separated by a comma. All elements are
# cast to strings.
def GenerateCSVRow(list) :
 
    "This procedure will generate a string containing the elements of 'list' separated by a comma"
 
    string = ''
    for item in list : string = string + str(item) + ',' 
    string = string.rstrip(',')
    
    return string
    
# This procedure will return a list of values contained
# in 'dictionary' referenced by 'keys'.
def GenerateFieldList(keys,dictionary) : 

    "This procedure will return a list of values contained in 'dictionary' referenced by 'keys'"
    
    list = []
    for key in keys : list.append(dictionary[key])
    
    return list
    
# This procedure returns a date object from a 'specimendate'.
def ReturnDate(specimendate) :

    "This procedure returns a date object from a 'specimendate'"
    
    list = specimendate.split('-')
    year = int(list[0])
    month = int(list[1])
    day = int(list[2])
    
    return date(year, month, day)
    
# This procedure will return a tier type string
def ReturnTierType(string) :

    "This procedure will return a shortened teir type string"
    
    result = string
    
    if ( string.startswith('utla') ) : result = 'upper'
    if ( string.startswith('ltla') ) : result = 'lower'
        
    return result
    
# This procedure returns a file name string based on todays date
# a 'base' string and a teir type string.
def ReturnFileName(base,type) :

    "This procedure returns a file name string based on todays date and a 'base' name"
    
    today = date.today()
    month = str(today.month)
    year = str(today.year) 
    day = str((today.day))    
    
    # Add leading 0 if required
    if ( len(month) == 1 ) : month = '0' + month 
    if ( len(day) == 1 ) : day = '0' + day
    
    name = base + '_' + type + '_' + year + month + day + '.csv'
    
    return name

# This procedure will remove the decimal part of a string representation
# of a float.
def GetDecimalPart(string) :

    "This procedure will remove the decimal part of a string representation of a float"
    
    part = string.split('.')[0]
    # Protection against empty fields in csv file.
    if ( len(part) == 0 ) : part = '0'
    
    return part
           
############
### MAIN ###
############

# Allowed variation in infetctious count.
Variation = 5

# File names and modes
Currentdir = os.getcwd()
LogDir = Currentdir + '\\log'
ErrorFilename = LogDir + '\\' + 'log.txt'
ConfigDir = Currentdir + '\\config'
ConfigurationFilename = ConfigDir + '\\' + 'pillar1_configuration.csv'
DataDir = Currentdir + '\\data'
append = 'a'
read = 'r'
overwrite = 'w'

# Function return values
invalid = failure = 0
empty = ''
success = 1

# Error levels
error = 'ERROR'
warning = 'WARNING'
info = 'INFO'

# Script names
module = 'pillar1_covid_update'

# Spreadsheet
Spreadsheet = 'excel.exe'

# Input data column numbers
Columns = {'Area':0,'Type':2,'Date':3,'Daily':4,'Cumulative':5,'Rate':6}

# Output data columns
OutColumns = ['Area','Date','Daily','Infectious','Cumulative','Rate']

# Create/open log file
ErrorFileObject = File.Open(ErrorFilename,append,failure)
Errormessage = 'Could not open ' + ErrorFilename
if ( ErrorFileObject == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

# Log start of script
File.Logerror(ErrorFileObject,module,'Started',info)

# Process optional configuration file argument
if ( len(sys.argv) > 1 ) : ConfigurationFilename = ConfigDir + '\\' + sys.argv[1]

# Log progress messages
Errormessage = 'Reading configuration file %s ' % ConfigurationFilename
File.Logerror(ErrorFileObject,module,Errormessage,info)

# Open and parse configuration file
ConfigurationFileObject = File.Open(ConfigurationFilename,read,failure)
Errormessage = 'Could not open ' + ConfigurationFilename
if ( ConfigurationFileObject == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

ConfigurationFileData = File.Read(ConfigurationFileObject,empty)
if ( ConfigurationFileData != empty ) : 
    ConfigurationFileDataList = ConfigurationFileData.split(',')
    CovidPage = ConfigurationFileDataList[0]
    TierString = ConfigurationFileDataList[1]
    StatisticsFilename = DataDir + '\\' + ReturnFileName('pillar1',ReturnTierType(TierString))
    InfectiousPeriod = int(ConfigurationFileDataList[2])
    Areas = ConfigurationFileDataList[3:]
else:
    Errormessage = 'No data in ' + ConfigurationFilename
    File.Logerror(ErrorfileObject,module,Errormessage,error)

# Close Configuration file
Errormessage = 'Could not close ' + ConfigurationFilename
if ( File.Close(ConfigurationFileObject,failure) == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,warning)

# Log progress messages
Errormessage = 'Retrieving file %s ' % CovidPage
File.Logerror(ErrorFileObject,module,Errormessage,info)

# 'Download' data file
Response = requests.get(CovidPage)
if ( Response.status_code != 200 ) :
    Errormessage = 'GET operation for %s failed' % CovidPage
    File.Logerror(ErrorFileObject,module,Errormessage,error)
     
ResponseLines = Response.text.splitlines()
if ( len(ResponseLines) == 0 ) :
    Errormessage = '%s is an empty file' % CovidPage
    File.Logerror(ErrorFileObject,module,Errormessage,error)
    
# Log progress messages
Errormessage = 'Extracting data for %s %s ' % (TierString,str(Areas))
File.Logerror(ErrorFileObject,module,Errormessage,info)

# Intialize Area data sets
AreaData = {}
for Area in Areas : AreaData[Area] = []

# Initialize area line counts
AreaDataCount = {}
for Area in Areas : AreaDataCount[Area] = 0

# Extract data for specified Area's.
for ResponseLine in ResponseLines :
    
    # Protect against empty lines.
    if ( len(ResponseLine) == 0 ) : break
    
    DataRow = ResponseLine.split(',')
    if ( IsPresent(TierString,Columns['Type'],DataRow) ) :
        for Area in Areas :     
            if ( IsPresent(Area,Columns['Area'],DataRow) ) :  
            
                AreaDataCount[Area] += 1
                
                # Replace date string with date object so date
                # differences can be calculated.
                DataRow[Columns['Date']] = ReturnDate(DataRow[Columns['Date']])
                
                # Protects against decimal and null values in these fields which makes no sense.
                DataRow[Columns['Daily']]  = GetDecimalPart(DataRow[Columns['Daily']])
                DataRow[Columns['Cumulative']]  = GetDecimalPart(DataRow[Columns['Cumulative']])
                
                # Note: data is provided in descending date order and must be reversed
                AreaData[Area].insert(0,DataRow)
                
# Dislay the number of dat items detected for each area
for Area in Areas :
    Errormessage = '%i data rows were found for %s %s ' % (AreaDataCount[Area],TierString,Area)
    File.Logerror(ErrorFileObject,module,Errormessage,info)
                          
# Open Statics file
StatisticsFileObject = File.Open(StatisticsFilename,overwrite,failure)
Errormessage = 'Could not open ' + StatisticsFilename
if ( StatisticsFileObject == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

# Set alarm to false
AttentionFlag = False

# Print enhanced data

# Column headings
Headings = GenerateCSVRow(OutColumns)
Headings = Headings + '\n'
File.Writeline(StatisticsFileObject,Headings,failure)

for Area in AreaData : 
    
    # Initialize infectious totals
    Infectious = 0
    InfectiousPrevious = 0
    
    for SpecimenPeriod in range(0,(len(AreaData[Area]))) :
               
        OutData = {}
        for Column in Columns : OutData[Column] = AreaData[Area][SpecimenPeriod][Columns[Column]]
               
        # Log increase/decrease messages
        if ( InfectiousPrevious != 0 ) :
            Indicator = 'Decreasing'
            InfectiousIncrease = Infectious - InfectiousPrevious
            if ( InfectiousIncrease > 0 ) : Indicator = 'Potentially Increasing'
            if ( InfectiousIncrease >= Variation  ) : Indicator = 'Increasing'
            Errormessage = 'Infectious cases %s in %s on %s' % (Indicator,Area,str(CurrentSpecimenDate))
            File.Logerror(ErrorFileObject,module,Errormessage,info)
        
        # Save previous infectious numbers for attention flag and increase/decrease warnings.
        InfectiousPrevious = Infectious
        
        # Determine number of cases no longer infectious (Recovered)
        Recovered = 0
        
        CurrentSpecimenDate = AreaData[Area][SpecimenPeriod][Columns['Date']]
        for PreviousPeriod in range(SpecimenPeriod,0,-1) : 
            PreviousSpecimenDate = AreaData[Area][PreviousPeriod][Columns['Date']]
            SpecimenDateDiff = CurrentSpecimenDate - PreviousSpecimenDate
            if ( SpecimenDateDiff.days >= InfectiousPeriod ) :
                Recovered = int(AreaData[Area][PreviousPeriod][Columns['Cumulative']])
                break
                   
        Cumulative = OutData['Cumulative'] 
        Infectious = int(Cumulative) - Recovered
        OutData['Infectious'] = str(Infectious)
               
        # Data row
        Row =  GenerateCSVRow(GenerateFieldList(OutColumns,OutData)) 
        Row = Row + '\n'
        File.Writeline(StatisticsFileObject,Row,failure)
    
    # Generate final trend message and determine if attention flag should be raised
    Indicator = 'Decreasing'
    InfectiousIncrease = Infectious - InfectiousPrevious  
    if ( InfectiousIncrease > 0 ) : Indicator = 'Potentially Increasing'
    if ( InfectiousIncrease >= Variation  ) : 
        Indicator = 'Increasing'
        AttentionFlag = True
    Errormessage = 'Infectious cases %s in %s on %s' % (Indicator,Area,str(CurrentSpecimenDate))
    File.Logerror(ErrorFileObject,module,Errormessage,info)
    
    # Log some good news
    if ( Infectious == 0  ) :
        Errormessage = 'No infectious Pillar 1 cases in %s on %s' % (Area,str(CurrentSpecimenDate))
        File.Logerror(ErrorFileObject,module,Errormessage,info)
        
        
# Close Statistics file
Errormessage = 'Could not close ' + StatisticsFilename
if ( File.Close(StatisticsFileObject,failure) == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,warning)   

# Display manual step message and launch Excel if increase in infectious total detected
if ( AttentionFlag )  :
    Errormessage = 'Increase in infectious count detected, please view %s' % StatisticsFilename
    File.Logerror(ErrorFileObject,module,Errormessage,warning)
    Interface.ViewSpeadsheet(Spreadsheet,StatisticsFilename)     
        
# Log end of script
File.Logerror(ErrorFileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + ErrorFilename
if ( File.Close(ErrorFileObject,failure) == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,warning)
