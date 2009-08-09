#!/usr/bin/python
#
# The microjoin script takes a specification configuration file and
# processes the instructions contained in the configuration file to construct
# a complete specification document.

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
        lfile = open("microjoin.log", "a")
        lfile.write(str + '\n')
        lfile.close()
    else:
        print str

##
# Processes a configuration file and performs the processing instructions
# contained therein.
#
# @param options The set of options containing the processing directives.
def processConfiguration(options):
    configFile = open(options.configFile, "r")
    outputFile = open(os.path.join(options.outputDir, options.outputFile), "w")

    # Process the configuration file
    for line in configFile:
        tokens = line.strip().split()

        if(len(tokens) > 0):
            if(tokens[0].startswith("#")):
                pass
            elif(tokens[0] == "include"):
                sfile = tokens[1]
                if(os.path.exists(sfile)):
                    #log("INFO: Including %s" % (sfile,))
                    source = open(sfile, "r")
                    outputFile.write(source.read())
                    source.close()
                else:
                    log("ERROR: Could not include the file named: %s" % \
                        (sfile))
                    sys.exit(1)
            
##
# Sets up the option string parser for this daemon.
#
# @param argv the argument list specified on the command line.
def setup_parser(argv):
    usage = "usage: %prog [options] CONFIGURATION_FILE"
    parser = OptionParser(usage)

    parser.add_option('-o', '--output-file',
        action='store', type='string', dest='outputFile',
        default="specification.html",
        help='the file to write the processing output to ' + \
            '[Default: specification.html]')

    parser.add_option('-d', '--output-directory',
        action='store', type='string', dest='outputDir',
        default="build",
        help='the directory to write the output file to ' + \
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
    options.configFile = largs[-1]

    # Check to make sure a spec file was specified
    if((len(largs) < 2) or not os.path.exists(options.configFile)):
        log("ERROR: A configuration file was not specified.")
        log("EXAMPLE: %s configs/html5-rdfa.conf" % (argv[0],))
        sys.exit(1)
    
    # Create the output directory if it doesn't already exist.
    if(not os.path.exists(options.outputDir)):
        try:
            os.makedirs(options.outputDir)
        except OSError:
            log("ERROR: The output directory could not be created.")
            sys.exit(1)

    processConfiguration(options)

# If the program was started from the command line, run main()
if __name__ == "__main__":
    main(sys.argv, sys.stdout, os.environ)
