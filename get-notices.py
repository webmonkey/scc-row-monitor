#!/usr/bin/python3

from bs4 import BeautifulSoup
import json
import requests
import telegram_send

SCCurl = 'https://www.surreycc.gov.uk/land-planning-and-development/countryside/footpaths-byways-and-bridleways/rights-of-way-public-notices'
lastFileName = "last_state"
telegramConfig = "surreytrf-group.conf"

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

print("Starting...")

currentByways = getByways(SCCurl)
lastByways = loadByways(lastFileName)

print(str(len(currentByways)) +" current byways")
print(str(len(lastByways)) +" byways from the last run")

newNotices = findNewByways(lastByways,currentByways)
removedNotices = findRemovedByways(lastByways,currentByways)

print(str(len(newNotices)) +" new notices")
print(str(len(removedNotices)) +" removed notices")

telegramMessages = []

if len(newNotices) > 0:
    newNoticesText = "*New Byways Notices*\n"
    for notice in newNotices.keys():
        newNoticesText += notice +" - "+ newNotices[notice] +"\n\n"

    telegramMessages.append(newNoticesText)


if len(removedNotices) > 0:
    removedNoticesText = "*Removed Byways Notices*\n"
    for notice in removedNotices.keys():
        removedNoticesText += notice +" - "+ removedNotices[notice] +"\n\n"

    telegramMessages.append(removedNoticesText)


if len(telegramMessages) > 0:
    telegram_send.send(messages=telegramMessages, conf=telegramConfig,parse_mode="markdown")

print("Saving data")

saveByways(currentByways,lastFileName)

print("Exiting...")
