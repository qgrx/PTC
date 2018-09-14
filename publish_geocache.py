# -*- coding: utf-8 -*-
import io
import argparse
import json
import requests
import urllib3
from requests import session
from bs4 import BeautifulSoup

# global cookie
c = 0
# global cache number
n = 1

urllib3.disable_warnings()

domain = 'https://www.geocaching.com'

def connect(u, p):
    global c

    c = session()
    c.cookies.clear()
     
    html = c.get(domain + '/account/login', verify=False)
    rvt = get_requestVerificationToken(html.text)
    payload = {
        'Username': u,
        'Password': p,
        '__RequestVerificationToken': rvt
    }

    r = c.post(domain + '/account/login/', data=payload, verify=False)
    print('== Login done (account : ' + u + ') ==')

        
def get_viewstate(html):
    bs = BeautifulSoup(html, "html.parser")
    viewstates = bs.find("input", {"id": "__VIEWSTATE"}).attrs['value']
    return viewstates

def get_viewstategenerator(html):
    bs = BeautifulSoup(html, "html.parser")
    viewstates = bs.find("input", {"id": "__VIEWSTATEGENERATOR"}).attrs['value']
    return viewstates

def get_requestVerificationToken(html):
    bs = BeautifulSoup(html, "html.parser")
    viewstates = bs.find("input", {"name": "__RequestVerificationToken"}).attrs['value']
    return viewstates

# 2
def post_typelocation():
    global c
    varjson = {}
    c.post(domain + '/hide/waypoints.aspx/SaveTraditionalGeocacheDraft', json=varjson)
        
# 3
def post_waypoints():
    global c
    varjson = {}
    c.post(domain + '/hide/waypoints.aspx/SaveTraditionalGeocacheDraft', json=varjson)

# 4
def post_description():
    global c
    varjson = {}
    c.post(domain + '/hide/description.aspx/SaveTraditionalGeocacheDraft', json=varjson)

# 5
def post_sizerating(elts, n):
    global c
    latitude = float(elts[0])
    longitude = float(elts[1])
    hint = elts[2]
    title = "[#" + str(n).zfill(3) + "] Power Trail de Champagne"

    headers = {'Content-Type': 'application/json'}
    varjson = {"draftSubmission":{"ContainerType":"Micro","DatePlaced":"2016-03-03T00:00:00","ChosenGeocacheAttributes":[{"GeocacheAttributeId":"13","IsApplicable":"true"},{"GeocacheAttributeId":"19","IsApplicable":"true"},{"GeocacheAttributeId":"43","IsApplicable":"true"}],"ContactName":"qgx","Coordinate":{"Latitude":latitude,"Longitude":longitude},"CountryId":73,"Description":"<p></p>\n","DifficultyRating":1,"GeocacheType":"TraditionalGeocache","Hint":hint,"IsPremiumMembersOnly":"false","Name":title,"StateId":418,"Summary":"<p>resume</p>\n","TerrainRating":1,"Waypoints":[]},"furthestProgressIndex":3,"tkn":"wffITq-HTVGgZQImBTnEnwsitFNQFbcwIrsFXqXrU3IuDShbAGWKpqygNLsk8YWzPjtVcRq_lMI8-c6JC6kP6wBieqyxpraGe3fpp_L5lXsTsAfM5ISqWav5b66H6G0NVYbrzOJxQVetBH3hJJlwdg2"}
    c.post(domain + '/hide/sizeratings.aspx/SaveTraditionalGeocacheDraft', json=varjson, headers=headers)
    
# 6
def post_reviewernotes(response):
    global c
    viewstate = get_viewstate(response.text)
    viewstategenerator = get_viewstategenerator(response.text)
    
    payload = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        'ctl00$ContentBody$tbReviewerNote': '',
        'ctl00$ContentBody$btnSubmit': 'Save and Preview'
    }

    resp = c.post(domain + '/hide/reviewernotes.aspx', data=payload)
    bs = BeautifulSoup(resp.text, "html.parser")
    
    with open("gc.txt", "a") as myfile:
        print (bs.find('title').contents[0].split()[0], end="")
        print(": [#" + str(n).zfill(3) + "] Power Trail de Champagne ", end="")
        myfile.write(bs.find('title').contents[0].split()[0])
        myfile.write("\n")

#########################################
#########################################
#########################################        

def create_cache(elts, n):
    global c
    resp = ''
    
    post_typelocation()
    print('1,', end="")

    post_waypoints()
    print('2,', end="")

    post_description()
    print('3,', end="")

    post_sizerating(elts, n)
    print('4, ', end="")

    resp = c.get(domain + '/hide/reviewernotes.aspx')
    post_reviewernotes(resp)
    print('OK ! ')

    
def parse_caches(myfile):
    global n
    with io.open(myfile,'r',encoding='utf8') as f:
        lines = f.readlines()
        
    for line in lines:
        elts = line.split('|')
        create_cache(elts, n)
        n = n + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username')
    parser.add_argument('-p', '--password')
    parser.add_argument('-F', '--powertrailFile')
    args = parser.parse_args()
    connect(args.username, args.password)

    with open(args.gccodeFile) as f: 
        for line in f:
            l = line.split('\t')
            coords = to_decimal(l[1])
            change_coords(l[0], coords)

    parse_caches(args.powertrailFile)
    