import requests
from requests.auth import HTTPBasicAuth
requests.packages.urllib3.disable_warnings()  # Disable warnings
from pprint import pprint
import json
import csv

# Get Ticket Function
def Get_APIC_EM_ticket(url, header, payload):
    ticket_ret = requests.post(url,headers=header,verify=False,data=json.dumps(payload))
    service_ticket_raw = json.loads(ticket_ret.text)
    return service_ticket_raw['response']['serviceTicket']

#RESTAPI GET function
def Get_REST(url, header, payload):
    ret = requests.get(url, headers=header, data=json.dumps(payload), verify=False)
    try:
        if json.loads(ret.text)['response']["errorCode"] == "Not found":
            return "error Not found"
    except:
        if ret.status_code is not 204:
            return json.loads(ret.text)['response']
        else:
            return "error 204"

# Get Ticket
ticket_url = 'https://192.168.9.4/api/v1/ticket'
ticket_header = {'content-type': 'application/json'}
ticket_payload = {"username":"admin","password":"C1sco123!"}
service_ticket = Get_APIC_EM_ticket(ticket_url, ticket_header, ticket_payload)

# Build Global URLs
base_url = 'https://192.168.9.4/api/v1/'
network_device_api_url = 'network-device/'
interface_api_url = 'interface/network-device/'
device_list_url = base_url + network_device_api_url

# Declare Global RESTAPI parameters
header = {"X-Auth-Token": service_ticket,'content-type': 'application/json'}
payload = {'scope': 'local'}

# Declare Spreadsheet Headers
# NOTE: Iteration will use these fields to select what is included in CSV output
device_fields_row = ['apManagerInterfaceIp','bootDateTime','collectionStatus','family','hostname','id','instanceUuid','interfaceCount','inventoryStatusDetail','lastUpdateTime','lastUpdated','lineCardCount','lineCardId','location','locationName','macAddress','managementIpAddress','memorySize','platformId','reachabilityFailureReason','reachabilityStatus','role','roleSource','serialNumber','series','snmpContact','snmpLocation','softwareVersion','tagCount','tunnelUdpPort','type','upTime']
interface_fields_row = ['description','deviceId','duplex','id','ifIndex','instanceUuid','interfaceType','ipv4Address','ipv4Mask','isisSupport','lastUpdated','macAddress','mappedPhysicalInterfaceId','mappedPhysicalInterfaceName','nativeVlanId','ospfSupport','pid','portMode','portName','portType','serialNo','series','speed','status','vlanId',]

# Get Device List
device_list = Get_REST(device_list_url, header, payload)
# Output Device List to CSV
device_writer = csv.writer(open('./outputs/Device_list.csv', 'w'))
device_writer.writerow(device_fields_row)

for device in device_list:
    # Identify device
    network_device_id = device['id']

    # Write device list into CSV
    row = []
    for h in device_fields_row:
        if device[h] == None:
            row.append("null")
        else:
            row.append(device[h])
    print("---------------------------------------------")
    if device['hostname'] == None:
        print("Device ID: " + network_device_id + " - Hostname <null> - Details")
    else:
        print("Device ID: " + network_device_id + " - Hostname - " + device['hostname'] + " - Details")
    print(row)
    device_writer.writerow(row)

    # Iterate and write config to text file per device
    device_config_url = base_url + network_device_api_url + network_device_id + '/config'
    config = Get_REST(device_config_url,header,payload)

    try:
        if config  == "error 204":
            print("Device ID: " + network_device_id + " - NO CONFIGURATION FOUND - null value returned by APIC-EM")
        elif config  == "error Not found":
            print("Device ID: " + network_device_id + " - NO CONFIGURATION FOUND - error not found returned by APIC-EM")
        else:
            print("Device ID: " + network_device_id + " - Configuration Obtained")
            configfile = open('./outputs/' + str(device['hostname']) + '.config.txt', 'w')
            configfile.write(config)
            configfile.close()
    except:
        print("Device ID: " + network_device_id + " - EXCEPTION when fetching configurations")


    # Iterate and write interfaces to CSV file per device
    device_interface_url = base_url + interface_api_url + network_device_id
    interfaces = Get_REST(device_interface_url,header,payload)
    try:
        if interfaces == "error 204":
            print("Device ID: " + network_device_id + " - NO INTERFACES FOUND - null value returned by APIC-EM")
        elif interfaces  == "error Not found":
            print("Device ID: " + network_device_id + " - NO INTERFACES FOUND - error not found returned by APIC-EM")
        else:
            interface_writer = csv.writer(open('./outputs/' + str(device['hostname']) + '.interfaces.csv', 'w'))
            interface_writer.writerow(interface_fields_row)
            print("Device ID: " + network_device_id + " - Interfaces Obtained")
            for interface in interfaces:
                interface_row = []
                for i in interface_fields_row:
                    interface_row.append(interface[i])
                interface_writer.writerow(interface_row)
    except:
        print("Device ID: " + network_device_id + " - EXCEPTION when fetching interfaces")



