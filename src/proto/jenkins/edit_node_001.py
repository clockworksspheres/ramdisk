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
parser.add_argument('--new_credentialsId', default="", help='New credentials ID to set')

args = parser.parse_args()

server = jenkins.Jenkins(args.url, username=args.user, password=args.token)

# Get current node config
config_xml = server.get_node_config(args.node_name)

print("\n")
print(config_xml)
print("\n")


root = ET.fromstring(config_xml)

if args.new_label:
    # Modify specific element: <label>
    label_elem = root.find('label')
    if label_elem is not None:
        label_elem.text = args.new_label
    else:
        label_elem = ET.SubElement(root, 'label')
        label_elem.text = args.new_label
"""
launcher = root.find('launcher')
if launcher is not None:

    credsID = launcher.find('credentialsId')

    print(f"{credsID.text}")

    if credsID is not None:
        credsID.text = args.new_label
    else:
        credsID = ET.SubElement(root, 'credentialsId')
        credsID.text = args.new_credentialsID

"""


if args.new_credentialsId:
    credsID = root.find('.//credentialsId')
    if credsID is not None:
        credsID.text = args.new_credentialsId
    else:
        credsID = ET.SubElement(root, 'credentialsId')
        credsID.text = args.new_credentialsId
        #credsID.text = "fred"



# Convert back to string
new_config = ET.tostring(root, encoding='unicode')

print("\n")
print(new_config)
print("\n")

sys.exit()



# Apply updated config
server.reconfig_node(args.node_name, new_config)
print(f"Node '{args.node_name}' label updated to '{args.new_label}'.")   


