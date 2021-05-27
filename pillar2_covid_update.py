# pillar2_covid_update.py
#
# Description
# -----------
# This script will download the current UK COVID-19 ( Pillar 2 ) testing series
# and death series data and output an enhanced sub-set of each data to csv files. 
# The following additional data is generated:
# 
# For testing series.
#
# - The percentage of each daily set of tests that are postive.
# - The number of positive tests in a rolling period up to the sample date
#
# For death series.
#
# - The number of deaths in a rolling period up to the sample date
#
# Log messages indicating whether the percentage of postive tests and the number of 
# deaths in a rolling period are decreasing or increasing are generated during the 
# processing of the respective data files. 'Variation' values for each of the data sets 
# are defined in the scripts configuration file which will modify the increasing/decreasing 
# messages to highlight where the increase detected is small (not significant). For further 
# details regarding Pillar 2 data see:
# 
# https://www.gov.uk/guidance/coronavirus-covid-19-information-for-the-public
# 
# Usage
# -----
# This script requires no command line arguments and may be run in the 
# following way:
#
# python pillar2_covid_update.py
#
# The script will launch 'spreadsheet' to display the generated csv
# file(s) if the number of deaths in the latest rolling period is greater 
# than in the previous rolling period, or the percentage of positive
# tests has increased between the two lastest sample dates.
#
# Statistics file
# ---------------
# This script will generate a csv file for each of the types of  
# data and will name them as below:
#
# .\data\pillar2_testing_<YYYY><MM><DD>
# .\data\pillar2_death_<YYYY><MM><DD>
#
# The first line of each file contains the headers for the data
# columns included. These headers are as follows:
#
# - For testing series
#
# Date,Daily,CumulativeDaily,Positive,Percentage,CumulativePositive,Rolling
# 
# - For death series
#
# Date,Daily,Cumulative,Rolling
#
# Data and configuration files
# ----------------------------
# The following configuration file is required by
# this script:
#
# .\config\pillar2_configuration.csv               
#
# This csv file consists of two lines one for each of the data sets. The lines can appear in any order
# in the file and have the following format:
#
# <data set type>,<url of download page>,<regular expression for determining download file name>,<pillar string>,<rolling period>,<variation>
# 
# Where:
# 
# - 'data set type' is one of the following and is used to distinguish which configuration line is for which data file.
#
#   testing
#   death
#
# - 'pillar string' is used to filter on the contents of the Pillar field in the testing series data so that only the relevant Pillar 2 data is included.
# - 'rolling period' is set to the length of the rolling period in days.
# - 'variation' is set to a increase in percentage or rolling value that is deemed to be insignificant.   
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

# Finds url for download file
def FindDownloadFile(url,content) :

    "Finds url for download file"
	
    Link = ""
     
    Httpresponse = requests.get(url)
    Httplines = Httpresponse.text.split('\n')
	
    # Search for content
	
    for Httpline in Httplines : 
        Httpmatch = re.search(content,Httpline)
        if Httpmatch: 
            Link = Httpmatch.group(0)
            break
			
    return Link
    
# This procedure will determine if the data type specified
# by string is valid. It compares string with all the key 
# values of dictionary.
def ConfigurationDataTypeValid(string,dictionary) :

    "This procedure will determine if the data type specified by string is valid"
    
    result = False
    
    for key in dictionary : 
        if ( key == string ) : result = True
    
    return result
    
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
# The dictionary 'conversion' is used to convert month strings
# to month numbers
def ReturnDateDeath(specimendate,conversion) :

    "This procedure returns a date object from a 'specimendate. The dictionary 'conversion' is used to convert month strings to month numbers"
    
    list = specimendate.split('-')
    yearstring = '20' + list[2]
    year = int(yearstring)
    daystring = list[0]
    day = int(daystring)
    monthstring = list[1]
    month = conversion[monthstring]
       
    return date(year, month, day)
    
# This procedure returns a date object from a 'specimendate'.
def ReturnDateTesting(specimendate) :

    "This procedure returns a date object from a 'specimendate. The dictionary 'conversion' is used to convert month strings to month numbers"
    
    # Fix for bad data. Hopefully this will be corrected soon.
    if ( specimendate.startswith('the') ) : specimendate = '20/06/2020'
    
    list = specimendate.split('/')
    year = int(list[2])
    month = int(list[1])
    day = int(list[0])
    
    return date(year, month, day)
    
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

# File names and modes
Currentdir = os.getcwd()
LogDir = Currentdir + '\\log'
ErrorFilename = LogDir + '\\' + 'log.txt'
ConfigDir = Currentdir + '\\config'
ConfigurationFilename = ConfigDir + '\\' + 'pillar2_configuration.csv'
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
module = 'pillar2_covid_update'

# Spreadsheet
Spreadsheet = 'excel.exe'

# Month conversion data
MonthConverter = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

# Data (file) types
testing = 'testing'
death = 'death'
ConfigurationDataTypes = [testing,death]
ConfigurationDataTypePresent = {}
ConfigurationDataTypeIndex = {}
AttentionFlag = {}

for ConfigurationDataType in ConfigurationDataTypes : 
    ConfigurationDataTypePresent[ConfigurationDataType] = False
    ConfigurationDataTypeIndex[ConfigurationDataType] = 0
    AttentionFlag[ConfigurationDataType] = False

# Input data column numbers
Columns = {}
Columns[testing] = {'Date':0,'Pillar':3,'Daily':6,'CumulativeDaily':7,'Positive':10,'CumulativePositive':11}
Columns[death] = {'Date':0,'Daily':3,'Cumulative':2}

# Data format change date whe neww columns relevant
# Columns[testing] = {'Date':0,'Pillar':3,'Daily':6,'CumulativeDaily':7,'Positive':12,'CumulativePositive':13}
TestingDataChangeDate = date(2020,7,1)
DeathDataFailDate = date(2020,7,16)
DataDecrement = 30301

# Output data columns
Output = {}
Output[testing] = {'Date':0,'Daily':1,'CumulativeDaily':2,'Positive':3,'Percentage':4,'CumulativePositive':5,'Rolling':6}
Output[death] = {'Date':0,'Daily':1,'Cumulative':2,'Rolling':3}

# Create/open log file
ErrorFileObject = File.Open(ErrorFilename,append,failure)
Errormessage = 'Could not open ' + ErrorFilename
if ( ErrorFileObject == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

# Log start of script
File.Logerror(ErrorFileObject,module,'Started',info)

# Log progress messages
Errormessage = 'Reading configuration file %s ' % ConfigurationFilename
File.Logerror(ErrorFileObject,module,Errormessage,info)

# Open and parse configuration file
ConfigurationFileObject = File.Open(ConfigurationFilename,read,failure)
Errormessage = 'Could not open ' + ConfigurationFilename
if ( ConfigurationFileObject == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,error)

ConfigurationFileData = File.Read(ConfigurationFileObject,empty)
if ( ConfigurationFileData != empty ) : 
    ConfigurationFileDataLines = ConfigurationFileData.split('\n')
else:
    Errormessage = 'No data in ' + ConfigurationFilename
    File.Logerror(ErrorfileObject,module,Errormessage,error)

# Close Configuration file
Errormessage = 'Could not close ' + ConfigurationFilename
if ( File.Close(ConfigurationFileObject,failure) == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,warning)

# Parse configuration file.
ConfigurationFileDataLists = []
DataIndex = 0

for ConfigurationFileDataLine in ConfigurationFileDataLines :

    ConfigurationFileDataList = ConfigurationFileDataLine.split(',')
    ConfigurationDataType = ConfigurationFileDataList[0]
    
    if ( ConfigurationDataTypeValid(ConfigurationDataType,ConfigurationDataTypePresent) ) :
        ConfigurationFileDataLists.append(ConfigurationFileDataList)
        ConfigurationDataTypePresent[ConfigurationDataType] = True
        ConfigurationDataTypeIndex[ConfigurationDataType] = DataIndex
    else :
        Errormessage = 'Data type %s specified in line %i is not valid ' % (ConfigurationDataType,(DataIndex + 1))
        File.Logerror(ErrorFileObject,module,Errormessage,warning)

    DataIndex += 1
    
# Determine url's for download files.
DownLoadFiles = []

for ConfigurationFileDataList in ConfigurationFileDataLists :

    # Scrape web content to determine download file urls.
    ConfigurationDataType = ConfigurationFileDataList[0]
    DownLoadWebPage = ConfigurationFileDataList[1]
    DownLoadFilePattern = ConfigurationFileDataList[2]
    DownLoadFile = FindDownloadFile(DownLoadWebPage,DownLoadFilePattern)
     
    if ( len(DownLoadFile) == 0 ) : 
        Errormessage = 'No download file for data type %s found' % ConfigurationDataType
        File.Logerror(ErrorFileObject,module,Errormessage,error)
    else:
        DownLoadFiles.append(DownLoadFile)


# Intialize series data sets
SeriesData = {}
for ConfigurationDataType in ConfigurationDataTypes : SeriesData[ConfigurationDataType] = []

# Initialize series line counts
SeriesDataCount = {}
for ConfigurationDataType in ConfigurationDataTypes : SeriesDataCount[ConfigurationDataType] = 0

# Download and parse data files 
for ConfigurationDataType in ConfigurationDataTypes :
        
    if ( ConfigurationDataTypePresent[ConfigurationDataType] ) : 
    
        # Retrieve configuration items
        DownLoadFile = DownLoadFiles[ConfigurationDataTypeIndex[ConfigurationDataType]]
        ConfigurationFileDataList = ConfigurationFileDataLists[ConfigurationDataTypeIndex[ConfigurationDataType]]
        PillarString = ConfigurationFileDataList[3]
        
        # Log progress messages
        Errormessage = 'Retrieving %s data file ' % ConfigurationDataType
        File.Logerror(ErrorFileObject,module,Errormessage,info)
        
        Response = requests.get(DownLoadFile)
        if ( Response.status_code != 200 ) :
            Errormessage = 'GET operation for %s failed' % DownLoadFile
            File.Logerror(ErrorFileObject,module,Errormessage,error)
     
        ResponseLines = Response.text.splitlines()
        if ( len(ResponseLines) == 0 ) :
            Errormessage = '%s is an empty file' % DownLoadFile
            File.Logerror(ErrorFileObject,module,Errormessage,error)
        
        # Remove header line of file
        ResponseLines.pop(0)
        
        for ResponseLine in ResponseLines :
        
            # Protect against empty lines
            if ( len(ResponseLine) == 0 ) : break
            
            # split data line
            DataRow = ResponseLine.split(',')
             
            # Skip any data lines in testing data that do not contain the right Pillar identification     
            # or are empty
            if ( ConfigurationDataType == testing ) :  
                if not ( IsPresent(PillarString,Columns[testing]['Pillar'],DataRow ) ) : continue
                if ( len(DataRow[Columns[testing]['Daily']]) == 0 ) : continue
                
            # Skip any data lines with non numeric data where there should be.
            if ( ConfigurationDataType == death ) :
                if not ( DataRow[Columns[death]['Cumulative']].isdigit() ) : continue

            # Process date information
            if ( ConfigurationDataType == death ) :
                DataRow[Columns[ConfigurationDataType]['Date']] = ReturnDateDeath(DataRow[Columns[ConfigurationDataType]['Date']],MonthConverter)
                            
            if ( ConfigurationDataType == testing ) :
                ConvertedDate = ReturnDateTesting(DataRow[Columns[ConfigurationDataType]['Date']])
                DataRow[Columns[ConfigurationDataType]['Date']] = ConvertedDate
                
                # Correct data after data change date.
                if ( ConvertedDate >= TestingDataChangeDate ) : 
                
                    DataRow[Columns[ConfigurationDataType]['Positive']] = DataRow[12]
                    
                    # Protect against non numerical values
                    if not ( DataRow[Columns[testing]['Positive']].isdigit() ) : continue
                    
                    CovertedCumlativePositive = str(int(DataRow[13]) + DataDecrement)
                    DataRow[Columns[ConfigurationDataType]['CumulativePositive']] = CovertedCumlativePositive          
                        
            # Build data structure
            SeriesDataCount[ConfigurationDataType] = SeriesDataCount[ConfigurationDataType] + 1
            SeriesData[ConfigurationDataType].append(DataRow)
            

# Process file data.
for ConfigurationDataType in ConfigurationDataTypes :

    # Log progress messages
    Errormessage = 'Processing %s data file ' % ConfigurationDataType
    File.Logerror(ErrorFileObject,module,Errormessage,info)
    
    # Retrieve configuration information
    ConfigurationFileDataList = ConfigurationFileDataLists[ConfigurationDataTypeIndex[ConfigurationDataType]]
    RollingPeriod =  int(ConfigurationFileDataList[4])
    if ( ConfigurationDataType == death) : Variation = int(ConfigurationFileDataList[5])
    if ( ConfigurationDataType == testing) : Variation = float(ConfigurationFileDataList[5])
    
    # Generate statistics file name
    StatisticsFilename = DataDir + '\\' + ReturnFileName('pillar2',ConfigurationDataType)
    
    # Open statics file
    StatisticsFileObject = File.Open(StatisticsFilename,overwrite,failure)
    Errormessage = 'Could not open ' + StatisticsFilename
    if ( StatisticsFileObject == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,error)
    
    # Column headings
    Headings = GenerateCSVRow(Output[ConfigurationDataType])
    Headings = Headings + '\n'
    File.Writeline(StatisticsFileObject,Headings,failure)
    
    # Generate derived data
    PercentagePrevious = 0
    RollingPrevious = 0
    Percentage = 0
    Rolling = 0
    
    for SpecimenPeriod in range(0,(len(SeriesData[ConfigurationDataType]))) :
        
        OutData = {} 
        for Column in Columns[ConfigurationDataType] : OutData[Column] = SeriesData[ConfigurationDataType][SpecimenPeriod][Columns[ConfigurationDataType][Column]]
        
        if ( ConfigurationDataType == death ) :
        
            if ( RollingPrevious != 0 ) :
                Indicator = 'Decreasing'
                RollingIncrease = Rolling - RollingPrevious
                if ( RollingIncrease > 0 ) : Indicator = 'Potentially increasing'
                if ( RollingIncrease >= Variation ) : Indicator = 'Increasing'
                Errormessage = 'The rolling number of deaths was %s on %s' % (Indicator,CurrentSpecimenDate)
                File.Logerror(ErrorFileObject,module,Errormessage,info)
            
            RollingPrevious = Rolling
            
            CurrentSpecimenDate = SeriesData[death][SpecimenPeriod][Columns[death]['Date']]
            for PreviousPeriod in range(SpecimenPeriod,0,-1) : 
                PreviousSpecimenDate = SeriesData[death][PreviousPeriod][Columns[death]['Date']]
                SpecimenDateDiff = CurrentSpecimenDate - PreviousSpecimenDate
                if ( SpecimenDateDiff.days >= RollingPeriod) :
                    Rolling = int(SeriesData[death][SpecimenPeriod][Columns[death]['Cumulative']]) - int(SeriesData[death][PreviousPeriod][Columns[death]['Cumulative']])
                    break
            
            # Output derived fields
            OutData['Rolling'] = Rolling      
        
        if ( ConfigurationDataType == testing ) :
            
            if ( PercentagePrevious != 0 ) :
                Indicator = 'Decreasing'
                PercentageIncrease = Percentage - PercentagePrevious
                if ( PercentageIncrease > 0 ) : Indicator = 'Potentially increasing'
                if ( PercentageIncrease >= Variation ) : Indicator = 'Increasing'
                Errormessage = 'The  percentage number of positive tests was %s on %s' % (Indicator,CurrentSpecimenDate)
                File.Logerror(ErrorFileObject,module,Errormessage,info)
            
            PercentagePrevious = Percentage
            
            CurrentSpecimenDate = SeriesData[testing][SpecimenPeriod][Columns[testing]['Date']]
            for PreviousPeriod in range(SpecimenPeriod,0,-1) : 
                PreviousSpecimenDate = SeriesData[testing][PreviousPeriod][Columns[testing]['Date']]
                SpecimenDateDiff = CurrentSpecimenDate - PreviousSpecimenDate
                if ( SpecimenDateDiff.days >= RollingPeriod) :
                    Rolling = int(SeriesData[testing][SpecimenPeriod][Columns[testing]['CumulativePositive']]) - int(SeriesData[testing][PreviousPeriod][Columns[testing]['CumulativePositive']])
                    break
              
            # Correct data after data change date.
            if ( CurrentSpecimenDate >= TestingDataChangeDate ) : OutData['CumulativePositive'] = str(int(SeriesData[testing][SpecimenPeriod][Columns[testing]['CumulativePositive']]) -  DataDecrement)
            
            # Output derived fields
            OutData['Rolling'] = Rolling    
            Percentage = (int(SeriesData[testing][SpecimenPeriod][Columns[testing]['Positive']])/int(SeriesData[testing][SpecimenPeriod][Columns[testing]['Daily']])) * 100
            Percentage = round(Percentage,2)
            OutData['Percentage'] = str(Percentage)
            
        # Data row
        Row =  GenerateCSVRow(GenerateFieldList(Output[ConfigurationDataType],OutData)) 
        Row = Row + '\n'
        File.Writeline(StatisticsFileObject,Row,failure)
        
    # Generate final trend messages and determine if an attention flag should be set   
    if ( ConfigurationDataType == death ) :
        Indicator = 'Decreasing'
        RollingIncrease = Rolling - RollingPrevious
        if ( RollingIncrease > 0 ) : Indicator = 'Potentially increasing'
        if ( RollingIncrease >= Variation ) : 
            Indicator = 'Increasing'
            AttentionFlag[death] = True
        Errormessage = 'The rolling number of deaths was %s on %s' % (Indicator,CurrentSpecimenDate)
        File.Logerror(ErrorFileObject,module,Errormessage,info)
        
    
    if ( ConfigurationDataType == testing ) :
        Indicator = 'Decreasing'
        PercentageIncrease = Percentage - PercentagePrevious
        if ( PercentageIncrease > 0 ) : Indicator = 'Potentially increasing'
        if ( PercentageIncrease >= Variation ) : 
            Indicator = 'Increasing'
            AttentionFlag[testing] = True
        Errormessage = 'The  percentage number of positive tests was %s on %s' % (Indicator,CurrentSpecimenDate)
        File.Logerror(ErrorFileObject,module,Errormessage,info)
             
    # Close Statistics file
    Errormessage = 'Could not close ' + StatisticsFilename
    if ( File.Close(StatisticsFileObject,failure) == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,warning)
            
# Processes attention flags.
for ConfigurationDataType in ConfigurationDataTypes :
    StatisticsFilename = DataDir + '\\' + ReturnFileName('pillar2',ConfigurationDataType)
    if ( AttentionFlag[ConfigurationDataType] ) :
        Errormessage = 'Attention flag set for %s please view' % StatisticsFilename
        File.Logerror(ErrorFileObject,module,Errormessage,warning)
        Interface.ViewSpeadsheet(Spreadsheet,StatisticsFilename) 
  
# Log end of script
File.Logerror(ErrorFileObject,module,'Completed',info)

# Close error log file
Errormessage = 'Could not close ' + ErrorFilename
if ( File.Close(ErrorFileObject,failure) == failure ) : File.Logerror(ErrorFileObject,module,Errormessage,warning)