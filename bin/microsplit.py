#!/usr/bin/python
#
# The microsplit script takes an HTML stub document and splits the document
# into its constituent parts. The script breaks on header elements and
# dumps the resulting sections into a directory specified on the command
# line.
import os, sys, re
from optparse import OptionParser

logToFile = False
options = object()

##
# Logs the output to the console or to a file, depending on the logging 
# variable
def log(str):
    global logging
    if(logToFile):
        lfile = open("microsplit.log", "a")
        lfile.write(str + '\n')
        lfile.close()
    else:
        print str

##
# Takes an input string and converts it to lower-case text with dashes and
# non-standard characters removed.
def dashifyText(text):
    rval = ""

    rval = text.lower()
    rval = rval.replace("&nbsp;", " ")
    rval = rval.replace("&lt;", "<")
    rval = rval.replace("(", "-").replace(")", "-").replace("/", "-")
    rval = rval.replace("'", "").replace('"', "").replace(",", "")
    rval = rval.replace(" ", "-")
    rval = rval.replace("+", "-")
    rval = re.sub(r'-[-]+', '-', rval)
    rval = re.sub(r'-$', '', rval)
    rval = re.sub(r'^-', '', rval)

    return rval

##
# Writes a given Table of Contents item to a file specified via tocItem and
# placed into options.outputDir.
#
# @param options the options object that contains the output directory.
# @param tocItem the table of contents file name to write to.
# @param text the text to write to the file.
def writeTocItem(options, tocItem, text):
    # Dump the text buffer to the given TOC item
    tocItemFilename = os.path.join(options.outputDir, tocItem)
    tocItemFile = open(tocItemFilename, "w")
    tocItemFile.write(text)
    tocItemFile.close()

##
# Processes a specification file and splits the file into microsections.
#
# @param options The set of options containing the specification filename.
def processSpecification(options):
    specfile = open(options.specFile, "r")

    # The table of contents stack tracks where we are in the current document
    tocStack = ["", "", "html5", "", ""]
    toc = ["header",]
    textBuffer = ""

    for line in specfile:
        # Get the entire contents of each header element if a header element
        # is detected
        hm = re.match(r"^.*\<h(?P<header>[0-9]).*?\>.*$", line)
        if(hm):
            maxLines = 0
            # While the ending tag has not been found for the header tag,
            # keep searching for it
            while(not re.match( \
                r"^.*\<h(?P<header>[0-9]).*?\>(?P<content>.*)\<\/h[0-9]\>.*$", 
                line.replace("\n", "")) and maxLines < 10):
                #print "LINE:", line
                line += specfile.next()
                maxLines += 1

            # Issue a warning if there was some sort of parse error
            #if(maxLines == 10):
                #log("WARNING: Closing header tag not found for:\n%s" % (line,))

        # Check to see if we have a header line
        m = re.match(
            r"^.*\<h(?P<header>[0-9]).*?\>(?P<content>.*)\<\/h[0-9]\>$", 
            line.replace("\n", ""))

        # If a complete header element is detected, process the header contents
        if(m):
            headerLevel = int(m.group('header'))
            # Strip the tags from the content
            content = re.sub(r'<[^>]*?>', '', m.group('content')) 
            dashHeader = dashifyText(content)
            #print headerLevel, "-", dashHeader

            # Build the proper header hierarchy, save it to the TOC and
            # dump the text buffer to the previous TOC item.
            if(headerLevel < 4):
                tocStack[headerLevel] = dashHeader
                tocItem = dashifyText("-".join(tocStack[2:headerLevel+1]))
                
                # Write the TOC item to a file
                if(len(textBuffer) > 1):
                    writeTocItem(options, toc[-1], textBuffer)
                else:
                    del toc[-1]

                # Append the tocItem to the TOC after checking to see that
                # duplicates do not exist.
                counter = 1
                while(tocItem in toc):
                    tokens = tocItem.split("-")[0:-1]
                    tokens.append("%i" % (counter,))
                    tocItem = "-".join(tokens)
                    counter += 1
                toc.append(tocItem)

                # Reset the text buffer with the new item
                textBuffer = line
            else:
                textBuffer += line
        else:
            textBuffer += line

    # Write the last TOC item to the file
    if(len(textBuffer) > 1):
        writeTocItem(options, toc[-1], textBuffer)

    # Generate the configuration file for the microjoin script
    ujFilename = os.path.join(options.outputDir, 
        options.specFile.split(os.sep)[-1]+".conf")
    ujFile = open(ujFilename, "w")

    # Write out the usage information for the file
    ujFile.write("""# This file was auto-generated using the microsplit.py tool.
#
# You may edit this file in a number of ways and process it using the 
# microjoin.py tool to create an entirely new specification. To create a new
# specification, copy this file to the "configs" directory in your repository
# and start modifying it.
#
# * To delete a section, delete any line from the list below. 
# * To add a section, insert a line like the folowing:
#      include YOUR_MICROSECTION_FILE
# * To apply a patch to the final, combined file, do the following:
#      (NOT IMPLEMENTED YET)
# * To construct a new source document, run the following command:
#      ./bin/microjoin.py THIS_CONFIGURATION_FILE THE_OUTPUT_FILE
#
""")

    for ti in toc:
        ujFile.write("include %s\n" % (os.path.join(options.outputDir,ti),))
    ujFile.close()

##
# Sets up the option string parser for this daemon.
#
# @param argv the argument list specified on the command line.
def setup_parser(argv):
    usage = "usage: %prog [options] SPEC_FILE"
    parser = OptionParser(usage)

    parser.add_option('-o', '--output-dir',
        action='store', type='string', dest='outputDir',
        default="build",
        help='the directory in which to store the output files ' + \
            '[Default: build]')

    options, args = parser.parse_args(argv)
    largs = parser.largs
    
    return (options, args, largs)

##
# The main entry point for the script.
#
# @param argv the argument list passed to the program.
# @param stdout the standard output stream assigned to the program.
# @param environ the execution environment for the program.
def main(argv, stdout, environ):
    # Parse the options
    options, args, largs = setup_parser(argv)
    options.specFile = largs[-1]

    # Check to make sure a spec file was specified
    if((len(largs) < 2) or not os.path.exists(options.specFile)):
        log("ERROR: A specification file was not specified")
        log("EXAMPLE: %s html5-hixie/source" % (argv[0],))
        sys.exit(1)

    # Create the output directory if it doesn't already exist.
    if(not os.path.exists(options.outputDir)):
        try:
            os.makedirs(options.outputDir)
        except OSError:
            log("ERROR: The output directory could not be created.")
            sys.exit(1)

    processSpecification(options)

# If the program was started from the command line, run main()
if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)
