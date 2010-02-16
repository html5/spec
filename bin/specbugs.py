#!/usr/bin/env python
#
# Retrieves a bug list, parses the bug list for the 
import sys, os, os.path
from optparse import OptionParser
import urllib
import getpass
from xml.etree.ElementTree import parse

# BUGLIST URL:
#http://www.w3.org/Bugs/Public/buglist.cgi?bug_file_loc=&bug_file_loc_type=allwordssubstr&bug_id=&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bugidtype=include&chfieldfrom=&chfieldto=Now&chfieldvalue=&component=HTML%2BRDFa%20%28editor%3A%20Manu%20Sporny%29&email1=&email2=&emailtype1=substring&emailtype2=substring&field-1-0-0=product&field-1-1-0=component&field-1-2-0=bug_status&field0-0-0=noop&keywords=&keywords_type=allwords&long_desc=&long_desc_type=allwordssubstr&product=HTML%20WG&query_format=advanced&remaction=&short_desc=&short_desc_type=allwordssubstr&status_whiteboard=&status_whiteboard_type=allwordssubstr&type-1-0-0=anyexact&type-1-1-0=anyexact&type-1-2-0=anyexact&type0-0-0=noop&value-1-0-0=HTML%20WG&value-1-1-0=HTML%2BRDFa%20%28editor%3A%20Manu%20Sporny%29&value-1-2-0=NEW%2CASSIGNED%2CREOPENED&value0-0-0=&votes=&ctype=csv

# BUG XML URL:
#http://www.w3.org/Bugs/Public/show_bug.cgi?ctype=xml&id=8998

# Opens a W3C URL
class W3CUrlOpener(urllib.FancyURLopener):
    def __init__(self):
        urllib.FancyURLopener.__init__(self)
        self.username = None
        self.password = None

    def prompt_user_passwd(self, host, realm):
        print "Enter your username and password for the W3C Bug tracker"

        if(self.username == None):
            self.username = getpass.getuser()
            self.password = getpass.getpass()
                
        return (self.username, self.password)

##
# Logs a string to the proper location (file or console)
def log(str):
    print str

##
# Sets up the option string parser for this script.
#
# @param argv the argument list specified on the command line.
def setupParser(argv):
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    
    parser.add_option('-w', '--working-dir',
        action='store', dest='workingDir', default="dist",
        help='The working directory for the application. [Default: %default]')

    parser.add_option('-s', '--spec',
        action='store', dest='specFile', 
        help='The specification file to modify with the buglist.')

    parser.add_option('-o', '--output-spec',
        action='store', dest='outFile', 
        help='The output specification file.')

    parser.add_option('-n', '--name',
        action='store', dest='specName', 
        help='The name of the specification file.')

    options, args = parser.parse_args(argv)
    largs = parser.largs

    return (options, args, largs)

##
# Adds the specification bug warnings
def addSpecBugWarnings(argv, stdout, environ):
    (options, args, largs) = setupParser(argv)
    
    component = "HTML+RDFa (editor: Manu Sporny)"
    quotedBugUrl = "http://www.w3.org/Bugs/Public/buglist.cgi?bug_file_loc=&bug_file_loc_type=allwordssubstr&bug_id=&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&bugidtype=include&chfieldfrom=&chfieldto=Now&chfieldvalue=&component=" + urllib.quote(component) + "&email1=&email2=&emailtype1=substring&emailtype2=substring&field-1-0-0=product&field-1-1-0=component&field-1-2-0=bug_status&field0-0-0=noop&keywords=&keywords_type=allwords&long_desc=&long_desc_type=allwordssubstr&product=HTML%20WG&query_format=advanced&remaction=&short_desc=&short_desc_type=allwordssubstr&status_whiteboard=&status_whiteboard_type=allwordssubstr&type-1-0-0=anyexact&type-1-1-0=anyexact&type-1-2-0=anyexact&type0-0-0=noop&value-1-0-0=HTML%20WG&value-1-1-0=" + urllib.quote(component) + "&value-1-2-0=NEW%2CASSIGNED%2CREOPENED&value0-0-0=&votes=&ctype=csv"
    bugs = {}
    
    # Create the buglist directory
    specBugsDir = os.path.join(options.workingDir, "specbugs")
    if(not os.path.exists(specBugsDir)):
        os.makedirs(specBugsDir)
    
    # Generate the buglist file name
    shortname = component.split()[0].lower().replace("+", "")
    buglistFile = os.path.join(specBugsDir, shortname + ".buglist")
    
    # Download the buglist if it doesn't already exist
    blFetcher = W3CUrlOpener()
    if(not os.path.exists(buglistFile)):
        log("INFO: Downloading %s buglist to %s..." % (buglistFile,))
        blFetcher.retrieve(quotedBugUrl, buglistFile)
        
    # Download all of the bugs in the buglist
    buglist = open(buglistFile)
    allBugs = []
    bugUrlBase = "http://www.w3.org/Bugs/Public/show_bug.cgi?ctype=xml&id="
    for line in buglist.readlines()[1:]:
        bugInfo = line.split(",")
        bugId = str(bugInfo[0])
        bugfilename = os.path.join(specBugsDir, bugId + ".bug")
        bugs[bugId] = {"filename": bugfilename}
        if(not os.path.exists(bugfilename)):
            log("INFO: Downloading bug %s to %s" % (bugId, bugfilename))
            blFetcher.retrieve(bugUrlBase + bugId, bugfilename)

    # Process each of the bug reports
    for (key, value) in bugs.items():
        log("INFO: Processing bug %s" % (key,))
        bug = None
        try:
            bug = parse(value["filename"])
        except Exception:
            log("ERROR: Failed to parse bug %s" % (key,))
            
        # If a bug was found extract all of the long descriptions and search
        # for -SPEC-SECTIONS
        if(bug != None):
            # Search all of the sections for spec section identifiers
            value["sections"] = []
            for element in bug.findall("bug/long_desc/thetext"):
                spos = element.text.find("-SPEC-SECTIONS")
                if(spos != -1):
                    spos = element.text.find("[", spos) + 1
                    epos = element.text.find("]", spos + 1)
                    sections = element.text[spos:epos].split(" ")
                    value["sections"] += sections

            # Save the short description
            for element in bug.findall("bug/short_desc"):
                value["description"] = element.text
            
            # Save the bug ID and URL for insertion into the spec source
            value["id"] = key
            value["url"] = \
                "http://www.w3.org/Bugs/Public/show_bug.cgi?id=%s#c0" % (key,)
        bugs[key] = value
    
    # Gather the bugs by spec section ID
    bugsBySection = {}
    for bugId, bugInfo in bugs.items():
        if(bugInfo.has_key("sections") and len(bugInfo["sections"]) > 0):
            for section in bugInfo["sections"]:
                if(not bugsBySection.has_key(section)):
                    bugsBySection[section] = []
                bugsBySection[section].append(bugInfo)
        else:
            log("WARNING: Bug %s does not have an associated spec section" % \
                (bugId,))

    # Process the input HTML file
    specfile = open(options.specFile, "r")
    outfile = open(options.outFile, "w")
    activeElement = None
    for line in specfile.readlines():
        idstart = line.find(" id=\"")
        if(idstart != -1):
            idstart += 5
            idend = line.find("\"", idstart)
            idvalue = line[idstart:idend]
            
            if(bugsBySection.has_key(idvalue)):
                aestart = line[:idstart].rfind("<") + 1
                activeElement = line[aestart:idstart-5].strip()

        outfile.write(line)
        
        if(activeElement != None and 
            line.find("</%s>" % activeElement) != -1):
            outfile.write(
                "\n<ul class=\"XXX annotation\"><li><b>Status</b>: " +
                "There are W3C bug tracker items associated with this " +
                " section.</b></li>\n")
            for bug in bugsBySection[idvalue]:
                outfile.write("<li class=\"XXX annotation\">" + 
                    "BUG #<a href=\"%s\">%s</a>: %s</li>" % \
                    (bug["url"], bug["id"], bug["description"]))
            outfile.write("</ul>")
            activeElement = None

    specfile.close()
    outfile.close()

# Call main function if run from command line.
if __name__ == "__main__":

    addSpecBugWarnings(sys.argv, sys.stdout, os.environ)

