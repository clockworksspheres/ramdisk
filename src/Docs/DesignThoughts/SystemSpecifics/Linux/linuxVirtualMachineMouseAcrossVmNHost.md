# Linux virtual machine across VM and host

from search.brave.com AI:

To enable seamless mouse movement between VMware Fusion and a Debian guest VM, install the following packages:

- **`open-vm-tools`**: Provides core VMware integration, including mouse and keyboard support. 
    
- **`open-vm-tools-desktop`**: Adds GUI enhancements like drag-and-drop, clipboard sharing, and improved mouse behavior. 
    

Run the following commands in your Debian VM terminal:

```
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop
```

After installation, **reboot the VM** to ensure all services start correctly.  This setup enables the mouse to move freely between the host and guest without requiring `Ctrl+Alt` to release the cursor.

# Prompt: "And for Rocky Linux?"

For Rocky Linux, install the following packages to enable mouse sharing between VMware Fusion and the guest:

- **`open-vm-tools`**: Provides core VMware integration. 
    
- **`open-vm-tools-desktop`**: Adds GUI features like seamless mouse, drag-and-drop, and clipboard sharing. 
    

Run these commands in your Rocky Linux VM:

```
sudo dnf update -y
sudo dnf install -y open-vm-tools open-vm-tools-desktop
sudo systemctl enable vmtoolsd --now
```

Reboot the VM afterward. This ensures the VMware tools service starts correctly and enables smooth mouse movement between host and guest.