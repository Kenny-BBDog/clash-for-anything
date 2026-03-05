import json

# Read the config
with open('/usr/local/x-ui/bin/config.json', 'r') as f:
    config = json.load(f)

# Update the SOCKS outbound to use HydraProxy (no auth, IP whitelist)
for outbound in config['outbounds']:
    if outbound.get('tag') == 'cladue-out':
        outbound['settings']['servers'] = [{
            'address': 'static2.hydraproxy.com',
            'port': 3114
            # No users field since it uses IP whitelist auth
        }]
        outbound['tag'] = 'hydra-static-ip'
        print(f"Updated outbound to HydraProxy")
        break
else:
    # Add new outbound if not found
    config['outbounds'].append({
        'protocol': 'socks',
        'settings': {
            'servers': [{
                'address': 'static2.hydraproxy.com',
                'port': 3114
            }]
        },
        'tag': 'hydra-static-ip'
    })
    print("Added new HydraProxy outbound")

# Add routing rule to send VLESS traffic through HydraProxy
# Find if rule already exists
has_rule = False
for rule in config['routing']['rules']:
    if rule.get('inboundTag') == ['inbound-4887']:
        rule['outboundTag'] = 'hydra-static-ip'
        has_rule = True
        print("Updated existing routing rule")
        break

if not has_rule:
    # Insert rule at the beginning (after api rule)
    config['routing']['rules'].insert(1, {
        'type': 'field',
        'inboundTag': ['inbound-4887'],
        'outboundTag': 'hydra-static-ip'
    })
    print("Added new routing rule for inbound-4887 -> hydra-static-ip")

# Write the updated config
with open('/usr/local/x-ui/bin/config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Config updated successfully!")
print("Please restart xray: systemctl restart x-ui")
