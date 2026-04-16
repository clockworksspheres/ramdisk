# Configuring SSH on the Jenkins Server Container

## copy node .ssh keys to ~/.ssh on the server

## ssh-add the key on the server

```
eval $(ssh-agent)
ssh-add <key-name>
```

## ssh to node from server command line

Need to get over the "accept" prompt (answer "yes"). this will put the machine in the server's known_hosts file.

## Run the create_jenkins_pipeline.py

Run this script to create a jenkins pipeline.

## Run the add_jenkins_test_node.py

Run this script to start the setup of a test machine/node in Jenkins.

Make sure the node is booted up, so the configuration can connect and finish an attempt to connect after the configuration is complete.

After this script to create the node is run, one needs to go into the node configuration on the Jenkins web server, on the bottom left of the page (after login), the nodes are listed.  

Choose the node that was just created, then click on the Configure link on the left hand side of the page.  

If the credentials have already been configured, select the appropriate credentials in the credentials field.  If not, just right of the credentials field, there is and "+ Add" button.  

Under the "kind" field, select "SSH Username with private key" field.

Create an ID in the ID field.  

Fill out the username of the user that Jenkins is using on the node.

Under the "Private Key" label, click the "Enter directly" selection.

Click on the "Add" button on the right and copy and paste the private key into the field below.

Click on the "Add button".

Click on the "Apply" button at the bottom, then the "Save" button.

If the "Relaunch Agent button" is on the top of the page, click it.  It should connect to the node.

If it doesn't, a debug session should start.

FAQ:

Q: When attempting to connect to the node, the field says "Connection timed out" in a line in the text field.  What can I do to fix that?

A: Make sure the node is up and running, and sshd is set up correctly on the node.

Q: Inside the text field, it says "ERROR: Server rejected the 1 private key(s) for amrobot" and the next line says "\[SSH\] Authentication failed.".  How do I fix that?

A: SSH from the Jenkins container to the node (make sure the node is set up and sshd is set up first) and make sure it automatically logs in.  If it asks for a "yes/no" response, type "yes" and hit enter.  Otherwise, the Jenkins server cannot connect.  If it continues to not connect right, make sure the public key is correctly installed on the client.  See the ssh setup instructions to correct the situation if necessary.

It is also possible that the private key in the jenkins server is incorrect, and one can go to the top right corner, click on the user icon, click on the credentials link in the bottom left, under "Credentials", click on the credential in question, click on "update" in the upper left, hit the "Replace" button in the lower part of the right hand side, and replace a the key with a good copy of the key, then hit the "Save" button on the lower left.  Go back to the node that is having the problem, click on configure, then save at the bottom, then the node should start working.



