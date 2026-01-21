
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