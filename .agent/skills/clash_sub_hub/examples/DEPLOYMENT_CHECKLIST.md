# Deployment & Verification Checklist

Follow these steps to verify a new Sub Hub v3 installation.

## 1. Service Health (VPS Side)
Confirm the bridge is running without port conflicts:
```bash
systemctl status clash-sub-bridge
# Check for "Sub Hub v3 running at http://...:8080/dashboard" in logs
journalctl -u clash-sub-bridge -n 50
```

## 2. Firewall Transparency
Ensure the proxy bridge port is open and accessible from the outside:
```bash
# Check if listening on all interfaces
netstat -tulpn | grep 8080
```

## 3. Subscription Integrity (API Test)
Verify that the YAML generator produces valid Clash config:
```bash
# Test a token-based sub
curl -s http://YOUR_IP:8080/sub/YOUR_TOKEN | grep -E "proxies:|proxy-groups:|behavior:"
```

## 4. UI Rendering (Browser)
Open the dashboard and check:
- [ ] Nodes are appearing in the "Nodes Pool".
- [ ] Subscriptions can be created and the links are clickable.
- [ ] Clicking "Sync" returns a success toast.

## 5. Local Bypass
If you use Clash locally on your PC, ensure the VPS IP is in the `DIRECT` rules:
```yaml
rules:
  - IP-CIDR,YOUR_VPS_IP/32,DIRECT,no-resolve
```
