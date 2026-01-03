
Install macOS of the Host system into UTM VM

 - default install is to download latest IPSW from Apple, of the host OS. moving forward, but with 80Gb HD and 24Gb ram.    [How to Setup macOS in a VM on macOS with UTM](https://danielraffel.me/2025/05/13/running-macos-in-a-vm-on-macos-with-utm/?utm_source=copilot.com)

 - need to figure out how to change # of CPUs (right click on VM, go to Edit -> System -> CPU cores )

 - start, follow prompts to set up.

 - go to softwareupdates, click on i next to update of current OS - de-select
   latest (Tahoe), select (sequoia) latest update.  Update the system

set up ssh (System Settings -> General -> Sharing -> Remote Login)

get ip address  

``` bash
ipconfig -a
```

Install xcode tools

``` bash
xcode-select --install
```

while downloading, looking into ansible configuration via local files

install homebrew - go to homebrew website and get the install command:  

``` bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install pyinstaller pyenv mas tree bpytop tmux byobu git pylint rsync
```

tried [IT Automation with Ansible #2 - Ansible Configuration File and Local Inventory](https://www.youtube.com/watch?v=N9CaJf6qGRs) and [Ansible Inventory File Example](https://www.youtube.com/watch?v=0MT9WvX_j4Y)

What worked:

Trying to get ansible set up on client for local config

``` bash
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/custom_key_name
ssh-copy-id <user>@<machine>
```

set up ansible

``` bash
mkdir ansible-tutorial
cd ansible-tutorial
vim ansible.cfg
```

``` ansible
[defaults]
inventory=./hosts
ansible_python_interpreter="/usr/bin/env python3"
private_key_file = ~/.ssh/custom_key_name
host_key_checking = False
```

create ansible hosts file

``` bash 
vim hosts
```

contents:

``` ansible
[local]
127.0.0.1

[localip]
<ip-address>
```

run ping:

``` bash
ansible all -m ping
ansible local -m ping
ansible localip -m ping
```

``` bash

vim install_homebrew_macos.yml

```

``` yaml
---
- name: Install Homebrew on macOS
  hosts: localhost
  connection: local
  vars:
    install_homebrew_if_missing: true
  pre_tasks:
    - name: Check if Homebrew is installed

      stat:
        path: /opt/homebrew/bin/brew
      register: homebrew_check

    - name: Fail if Homebrew is missing and install flag is false
      fail:
        msg: "Homebrew is missing, install from https://brew.sh"
      when:
        - not homebrew_check.stat.exists
        - not install_homebrew_if_missing

    - name: Install Homebrew (Apple Silicon)
      shell: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
      args:
        executable: /bin/bash
      environment:
        NONINTERACTIVE: 1
      when: not homebrew_check.stat.exists
      become: false
  tasks:
    - name: Ensure Homebrew PATH is set
      lineinfile:
        path: ~/.zshrc
        line: 'export PATH="/opt/homebrew/bin:$PATH"'
        create: true
      when: not homebrew_check.stat.exists
```

``` bash
vim install_homebrew_packages.yml
```

``` yaml
---
- name: Install git, tree, rsync with Homebrew
  hosts: localhost
  connection: local
  tasks:
    - name: Install packages
      community.general.homebrew:
        name:
          - git
          - tree
          - rsync
          - pyinstaller
          - pyenv
          - mas
          - bpytop
          - tmux
          - byobu
          - pylint
        state: present
```

``` bash
vim configure_macos.yaml
```

  
``` yaml
 - import_playbook: install_homebrew_macos.yml
 - import_playbook: install_homebrew_packages.yml
```

``` bash
ansible-playbook configure_macos.yml
```

run ping:

``` bash
ansible all -m ping
ansible local -m ping
ansible localip -m ping
```

# References

How to [Setup macOS in a VM](https://danielraffel.me/2025/05/13/running-macos-in-a-vm-on-macos-with-utm/?utm_source=copilot.com) on macOS with UTM

Youtube: IT Automation with Ansible #2 - [Ansible Configuration File and Local Inventory](https://www.youtube.com/watch?v=N9CaJf6qGRs)

Youtube: [Ansible Inventory File Example](https://www.youtube.com/watch?v=0MT9WvX_j4Y)

Jeff Geerling's [ansible](https://github.com/geerlingguy/mac-dev-playbook) repo





