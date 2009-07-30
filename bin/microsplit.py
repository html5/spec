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
        lfile = open("microsection.log", "a")
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
    rval = re.sub(r'-[-]+', '-', rval)
    rval = re.sub(r'-$', '', rval)

    return rval

##
# Processes a specification file and splits the file into microsections.
#
# @param options The set of options containing the specification filename.
def processSpecification(options):
    specfile = open(options.specFile, "r")

    # The table of contents stack tracks where we are in the current document
    tocStack = ["", "", "html5", "", ""]
    toc = []
    textBuffer = ""

    for line in specfile:
        m = re.match(r"^.*\<h(?P<header>.).*?\>(?P<content>.*)\<\/h.\>$", line)
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
                tocItem = "-".join(tocStack[2:headerLevel+1])

                # Dump the text buffer to the previous TOC item
                if(len(toc) > 1):
                   tocItemFilename = os.path.join(options.outputDir, toc[-1])
                   tocItemFile = open(tocItemFilename, "w")
                   tocItemFile.write(textBuffer)
                   tocItemFile.close()

                # Append the tocItem to the TOC
                toc.append(tocItem)

                # Reset the text buffer with the new item
                textBuffer = line
        else:
            textBuffer += line

    # Generate the configuration file for the microjoin script
    ujFilename = os.path.join(options.outputDir, 
        options.specFile.split(os.sep)[-1]+".conf")
    ujFile = open(ujFilename, "w")
    ujFile.write("\n".join(toc))
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
                      default="microsections.cache",
                      help='the directory in which to store the output files')

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
