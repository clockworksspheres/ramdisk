# Preparing RHEL based systems for the Jenkins agent

# Package(s) to install

```
sudo apt install java-21-openjdk java-21-openjdk-devel
sudo aptd install openssh-server
```

# Create SSH keys for use by the Jenkins Server-Agent interaction

On the Jenkins server

```
ssh-keygen -t ed25519 -C "your_email@example.com" -f <key-name>
ssh-copy-id -i <key-name>.pub user@jenkins_agent_remote_host
eval $(ssh-agent)
ssh-add <key-name>
```

## Install the private key to the Jenkins web service:

 Examples:

* Add ~/.ssh/id_rsa as a Jenkins credential:

``` bash
     ./jenkinsTools/JenkinsTools/AddSshKeyCredential.py \
      --url http://localhost:8080 \
      --jenkins-user admin \
      --jenkins-token API_TOKEN \
      --credential-id linux-agent-key \
      --ssh-user jenkins \
      --private-key ~/.ssh/id_rsa
```
  
 * Add an encrypted SSH key:

``` bash
    ./jenkinsTools/JenkinsTools/AddSshKeyCredential.py \
      --url http://jenkins:8080 \
      --jenkins-user admin \
      --jenkins-token API_TOKEN \
      --credential-id secure-key \
      --ssh-user jenkins \
      --private-key ~/.ssh/id_rsa_secure \
      --key-passphrase "mySecretPassphrase"
```

# Prepare SSHD on the destination side (Jenkins Agent)

## Enabled and Start sshd on the Jenkins Agent 

```
sudo systemctl enable ssh
sudo systemctl restart ssh
```

## Set up Sudoers to allow for py.test to run

### Systemd systems

```
vim /etc/sudoers.d/<username>
```

File should look like:

```
<username> ALL=(ALL) NOPASSWD:/usr/bin/py.test
```

