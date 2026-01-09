# Adding a new Test Node.

1 - on the node, create the jenkins-agent directory

2 - on the node make sure java is installed

3 - on the server, use ```ssh-copy-id``` to copy a new key to the new node (create one if one doesn't exist)

4 - in Web UI add the new test node to the "Build Executor Status" node list

5 - add node to project Jenkinsfile

6 - do a test run to see if all is good.


