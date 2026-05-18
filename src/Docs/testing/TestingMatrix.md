# Testing Matrix for the mvm project

## Testing Methods

Some of the testing is provided by a Jenkins pipeline, but most of the testing is currently done by hand.

### Runs on

 | macOS Host | Windows Host | Linux Host
 ---|------------|-------------|---------------
 UTM | Available | N/A | N/A
 HyperV | N/A | Available | N/A
 VirtualBox | Available | Available | Available
 VMware | Available | Available | Available
 QEMU | Available | Available | Available
 KVM | N/A | N/A | Available

### Capabilities

  | Hypervisor Type | Provides Emulation | provides HW Virtualization | Nested Virtualization 
 --- | --- | --- | --- | ---
 UTM | 2 | Yes | Yes | in some cases
 HyperV | 1 | ?? | Yes | Yes, only for Windows guests
 VirtualBox | 2 | Yes | Yes | If supported by initial guest
 VMware | 2 | ?? | Yes | If supported by initial guest
 QEMU | 2 | Yes | Yes | if supported by initial guest
 KVM | 1 | ?? | Yes | ??

### Tested - guest on a Host hardware

Time has allowed for the following

 | macOS Host | Windows Host | Linux Host
 ---|------------|-------------|---------------
UTM | Yes | N/A | N/A
HyperV | N/A | Yes | N/A
VirtualBox | Yes | Yes | Yes (nested vm)
VMware | Yes | No | No
QEMU | (via UTM) | No | No
KVM | No | No | No

### OS's Tested

Time has allowed for the following

 | macOS guest | Windows guest | Linux guest
 ---|------------|-------------|---------------
macOS | Yes | Not Supported | Not Supported
Windows | Yes | Yes | No
Debian | Yes | Yes | Yes
Ubuntu | Yes | Yes | Yes
Rocky Linux | Yes | No | No
Alma Linux | Yes | No | No

## As a Guest on macOS

Time has allowed for the following

 | macOS | Windows | Debian | Ubuntu | Rocky | Alma
 ---| --- | --- | --- | --- | --- | ---
UTM | Yes | Yes | Yes | No | No | No 
HyperV | N/A | Yes | Yes | Yes | No | No
VirtualBox | No | Yes | Yes | Yes | No | No
VMware | No | No | Yes | Yes | Yes | Yes
QEMU | (via UTM) | (via UTM) | (via UTM) | No | No | No
KVM | N/A | No | No | No | No | No

## As a Guest on Windows

Time has allowed for the following

Virtualbox - Debian & Ubuntu
HyperV - Ubuntu & Windows

## As a Guest on Linux

Time has allowed for the following - project doesn't have hardware to put Linux on to test guest OSs.  Linux Guest OS's on a Linux Host have to be tested in a hyperV provided Linux OS, where the guest inside the Linux OS being emulated rather than virtualized.

Virtualbox (Emulated as a VM in a Ubuntu VM, on HyperV)- Debian

