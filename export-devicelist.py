import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()  # Disable warnings
from pprint import pprint
import json
import csv

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
network_device_api_url = 'network-device/'
devicelist_url = base_url + network_device_api_url
interface_api_url = 'interface/network-device/'

# Parameters
payload = {'scope': 'local'}

# GET DEVICE LIST
header = {"X-Auth-Token": service_ticket,'content-type': 'application/json'}
ret = requests.get(devicelist_url,headers=header,verify=False)
device_list = json.loads(ret.text)['response']

# OPEN DEVICE LIST CSV
device_writer = csv.writer(open('./outputs/Device_list.csv', 'w'))
# CREATE HEADER AND ITERATE
fields_row = ['apManagerInterfaceIp','bootDateTime','collectionStatus','family','hostname','id','instanceUuid','interfaceCount','inventoryStatusDetail','lastUpdateTime','lastUpdated','lineCardCount','lineCardId','location','locationName','macAddress','managementIpAddress','memorySize','platformId','reachabilityFailureReason','reachabilityStatus','role','roleSource','serialNumber','series','snmpContact','snmpLocation','softwareVersion','tagCount','tunnelUdpPort','type','upTime']
interface_fields_row = ['description','deviceId','duplex','id','ifIndex','instanceUuid','interfaceType','ipv4Address','ipv4Mask','isisSupport','lastUpdated','macAddress','mappedPhysicalInterfaceId','mappedPhysicalInterfaceName','nativeVlanId','ospfSupport','pid','portMode','portName','portType','serialNo','series','speed','status','vlanId',]
device_writer.writerow(fields_row)

# ITERATE
for device in device_list:
    # WRITE DEVICE LIST INTO CSV
    row = []
    for h in fields_row:
        if device[h] == None:
            row.append("null")
        else:
            row.append(device[h])
    device_writer.writerow(row)

    # WRITE CONFIG TO CFG FILE
    network_device_id = device['id']
    device_config_url = base_url + network_device_api_url + network_device_id + '/config'
    ret3 = requests.get(device_config_url,headers=header,verify=False)
    config = json.loads(ret3.text)['response']
    configfile = open('./outputs/' + str(device['hostname'])+'.config.txt','w')
    configfile.write(config)
    configfile.close()

    # obtain per device interface dict
    device_interface_url = base_url + interface_api_url + network_device_id
    ret4 = requests.get(device_interface_url,headers=header,verify=False)
    interfaces = json.loads(ret4.text)['response']

    interface_writer = csv.writer(open('./outputs/' + str(device['hostname']) + '.interfaces.csv', 'w'))
    interface_writer.writerow(interface_fields_row)
    for interface in interfaces:
        interface_row = []
        for i in interface_fields_row:
            interface_row.append(interface[i])
        interface_writer.writerow(interface_row)



