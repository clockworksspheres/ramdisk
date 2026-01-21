
# OS Configure Rocky Linux

## Getting DNS working on Rocky Linux (systemd, NetworkManager)

1. **Set DNS via NetworkManager**:
    
    ```
    sudo nmcli connection modify <connection_name> ipv4.dns "8.8.8.8,1.1.1.1"
    ```
    
    Replace `<connection_name>` (e.g., `eth0`, `ens160`) with your active connection.
    
2. **Restart NetworkManager**:
    
    ```
    sudo systemctl restart NetworkManager
    ```
    
3. **Verify**:
    
    - Check `/etc/resolv.conf` contains your DNS servers.
        
    - Test with `dig google.com` or `nslookup google.com`. 
        

**Do not edit `/etc/resolv.conf` directly**; it's managed by NetworkManager.

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

