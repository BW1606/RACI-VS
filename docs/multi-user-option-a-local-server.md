# Option A — Run on a shared local machine (zero code changes)

## Summary

Pick one always-on machine in the office. Run the app on it. Everyone opens the same URL in their browser. No Azure, no database migration, works today for free.

## When to use this

- Team is in the same office or connected via VPN
- You want the simplest possible setup
- No Azure subscription or monthly cost required

## Setup steps

1. **Choose a host machine** — a spare PC, an existing Windows Server, or any machine that is always on during working hours.

2. **Install Python 3.11+** on that machine (if not already installed): https://www.python.org/downloads/

3. **Copy or clone the repo** onto that machine:
   ```
   git clone https://github.com/BW1606/RACI-VS.git
   cd RACI-VS
   pip install -r requirements.txt
   ```

4. **Start the server** (listening on all network interfaces, not just localhost):
   ```
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Find the machine's local IP address** (run in PowerShell):
   ```
   (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Ethernet*","Wi-Fi*").IPAddress
   ```

6. **Share the URL** with colleagues: `http://<machine-ip>:8000`

## Keep it running automatically (optional)

To start the server automatically on Windows startup, create a scheduled task:

```powershell
$action = New-ScheduledTaskAction -Execute "uvicorn" -Argument "main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "C:\path\to\RACI-VS"
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName "RACI-VS Server" -Action $action -Trigger $trigger -RunLevel Highest
```

## Limitations

- Machine must stay on for the app to be reachable
- No HTTPS (plain HTTP only) unless you add a reverse proxy like Caddy or nginx
- Only reachable within the local network — colleagues working from home need a VPN
