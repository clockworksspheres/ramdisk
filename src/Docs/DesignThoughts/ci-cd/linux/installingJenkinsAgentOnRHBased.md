# Preparing RHEL based systems for the Jenkins agent

# Package(s) to install

```
sudo dnf install java-21-openjdk java-21-openjdk-devel   
```

# Prepare ssh on the source side (Jenkins Server)

```
ssh-keygen -t ed25519 -C "your_email@example.com" -f <key-name>
ssh-copy-id -i <key-name>.pub user@jenkins_agent_remote_host
eval $(ssh-agent)
ssh-add <key-name>
```

# Prepare SSHD on the destination side (Jenkins Agent)

```
vim /etc/ssh/sshd_config
```

Check the /etc/ssh/sshd_config for the following directives before taking the above steps:

```
Port 22                  # Default SSH port
PermitRootLogin no       # Disable root login for security
PasswordAuthentication yes  # Allow password login (or set to 'no' if using keys only)
PubkeyAuthentication yes # Enable public key authentication
```

Then run:

```
sudo systemctl enable ssh
sudo systemctl restart ssh
```

