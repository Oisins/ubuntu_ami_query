#!/usr/bin/env python
import argparse
import nagiosplugin
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
#parser.add_argument("-s", dest="searchParams", type=str, required=True, help="Search Keys")
parser.add_argument("-r", dest="searchZone", type=str, help="Search Zone", default="eu-west-1")
parser.add_argument("-n", dest="searchName", type=str, help="Search Name")
parser.add_argument("-v", dest="searchVersion", type=str, help="Search Version")
parser.add_argument("-a", dest="searchArch", type=str, help="Search Arch", default="amd64")
parser.add_argument("-i", dest="searchInstanceType", type=str, help="Search Instance_Type", default="ebs")
parser.add_argument("-re", dest="searchRelease", type=str, help="Search Release")
parser.add_argument("-amk", dest="searchAMI_ID", type=str, help="Search AMI_ID")
parser.add_argument("-aki", dest="searchAKI_ID", type=str, help="Search AKI_ID")
args = parser.parse_args()

resp, content = connectToCI()


fixContent = content[:-7]  # Remove Tailing ,
contentList = fixContent.split("[")

contentList = contentList[2:]
for i in range(0, len(contentList)):

	contentList[i] = contentList[i][1:].split('","')  # Strip the " & the last element
	'''Find the AMI_ID by striping the href und leaving the ID'''
	firstPos = contentList[i][6].find('"') + 1  # Find the first "
	ami_id = contentList[i][6][firstPos:].find('"') + len(contentList[i][6][:firstPos])  # Find the 2nd " in the shortend String
	ami_id_pos = ami_id + 2  # Get the Absolute Pos by taking of the remaining ">

	contentList[i] = {"Zone": contentList[i][0],
					"Name": contentList[i][1],
					"Version": contentList[i][2],
					"Arch": contentList[i][3],
					"Instance_Type": contentList[i][4],
					"Release": contentList[i][5],
					"AMI_ID": contentList[i][6][ami_id_pos:-4],  
					"AKI_ID": contentList[i][7][:-4]}




searchParams = [args.searchZone, args.searchName, args.searchVersion, args.searchArch, args.searchInstanceType, args.searchRelease, args.searchAMI_ID, args.searchAKI_ID]
matchList = []
i = 0
for ami in contentList:
	matches = 0
	#print(i)
	#print(ami)
	for search in searchParams:
		if search in ami.values() or search is None:
			matches = matches + 1
	if matches == len(searchParams):
		matchList = ami["AMI_ID"]
	i = i + 1

print(matchList)

