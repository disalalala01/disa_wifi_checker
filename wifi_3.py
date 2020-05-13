from requests.auth import HTTPBasicAuth
import requests
import sys
import scp
import os
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException
from bs4 import BeautifulSoup

auth_token = 'Authorization=Basic%20YWRtaW46YjAxYzZmYzYyMDgwMzA5Y2ZiMzc2ZTE4NzI3YzMwNzk%3D'
url = 'http://192.168.1.1/'


def logout(session_id):
    r = requests.get(url+'/'+session_id+'/userRpm/LogoutRpm.htm',headers={'Referer':+'/'+session_id+'/userRpm/MenuRpm.htm','Cookie': auth_token})  
    if r.status_code==200:
        return 'Loging out: '+str(r.status_code)
    else:
        return 'Unnable to logout'

def login():
    url = 'http://192.168.1.1/'

    r = requests.get(url+'/userRpm/LoginRpm.htm?Save=Save',headers={'Referer':url+'/','Cookie': auth_token})

    if r.status_code==200:
        x=1
        while x<3:
            try:
                session_id=r.text[r.text.index(url)+len(url)+1:r.text.index('userRpm')-1]
                return session_id
                break

            except ValueError:
                return 'Login error'
            
            x+=1
    else:
        return 'IP unreachable'


def hts():
    

    url = 'http://192.168.1.1/'
    name =  'QZhub'
    passw = 'q8@XL4sqL9qaYQ2'
    auth = HTTPBasicAuth(name,passw)
    r = requests.get(url+'/services/dhcp.asp' ,  auth=auth)
    soup = BeautifulSoup(r.content, 'html.parser')
    div = soup.find('div', {'id': 'dhcpClientsTable'})
    table = div.find('table', {'class': 'form'}) 
    print(table)
    presence='Дома находятся:'
    
    if '5D:D7' in div:
        print(presence)
        presence = presence+'\n'+'DC-31-54-97-51-06'
    return presence


    

def howMuchUser():
    session = login()
    url = 'http://192.168.1.1/'
    r = requests.get(url +'/'+session+'/userRpm/WlanStationRpm.htm',headers={'Referer':url+'/'+session+'/userRpm/MenuRpm.htm','Cookie': auth_token})
    status=str(r.status_code)
    
    print (logout(session))
    presence='Дома находятся:'

    if 'DC-31-54-97-51-06' in r.text:
        presence=presence+'\n'+'DC-31-54-97-51-06'
    return presence 

class sshClient:
    def __init__(self, host, user, key_path):
        self.host = host
        self.user = user
        self.key = key_path
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def connect(self):
        self.client.connect(self.host,
                                username=self.user,
                                key_filename=self.key,
                                look_for_keys=True,
                                timeout=5000)
        self.scp = SCPClient(self.client.get_transport())  # For later

client = sshClient('qzhub.hopto.org','QZhub','C:\\Users\\Dias\\.ssh\\known_hosts')
client.connect()
        


