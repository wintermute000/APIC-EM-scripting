import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()  # Disable warnings
from pprint import pprint
import json


# Get Ticket
ticket_url = 'https://192.168.9.4/api/v1/ticket'
ticket_header = {'content-type': 'application/json'}
ticket_content = {"username":"admin","password":"C1sco123!"}
ticket_ret = requests.post(ticket_url,headers=ticket_header,verify=False,data=json.dumps(ticket_content))
print('Obtaining Ticket...')
print(ticket_ret.text)
service_ticket_raw = json.loads(ticket_ret.text)
service_ticket = service_ticket_raw['response']['serviceTicket']

# Build RESTAPI URL
base_url = 'https://192.168.9.4/api/v1/'
#network_device_config_api_url = 'network-device/config'
network_device_api_url = 'network-device/'
#config_url = base_url + network_device_config_api_url
devicelist_url = base_url + network_device_api_url
interface_api_url = 'interface/network-device/'

# Parameters
payload = {'scope': 'local'}

# GET DEVICE LIST
header = {"X-Auth-Token": service_ticket,'content-type': 'application/json'}
ret = requests.get(devicelist_url,headers=header,verify=False)
#ret2 = requests.get(config_url,headers=header,verify=False)

devicelist = json.loads(ret.text)['response']
#configurations = json.loads(ret2.text)['response']

#GET PER HOST CONFIGS AND INTERFACES AND ADD KEY:VALUE TO DEVICELIST
for device in devicelist:
    network_device_id = device['id']
    # obtain per device config
    device_config_url = base_url + network_device_api_url + network_device_id + '/config'
    ret3 = requests.get(device_config_url,headers=header,verify=False)
    config = json.loads(ret3.text)['response']
    # obtain per device interface dict
    device_interface_url = base_url + interface_api_url + network_device_id
    ret4 = requests.get(device_interface_url,headers=header,verify=False)
    interfaces = json.loads(ret4.text)['response']
    # append
    device[u'show_run'] = config
    device[u'interfaces'] = interfaces

pprint(devicelist)


