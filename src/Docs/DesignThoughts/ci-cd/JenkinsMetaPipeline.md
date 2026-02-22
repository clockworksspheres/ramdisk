# Jenkins Meta Pipeline

Jenkins pipeline software:  https://github.com/clockworksspheres/jenkinsTools.git
Virtual Machine Manage - (vmm): https://github.com/clockworksspheres/vmm.git

## Start Infrastructure

### Start jenkins server container

At this time, the Jenkins server is run in Docker on a macOS host, with Docker Desktop.  This will be automated in the future.

### Start hypervisors

This document is built on the Linux VM's being built on VMware Fusion, macOS VM's built on UTM - all on an M4 based macOS host.

The Window OS's are built on x86_64 Windows machine, as aarm64 Windows isn't as well supported.

Orchestrating the meta-pipeline of macOS host and Windows host from one machine has yet to be developed.

## Run each of the pipelines

---

### Start Redhat based VM's

``` bash
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/Rocky10-aarm64.vmwarevm/Rocky10-aarm64.vmx"
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/Rocky Linux 9-7 64-bit Arm.vmwarevm/Rocky Linux 9-7 64-bit Arm.vmx"
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/AlmaLinux 64-bit Arm.vmwarevm/AlmaLinux 64-bit Arm.vmx"
```

### Start Redhat OS Based Pipeline

``` bash
jenkinsTools/jenkinsPipelineTool.py run --job ramdisk_redhat --user <jenkinsUsername> --url http://localhost:8080 --token 123abc456... --verbose
```

### Stop Redhat based VM's

``` bash
vmm/vmm.py stop vmware "/Users/<username>/Virtual Machines.localized/Rocky10-aarm64.vmwarevm/Rocky10-aarm64.vmx"
vmm/vmm.py stop vmware "/Users/<username>/Virtual Machines.localized/Rocky Linux 9-7 64-bit Arm.vmwarevm/Rocky Linux 9-7 64-bit Arm.vmx"
vmm/vmm.py stop vmware "/Users/<username>/Virtual Machines.localized/AlmaLinux 64-bit Arm.vmwarevm/AlmaLinux 64-bit Arm.vmx"
```

---

### Start Debian based VM's

``` bash
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/Debian 12.x 64-bit Arm.vmwarevm/Debian 12.x 64-bit Arm.vmx"
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/Ubuntu 64-bit Arm 24.04.vmwarevm/Ubuntu 64-bit Arm 24.04.vmx"
```

### Run Debian OS Based Pipeline

``` bash
jenkinsTools/jenkinsPipelineTool.py run --job ramdisk-deb --user <jenkinsUsername> --url http://localhost:8080 --token 123abc456... --verbose
```

### Stop Debian based VMs

``` bash
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/Debian 12.x 64-bit Arm.vmwarevm/Debian 12.x 64-bit Arm.vmx"
vmm/vmm.py start vmware "/Users/<username>/Virtual Machines.localized/Ubuntu 64-bit Arm 24.04.vmwarevm/Ubuntu 64-bit Arm 24.04.vmx"
```

---

### Start macOS based VM's

```
vmm/vmm.py start utm macOS
```

### Run Redhat OS Based Pipeline

__macos pipeline not yet implemented__

### Stop macOS based VM's

```
vmm/vmm.py stop utm macOS
```

---

__Windows supported VMs and pipeline not yet implemented.__

### Start Windows based VM's

### Run Windows OS Based Pipeline

### Stop Windows based VM's

---

## Collect Pipeline Run Output

```
rheloutput = jenkinsPipelineTools check ramdisk-redhat -user <jenkinsUsername> --url http://localhost:8080 --token 123abc456... --verbose --get-full-run
deboutput = jenkinsPipelineTools check ramdisk-debbased -user <jenkinsUsername> --url http://localhost:8080 --token 123abc456... --verbose --get-full-run
macosoutput = jenkinsPipelineTools check ramdisk-macos -user <jenkinsUsername> --url http://localhost:8080 --token 123abc456... --verbose --get-full-run
win32output = jenkinsPipelineTools check ramdisk-windows -user <jenkinsUsername> --url http://localhost:8080 --token 123abc456... --verbose --get-full-run
```

## Possibly stop Infrastructure

