# DNS Indexing and Multiple DNS Servers Explained

## DNS Index Overview

### **What is DNS Index?**
The `index` parameter in `netsh interface ip add dns` specifies the **priority order** of DNS servers. Lower index numbers have higher priority.

### **Index Values:**
- **Index 1**: Primary DNS server (highest priority)
- **Index 2**: Secondary DNS server (used if primary fails)
- **Index 3**: Tertiary DNS server (used if primary and secondary fail)
- **Index 4+**: Additional fallback DNS servers

## How DNS Resolution Works

### **Sequential DNS Lookup:**
1. **Primary DNS (Index 1)**: First attempt for all queries
2. **Secondary DNS (Index 2)**: Used if primary times out or fails
3. **Tertiary DNS (Index 3)**: Used if both primary and secondary fail
4. **Additional DNS**: Used in order if all previous fail

### **Timeout Behavior:**
- Each DNS server gets a chance to respond
- If one fails, Windows automatically tries the next
- This provides redundancy and reliability

## DNS Configuration Examples

### **Basic Configuration (2 DNS servers):**
```cmd
netsh interface ip set dns "Wi-Fi" static 8.8.8.8
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
```
**Result:**
- Primary: 8.8.8.8 (Google DNS)
- Secondary: 8.8.4.4 (Google DNS backup)

### **Enhanced Configuration (3 DNS servers):**
```cmd
netsh interface ip set dns "Wi-Fi" static 8.8.8.8
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
netsh interface ip add dns "Wi-Fi" 1.1.1.1 index=3
```
**Result:**
- Primary: 8.1.1.1 (Google DNS)
- Secondary: 8.8.4.4 (Google DNS backup)
- Tertiary: 1.1.1.1 (Cloudflare DNS)

### **Corporate + External DNS (4 servers):**
```cmd
netsh interface ip set dns "Wi-Fi" static 10.77.94.22
netsh interface ip add dns "Wi-Fi" 10.77.64.22 index=2
netsh interface ip add dns "Wi-Fi" 8.8.8.8 index=3
netsh interface ip add dns "Wi-Fi" 1.1.1.1 index=4
```
**Result:**
- Primary: 10.77.94.22 (Corporate DNS)
- Secondary: 10.77.64.22 (Corporate DNS backup)
- Tertiary: 8.8.8.8 (Google DNS - for blocked domains)
- Quaternary: 1.1.1.1 (Cloudflare DNS - additional backup)

## Benefits of Multiple DNS Servers

### **Reliability:**
- If one DNS server fails, others continue working
- Reduces network downtime
- Provides redundancy

### **Performance:**
- Faster response if primary DNS is slow
- Load distribution across multiple servers
- Geographic redundancy

### **Bypass Restrictions:**
- Corporate DNS for internal resources
- External DNS for blocked domains
- Fallback options if some DNS servers are blocked

## Practical Applications for Cursor

### **Scenario 1: Corporate DNS Blocks Cursor**
```cmd
# Keep corporate DNS for internal resources
netsh interface ip set dns "Wi-Fi" static 10.77.94.22
# Add external DNS for Cursor domains
netsh interface ip add dns "Wi-Fi" 8.8.8.8 index=2
netsh interface ip add dns "Wi-Fi" 1.1.1.1 index=3
```

### **Scenario 2: Pure External DNS**
```cmd
# Use only external DNS servers
netsh interface ip set dns "Wi-Fi" static 8.8.8.8
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
netsh interface ip add dns "Wi-Fi" 1.1.1.1 index=3
```

### **Scenario 3: Maximum Redundancy**
```cmd
# Multiple external DNS providers
netsh interface ip set dns "Wi-Fi" static 8.8.8.8
netsh interface ip add dns "Wi-Fi" 8.8.4.4 index=2
netsh interface ip add dns "Wi-Fi" 1.1.1.1 index=3
netsh interface ip add dns "Wi-Fi" 1.0.0.1 index=4
netsh interface ip add dns "Wi-Fi" 208.67.222.222 index=5
```

## DNS Server Options

### **Google DNS:**
- **Primary**: 8.8.8.8
- **Secondary**: 8.8.4.4
- **Features**: Fast, reliable, good for blocked domains

### **Cloudflare DNS:**
- **Primary**: 1.1.1.1
- **Secondary**: 1.0.0.1
- **Features**: Privacy-focused, very fast

### **OpenDNS:**
- **Primary**: 208.67.222.222
- **Secondary**: 208.67.220.220
- **Features**: Good filtering options

### **Quad9 DNS:**
- **Primary**: 9.9.9.9
- **Secondary**: 149.112.112.112
- **Features**: Security-focused, blocks malicious domains

## Testing DNS Configuration

### **Check Current DNS:**
```cmd
ipconfig /all | findstr "DNS Servers"
```

### **Test Specific DNS Server:**
```cmd
nslookup cursor.sh 8.8.8.8
nslookup cursor.sh 1.1.1.1
```

### **Test DNS Resolution Order:**
```cmd
nslookup cursor.sh
# This will use the configured DNS servers in order
```

## Best Practices

### **For Cursor Access:**
1. **Start with 2 DNS servers** (Google DNS)
2. **Add Cloudflare as tertiary** for redundancy
3. **Test each configuration** before committing
4. **Keep corporate DNS** if internal resources are needed

### **Configuration Strategy:**
- **Index 1**: Fastest/most reliable DNS
- **Index 2**: Backup DNS from same provider
- **Index 3**: Alternative provider for redundancy
- **Index 4+**: Additional fallbacks if needed

### **Reverting Changes:**
```cmd
# Return to DHCP (automatic DNS)
netsh interface ip set dns "Wi-Fi" dhcp
```

## Troubleshooting

### **If DNS Change Fails:**
- Check admin rights requirements
- Verify network adapter name
- Try different adapter names (Ethernet, Wi-Fi, etc.)

### **If Some Domains Still Don't Work:**
- Corporate firewall may be blocking at IP level
- Try different DNS providers
- Check if domains are blocked at firewall level

### **Performance Issues:**
- Too many DNS servers can slow resolution
- Stick to 2-4 DNS servers maximum
- Test performance with different configurations 