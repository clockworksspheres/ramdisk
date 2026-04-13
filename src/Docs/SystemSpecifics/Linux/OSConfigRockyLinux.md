
# OS Configure Rocky Linux

## Getting a network interface working that is disabled:


1. Confirm that the device exists:

```
nmcli device status
```

which will show the device name

2. Find the connection profile name

```
nmcli connection show
```

3. Bind the profile to the device:

```
sudo nmcli connection modify ens160 connection.interface-name enp2s0
```

where ens160 is the name of the interface and enp2s0 is the device name.  If the profile has a name of "wired connection 0", then make sure to put quotes around that in the command above.

Enable DHCP:

```
sudo nmcli connection modify ens160 ipv4.method auto
```

See if an IP address has been assigned:

```
ip addr show
nmcli device show enp2s0
```

4. If no profile exists:

```
sudo nmcli connection add type ethernet ifname enp2s0 con-name enp2s0 ipv4.method auto
```

Then bring it up:

```
sudo nmcli connection up enp2s0
```

5. Verify

```
ip addr show enp2s0
nmcli device show enp2s0
```
      

## Upping idle timeout time for GUI lockscreen

**Increase Lock Screen Timeout on Rocky Linux 9**

For the default GNOME desktop:

1. **Graphical Method**:
    
    - Open **Settings**.
        
    - Go to **Privacy** > **Screen Lock**.
        
    - Set **Automatic Screen Lock Delay** to your desired time (e.g., 30 minutes, 1 hour) or turn it **Off**. 
        
2. **Command Line Method**:
    
    - Use `gsettings` to change the idle delay (time before the system is considered idle and can be locked). For example, to set it to 1 hour (3600 seconds):
        
        ```
        gsettings set org.gnome.desktop.session idle-delay 3600
        ```
        
    - To disable automatic locking entirely:
        
        ```
        gsettings set org.gnome.desktop.screensaver lock-enabled false
        ```

