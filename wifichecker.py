import time
import copy
import paramiko
import datetime
import urllib.request as urllib2
import json
import codecs
import dns.resolver
import dns.reversename
import sys

# authentication
USER = 'QZhub'
PASSWORD = 'q8@XL4sqL9qaYQ2'
NAMESERVER = '192.168.0.1'

# set date and time
now = datetime.datetime.now()

def get_ptr(address):
	my_resolver = dns.resolver.Resolver(configure=False)
	name = ''
	my_resolver.nameservers = [NAMESERVER]
	try:
		addr = dns.reversename.from_address(address)
		name = str(my_resolver.query(addr,'PTR')[0])
	except:
		return 'DNS Error'
	return name

class arptablecl():
    macaddr = ''
    ipaddr = ''
    vlanid = ''

class intervlanrouter():
    arplist = []
    ipaddr = ''
    def __init__(self,swip):
        self.ipaddr = swip

class hostdata():
    #def __init__(self,mac,ip,port,vlan,vendor):
    macaddr = ''
    ipaddr = ''
    swport = ''
    vlanid = ''
    vendorbymac = ''
    dns = ''
    def setip(self,ip):
        self.ipaddr = ip
    def setdns(self,dnsvar):
        self.dns = dnsvar

class swdata():
    hostdatalist = []
    swipaddr = ''
    def __init__(self,swip):
        self.swipaddr = swip
    def sampleprint(self):
        print('switch ip: ' + self.swipaddr)
        print('MAC and IP address table:')
        for itm in self.hostdatalist:
            print(itm.macaddr + ' ' + itm.vlanid + ' ' + itm.swport + ' ' + itm.vendorbymac + ' ' + ' ' + itm.ipaddr + ' ' + itm.dns)
    def findip(self,intervlanrouter1):
        for itm in self.hostdatalist:
            for arplist in intervlanrouter1.arplist:
                if itm.macaddr == arplist.macaddr:
                    itm.setip(arplist.ipaddr)
    def finddns(self):
        for itm in self.hostdatalist:
            dnsval = get_ptr(itm.ipaddr)
            if dnsval.find('Error') != -1:
                dnsval = ' '
            itm.setdns(dnsval)


class GetDataFromSw():
    #return vendor from MAC (OUI)
    def getvendor(mac_address):
        url = "http://macvendors.co/api/"
        request = urllib2.Request(url + mac_address, headers={'User-Agent': "API Browser"})
        response = urllib2.urlopen(request)
        reader = codecs.getreader("utf-8")
        obj = json.load(reader(response))
        if 'company' in obj['result']:
            rtv = obj['result']['company']
        else:
            rtv = 'Unknown'
        return rtv
    def getmactable(self,swip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        output = ''
        retmacaddrs = []
        try:
            client.connect(swip, username=USER, password=PASSWORD)
            chan = client.invoke_shell()
            chan.send('term len 0\n')
            time.sleep(1)
            chan.send('term width 500\n')
            time.sleep(1)
            output = chan.recv(99999)
            chan.send('sh mac address-table | inc (Fa|Gi)\n')
            time.sleep(1)
            output = chan.recv(99999)
            client.close()
        except Exception as e:
            print(e)
        if len(output) > 0:
            string1 = output.decode('utf8')
            string2 = string1.split('\r\n')
            if len(string2) > 2:
                #print(output)
                del string2[0]
                del string2[-1]
                #print(string2)
                for str in string2:
                    strs = str.split()
                    #print(strs)
                    retmacaddrs.append(strs)
            #print(retmacaddrs)
            return retmacaddrs
    def getarptable(self,swip):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        output = ''
        retarptable = []
        try:
            client.connect(swip, username=USER, password=PASSWORD)
            chan = client.invoke_shell()
            chan.send('term len 0\n')
            time.sleep(1)
            chan.send('term width 500\n')
            time.sleep(1)
            output = chan.recv(99999)
            chan.send('sh ip arp\n')
            time.sleep(1)
            output = chan.recv(99999)
            client.close()
        except Exception as e:
            print(e)
        if len(output) > 0:
            string1 = output.decode('utf8')
            string2 = string1.split('\r\n')
            if len(string2) > 2:
                del string2[0]
                del string2[0]
                del string2[-1]
                for itm in string2:
                    stms = itm.split()
                    #print(stms)
                    tmlist =[]
                    if stms[3].find('ncomplete')== -1:
                        tmlist.append(stms[1])
                        tmlist.append(stms[3])
                        tmlist.append(stms[5])
                        retarptable.append(tmlist)
            return retarptable
if __name__ == "__main__":
    if len(sys.argv) < 5:
        print('Need parameters: <ip address Inter VLAN router> <ip address switch> <nameserver> <username> <password>')
        print('example: python consoleout.py 192.168.1.1 192.168.1.200 192.168.1.2 Cisco P@ssw0rd')
        exit()
    else:
        rtr = sys.argv[1]
        swa = sys.argv[2]
        NAMESERVER = sys.argv[3]
        USER = sys.argv[4]
        PASSWORD = sys.argv[5]

        swtest = GetDataFromSw()
        macaddrs = swtest.getmactable(swa)
        swdata1 = swdata(swa)
        for item in macaddrs:
            if len(item) > 3:
                venname = GetDataFromSw.getvendor(item[1])
                hostdata1 = hostdata()
                hostdata1.macaddr = item[1]
                hostdata1.vlanid = item[0]
                hostdata1.swport = item[3]
                hostdata1.vendorbymac = venname
                swdata.hostdatalist.append(copy.deepcopy(hostdata1))

        intervlanr = intervlanrouter(rtr)
        arptable = swtest.getarptable(rtr)
        for item in arptable:
            if len(item) > 2:
                macrec = arptablecl()
                macrec.ipaddr = item[0]
                macrec.macaddr = item[1]
                macrec.vlanid = item[2]
                intervlanr.arplist.append(copy.deepcopy(macrec))
        swdata1.findip(intervlanr)
        swdata1.finddns()

        swdata1.sampleprint()

        print('The End')
