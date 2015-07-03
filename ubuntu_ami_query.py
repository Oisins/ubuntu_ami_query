#!/usr/bin/env python
import argparse
import nagiosplugin
import os
from httplib2 import Http
from urllib import urlencode


def connectToCI():
    h = Http()
    data = dict()
    url = "http://cloud-images.ubuntu.com/locator/ec2/releasesTable"
    resp, content = h.request(url, "POST", urlencode(data))
    assert resp["status"] == "200", "Connection Failed"
    return resp, content

parser = argparse.ArgumentParser(description="Search for a AMI Version")
parser.add_argument("-n", dest="searchName", type=str, help="Search Name")
parser.add_argument("-i", dest="searchInstanceType", type=str, help="Search Instance_Type")
parser.add_argument("-r", dest="searchZone", type=str, help="Search Zone", default="eu-west-1")
parser.add_argument("--non_lts", dest="nonLTS", action="store_true", help="default behavious fetches only LTS")
args = parser.parse_args()

lts = None
if args.nonLTS:
    lts = "LTS"
resp, content = connectToCI()

fixContent = content[:-7]  # Remove Tailing ,
contentList = fixContent.split("[")
contentList = contentList[2:]

for i in range(0, len(contentList)):
    contentList[i] = contentList[i][1:].split('","')  # Strip the "
    '''Find the AMI_ID by striping the href und leaving the ID'''
    firstPos = contentList[i][6].find('"') + 1  # Find the first "
    ami_id = contentList[i][6][firstPos:].find('"') + len(contentList[i][6][:firstPos])  # Find the 2nd " in the shortend String
    ami_id_pos = ami_id + 2  # Get the Pos by taking of the remaining ">

    contentList[i] = {"Zone": contentList[i][0],
                      "Name": contentList[i][1],
                      "Version": contentList[i][2][-3:],
                      "Arch": contentList[i][3],
                      "Instance_Type": contentList[i][4],
                      "Release": contentList[i][5],
                      "AMI_ID": contentList[i][6][ami_id_pos:-4],
                      "AKI_ID": contentList[i][7][:-4]}

searchParamsFull = [args.searchZone,
                    args.searchName,
                    args.searchInstanceType,
                    "amd64"]

searchParams = []
for param in searchParamsFull:
    if param is not None:
        searchParams.append(param)
matchList = []
match = ""
i = 0
for ami in contentList:
    matches = 0
    for value in ami.values():
        if str(value) in searchParams and ami["Version"] != lts:
            matches += 1
    if matches == len(searchParams):
        matchList.append(ami)
        match = ami["AMI_ID"]
    i += 1

maxDate = 0
for match in matchList:
    if float(match["Release"]) > float(maxDate):
        maxDate = match["Release"]
        newest = match

fileName = "ami_id.properties"
if not os.path.exists(fileName):
    file = open(fileName, "w")
    file.write(newest["AMI_ID"])
    file.close()
else:
    file = open(fileName, "w+")
    content = file.read()
    if content != newest["AMI_ID"]:
        file.truncate()
        file.write(newest["AMI_ID"])
        file.close()
