
# Running VM's on HyperV

specifically Rocky Linux, but others will work as well. Using copilot.com:

# First prompt:  "rocky linux on. huper-V windows 11"

Got it 👍 — you want to run **Rocky Linux** inside **Hyper‑V on Windows 11**. Let me walk you through the setup clearly:

---

## 🖥️ Steps to Install Rocky Linux on Hyper‑V (Windows 11)

### 1. Enable Hyper‑V

- Open **Control Panel → Programs → Turn Windows features on or off**.
- Check **Hyper‑V** (both Hyper‑V Management Tools and Hyper‑V Platform).
- Restart your PC.

### 2. Download Rocky Linux ISO

- Go to the [Rocky Linux official site](https://rockylinux.org/download).
- Choose the latest stable release (usually the DVD ISO for full installation).

### 3. Create a New Virtual Machine

- Open **Hyper‑V Manager**.
- Click **New → Virtual Machine**.
- Configure:
    - **Name**: RockyLinuxVM
    - **Generation**: Choose **Generation 2** (UEFI support).
    - **Memory**: At least 2 GB (4 GB recommended).
    - **Networking**: Attach to a virtual switch (External for internet access).
    - **Virtual Hard Disk**: 20 GB+ recommended.
    - **Installation Media**: Select the Rocky Linux ISO you downloaded.

### 4. Install Rocky Linux

- Start the VM.
- Boot from the ISO.
- Follow the installer steps:
    - Select language and keyboard.
    - Configure disk partitioning (automatic is fine for most users).
    - Set root password and create a user.
    - Begin installation.

### 5. Post‑Installation Setup

- After reboot, log in with your user.
- Update system:
    
    ```bash
    sudo dnf update -y
    ```
    
- Install **Hyper‑V integration services** (for better performance):
    
    ```bash
    sudo dnf install hyperv-daemons -y
    ```
    
- Reboot to apply changes.

---

## ⚡ Tips

- **Enhanced Session Mode**: Hyper‑V supports clipboard sharing and dynamic resolution if integration services are installed.
- **Networking**: If you don’t see internet, check that your VM is connected to an **External Virtual Switch** in Hyper‑V.
- **Snapshots**: Use checkpoints in Hyper‑V to save VM states before major changes.

---

Would you like me to also give you a **step‑by‑step command list** (like a cheat sheet) so you can copy‑paste directly during setup?


# Second prompt: (answer below) "instructions at the powershell prompt"

Perfect — let’s do this entirely from the **PowerShell prompt** so you can set up **Rocky Linux on Hyper‑V in Windows 11** without clicking through menus.

Here’s a step‑by‑step script you can run (adjust values as needed):

---

## 🖥️ PowerShell Instructions

### 1. Enable Hyper‑V

Run PowerShell as Administrator:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

Restart your computer when prompted.

---

### 2. Create a Virtual Switch (for networking)

This connects your Rocky Linux VM to the internet:

```powershell
New-VMSwitch -Name "ExternalSwitch" -NetAdapterName (Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object -First 1).Name -AllowManagementOS $true
```

---

### 3. Create the Rocky Linux VM

Replace the ISO path with the location where you downloaded the Rocky Linux ISO.

```powershell
New-VM -Name "RockyLinuxVM" -MemoryStartupBytes 4GB -Generation 2 -NewVHDPath "C:\VMs\RockyLinuxVM\RockyLinux.vhdx" -NewVHDSizeBytes 40GB -SwitchName "ExternalSwitch"
```

---

### 4. Attach the Rocky Linux ISO

```powershell
Set-VMFirmware -VMName "RockyLinuxVM" -EnableSecureBoot Off
Add-VMDvdDrive -VMName "RockyLinuxVM" -Path "C:\ISOs\Rocky-9.4-x86_64-dvd.iso"
Set-VM -Name "RockyLinuxVM" -ProcessorCount 2
```

---

### 5. Start the VM

```powershell
Start-VM -Name "RockyLinuxVM"
```

At this point, open **Hyper‑V Manager** or use:

```powershell
vmconnect.exe localhost RockyLinuxVM
```

This launches the console so you can install Rocky Linux from the ISO.

---

### 6. After Installation (inside Rocky Linux)

Once Rocky Linux is installed and booted:

```bash
sudo dnf update -y
sudo dnf install hyperv-daemons -y
```

This ensures integration with Hyper‑V (clipboard, shutdown, etc.).

---

✅ That’s the full PowerShell workflow: enable Hyper‑V, create a switch, build the VM, attach the ISO, and boot into the installer.

Do you want me to also give you a **single PowerShell script** that automates all these steps in one go (so you just run it once)?


# Third prompt: "can one run multiple VM's this way?"

Absolutely ✅ — you can run **multiple Rocky Linux (or other) VMs** in Hyper‑V on Windows 11 using PowerShell. Hyper‑V is designed to manage many virtual machines at once, as long as your hardware resources (CPU, RAM, disk space) can handle it.

---

## 🖥️ Running Multiple VMs with PowerShell

### 1. Create Additional VMs

You can repeat the `New-VM` command with different names and storage paths. For example:

```powershell
New-VM -Name "RockyLinuxVM1" -MemoryStartupBytes 4GB -Generation 2 -NewVHDPath "C:\VMs\RockyLinuxVM1\RockyLinux.vhdx" -NewVHDSizeBytes 40GB -SwitchName "ExternalSwitch"

New-VM -Name "RockyLinuxVM2" -MemoryStartupBytes 4GB -Generation 2 -NewVHDPath "C:\VMs\RockyLinuxVM2\RockyLinux.vhdx" -NewVHDSizeBytes 40GB -SwitchName "ExternalSwitch"
```

Each VM gets its own virtual hard disk and name.

---

### 2. Attach ISO to Each VM

```powershell
Add-VMDvdDrive -VMName "RockyLinuxVM1" -Path "C:\ISOs\Rocky-9.4-x86_64-dvd.iso"
Add-VMDvdDrive -VMName "RockyLinuxVM2" -Path "C:\ISOs\Rocky-9.4-x86_64-dvd.iso"
```

---

### 3. Start Multiple VMs

```powershell
Start-VM -Name "RockyLinuxVM1"
Start-VM -Name "RockyLinuxVM2"
```

You can run as many as your system resources allow.

---

### 4. Manage All VMs

- List all VMs:
    
    ```powershell
    Get-VM
    ```
    
- Stop a VM:
    
    ```powershell
    Stop-VM -Name "RockyLinuxVM1"
    ```
    
- Connect to a VM console:
    
    ```powershell
    vmconnect.exe localhost RockyLinuxVM2
    ```
    

---

## ⚡ Things to Keep in Mind

- **RAM & CPU**: Each VM consumes resources. If you allocate 4 GB RAM per VM, 3 VMs = 12 GB total.
- **Networking**: All VMs can share the same virtual switch (ExternalSwitch) for internet access.
- **Storage**: Ensure you have enough disk space for multiple `.vhdx` files.

---

So yes — you can run multiple Rocky Linux VMs this way, and even mix in other OSes (Ubuntu, Debian, Windows Server) using the same PowerShell workflow.

👉 Do you want me to show you a **PowerShell loop script** that automatically creates, configures, and starts several VMs at once (instead of repeating commands manually)?