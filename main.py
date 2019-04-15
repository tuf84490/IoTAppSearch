import sys
import subprocess
import os
import sqlite3
import datetime

def openConfig():
    #search through the current directory for a specified string. Get input from config file and repeat for each string found in config file.
    searchStrings = []
    configFile = open("config.txt")
    configLine = configFile.readline()
    while (configLine != ''):
        aString = configLine.rstrip()
        searchStrings.append(aString)
        configLine = configFile.readline()
    configFile.close()
    return searchStrings

#pass in a pointer to a log file that we write to whenever we find a match
def search(listOfStrings, packageLocation, output):
    path = packageLocation + "/"
    for file in os.listdir(path):
        fileIndex = path + file
        print("NOW SCANNING : " + fileIndex)
        #check to see if its a file first, because if its a directory then we cant really open and scan through it
        if(os.path.isfile(fileIndex)):
            openFile = open(fileIndex)
            try:
                line = openFile.readline()
            except:
                #if we are unable to read the lines in the file due to a strange encoding, just skip this file
                break
            lineNumber = 1
            while (line != ''):
                #search through every line for all search terms
                for searchTerm in listOfStrings:
                    #make the search terms not case sensitive to reduce number of searches performed
                    caseInsensitiveLine = line.lower()
                    foundString = caseInsensitiveLine.find(searchTerm.lower())
                    #if the term starts with the ! character, search for strings of size specified after the !
                    if(searchTerm[0] == "!"):
                        keyLength = int(searchTerm[1:])
                        hits = []
                        for i in range(0, len(line)-keyLength+1):
                            charGroup = line[i:keyLength]
                            if(charGroup.isalnum):
                                hits.append(charGroup)
                        #if we do find a string of that length, log it
                        if(len(hits) != 0):
                            hitsString = ", ".join(hits)
                            output.write("STRING(S) OF LENGTH " + str(keyLength) + " FOUND IN: " + fileIndex + ", AT LINE: " + str(lineNumber) + ". STRINGS : " + hitsString + ". LINE : " + line)
                        #if we dont, then skip the next part
                        else:
                            continue
                    if(foundString != -1):
                        #instead of printing these, eventually log them by getting them all into a huge log string and storing it in the database
                        output.write("FOR TERM " + searchTerm + ", MATCH IN: " + fileIndex + ", AT LINE: " + str(lineNumber) + ", LINE : " + line)
                #always encompas the readline in a try catch block in case encoding errrors prevent us from reading a specific line
                try:
                    line = openFile.readline()
                except:
                    break                
                lineNumber += 1
            openFile.close()
        else:
            for searchTerm in listOfStrings:
                caseInsensitiveIndex = fileIndex.lower()
                #if the directory itself contains a suspicious name, log it
                if(caseInsensitiveIndex.find(searchTerm.lower()) != -1):
                    #instead of printing these, eventually log them by getting them all into a huge log string and storing it in the database
                    output.write("FOR TERM " + searchTerm + ", SUSPICIOUS DIRECTORY FOUND AT: " + fileIndex)
                #if its is a directory, search through it recursively
                if(os.path.exists(fileIndex)):
                    search(listOfStrings, fileIndex, output)


#get input cleanly. Will do both by default (mode = 0). If mode = 1 just download, if mode = 2 just unpackage/just scan
inputs = len(sys.argv)
if(inputs == 2):
    link = sys.argv[1]
    mode = 0
elif(inputs == 3):
    link = sys.argv[1]
    mode = int(sys.argv[2])
else:
    print("ERROR. Invalid input. Please try again.")
    sys.exit()
if(mode > 2 or mode < 0):
    print("ERROR. Mode can only be 1 for just download, 2 for just unpackage, or 0 for both (is by default, do not need to specify 0). Please try again.")
    sys.exit()

database = sqlite3.connect("appStats.db")
dbManager = database.cursor()
command = """CREATE TABLE IF NOT EXISTS stats (
                app_name VARCHAR(255),
                date_checked DATETIME,
                dangerous bit,
                output_log MEDIUMTEXT
            );"""
dbManager.execute(command)

download = "gplaycli --device-codename hammerhead -d " + link
threshold = 10
if(mode == 1 or mode == 0):
    print("Now downloading " + link)
    while threshold > 0:
        errorcheck = subprocess.run(download, shell=True, capture_output=True)
        #if stderr is an empty byte (aka b''), that means it downloaded so continue
        if(errorcheck.stderr == b''):
            print("Finished Download.")
            break
        #if not keep trying 
        else:
            errorString = errorcheck.stderr.decode("utf-8")
            print("Failed because : " + errorString + ". Retrying .... ")
            threshold -= 1
    if(threshold <= 0):
        print("Could not download the apk. Please try again.")
        sys.exit()

apkName = link + ".apk"
unpackage = "apktool d " + apkName
if(mode == 2 or mode == 0):
    print("Now unpackaging " + apkName)
    subprocess.run(unpackage, shell=True)

#open the output file
currentTime = str(datetime.datetime.now())
currentTimeString = ""
for char in currentTime:
    if(char.isalnum()):
        currentTimeString = currentTimeString + char
outputFileName = apkName + currentTimeString
output = open(outputFileName, "w")
#get all words to search for
configResults = openConfig()
#search through the package for suspicious terms
search(configResults, link, output)
output.close()