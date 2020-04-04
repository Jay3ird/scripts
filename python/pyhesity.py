#!/usr/bin/env python
"""Cohesity Python REST API Wrapper Module - v2.0.8 - Brian Seltzer - Mar 2020"""

##########################################################################################
# Change Log
# ==========
#
# 1.1 - added encrypted password storage - August 2017
# 1.2 - added date functions and private api access - April 2018
# 1.3 - simplified password encryption (weak!) to remove pycrypto dependency - April 2018
# 1.4 - improved error handling, added display function - May 2018
# 1.5 - added no content return - May 2018
# 1.6 - added dayDiff function - May 2018
# 1.7 - added password update feature - July 2018
# 1.8 - added support for None JSON returned - Jan 2019
# 1.9 - supressed HTTPS warning in Linux and PEP8 compliance - Feb 2019
# 1.9.1 - added support for interactive password prompt - Mar 2019
# 2.0 - python 3 compatibility - Mar 2019
# 2.0.1 - fixed date functions for pythion 3 - Mar 2019
# 2.0.2 - added file download - Jun 2019
# 2.0.3 - added silent error handling, apdrop(), apiconnected() - Jun 2019
# 2.0.4 - added pw and storepw - Aug 2019
# 2.0.5 - added showProps - Nov 2019
# 2.0.6 - handle another None return condition - Dec 2019
# 2.0.7 - added storePasswordFromInput function - Feb 2020
# 2.0.8 - added helios support - Mar 2020
# 2.0.9 - helios and error handling changes - Mar 2020
#
##########################################################################################
# Install Notes
# =============
#
# Requires module: requests
# sudo easy_install requests
#         - or -
# sudo yum install python-requests
#
##########################################################################################

from datetime import datetime
import time
import json
import requests
import getpass
import os
import urllib3
from os.path import expanduser

### ignore unsigned certificates
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__all__ = ['apiauth',
           'api',
           'usecsToDate',
           'dateToUsecs',
           'timeAgo',
           'dayDiff',
           'display',
           'fileDownload',
           'apiconnected',
           'apidrop',
           'pw',
           'storepw',
           'showProps',
           'storePasswordFromInput',
           'heliosCluster',
           'heliosClusters']

APIROOT = ''
HEADER = ''
AUTHENTICATED = False
APIMETHODS = ['get', 'post', 'put', 'delete']
CONFIGDIR = expanduser("~") + '/.pyhesity'


### authentication
def apiauth(vip='helios.cohesity.com', username='helios', domain='local', password=None, updatepw=None, prompt=None, quiet=None, helios=False):
    """authentication function"""
    global APIROOT
    global HEADER
    global AUTHENTICATED
    global HELIOSCLUSTERS
    global CONNECTEDHELIOSCLUSTERS

    if helios is True:
        vip = 'helios.cohesity.com'
    pwd = password
    if password is None:
        pwd = __getpassword(vip, username, password, domain, updatepw, prompt)
    HEADER = {'accept': 'application/json', 'content-type': 'application/json'}
    APIROOT = 'https://' + vip + '/irisservices/api/v1'
    if vip == 'helios.cohesity.com':
        HEADER = {'accept': 'application/json', 'content-type': 'application/json', 'apiKey': pwd}
        URL = 'https://helios.cohesity.com/mcm/clusters/connectionStatus'
        try:
            HELIOSCLUSTERS = (requests.get(URL, headers=HEADER, verify=False)).json()
            CONNECTEDHELIOSCLUSTERS = [cluster for cluster in HELIOSCLUSTERS if cluster['connectedToCluster'] is True]
            AUTHENTICATED = True
            if(quiet is None):
                print("Connected!")
        except requests.exceptions.RequestException as e:
            AUTHENTICATED = False
            if quiet is None:
                print(e)
    else:
        creds = json.dumps({"domain": domain, "password": pwd, "username": username})

        url = APIROOT + '/public/accessTokens'
        try:
            response = requests.post(url, data=creds, headers=HEADER, verify=False)
            if response != '':
                if response.status_code == 201:
                    accessToken = response.json()['accessToken']
                    tokenType = response.json()['tokenType']
                    HEADER = {'accept': 'application/json',
                              'content-type': 'application/json',
                              'authorization': tokenType + ' ' + accessToken}
                    AUTHENTICATED = True
                    if(quiet is None):
                        print("Connected!")
                else:
                    print(response.json()['message'])
        except requests.exceptions.RequestException as e:
            AUTHENTICATED = False
            if quiet is None:
                print(e)


def apiconnected():
    return AUTHENTICATED


def apidrop():
    global AUTHENTICATED
    AUTHENTICATED = False


def heliosCluster(clusterName=None, verbose=False):
    global HEADER
    if clusterName is not None:
        if isinstance(clusterName, dict) is True:
            clusterName = clusterName['name']
        accessCluster = [cluster for cluster in CONNECTEDHELIOSCLUSTERS if cluster['name'].lower() == clusterName.lower()]
        if not accessCluster:
            print('Cluster %s not connected to Helios' % clusterName)
        else:
            HEADER['accessClusterId'] = str(accessCluster[0]['clusterId'])
            if verbose is True:
                print('Using %s' % clusterName)
    else:
        print("\n{0:<20}{1:<36}{2}".format('ClusterID', 'SoftwareVersion', "ClusterName"))
        print("{0:<20}{1:<36}{2}".format('---------', '---------------', "-----------"))
        for cluster in sorted(CONNECTEDHELIOSCLUSTERS, key=lambda cluster: cluster['name'].lower()):
            print("{0:<20}{1:<36}{2}".format(cluster['clusterId'], cluster['softwareVersion'], cluster['name']))


def heliosClusters():
    return sorted(CONNECTEDHELIOSCLUSTERS, key=lambda cluster: cluster['name'].lower())


### api call function
def api(method, uri, data=None, quiet=None):
    """api call function"""
    if AUTHENTICATED is False:
        print('Not Connected')
        return None
    response = ''
    if uri[0] != '/':
        uri = '/public/' + uri
    if method in APIMETHODS:
        try:
            if method == 'get':
                response = requests.get(APIROOT + uri, headers=HEADER, verify=False)
            if method == 'post':
                response = requests.post(APIROOT + uri, headers=HEADER, json=data, verify=False)
            if method == 'put':
                response = requests.put(APIROOT + uri, headers=HEADER, json=data, verify=False)
            if method == 'delete':
                response = requests.delete(APIROOT + uri, headers=HEADER, json=data, verify=False)
        except requests.exceptions.RequestException as e:
            if quiet is None:
                print(e)

        if isinstance(response, bool):
            return ''
        if response != '':
            if response.status_code == 204:
                return ''
            if response.status_code == 404:
                if quiet is None:
                    print('Invalid api call: ' + uri)
                return None
            try:
                responsejson = response.json()
            except ValueError:
                return ''
            if isinstance(responsejson, bool):
                return ''
            if responsejson is not None:
                if 'errorCode' in responsejson:
                    if quiet is None:
                        if 'message' in responsejson:
                            print('\033[93m' + responsejson['errorCode'][1:] + ': ' + responsejson['message'] + '\033[0m')
                        else:
                            print(responsejson)
                    return None
                else:
                    return responsejson
    else:
        if quiet is None:
            print("invalid api method")


### convert usecs to date
def usecsToDate(uedate):
    """Convert Unix Epoc Microseconds to Date String"""
    uedate = int(uedate) / 1000000
    return datetime.fromtimestamp(uedate).strftime('%Y-%m-%d %H:%M:%S')


### convert date to usecs
def dateToUsecs(datestring):
    """Convert Date String to Unix Epoc Microseconds"""
    dt = datetime.strptime(datestring, "%Y-%m-%d %H:%M:%S")
    # msecs = int(dt.strftime("%s"))
    # usecs = msecs * 1000000
    return int(time.mktime(dt.timetuple())) * 1000000


### convert date difference to usecs
def timeAgo(timedelta, timeunit):
    """Convert Date Difference to Unix Epoc Microseconds"""
    nowsecs = int(time.mktime(datetime.now().timetuple())) * 1000000
    secs = {'seconds': 1, 'sec': 1, 'secs': 1,
            'minutes': 60, 'min': 60, 'mins': 60,
            'hours': 3600, 'hour': 3600,
            'days': 86400, 'day': 86400,
            'weeks': 604800, 'week': 604800,
            'months': 2628000, 'month': 2628000,
            'years': 31536000, 'year': 31536000}
    age = int(timedelta) * int(secs[timeunit.lower()]) * 1000000
    return nowsecs - age


def dayDiff(newdate, olddate):
    """Return number of days between usec dates"""
    return int(round((newdate - olddate) / float(86400000000)))


### get/store password for future runs
def __getpassword(vip, username, password, domain, updatepw, prompt):
    """get/set stored password"""
    if password is not None:
        return password
    if prompt is not None:
        pwd = getpass.getpass("Enter your password: ")
        return pwd
    pwpath = os.path.join(CONFIGDIR, 'lt.' + vip + '.' + username + '.' + domain)
    if(updatepw is not None):
        if(os.path.isfile(pwpath) is True):
            os.remove(pwpath)
    try:
        pwdfile = open(pwpath, 'r')
        pwd = ''.join(map(lambda num: chr(int(num) - 1), pwdfile.read().split(', ')))
        pwdfile.close()
        return pwd
    except Exception:
        pwd = getpass.getpass("Enter your password: ")
        pwdfile = open(pwpath, 'w')
        pwdfile.write(', '.join(str(char) for char in list(map(lambda char: ord(char) + 1, pwd))))
        pwdfile.close()
        return pwd


### pwstore for alternate infrastructure
def pw(vip, username, domain='local', password=None, updatepw=None, prompt=None):
    return __getpassword(vip, username, password, domain, updatepw, prompt)


def storepw(vip, username, domain='local', password=None, updatepw=True, prompt=None):
    pwd1 = '1'
    pwd2 = '2'
    while(pwd1 != pwd2):
        pwd1 = __getpassword(vip, username, password, domain, updatepw, prompt)
        pwd2 = getpass.getpass("Re-enter your password: ")
        if(pwd1 != pwd2):
            print('Passwords do not match! Please re-enter...')


### store password from input
def storePasswordFromInput(vip, username, password, domain):
    pwpath = os.path.join(CONFIGDIR, 'lt.' + vip + '.' + username + '.' + domain)
    pwdfile = open(pwpath, 'w')
    pwdfile.write(', '.join(str(char) for char in list(map(lambda char: ord(char) + 1, password))))
    pwdfile.close()


### display json/dictionary as formatted text
def display(myjson):
    """prettyprint dictionary"""
    if(isinstance(myjson, list)):
        # handle list of results
        for result in myjson:
            print(json.dumps(result, sort_keys=True, indent=4, separators=(', ', ': ')))
    else:
        # or handle single result
        print(json.dumps(myjson, sort_keys=True, indent=4, separators=(', ', ': ')))


def fileDownload(uri, fileName):
    """download file"""
    if AUTHENTICATED is False:
        return "Not Connected"
    if uri[0] != '/':
        uri = '/public/' + uri
    response = requests.get(APIROOT + uri, headers=HEADER, verify=False, stream=True)
    f = open(fileName, 'wb')
    for chunk in response.iter_content(chunk_size=1048576):
        if chunk:
            f.write(chunk)
    f.close()


def showProps(obj, parent='myobject', search=None):
    if isinstance(obj, dict):
        for key in sorted(obj):  # obj.keys():
            showProps(obj[key], "%s['%s']" % (parent, key), search)
    elif isinstance(obj, list):
        x = 0
        for item in obj:
            showProps(obj[x], "%s[%s]" % (parent, x), search)
            x = x + 1
    else:
        if search is not None:
            if search.lower() in parent.lower():
                print("%s = %s" % (parent, obj))
            elif isinstance(obj, unicode) and search.lower() in obj.lower():
                print("%s = %s" % (parent, obj))
        else:
            print("%s = %s" % (parent, obj))


### create CONFIGDIR if it doesn't exist
if os.path.isdir(CONFIGDIR) is False:
    os.mkdir(CONFIGDIR)
