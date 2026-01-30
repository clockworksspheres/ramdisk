import jenkins

# Connect to Jenkins
server = jenkins.Jenkins('http://localhost:8080', username='admin', password='admin')

# Define node parameters
node_name = 'my-agent-node'
remote_fs = '/home/jenkins'
labels = 'linux docker'

# Inline private key (string)
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...rest of your key...
-----END RSA PRIVATE KEY-----"""

# Create node with inline key
server.create_node(
    name=node_name,
    numExecutors=2,
    remoteFS=remote_fs,
    labels=labels,
    exclusive=False,
    launcher=jenkins.LAUNCHER_SSH,
    launcher_params={
        'host': '192.168.1.100',
        'port': 22,
        'username': 'jenkins',
        'privatekey': private_key,   # key inline here
    }
)

print(f"Node '{node_name}' created successfully!")


