# Configuring SSH on the Jenkins Server Container

## copy node .ssh keys to ~/.ssh on the server

## ssh-add the key on the server

```
eval $(ssh-agent)
ssh-add <key-name>
```

## ssh to node from server command line

Need to get over the "accept" prompt (answer "yes"). this will put the machine in the server's known_hosts file.
