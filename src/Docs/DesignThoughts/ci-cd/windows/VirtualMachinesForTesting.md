
# Virtual Machines for Testing

## For remotely managing the jenkins server interface

http://github.com/clockworksspheres/jenkinsTools.git

## For managing local VMs for cross platform projects on macOS and Windows

https://github.com/clockworksspheres/vmm.git

Designed for the following hypervisors currently:

* UTM
* HyperV
* VMware Workstation & Fusion
* Oracle VirtualBox

## Can hyper-v work at the same time as vmware workstation and virtualbox

** answer by copilot.com **

**Short answer: Yes, Hyper‑V _can_ coexist with VMware Workstation and VirtualBox—but with important limitations.** Modern Windows versions allow them to be installed together, but they cannot all run full‑performance VMs at the same time unless they use Microsoft’s Windows Hypervisor Platform (WHP), and even then, performance varies. [H2S Media](https://www.how2shout.com/how-to/use-virtualbox-and-hyper-v-together-on-windows-10.html) [vInfrastructure Blog](https://vinfrastructure.it/2024/10/how-to-use-both-vmware-workstation-and-microsoft-hyper-v/)

---

## 🖥️ Can they run _simultaneously_?

Here’s the practical breakdown:

### ✅ **Hyper‑V + VirtualBox**

- Since Windows 10 version 1803, VirtualBox can run using the **Windows Hypervisor Platform (WHP)** even when Hyper‑V is enabled.
- Performance is usually lower than native VT‑x mode, but it works.  
    [H2S Media](https://www.how2shout.com/how-to/use-virtualbox-and-hyper-v-together-on-windows-10.html)

### ⚠️ **Hyper‑V + VMware Workstation**

- Historically incompatible because Hyper‑V occupies the hardware virtualization layer (ring ‑1).
- Newer VMware versions can run using WHP, but performance may be reduced.
- VMware Workstation _can be installed_ alongside Hyper‑V, but running VMs concurrently is hit‑or‑miss depending on configuration.  
    [vInfrastructure Blog](https://vinfrastructure.it/2024/10/how-to-use-both-vmware-workstation-and-microsoft-hyper-v/)

### ⚠️ **VMware Workstation + VirtualBox**

- These two can coexist, but **should not run VMs at the same time** unless both are using WHP mode.
- Even then, stability varies.  
    [virtualbox.org](https://forums.virtualbox.org/viewtopic.php?t=110273)

---

## 🧩 Why the conflict?

- Hyper‑V is a **Type‑1 hypervisor** that loads before Windows and takes exclusive control of virtualization hardware.
- VMware and VirtualBox are **Type‑2 hypervisors** that expect direct access to VT‑x/AMD‑V.
- WHP acts as a compatibility layer, allowing Type‑2 hypervisors to run on top of Hyper‑V—but with overhead.  
    [TheWindowsClub](https://www.thewindowsclub.com/run-hyper-v-virtualbox-vmware-on-same-computer)

---

## ✔️ What _does_ work reliably?

|Combination|Install Together|Run VMs Together|Notes|
|---|---|---|---|
|**Hyper‑V + VirtualBox**|Yes|Yes (WHP mode)|Reduced performance|
|**Hyper‑V + VMware Workstation**|Yes|Sometimes (WHP mode)|May be slow or unstable|
|**VMware + VirtualBox**|Yes|Not recommended|Avoid running VMs simultaneously|

---

## 🏁 Bottom line

You _can_ have all three installed on the same Windows machine.  
You _can_ run them at the same time **only if** VMware and VirtualBox operate in WHP mode while Hyper‑V is enabled—but expect reduced performance and occasional compatibility issues.

If you want the smoothest experience, choose **one primary hypervisor** and disable Hyper‑V when using VMware or VirtualBox for full performance.

If you want, I can walk you through:

- Checking whether WHP is enabled
- Configuring VMware/VirtualBox to use Hyper‑V mode
- Choosing the best setup for your hardware and use case