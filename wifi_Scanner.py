from requests.auth import HTTPBasicAuth
import requests
import sys
import scp
import os
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException
from bs4 import BeautifulSoup
import subprocess

auth_token = 'Authorization=Basic%20YWRtaW46YjAxYzZmYzYyMDgwMzA5Y2ZiMzc2ZTE4NzI3YzMwNzk%3D'
url = 'http://192.168.1.1/'



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
                                password=self.key,
                                allow_agent=False,
                                look_for_keys=False)
        self.scp = SCPClient(self.client.get_transport())  # For later
        stdin, stdout, stderr = self.client.exec_command('cli st dhcp')
        stdout.channel.recv_exit_status()
        response = stdout.readlines()
        print(response)
        for line in response:
            print(f'INPUT: {cmd} | OUTPUT: {line}')
client = sshClient('qzhub.hopto.org','QZhub','q8@XL4sqL9qaYQ2')

client.connect()
        
