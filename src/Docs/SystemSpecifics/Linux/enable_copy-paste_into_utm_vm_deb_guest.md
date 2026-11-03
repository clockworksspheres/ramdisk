# do the spice agent guest tools work on debian?

Yes, `spice-vdagent` is available in Debian's repos and works with UTM. The [UTM docs](https://docs.getutm.app/guest-support/linux/) specifically list Debian:

```bash
sudo apt install spice-vdagent
```

**Caveats to be aware of:**

- **X11 only** — clipboard sharing requires an X11 session. Pure Wayland compositors (e.g., Sway) won't work. GNOME on Wayland *does* work because Mutter bridges both clipboard backends.
- **Two processes must run:** `spice-vdagentd` (system daemon, started via systemd) and `spice-vdagent` (per-user X11 agent, auto-started by desktop environments that honor `/etc/xdg/autostart`). On minimal or non-standard desktops, you may need to start the user agent manually:
  ```bash
  spice-vdagent &
  ```
- **Debian 12 (Bookworm) note:** Some users report needing to manually launch `spice-vdagent` as the logged-in user even when the systemd service is running, particularly with KDE Plasma.

If you're using a standard desktop (XFCE, GNOME on Xorg, etc.) it should "just work" after install and reboot.

# the UTM guest tools are not available via the cd icon - how do I install them?

For **Linux guests**, the "Install Guest Tools" CD option is essentially **Windows-only** — it mounts an ISO containing a Windows `.exe` installer. For Debian, you install the equivalent packages directly from the distro repos:

```bash
sudo apt update
sudo apt install spice-vdagent
```

If you also want **shared directory** support (SPICE WebDAV mode), add:

```bash
sudo apt install spice-webdavd
```

Then **reboot the VM** and make sure **Clipboard sharing** is enabled in UTM's VM settings (Sharing pane).

> **Note:** `spice-vdagent` requires an X11 session — it won't provide clipboard sharing on a headless/server install without a desktop environment.






