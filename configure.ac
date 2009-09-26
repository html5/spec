# Configure script for HTML5 specification
# Usage: Run the following commands to build the configure script
#        autoconf
# Author: Manu Sporny

AC_INIT([html],[5.0],[msporny@digitalbazaar.com])
AC_CONFIG_AUX_DIR(setup)

# Check for the existence of Anolis and Subversion
ANOLIS=`pwd`/utils/anolis
AC_CHECK_PROGS(SVN, svn /usr/bin/svn /usr/local/bin/svn, [not found], $PATH)
AC_CHECK_PROGS(WGET, wget /usr/bin/wget /usr/local/bin/wget, [not found], $PATH)

ISSUE_ANNOTATIONS=build/issue-annotations.xml

# Setup the flags needed for Anolis
ANOLIS_FLAGS="--w3c-compat-xref-a-placement --parser=lxml.html --output-encoding=us-ascii --allow-duplicate-dfns --annotations=$ISSUE_ANNOTATIONS --annotate-w3c-issues"
AC_SUBST(ANOLIS_FLAGS)

# Generate the printable date string
DAY=`date +%d`
MONTH=`date +%B`
MONTH_NUMBER=`date +%m`
YEAR=`date +%Y`
DATE_STRING="$DAY $MONTH $YEAR"
CONDENSED_DATE_STRING="$DAY$MONTH_NUMBER$YEAR"

AC_SUBST(DAY)
AC_SUBST(MONTH)
AC_SUBST(MONTH_NUMBER)
AC_SUBST(YEAR)
AC_SUBST(DATE_STRING)
AC_SUBST(CONDENSED_DATE_STRING)
AC_SUBST(ANOLIS)
AC_SUBST(WGET)
AC_SUBST(ISSUE_ANNOTATIONS)

# Ensure that Anolis and Subversion were found
if test "x$WGET" == "xnot found"; then
   echo "The configuration process was unable to find the wget program on"
   echo "your system. Wget is required to build the HTML5 Specification."
   exit 0
fi

if test "x$SVN" == "xnot found"; then
   echo "The configuration process was unable to find the Subversion program on"
   echo "your system. Subversion is required to build the HTML5 Specification."
   echo "More information can be found on the Subversion website:"
   echo ""
   echo "   http://subversion.tigris.org/"
   exit 0
fi

# Generating files
AC_CONFIG_FILES([
	Makefile
        headers/header-w3c-html5
        headers/header-w3c-profile
        headers/header-w3c-rdfa
	headers/header-w3c-msporny
	headers/header-w3c-microdata
])

AC_OUTPUT

# Dump the configuration
echo -e "\n--------- HTML5 Specification Build Configuration -----------"
