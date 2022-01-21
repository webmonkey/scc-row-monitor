#!/usr/bin/python3

import requests
import json
from bs4 import BeautifulSoup

SCCurl = 'https://www.surreycc.gov.uk/land-planning-and-development/countryside/footpaths-byways-and-bridleways/rights-of-way-public-notices'
lastFileName = "last_state"

def getByways(url):

    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')

    byways = {}

    for h2 in soup.find_all('h2'):
        ul = h2.next_sibling
        if ul.name != "ul":
            continue
 
        for li in ul.children:
            if "yway" in li.a.string:
                byways[li.a.string] = li.a['href']

    return byways


def saveByways(byways,file):
    f = open(file,"w")
    f.write(json.dumps(byways))

def loadByways(file):
    f = open(file,"r")
    return json.loads(f.read())

def findNewByways(last,current):
    newByways = {}
    for byway in current.keys():
        if byway not in last:
            newByways[byway] = current[byway]

    return newByways

def findRemovedByways(last,current):
    removedByways = {}

    for byway in last.keys():
        if byway not in current:
            removedByways[byway] = last[byway]

    return removedByways


currentByways = getByways(SCCurl)
lastByways = loadByways(lastFileName)

print("New Byways Entries")
print(findNewByways(lastByways,currentByways))
print("Removed Byways Entries")
print(findRemovedByways(lastByways,currentByways))



saveByways(currentByways,lastFileName)
