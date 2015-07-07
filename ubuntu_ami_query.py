#!/usr/bin/env python
import argparse
import os
import json
import re
import xml.etree.ElementTree as ET
from httplib2 import Http
from urllib import urlencode


def connectToCI():
    '''Get the Json list of all AMIs'''
    h = Http()
    data = dict()
    url = "http://cloud-images.ubuntu.com/locator/ec2/releasesTable"
    resp, content = h.request(url, "POST", urlencode(data))
    assert resp["status"] == "200", "Connection Failed"
    return content


def readArgs():
    parser = argparse.ArgumentParser(description="Search for a AMI Version")
    parser.add_argument("-s", required=True, type=str, help="Search")

    args = parser.parse_args()
    args.search = args.s.split(" ")
    return args


def indexAMI(contentList):
    '''Index all AMIs'''
    data = []
    for i in contentList:
        data.append({"Zone": i[0],
                     "Name": i[1],
                     "Version": i[2],
                     "Arch": i[3],
                     "Instance_Type": i[4],
                     "Release": i[5],
                     "AMI_ID": ET.fromstring(i[6]).text,
                     "AKI_ID": i[7]})
    return data


def match(searchParams, attribute):
    for searchParam in searchParams:
        if re.search(searchParam, attribute):
            return True
    return False


def compareParams(searchParams, contentList):
    '''Compare searchParams to AMI Values'''
    matchList = []
    i = 0

    for ami in contentList:
        matches = 0
        for value in ami.itervalues():
            if match(searchParams, value):
                matches += 1
        if matches == len(searchParams):
            matchList.append(ami)
        i += 1
    return matchList


def findLatest(matchList):
    '''Find Latest AMI Release'''
    maxDate = 0
    newest = None
    for match in matchList:
        if float(match["Release"]) > float(maxDate):
            maxDate = match["Release"]
            newest = match
    assert newest is not None, "No AMI Found"
    return newest


def main():
    args = readArgs()

    content = connectToCI()

    '''Fix the recieved Json File'''
    fixContent = content[:-6] + content[-5:]  # Remove Tailing ,
    contentList = json.loads(fixContent)
    contentList = contentList["aaData"]

    amiList = indexAMI(contentList)
    searchParams = args.search
    matchList = compareParams(searchParams, amiList)
    latest = findLatest(matchList)
    print(latest)


if __name__ == "__main__":
    main()
