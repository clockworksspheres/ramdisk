# vmctl list qemu
libvirtd
Traceback (most recent call last):
  File "/home/amrobot/Documents/src/github/clockworksspheres/mvm/src/projEnv/bin/vmctl", line 6, in <module>
    sys.exit(main())
             ~~~~^^
  File "/home/amrobot/Documents/src/github/clockworksspheres/mvm/src/projEnv/lib/python3.13/site-packages/mvm/vmctl.py", line 179, in main
    mvm_run(args)
    ~~~~~~~^^^^^^
  File "/home/amrobot/Documents/src/github/clockworksspheres/mvm/src/projEnv/lib/python3.13/site-packages/mvm/mvm_run.py", line 55, in mvm_run
    table = mvm.list_vms()
  File "/home/amrobot/Documents/src/github/clockworksspheres/mvm/src/projEnv/lib/python3.13/site-packages/mvm/ManageVirtualMachines.py", line 71, in list_vms
    table = self.mvm.list_vms(**kwargs)
  File "/home/amrobot/Documents/src/github/clockworksspheres/mvm/src/projEnv/lib/python3.13/site-packages/mvm/LinuxQemuMvm.py", line 145, in list_vms
    name = dom.getName()          # ← correct: VM name
           ^^^^^^^^^^^
AttributeError: 'virDomain' object has no attribute 'getName'. Did you mean: 'getTime'?


## To fix this issue, you need to activate the virtual network named 'default' in libvirt and configure it to start automatically on boot. This error happens because the virtual machine is configured to use the default NAT network interface, but that network service is currently stopped. [1] (/goto?url=CAESaAHrOzAVI2uWV2XpZQIm4sYCIvkbvWvO00vxnle0fULJWexQEQsoJkQwG_6IvpOrCypbq5EBqBEjihibrotaLui5h3oikrEtBifdDZtl5It0CHMmTbdQHNYvRci3MDCETQZwas_eGQlz)
Run the following commands in your terminal to resolve the problem:

1. Start the default network

Force the network to start immediately:
bash
sudo virsh net-start default
Use code with caution.

2. Configure it to start on boot

Ensure you don't encounter this issue again after a system restart:
bash
sudo virsh net-autostart default
Use code with caution.

3. Verify the network status

You can check if the network is successfully running by listing all networks:
bash
sudo virsh net-list --all
Use code with caution.
You should see default marked as active and autostart: yes. Once verified, return to virt-manager and start your virtual machine. [1] (/goto?url=CAESaAHrOzAVI2uWV2XpZQIm4sYCIvkbvWvO00vxnle0fULJWexQEQsoJkQwG_6IvpOrCypbq5EBqBEjihibrotaLui5h3oikrEtBifdDZtl5It0CHMmTbdQHNYvRci3MDCETQZwas_eGQlz)

🛠️ Troubleshooting Persistent Issues

If the net-start command throws a different error (such as a conflict with dnsmasq or missing package dependencies), try these steps:
• Check for dnsmasq conflicts: libvirt manages its own instance of dnsmasq. If you have a system-wide dnsmasq service running, it might block libvirt. Test this by stopping it temporarily (sudo systemctl stop dnsmasq) and running the net-start command again. [1] (/goto?url=CAESbAHrOzAV0RjP5MSIeVf1RwfIMmXrRCb5gDqztnW8rNruTGm7IggSm5EXQXWoYXUo0py212z79g1afDZkgi6Oi6AGjikEv_ysNDiFuPJsau5Vn5MY4q9sJSraIbvMX0p4gfIKoBFTGRgWbcxNGg)
• Missing iptables/ebtables: libvirt relies on firewall packages to create the NAT network routing. If you are on an Arch-based system or a minimal installation, ensure you have your firewall dependencies installed (sudo pacman -S iptables-nft or equivalent). [1] (/goto?url=CAESbAHrOzAV0RjP5MSIeVf1RwfIMmXrRCb5gDqztnW8rNruTGm7IggSm5EXQXWoYXUo0py212z79g1afDZkgi6Oi6AGjikEv_ysNDiFuPJsau5Vn5MY4q9sJSraIbvMX0p4gfIKoBFTGRgWbcxNGg)
If you see a specific error message when attempting to run sudo virsh net-start default, let me know the exact output text so we can solve that specific blocker!

