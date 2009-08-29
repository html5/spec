#!/usr/bin/env python
#
# Analyzes W3C polls to determine possible outcomes based on
# one-vote-per-company vs. one-vote-per-person. This script was
# quickly hacked together and is not intended for mass distribution.
#
# @author Manu Sporny
import os, sys, operator

gVotes = {}
gVotes["allVotes"] = []

def calculateTotalVotes(vt):
    total = 0

    for v in vt[-1].values():
        total += v

    return total

def tallyVotes(votes):
    voteTally = []
    for vote in votes:
        i = 0
        for datum in vote["data"]:
            if(len(voteTally) <= i):
                voteTally.append({})
            if(not voteTally[i].has_key(datum)):
                voteTally[i][datum] = 0
            voteTally[i][datum] += 1
            i += 1
    return voteTally

def processVote(voteText):
    text = voteText.strip().replace("\n", " ").replace("\r", " ").replace("&#039;", "'")

    # Build a vote object
    vote = {}
    soffset = 0
    eoffset = 0

    soffset = text.find("<a href=")
    soffset = text.find(">", soffset) + 1
    eoffset = text.find("</a>", soffset)
    familyName = text[soffset:eoffset]

    soffset = text.find("<td>", eoffset) + 4
    eoffset = text.find("</td>", soffset)
    givenName = text[soffset:eoffset]
    vote["name"] = givenName + " " + familyName

    soffset = text.find("<td>", eoffset) + 4
    eoffset = text.find("</td>", soffset)
    company = text[soffset:eoffset]
    if(company.strip() == ""):
        vote["company"] = "W3C Invited Experts"
    else:
        vote["company"] = company

    vote["data"] = []
    while(text.find("<td>", soffset) > 0):
        soffset = text.find("<td>", soffset) + 4
        eoffset = text.find("</td>", soffset)
        data = text[soffset:eoffset]
        vote["data"].append(data)

    # Categorize votes by organization
    global gVotes

    if(not gVotes.has_key(vote["company"])):
        gVotes[vote["company"]] = []
    gVotes[vote["company"]].append(vote)
    gVotes["allVotes"].append(vote)

def analyzePoll(pollFilename):
    pf = open(pollFilename, "r")
    startScanning = False
    vote = ""
    for line in pf.readlines():
        if("/Systems/db/user" in line):
            startScanning = True
        if("<tr>" in line):
            if(vote != ""):
                processVote(vote)
                vote = ""
        if(startScanning):
            vote += line
    processVote(vote)
    vote = ""

    print "Tally of votes (one-per-individual):"
    global gVotes
    voteTally = tallyVotes(gVotes["allVotes"])
    i = 0
    voteDescriptions = [ \
        "Publish HTML Draft without warnings",
        "Publish HTML Draft with warnings",
        "a: Publish any draft with > 50%, b: Only publish draft with most votes"]
    for question in voteTally:
        print "  ", voteDescriptions[i]
        for k,v in question.items():
            print "   %6s: %s" % (k, v)
        i += 1

    print "\nVotes per organization:"
    vpo = []
    for company in gVotes.keys():
        if(company != "allVotes"):
            cvotes = gVotes[company]
            voteTally = tallyVotes(cvotes)
            vpo.append((company, calculateTotalVotes(voteTally)))

    # Reverse sort the votes by number per organization
    vpo.sort(key=operator.itemgetter(1, 0))
    vpo.reverse()
    for v in vpo[1:]:
        print " %25s %s " % (v[0], v[1])
    print " %25s %s " % (vpo[0][0], vpo[0][1])

    # Tally of votes (one-per-organization)
    print "\nTally of votes (one-per-organization):"
    oneVotePerOrg = {"allVotes" : []}
    for company, votes in gVotes.items():
        if("W3C Invited Experts" in company):
            oneVotePerOrg["allVotes"].extend(votes)
            continue
        if("allVotes" in company):
            continue
        consensus = []
        tally = tallyVotes(votes)
        for answers in tally:
            maxVote = ('', 0)
            for k,v in answers.items():
                if(v > maxVote[1]):
                    maxVote = (k, v)
            consensus.append(maxVote[0])
        vote = {}
        vote["company"] = company
        vote["name"] = company
        vote["data"] = consensus
        oneVotePerOrg["allVotes"].append(vote)

    voteTally = tallyVotes(oneVotePerOrg["allVotes"])
    i = 0
    for question in voteTally:
        print "  ", voteDescriptions[i]
        for k,v in question.items():
            print "   %6s: %s" % (k, v)
        i += 1

# Analyze the poll file given on the command line
if(len(sys.argv) < 2):
    print "Usage:", sys.argv[0], " COMPACT_POLL_FILE.html"
    sys.exit(1)


pollFilename = sys.argv[1]
print "Analyzing W3C compact poll %s" % (pollFilename,)

if(os.path.exists(pollFilename)):
    analyzePoll(pollFilename)
