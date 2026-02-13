import sys
import jenkins
import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('node_name', help='Jenkins node name')
parser.add_argument('--url', required=True)
parser.add_argument('--user', required=True)
parser.add_argument('--token', required=True)
parser.add_argument('--new_label', default="", help='New label to set')
parser.add_argument('--new_remoteFS', default="", help='New remoteFS to set')
parser.add_argument('--new_numExecutors', default="", help='New numExecutors to set')
parser.add_argument('--new_host', default="", help='New host to set')
parser.add_argument('--new_port', default="", help='New port to set')
parser.add_argument('--new_credentialsId', default="", help='New credentials ID to set')

args = parser.parse_args()

server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

# Get current node config
config_xml = server.get_node_config(args.node_name)

print("\n")
print(config_xml)
print("\n")

root = ET.fromstring(config_xml)

#####
# remoteFS
if args.new_remoteFS:
    remoteFS_elem = root.find('remoteFS')
    if remoteFS_elem is not None:
        remoteFS_elem.text = args.new_remoteFS

#####
# numExecutors
if args.new_numExecutors:
    numExecutors_elem = root.find('numExecutors')
    if numExecutors_elem is not None:
        numExecutors_elem.text = args.new_numExecutors

#####
# label
if args.new_label:
    # Modify specific element: <label>
    label_elem = root.find('label')
    if label_elem is not None:
        label_elem.text = args.new_label
    else:
        label_elem = ET.SubElement(root, 'label')
        label_elem.text = args.new_label

#####
# launcher related variables

#####
# Host
if args.new_host:
    host = root.find('.//host')
    if host is not None:
        port.text = args.new_host
    # else:
    #     port = ET.SubElement(root, 'port')
    #     port.text = args.new_credentialsId

#####
# Port
if args.new_port:
    port = root.find('.//port')
    if port is not None:
        port.text = args.new_port
    # else:
    #     port = ET.SubElement(root, 'port')
    #     port.text = args.new_credentialsId

#####
# credentialsId
if args.new_credentialsId:
    credsID = root.find('.//credentialsId')
    if credsID is not None:
        credsID.text = args.new_credentialsId
    # else:
    #    credsID = ET.SubElement(root, 'credentialsId')
    #    credsID.text = args.new_credentialsId

# Convert back to string
new_config = ET.tostring(root, encoding='unicode')

print("\n")
print(new_config)
print("\n")

sys.exit()



# Apply updated config
server.reconfig_node(args.node_name, new_config)
print(f"Node '{args.node_name}' label updated to '{args.new_label}'.")   


