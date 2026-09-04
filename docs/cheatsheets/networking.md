# Networking Cheatsheet

Quick-reference networking commands and techniques for Linux, Windows, PowerShell, troubleshooting, reconnaissance and authorised penetration testing.

This cheatsheet focuses on practical network assessment:

```text
Local Host
    |
    v
Interfaces
    |
    v
IP / Subnet
    |
    v
Routes
    |
    v
DNS
    |
    v
ARP / Neighbours
    |
    v
Listening Services
    |
    v
Remote Connectivity
    |
    v
Service Enumeration
    |
    v
Traffic Analysis
    |
    v
Pivoting / Tunnelling
```

!!! warning "Authorised testing only"
    Use these commands only against systems and networks you own or are explicitly authorised to assess. Network scanning, service enumeration, packet capture and pivoting can affect production systems and may expose sensitive information.

---

# Quick Reference

## Linux

```bash
ip addr
ip route
ip neigh
ss -tulpn
cat /etc/resolv.conf
ping -c 4 10.10.10.10
traceroute 10.10.10.10
curl -I https://example.com
dig example.com
nc -vz 10.10.10.10 443
```

## Windows

```cmd
ipconfig /all
route print
arp -a
netstat -ano
nslookup example.com
ping 10.10.10.10
tracert 10.10.10.10
```

## PowerShell

```powershell
Get-NetIPConfiguration
Get-NetIPAddress
Get-NetRoute
Get-NetNeighbor
Get-DnsClientServerAddress
Get-NetTCPConnection
Get-NetUDPEndpoint
Resolve-DnsName example.com
Test-NetConnection example.com -Port 443
```

---

# OSI Model

```text
Layer 7 - Application
Layer 6 - Presentation
Layer 5 - Session
Layer 4 - Transport
Layer 3 - Network
Layer 2 - Data Link
Layer 1 - Physical
```

Common protocols:

| Layer | Examples |
|---|---|
| Application | HTTP, HTTPS, DNS, SMB, SSH, FTP, SMTP |
| Transport | TCP, UDP |
| Network | IPv4, IPv6, ICMP |
| Data Link | Ethernet, ARP |

For practical testing:

```text
Application
     |
     v
TCP / UDP
     |
     v
IP
     |
     v
Ethernet / Wi-Fi
```

---

# TCP/IP Model

```text
Application
    |
    v
Transport
    |
    v
Internet
    |
    v
Network Access
```

---

# IPv4

Example:

```text
192.168.1.25
```

IPv4 contains four octets:

```text
192 . 168 . 1 . 25
```

Each octet:

```text
0 - 255
```

---

# Private IPv4 Ranges

```text
10.0.0.0/8

172.16.0.0/12

192.168.0.0/16
```

Loopback:

```text
127.0.0.0/8
```

Common localhost address:

```text
127.0.0.1
```

Link-local:

```text
169.254.0.0/16
```

---

# CIDR

Examples:

```text
10.10.10.0/24
10.10.0.0/16
10.0.0.0/8
```

Common IPv4 prefixes:

| CIDR | Subnet Mask | Addresses |
|---:|---|---:|
| /8 | 255.0.0.0 | 16,777,216 |
| /16 | 255.255.0.0 | 65,536 |
| /20 | 255.255.240.0 | 4,096 |
| /22 | 255.255.252.0 | 1,024 |
| /23 | 255.255.254.0 | 512 |
| /24 | 255.255.255.0 | 256 |
| /25 | 255.255.255.128 | 128 |
| /26 | 255.255.255.192 | 64 |
| /27 | 255.255.255.224 | 32 |
| /28 | 255.255.255.240 | 16 |
| /29 | 255.255.255.248 | 8 |
| /30 | 255.255.255.252 | 4 |
| /32 | 255.255.255.255 | 1 |

Remember that traditional subnet calculations reserve the network and broadcast addresses where applicable.

---

# IPv6

Loopback:

```text
::1
```

Link-local:

```text
fe80::/10
```

Unique local:

```text
fc00::/7
```

Common global unicast space:

```text
2000::/3
```

---

# Linux - Interfaces

```bash
ip addr
```

Short:

```bash
ip a
```

Specific interface:

```bash
ip addr show eth0
```

Interfaces:

```bash
ip link
```

---

# Linux - IPv4 Addresses

```bash
ip -4 addr
```

---

# Linux - IPv6 Addresses

```bash
ip -6 addr
```

---

# Linux - Legacy ifconfig

```bash
ifconfig
```

All:

```bash
ifconfig -a
```

Prefer modern `ip` commands where available.

---

# Windows - Interfaces

```cmd
ipconfig
```

Detailed:

```cmd
ipconfig /all
```

---

# PowerShell - Interfaces

```powershell
Get-NetIPConfiguration
```

Addresses:

```powershell
Get-NetIPAddress
```

IPv4:

```powershell
Get-NetIPAddress -AddressFamily IPv4
```

IPv6:

```powershell
Get-NetIPAddress -AddressFamily IPv6
```

Adapters:

```powershell
Get-NetAdapter
```

---

# MAC Address

Linux:

```bash
ip link
```

Windows:

```cmd
getmac
```

PowerShell:

```powershell
Get-NetAdapter |
    Select-Object Name,MacAddress,Status
```

---

# Default Gateway

Linux:

```bash
ip route
```

Typical:

```text
default via 192.168.1.1 dev eth0
```

Windows:

```cmd
ipconfig
```

or:

```cmd
route print
```

PowerShell:

```powershell
Get-NetRoute -DestinationPrefix '0.0.0.0/0'
```

---

# Routing Table - Linux

```bash
ip route
```

IPv4:

```bash
ip -4 route
```

IPv6:

```bash
ip -6 route
```

Specific destination:

```bash
ip route get 10.10.10.10
```

This is useful for determining which interface and gateway Linux would use.

---

# Routing Table - Windows

```cmd
route print
```

IPv4:

```cmd
route print -4
```

IPv6:

```cmd
route print -6
```

PowerShell:

```powershell
Get-NetRoute
```

IPv4:

```powershell
Get-NetRoute -AddressFamily IPv4 |
    Sort-Object RouteMetric
```

---

# ARP - Linux

Modern:

```bash
ip neigh
```

Legacy:

```bash
arp -a
```

---

# ARP - Windows

```cmd
arp -a
```

PowerShell:

```powershell
Get-NetNeighbor
```

IPv4:

```powershell
Get-NetNeighbor -AddressFamily IPv4
```

---

# DNS Configuration - Linux

```bash
cat /etc/resolv.conf
```

systemd-resolved:

```bash
resolvectl status
```

---

# DNS Configuration - Windows

```cmd
ipconfig /all
```

PowerShell:

```powershell
Get-DnsClientServerAddress
```

IPv4:

```powershell
Get-DnsClientServerAddress -AddressFamily IPv4
```

---

# DNS Lookup

Linux:

```bash
dig example.com
```

Short:

```bash
dig +short example.com
```

Specific resolver:

```bash
dig @8.8.8.8 example.com
```

Windows:

```cmd
nslookup example.com
```

PowerShell:

```powershell
Resolve-DnsName example.com
```

---

# DNS Record Types

Common:

```text
A       IPv4 address
AAAA    IPv6 address
CNAME   Alias
MX      Mail server
NS      Name server
TXT     Text record
PTR     Reverse lookup
SOA     Zone authority information
SRV     Service location
CAA     Certificate authority policy
```

---

# Query A Record

```bash
dig A example.com
```

PowerShell:

```powershell
Resolve-DnsName example.com -Type A
```

---

# Query AAAA

```bash
dig AAAA example.com
```

---

# Query MX

```bash
dig MX example.com
```

PowerShell:

```powershell
Resolve-DnsName example.com -Type MX
```

---

# Query TXT

```bash
dig TXT example.com
```

PowerShell:

```powershell
Resolve-DnsName example.com -Type TXT
```

---

# Query NS

```bash
dig NS example.com
```

---

# Query SOA

```bash
dig SOA example.com
```

---

# Query SRV

```bash
dig SRV _ldap._tcp.example.local
```

Active Directory example:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

---

# Reverse DNS

```bash
dig -x 192.0.2.10
```

PowerShell:

```powershell
Resolve-DnsName 192.0.2.10 -Type PTR
```

---

# DNS Trace

```bash
dig +trace example.com
```

---

# DNS Zone Transfer

Authorised testing only:

```bash
dig AXFR example.com @ns1.example.com
```

A successful unauthorised zone transfer can expose:

```text
Hosts
Subdomains
Infrastructure
Mail Servers
Internal Naming
Service Records
```

Do not assume AXFR is permitted merely because a DNS server is reachable.

---

# Ping

Linux:

```bash
ping -c 4 10.10.10.10
```

Windows:

```cmd
ping 10.10.10.10
```

PowerShell:

```powershell
Test-Connection 10.10.10.10
```

ICMP failure does not prove a host is offline.

Firewalls commonly block ICMP.

---

# Traceroute

Linux:

```bash
traceroute 10.10.10.10
```

Windows:

```cmd
tracert 10.10.10.10
```

PowerShell:

```powershell
Test-NetConnection 10.10.10.10 -TraceRoute
```

---

# TCP Connectivity

Linux with Netcat:

```bash
nc -vz 10.10.10.10 443
```

PowerShell:

```powershell
Test-NetConnection 10.10.10.10 -Port 443
```

Boolean:

```powershell
Test-NetConnection 10.10.10.10 -Port 443 -InformationLevel Quiet
```

---

# Common Port Tests

HTTP:

```powershell
Test-NetConnection 10.10.10.10 -Port 80
```

HTTPS:

```powershell
Test-NetConnection 10.10.10.10 -Port 443
```

SSH:

```powershell
Test-NetConnection 10.10.10.10 -Port 22
```

SMB:

```powershell
Test-NetConnection 10.10.10.10 -Port 445
```

RDP:

```powershell
Test-NetConnection 10.10.10.10 -Port 3389
```

WinRM:

```powershell
Test-NetConnection 10.10.10.10 -Port 5985
```

WinRM TLS:

```powershell
Test-NetConnection 10.10.10.10 -Port 5986
```

---

# Common Ports

| Port | Protocol / Service |
|---:|---|
| 20 | FTP Data |
| 21 | FTP Control |
| 22 | SSH |
| 23 | Telnet |
| 25 | SMTP |
| 53 | DNS |
| 67 | DHCP Server |
| 68 | DHCP Client |
| 69 | TFTP |
| 80 | HTTP |
| 88 | Kerberos |
| 110 | POP3 |
| 111 | RPCbind |
| 123 | NTP |
| 135 | MS RPC Endpoint Mapper |
| 137 | NetBIOS Name Service |
| 138 | NetBIOS Datagram |
| 139 | NetBIOS Session |
| 143 | IMAP |
| 161 | SNMP |
| 162 | SNMP Trap |
| 389 | LDAP |
| 443 | HTTPS |
| 445 | SMB |
| 464 | Kerberos password change |
| 465 | SMTP over TLS |
| 500 | IKE |
| 514 | Syslog |
| 587 | SMTP Submission |
| 636 | LDAPS |
| 993 | IMAPS |
| 995 | POP3S |
| 1433 | Microsoft SQL Server |
| 1521 | Oracle |
| 2049 | NFS |
| 3268 | Active Directory Global Catalog |
| 3269 | Global Catalog over TLS |
| 3306 | MySQL |
| 3389 | RDP |
| 5432 | PostgreSQL |
| 5985 | WinRM HTTP |
| 5986 | WinRM HTTPS |
| 6379 | Redis |
| 8080 | Common alternate HTTP |
| 8443 | Common alternate HTTPS |

Ports identify transport endpoints, not guaranteed applications.

Always verify the actual service.

---

# TCP

TCP is connection-oriented.

Simplified handshake:

```text
Client                       Server

SYN ------------------------>

    <---------------- SYN/ACK

ACK ------------------------>

Connection Established
```

---

# TCP Flags

Common:

```text
SYN
ACK
FIN
RST
PSH
URG
```

---

# UDP

UDP is connectionless.

```text
Client
   |
   +-------- Datagram --------> Server
```

A lack of UDP response does not reliably mean the port is closed.

---

# Local Listening Ports - Linux

```bash
ss -tulpn
```

TCP:

```bash
ss -ltnp
```

UDP:

```bash
ss -lunp
```

All TCP connections:

```bash
ss -tanp
```

---

# netstat - Linux

If installed:

```bash
netstat -tulpn
```

Modern Linux systems generally prefer `ss`.

---

# Listening Ports - Windows

```cmd
netstat -ano
```

Listening only:

```cmd
netstat -ano | findstr LISTENING
```

PowerShell:

```powershell
Get-NetTCPConnection -State Listen
```

UDP:

```powershell
Get-NetUDPEndpoint
```

---

# Map Port to Process - Linux

```bash
ss -ltnp
```

Alternative:

```bash
sudo lsof -i
```

Specific port:

```bash
sudo lsof -i :443
```

---

# Map Port to Process - Windows

```cmd
netstat -ano
```

Then:

```cmd
tasklist /FI "PID eq 1234"
```

PowerShell:

```powershell
Get-Process -Id 1234
```

---

# HTTP with curl

GET:

```bash
curl https://example.com/
```

Headers:

```bash
curl -I https://example.com/
```

Verbose:

```bash
curl -v https://example.com/
```

Follow redirects:

```bash
curl -L https://example.com/
```

Save:

```bash
curl -o output.html https://example.com/
```

Custom header:

```bash
curl -H 'X-Test: value' https://example.com/
```

---

# HTTP Status Only

```bash
curl -s -o /dev/null -w '%{http_code}\n' https://example.com/
```

---

# HTTP Response Headers

```bash
curl -s -D - -o /dev/null https://example.com/
```

---

# HTTP Methods

OPTIONS:

```bash
curl -i -X OPTIONS https://example.com/
```

HEAD:

```bash
curl -I https://example.com/
```

Use potentially state-changing methods only where explicitly authorised.

---

# PowerShell HTTP

```powershell
Invoke-WebRequest -Uri 'https://example.com/'
```

Headers:

```powershell
$response = Invoke-WebRequest -Uri 'https://example.com/'
$response.Headers
```

Status:

```powershell
$response.StatusCode
```

---

# TLS Inspection

OpenSSL:

```bash
openssl s_client -connect example.com:443
```

With SNI:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

Certificate information:

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null |
    openssl x509 -noout -subject -issuer -dates
```

---

# TLS Certificate SANs

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null |
    openssl x509 -noout -ext subjectAltName
```

---

# TLS Certificate Fingerprint

```bash
openssl s_client -connect example.com:443 -servername example.com </dev/null 2>/dev/null |
    openssl x509 -noout -fingerprint -sha256
```

---

# OpenSSL Protocol Test

Example:

```bash
openssl s_client -connect example.com:443 -servername example.com -tls1_2
```

Do not infer full TLS security posture from a single successful connection.

---

# Netcat

TCP connection:

```bash
nc 10.10.10.10 80
```

Port test:

```bash
nc -vz 10.10.10.10 443
```

Range:

```bash
nc -vz 10.10.10.10 20-25
```

UDP:

```bash
nc -vzu 10.10.10.10 53
```

Netcat implementations differ between operating systems.

---

# Nmap

Host discovery:

```bash
nmap -sn 10.10.10.0/24
```

Basic TCP scan:

```bash
nmap 10.10.10.10
```

Specific ports:

```bash
nmap -p 22,80,443 10.10.10.10
```

All TCP ports:

```bash
nmap -p- 10.10.10.10
```

Service detection:

```bash
nmap -sV 10.10.10.10
```

Default scripts and service detection:

```bash
nmap -sC -sV 10.10.10.10
```

---

# Nmap - Save Output

Normal:

```bash
nmap -sV 10.10.10.10 -oN nmap.txt
```

XML:

```bash
nmap -sV 10.10.10.10 -oX nmap.xml
```

All common formats:

```bash
nmap -sV 10.10.10.10 -oA target
```

Creates:

```text
target.nmap
target.gnmap
target.xml
```

---

# Nmap - SYN Scan

Where privileges permit:

```bash
sudo nmap -sS 10.10.10.10
```

---

# Nmap - TCP Connect Scan

```bash
nmap -sT 10.10.10.10
```

---

# Nmap - UDP

```bash
sudo nmap -sU 10.10.10.10
```

Specific ports:

```bash
sudo nmap -sU -p 53,123,161 10.10.10.10
```

UDP scanning can be slow and results require careful interpretation.

---

# Nmap - No Ping

When host discovery is blocked:

```bash
nmap -Pn 10.10.10.10
```

---

# Nmap - Version Detection

```bash
nmap -sV 10.10.10.10
```

More aggressive version detection:

```bash
nmap -sV --version-all 10.10.10.10
```

---

# Nmap - OS Detection

```bash
sudo nmap -O 10.10.10.10
```

OS detection is probabilistic.

---

# Nmap - Useful Assessment Pattern

```bash
nmap -Pn -p- 10.10.10.10 -oA all-ports
```

Then targeted service enumeration:

```bash
nmap -Pn -sC -sV -p 22,80,443,445 10.10.10.10 -oA services
```

Adjust scan rate to the environment and rules of engagement.

---

# Nmap NSE

List scripts:

```bash
ls /usr/share/nmap/scripts/
```

Search:

```bash
ls /usr/share/nmap/scripts/ | grep smb
```

Help:

```bash
nmap --script-help smb2-security-mode
```

Use scripts selectively.

Some NSE scripts are intrusive.

---

# SMB Enumeration

Connectivity:

```bash
nc -vz 10.10.10.10 445
```

Nmap:

```bash
nmap -p 445 --script smb2-security-mode,smb2-time 10.10.10.10
```

SMB protocol information:

```bash
nmap -p 445 --script smb-protocols 10.10.10.10
```

Use the dedicated SMB, NetExec and Active Directory notes for deeper assessment.

---

# LDAP Connectivity

LDAP:

```bash
nc -vz 10.10.10.10 389
```

LDAPS:

```bash
nc -vz 10.10.10.10 636
```

Global Catalog:

```bash
nc -vz 10.10.10.10 3268
```

TLS Global Catalog:

```bash
nc -vz 10.10.10.10 3269
```

---

# Kerberos Connectivity

TCP:

```bash
nc -vz 10.10.10.10 88
```

UDP availability depends on the Netcat implementation and network behaviour.

---

# RDP

```bash
nc -vz 10.10.10.10 3389
```

Nmap:

```bash
nmap -p 3389 -sV 10.10.10.10
```

---

# WinRM

HTTP:

```bash
nc -vz 10.10.10.10 5985
```

HTTPS:

```bash
nc -vz 10.10.10.10 5986
```

---

# SSH

Banner:

```bash
nc 10.10.10.10 22
```

Client verbose:

```bash
ssh -v user@10.10.10.10
```

More verbose:

```bash
ssh -vvv user@10.10.10.10
```

Use verbose output carefully because it may contain usernames, key paths and environment information.

---

# SMTP

Connectivity:

```bash
nc -vz mail.example.com 25
```

TLS:

```bash
openssl s_client -starttls smtp -connect mail.example.com:25
```

---

# IMAP

TLS:

```bash
openssl s_client -connect mail.example.com:993
```

STARTTLS:

```bash
openssl s_client -starttls imap -connect mail.example.com:143
```

---

# POP3

TLS:

```bash
openssl s_client -connect mail.example.com:995
```

---

# FTP

```bash
ftp 10.10.10.10
```

Nmap:

```bash
nmap -p 21 -sV 10.10.10.10
```

FTP sends credentials in cleartext unless protected by an appropriate TLS configuration.

---

# SNMP

Common port:

```text
UDP 161
```

Basic version detection:

```bash
sudo nmap -sU -p 161 -sV 10.10.10.10
```

SNMP enumeration can disclose significant infrastructure information.

Use only where authorised.

---

# NFS

Common port:

```text
TCP/UDP 2049
```

List exports:

```bash
showmount -e 10.10.10.10
```

Nmap:

```bash
nmap -p 111,2049 10.10.10.10
```

---

# RPC

Linux RPC:

```bash
rpcinfo -p 10.10.10.10
```

Windows RPC Endpoint Mapper commonly uses:

```text
TCP 135
```

RPC services may then use dynamic ports.

---

# MSSQL

Default:

```text
TCP 1433
```

Test:

```bash
nc -vz 10.10.10.10 1433
```

---

# MySQL

Default:

```text
TCP 3306
```

```bash
nc -vz 10.10.10.10 3306
```

---

# PostgreSQL

Default:

```text
TCP 5432
```

```bash
nc -vz 10.10.10.10 5432
```

---

# Redis

Default:

```text
TCP 6379
```

```bash
nc -vz 10.10.10.10 6379
```

Do not assume a database is unauthenticated based only on port exposure.

---

# Proxy Discovery

Linux:

```bash
env | grep -i proxy
```

Windows:

```cmd
netsh winhttp show proxy
```

PowerShell:

```powershell
Get-ChildItem Env: |
    Where-Object Name -match 'proxy'
```

---

# Public IP

When Internet access is authorised:

```bash
curl https://ifconfig.me
```

IPv4:

```bash
curl -4 https://ifconfig.me
```

IPv6:

```bash
curl -6 https://ifconfig.me
```

Do not use external IP-check services from sensitive networks unless permitted.

---

# Linux Firewall

nftables:

```bash
sudo nft list ruleset
```

iptables:

```bash
sudo iptables -L -n -v
```

UFW:

```bash
sudo ufw status verbose
```

---

# Windows Firewall

```cmd
netsh advfirewall show allprofiles
```

PowerShell:

```powershell
Get-NetFirewallProfile
```

Rules:

```powershell
Get-NetFirewallRule
```

---

# Packet Capture - tcpdump

Interfaces:

```bash
tcpdump -D
```

Capture:

```bash
sudo tcpdump -i eth0
```

No name resolution:

```bash
sudo tcpdump -n -i eth0
```

Verbose:

```bash
sudo tcpdump -nn -i eth0
```

---

# tcpdump - Host Filter

```bash
sudo tcpdump -nn host 10.10.10.10
```

Source:

```bash
sudo tcpdump -nn src host 10.10.10.10
```

Destination:

```bash
sudo tcpdump -nn dst host 10.10.10.10
```

---

# tcpdump - Port Filter

```bash
sudo tcpdump -nn port 443
```

Source port:

```bash
sudo tcpdump -nn src port 443
```

Destination:

```bash
sudo tcpdump -nn dst port 443
```

---

# tcpdump - Protocol

TCP:

```bash
sudo tcpdump -nn tcp
```

UDP:

```bash
sudo tcpdump -nn udp
```

ICMP:

```bash
sudo tcpdump -nn icmp
```

---

# tcpdump - Multiple Conditions

HTTP or HTTPS:

```bash
sudo tcpdump -nn 'port 80 or port 443'
```

Host and port:

```bash
sudo tcpdump -nn 'host 10.10.10.10 and port 443'
```

---

# Save PCAP

```bash
sudo tcpdump -i eth0 -w capture.pcap
```

Read:

```bash
tcpdump -nn -r capture.pcap
```

PCAP files may contain:

```text
Credentials
Session Tokens
Internal Addresses
DNS Queries
Application Data
Personal Information
```

Treat them as sensitive evidence.

---

# tshark

Interfaces:

```bash
tshark -D
```

Capture:

```bash
sudo tshark -i eth0
```

Read PCAP:

```bash
tshark -r capture.pcap
```

Display filter:

```bash
tshark -r capture.pcap -Y 'http'
```

DNS:

```bash
tshark -r capture.pcap -Y 'dns'
```

---

# Wireshark Display Filters

IP:

```text
ip.addr == 10.10.10.10
```

Source:

```text
ip.src == 10.10.10.10
```

Destination:

```text
ip.dst == 10.10.10.10
```

TCP port:

```text
tcp.port == 443
```

HTTP:

```text
http
```

DNS:

```text
dns
```

SMB:

```text
smb2
```

Kerberos:

```text
kerberos
```

LDAP:

```text
ldap
```

TLS:

```text
tls
```

---

# Capture vs Display Filters

Important distinction:

```text
Capture Filter
     |
     +--> Determines what enters the PCAP

Display Filter
     |
     +--> Determines what Wireshark shows
```

Example capture filter:

```text
host 10.10.10.10 and port 443
```

Example Wireshark display filter:

```text
ip.addr == 10.10.10.10 && tcp.port == 443
```

---

# Network Discovery

A practical workflow:

```text
Interface
   |
   v
Local Address
   |
   v
Subnet
   |
   v
Gateway
   |
   v
Routes
   |
   v
Neighbours
   |
   v
Reachable Hosts
   |
   v
Open Ports
   |
   v
Services
```

---

# Passive Before Active

Where practical:

```text
Local Configuration
        |
        v
Routes
        |
        v
ARP / Neighbours
        |
        v
DNS
        |
        v
Existing Connections
        |
        v
Active Scanning
```

This can reduce unnecessary network traffic.

---

# Host Discovery

Authorised subnet:

```bash
nmap -sn 10.10.10.0/24
```

Remember:

```text
No Response
    !=
Host Offline
```

Host discovery can be affected by:

```text
Firewalls
ICMP Filtering
Network ACLs
Routing
Endpoint Security
```

---

# ARP Discovery

On the local Ethernet segment, ARP-based discovery can be useful.

If installed:

```bash
sudo arp-scan --localnet
```

Specific subnet:

```bash
sudo arp-scan 192.168.1.0/24
```

Only scan authorised networks.

---

# Service Enumeration Workflow

```text
Host
 |
 v
Open Port
 |
 v
Protocol
 |
 v
Service
 |
 v
Version
 |
 v
Configuration
 |
 v
Authentication
 |
 v
Security Controls
```

Do not jump directly from:

```text
Port 443 Open
```

to:

```text
HTTPS Application Vulnerable
```

---

# Network Segmentation

Test expected paths rather than indiscriminately scanning everything.

Example:

```text
Workstation
    |
    X
    |
Server Management Network
```

A useful segmentation test asks:

```text
Can Source A Reach Destination B
on Protocol C?
```

PowerShell:

```powershell
Test-NetConnection 10.20.30.40 -Port 445
```

Linux:

```bash
nc -vz 10.20.30.40 445
```

Record:

```text
Source
Destination
Protocol
Port
Expected Result
Actual Result
```

---

# Network Segmentation Matrix

Example:

| Source | Destination | Port | Expected | Actual |
|---|---|---:|---|---|
| User VLAN | DC | 445 | Allowed | Allowed |
| User VLAN | SQL Admin | 1433 | Blocked | Blocked |
| Guest VLAN | Internal Server | 443 | Blocked | Allowed |
| Server VLAN | Management | 5985 | Restricted | Allowed |

The matrix provides stronger evidence than an isolated connectivity test.

---

# Pivoting

Pivoting allows traffic to reach networks not directly accessible from the assessment host.

Concept:

```text
Attacker / Tester
       |
       v
Compromised or Authorised Pivot
       |
       v
Internal Network
       |
       v
Target
```

Use pivoting only where explicitly authorised.

---

# Routing vs Proxying

```text
Routing
   |
   +--> Network-layer path

Proxying
   |
   +--> Application/session forwarding

Port Forwarding
   |
   +--> Specific listener -> destination

SOCKS
   |
   +--> Dynamic application proxy
```

---

# SSH Local Port Forward

Authorised example:

```bash
ssh -L 8443:10.10.20.10:443 user@pivot.example.com
```

Flow:

```text
localhost:8443
      |
      v
SSH Tunnel
      |
      v
10.10.20.10:443
```

Then:

```bash
curl https://127.0.0.1:8443/
```

Certificate hostname mismatches may occur because the connection uses localhost.

---

# SSH Remote Port Forward

General form:

```bash
ssh -R REMOTE_PORT:DESTINATION:DESTINATION_PORT user@ssh-server
```

Example for a controlled lab service:

```bash
ssh -R 8080:127.0.0.1:8000 user@jump.example.com
```

Review SSH server forwarding policy before use.

---

# SSH Dynamic SOCKS Proxy

```bash
ssh -D 1080 user@pivot.example.com
```

This creates a local SOCKS proxy.

Concept:

```text
Application
    |
    v
127.0.0.1:1080
    |
    v
SSH
    |
    v
Pivot
    |
    v
Internal Destination
```

---

# ProxyChains

Configuration commonly resides at:

```text
/etc/proxychains4.conf
```

Example SOCKS entry:

```text
socks5 127.0.0.1 1080
```

Then, for tools that work correctly through the proxy:

```bash
proxychains4 curl http://10.10.20.10/
```

Not every protocol or scanning mode works reliably through SOCKS.

---

# Nmap Through Proxy

Full SYN scanning does not operate through a normal SOCKS proxy in the same way as direct raw-packet scanning.

For limited TCP connect testing:

```bash
proxychains4 nmap -sT -Pn -n -p 80,443 10.10.20.10
```

Expect limitations and slower performance.

---

# Chisel

Project:

[Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }

Chisel can transport connections over HTTP using an SSH-secured tunnel.

Typical assessment use cases include:

```text
Port Forwarding
SOCKS Proxying
Traversing Restricted Network Paths
```

Use the current project documentation for exact client/server syntax because options can change between versions.

---

# Ligolo-ng

Project:

[Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }

Ligolo-ng provides network tunnelling using a TUN-based approach.

Conceptually:

```text
Tester
  |
  v
Ligolo Proxy
  |
  v
Agent
  |
  v
Internal Network
```

A TUN approach can make many tools behave more naturally than application-level SOCKS proxying.

Use the project's current documentation for exact deployment and route configuration.

---

# socat

TCP listener forwarding to a controlled service:

```bash
socat TCP-LISTEN:8080,fork TCP:127.0.0.1:8000
```

Concept:

```text
:8080
  |
  v
socat
  |
  v
127.0.0.1:8000
```

Be careful about listener binding.

A listener exposed on all interfaces can unintentionally expose an internal service to other networks.

---

# SSH Tunnels - Security Considerations

Before creating a tunnel determine:

```text
Who Can Connect to the Listener?
Where Does It Forward?
Does It Cross a Segmentation Boundary?
Does It Expose an Internal Service?
Will It Persist?
How Will It Be Removed?
```

Prefer loopback listeners where remote access is unnecessary.

---

# Linux IP Forwarding

Check:

```bash
sysctl net.ipv4.ip_forward
```

or:

```bash
cat /proc/sys/net/ipv4/ip_forward
```

Do not enable forwarding on production systems merely for testing without explicit authorisation.

---

# Windows IP Forwarding

Inspect routing-related configuration rather than enabling forwarding by default.

Routing behaviour may also be provided by:

```text
RRAS
VPN Software
Hyper-V
Containers
Security Products
Third-Party Networking Software
```

---

# Network Namespaces - Linux

List:

```bash
ip netns list
```

Interfaces can also exist in:

```text
Containers
Network Namespaces
Virtual Machines
VPNs
```

so the default namespace may not show every relevant network path.

---

# VPN Interfaces

Linux:

```bash
ip addr
```

Look for interfaces such as:

```text
tun0
tap0
wg0
ppp0
```

Windows:

```powershell
Get-NetAdapter
```

---

# WireGuard

Linux:

```bash
wg show
```

Routes still matter:

```bash
ip route
```

---

# Docker Networking

Networks:

```bash
docker network ls
```

Inspect:

```bash
docker network inspect bridge
```

Container interfaces and routes can expose additional network paths.

Only query Docker where authorised and accessible.

---

# Kubernetes Networking

Basic context:

```bash
kubectl cluster-info
```

Services:

```bash
kubectl get services -A
```

Pods:

```bash
kubectl get pods -A -o wide
```

Network assessment of Kubernetes should use dedicated container/Kubernetes methodology rather than relying solely on host networking commands.

---

# Cloud Metadata Addresses

A commonly used link-local address is:

```text
169.254.169.254
```

Cloud providers use metadata services differently and modern deployments often require additional authentication or request controls.

Do not query metadata endpoints outside explicit scope.

---

# Loopback Services

Linux:

```bash
ss -ltnp
```

Look for:

```text
127.0.0.1
::1
```

Windows:

```powershell
Get-NetTCPConnection -State Listen |
    Where-Object {
        $_.LocalAddress -eq '127.0.0.1' -or
        $_.LocalAddress -eq '::1'
    }
```

A loopback-only service may still matter after obtaining authorised local access or through an approved tunnel.

---

# Binding Addresses

Important distinction:

```text
127.0.0.1:8080
```

means IPv4 loopback only.

```text
0.0.0.0:8080
```

generally means all IPv4 interfaces.

```text
[::]:8080
```

generally means all IPv6 interfaces and can have platform-specific dual-stack behaviour.

---

# Network Exposure Model

```text
Process
   |
   v
Socket
   |
   v
Bind Address
   |
   v
Firewall
   |
   v
Routing
   |
   v
Network ACL
   |
   v
Remote Client
```

An open local socket does not automatically mean it is remotely reachable.

---

# Proxy Awareness

When testing HTTP connectivity consider:

```text
Application Proxy
System Proxy
Environment Proxy
Transparent Proxy
Security Gateway
Direct Route
```

The path observed by `curl` may differ from the path used by another application.

---

# HTTP Proxy with curl

```bash
curl -x http://127.0.0.1:8080 https://example.com/
```

SOCKS5:

```bash
curl --socks5 127.0.0.1:1080 https://example.com/
```

SOCKS with proxy-side DNS resolution:

```bash
curl --socks5-hostname 127.0.0.1:1080 https://example.com/
```

The DNS distinction is important during pivoting.

---

# DNS Through a Proxy

A common mistake is:

```text
Application traffic -> Proxy
DNS lookup -> Local machine
```

This can:

```text
Fail to resolve internal names
Leak DNS queries
Produce misleading results
```

Use proxy-aware DNS resolution where supported.

---

# HTTPX

Project:

[httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

Probe hosts:

```bash
httpx -l hosts.txt
```

Useful information:

```bash
httpx -l hosts.txt -status-code -title -tech-detect
```

Save:

```bash
httpx -l hosts.txt -status-code -title -tech-detect -o alive.txt
```

Use only against authorised targets.

---

# Subdomain to Alive Host Workflow

```text
Subdomain Enumeration
        |
        v
DNS Resolution
        |
        v
HTTP Probe
        |
        v
Alive Web Services
```

Example:

```bash
subfinder -d example.com -silent > subdomains.txt
```

Then:

```bash
httpx -l subdomains.txt -silent -status-code -title -tech-detect -o alive.txt
```

This confirms responsive HTTP/HTTPS services, not whether the host itself is "alive" for every protocol.

---

# Nmap vs httpx

```text
Nmap
 |
 +--> Network ports
 +--> Service detection
 +--> TCP / UDP

httpx
 |
 +--> HTTP / HTTPS
 +--> Status
 +--> Titles
 +--> Web technologies
```

They complement rather than replace one another.

---

# Curl vs Test-NetConnection

```text
Test-NetConnection
       |
       +--> Can TCP connection be established?

curl / Invoke-WebRequest
       |
       +--> Does the application protocol work?
```

For example:

```powershell
Test-NetConnection example.com -Port 443
```

may succeed while:

```powershell
Invoke-WebRequest https://example.com/
```

fails because of:

```text
TLS
Proxy
HTTP Authentication
Application Behaviour
Certificate Validation
```

---

# Connectivity Troubleshooting

Use layers:

```text
Interface
   |
   v
Address
   |
   v
Route
   |
   v
DNS
   |
   v
TCP
   |
   v
TLS
   |
   v
Application
```

Example:

```bash
ip addr
ip route
dig example.com
nc -vz example.com 443
openssl s_client -connect example.com:443 -servername example.com
curl -v https://example.com/
```

---

# Windows Connectivity Troubleshooting

```powershell
Get-NetIPConfiguration
Get-NetRoute
Resolve-DnsName example.com
Test-NetConnection example.com -Port 443
Invoke-WebRequest https://example.com/
```

---

# Linux Connectivity Troubleshooting

```bash
ip addr
ip route
ip neigh
cat /etc/resolv.conf
dig example.com
ping -c 4 example.com
traceroute example.com
nc -vz example.com 443
curl -v https://example.com/
```

---

# Network Segmentation Testing Workflow

```text
Identify Source Zone
        |
        v
Identify Destination Zone
        |
        v
Define Expected Policy
        |
        v
Test Required Ports
        |
        v
Compare Expected vs Actual
        |
        v
Record Evidence
```

Avoid unnecessary full-port scans where the assessment objective can be answered with specific connectivity tests.

---

# Internal Network Enumeration

After obtaining authorised access to an internal host, start with local information:

Linux:

```bash
ip addr
ip route
ip neigh
ss -tulpn
cat /etc/resolv.conf
```

Windows:

```powershell
Get-NetIPConfiguration
Get-NetRoute
Get-NetNeighbor
Get-NetTCPConnection
Get-DnsClientServerAddress
```

This often reveals:

```text
Internal Subnets
Gateways
DNS Servers
Domain Controllers
Management Networks
VPN Networks
Local Services
Existing Connections
```

without immediately scanning the network.

---

# Existing Connections

Linux:

```bash
ss -tanp
```

Windows:

```powershell
Get-NetTCPConnection -State Established
```

Existing connections can reveal important infrastructure without generating new scan traffic.

---

# Network Shares

Windows:

```cmd
net use
```

PowerShell:

```powershell
Get-SmbMapping
```

Linux mounts:

```bash
mount
```

NFS:

```bash
mount -t nfs
```

Existing mounts can reveal trusted infrastructure.

---

# Hosts File

Linux:

```bash
cat /etc/hosts
```

Windows:

```powershell
Get-Content "$env:WINDIR\System32\drivers\etc\hosts"
```

Hosts-file entries may reveal:

```text
Internal Names
Development Systems
Legacy Infrastructure
Overrides
```

---

# Linux Network Configuration Files

Depending on distribution:

```text
/etc/network/interfaces
/etc/netplan/
/etc/NetworkManager/
/etc/systemd/network/
/etc/resolv.conf
```

Do not modify network configuration during enumeration.

---

# Windows Network Configuration

```powershell
Get-NetIPConfiguration
Get-NetAdapter
Get-NetIPAddress
Get-NetRoute
Get-DnsClientServerAddress
```

---

# Active Directory Networking

Important protocols commonly include:

| Port | Protocol |
|---:|---|
| 53 | DNS |
| 88 | Kerberos |
| 135 | RPC Endpoint Mapper |
| 389 | LDAP |
| 445 | SMB |
| 464 | Kerberos password change |
| 636 | LDAPS |
| 3268 | Global Catalog |
| 3269 | Global Catalog TLS |
| 5985 | WinRM HTTP |
| 5986 | WinRM HTTPS |

RPC also uses dynamic ports.

Do not assume AD communication is limited to this table.

---

# Domain Controller Discovery

Windows:

```cmd
nltest /dsgetdc:example.local
```

List:

```cmd
nltest /dclist:example.local
```

DNS:

```bash
dig SRV _ldap._tcp.dc._msdcs.example.local
```

Kerberos:

```bash
dig SRV _kerberos._tcp.example.local
```

---

# SMB Signing

Nmap:

```bash
nmap -p 445 --script smb2-security-mode 10.10.10.10
```

Signing configuration is especially important when assessing NTLM relay exposure.

See the dedicated Active Directory and SMB notes for deeper analysis.

---

# LDAP TLS

Test LDAPS:

```bash
openssl s_client -connect dc01.example.local:636 -servername dc01.example.local
```

LDAP StartTLS can be assessed using appropriate LDAP tooling.

Certificate presence alone does not prove that all LDAP clients are protected.

---

# Proxy Protocol Limitations

Not all protocols work through all proxies.

```text
SOCKS
 |
 +--> TCP applications generally work well
 |
 +--> UDP support depends on tool/proxy
 |
 +--> Raw packets generally do not work
 |
 +--> SYN scanning does not behave like direct scanning
```

Choose tooling based on the actual transport path.

---

# Network Performance

Linux interface statistics:

```bash
ip -s link
```

Socket summary:

```bash
ss -s
```

Windows adapter statistics:

```powershell
Get-NetAdapterStatistics
```

---

# Listening Service Review

Linux:

```bash
ss -ltnp
```

Windows:

```powershell
Get-NetTCPConnection -State Listen
```

For every unexpected listener determine:

```text
Process
   |
   v
Service
   |
   v
Bind Address
   |
   v
Firewall Exposure
   |
   v
Authentication
   |
   v
Business Requirement
```

---

# External Exposure vs Internal Exposure

```text
Listening on 0.0.0.0
        |
        v
Host Firewall
        |
        v
Network Firewall
        |
        v
NAT / Load Balancer
        |
        v
Internet
```

A service bound to all interfaces is not necessarily Internet exposed.

Validate the complete path.

---

# NAT

Concept:

```text
Private Host
    |
    v
NAT Gateway
    |
    v
Public Address
```

Common forms:

```text
SNAT
DNAT
PAT
```

NAT is not itself a security control equivalent to a firewall.

---

# Port Forwarding

Concept:

```text
Listener A
    |
    v
Forwarder
    |
    v
Destination B
```

Port forwarding can be legitimate:

```text
Load Balancing
Reverse Proxy
SSH Administration
Containers
Development
```

or security-sensitive when it crosses intended network boundaries.

---

# Reverse Proxy

Concept:

```text
Client
   |
   v
Reverse Proxy
   |
   +--> Application 1
   +--> Application 2
   +--> Application 3
```

Common technologies include:

```text
Nginx
Apache
HAProxy
Traefik
IIS ARR
Cloud Load Balancers
```

When testing a reverse proxy, distinguish proxy behaviour from backend behaviour.

---

# Forward Proxy

```text
Client
   |
   v
Forward Proxy
   |
   v
Internet / Destination
```

Forward proxies can enforce:

```text
Authentication
URL Filtering
TLS Inspection
Logging
Network Egress Policy
```

---

# Egress Testing

Define exactly what should be allowed.

Example:

```text
Endpoint
   |
   v
TCP 443
   |
   v
Approved Proxy
   |
   v
Internet
```

Testing should answer questions such as:

```text
Can the host connect directly?
Must it use the proxy?
Which ports are allowed?
Which destinations are allowed?
Is DNS restricted?
```

Avoid unnecessary external callbacks when a simple controlled connectivity test answers the question.

---

# HTTP Connectivity Test

Linux:

```bash
curl -I https://example.com/
```

Windows:

```powershell
Invoke-WebRequest -Uri 'https://example.com/' -Method Head
```

TCP-only:

```powershell
Test-NetConnection example.com -Port 443
```

These test different layers.

---

# Network Evidence

For every network finding record:

```text
Source Host
Source IP
Destination Host
Destination IP
Protocol
Port
Timestamp
Command
Result
Expected Policy
Actual Policy
```

---

# Example Segmentation Finding

Weak:

```text
Port 445 is open.
```

Better:

```text
A standard-user workstation in the User VLAN was able to
establish an SMB connection to TCP/445 on a server in the
restricted management network, despite the documented
segmentation policy requiring SMB traffic between these
zones to be blocked.
```

---

# Example Listener Finding

Weak:

```text
Port 8080 is listening.
```

Better:

```text
The administrative web service listens on 0.0.0.0:8080
and is reachable from the standard user network without
an intermediate access-control boundary.
```

Then validate authentication and business requirements before assigning severity.

---

# Example DNS Finding

Weak:

```text
DNS zone transfer works.
```

Better:

```text
The authoritative DNS server permitted an unauthenticated
AXFR request for the assessed zone from the testing network,
disclosing the zone's host and service records.
```

---

# Example Firewall Finding

Weak:

```text
Firewall allows traffic.
```

Better:

```text
The assessed endpoint was able to establish direct outbound
TCP/443 connections to Internet destinations despite the
documented requirement that Internet traffic traverse the
organisation's authenticated web proxy.
```

---

# Network Assessment Checklist

## Local Host

- [ ] Identify hostname
- [ ] Identify interfaces
- [ ] Identify IPv4 addresses
- [ ] Identify IPv6 addresses
- [ ] Identify MAC addresses
- [ ] Identify gateways
- [ ] Identify DNS servers
- [ ] Review routing table
- [ ] Review ARP / neighbours
- [ ] Review hosts file

## Local Services

- [ ] Enumerate TCP listeners
- [ ] Enumerate UDP listeners
- [ ] Map ports to processes
- [ ] Identify bind addresses
- [ ] Review host firewall
- [ ] Identify loopback-only services
- [ ] Identify unexpected exposed services

## Discovery

- [ ] Determine authorised ranges
- [ ] Perform passive discovery first
- [ ] Perform host discovery where required
- [ ] Resolve DNS
- [ ] Identify open ports
- [ ] Identify services
- [ ] Identify versions carefully
- [ ] Avoid unnecessary high-rate scanning

## DNS

- [ ] Identify resolvers
- [ ] Query A/AAAA
- [ ] Query MX
- [ ] Query NS
- [ ] Query TXT
- [ ] Query SRV where relevant
- [ ] Check reverse DNS
- [ ] Test zone transfer only where authorised

## Web

- [ ] HTTP
- [ ] HTTPS
- [ ] Redirects
- [ ] Headers
- [ ] TLS certificate
- [ ] SNI
- [ ] Proxy path
- [ ] HTTP technology probing where authorised

## Windows / AD

- [ ] DNS
- [ ] Kerberos
- [ ] LDAP
- [ ] LDAPS
- [ ] SMB
- [ ] RPC
- [ ] Global Catalog
- [ ] WinRM
- [ ] RDP where relevant
- [ ] SMB signing where relevant

## Segmentation

- [ ] Define source zone
- [ ] Define destination zone
- [ ] Define expected policy
- [ ] Test required protocols
- [ ] Record actual result
- [ ] Compare against architecture
- [ ] Avoid unnecessary broad scanning

## Traffic Analysis

- [ ] Identify correct interface
- [ ] Apply targeted capture filters
- [ ] Store PCAP securely
- [ ] Minimise sensitive-data collection
- [ ] Use display filters
- [ ] Remove captures when no longer required

## Pivoting

- [ ] Explicitly confirm pivoting is in scope
- [ ] Identify reachable subnet
- [ ] Choose routing/proxying/forwarding model
- [ ] Restrict listener exposure
- [ ] Record tunnel configuration
- [ ] Avoid persistence unless explicitly required
- [ ] Remove tunnel when testing is complete

## Evidence

- [ ] Record timestamp
- [ ] Record source
- [ ] Record destination
- [ ] Record protocol
- [ ] Record port
- [ ] Record exact command
- [ ] Capture relevant output
- [ ] Record expected behaviour
- [ ] Record actual behaviour
- [ ] Protect PCAPs and logs

---

# Quick Troubleshooting Checklist

When a service cannot be reached:

```text
1. Is the local interface up?
2. Does the host have the expected IP?
3. Is there a route?
4. Does DNS resolve correctly?
5. Is the destination reachable?
6. Is the TCP/UDP port reachable?
7. Is TLS working?
8. Is the application responding?
9. Is a proxy required?
10. Is a firewall or ACL blocking the path?
```

Linux:

```bash
ip addr
ip route
dig example.com
ping -c 4 example.com
nc -vz example.com 443
openssl s_client -connect example.com:443 -servername example.com
curl -v https://example.com/
```

Windows:

```powershell
Get-NetIPConfiguration
Get-NetRoute
Resolve-DnsName example.com
Test-Connection example.com
Test-NetConnection example.com -Port 443
Invoke-WebRequest https://example.com/
```

---

# Quick Pentest Workflow

```text
Scope
  |
  v
Local Network Context
  |
  v
Passive Discovery
  |
  v
Host Discovery
  |
  v
Port Discovery
  |
  v
Service Identification
  |
  v
Protocol Enumeration
  |
  v
Segmentation Testing
  |
  v
Application Testing
  |
  v
Evidence
```

Useful initial Linux commands:

```bash
ip addr
ip route
ip neigh
cat /etc/resolv.conf
ss -tulpn
```

Then, for an authorised target:

```bash
nmap -Pn -p- 10.10.10.10 -oA all-ports
```

Follow with targeted service enumeration:

```bash
nmap -Pn -sC -sV -p 22,80,443,445 10.10.10.10 -oA services
```

---

# Do Not Overreport

Do not automatically report:

```text
Port 445 Open
Port 3389 Open
WinRM Enabled
IPv6 Enabled
ICMP Allowed
DNS Reachable
Internal Route Exists
HTTP Service Uses Port 8080
Service Bound to 0.0.0.0
```

Instead determine:

```text
Is It Reachable?
      |
      v
From Where?
      |
      v
Should It Be Reachable?
      |
      v
What Authentication Exists?
      |
      v
What Security Boundary Is Affected?
```

---

# Safe Validation Model

Prefer:

```text
Read Local Configuration
        |
        v
Review Existing Connections
        |
        v
Test Specific Connectivity
        |
        v
Enumerate Required Service
        |
        v
Document Result
```

before:

```text
Broad Scanning
High-Rate Scanning
Intrusive NSE Scripts
Protocol Mutation
Service Exploitation
Network Reconfiguration
```

---

# Network Testing Model

A network finding generally involves more than an open port.

```text
Source
  |
  v
Route
  |
  v
Firewall / ACL
  |
  v
Destination
  |
  v
Service
  |
  v
Authentication
  |
  v
Application
```

For segmentation:

```text
Source Zone
    |
    v
Expected Restriction
    |
    v
Unexpected Reachability
    |
    v
Security Impact
```

For exposed services:

```text
Service
   |
   v
Bind Address
   |
   v
Firewall
   |
   v
Reachability
   |
   v
Authentication
   |
   v
Impact
```

For pivoting:

```text
Tester
   |
   v
Authorised Pivot
   |
   v
Previously Unreachable Network
   |
   v
Approved Target
```

The key distinction is:

```text
Network Reachability
       !=
Vulnerability
```

Reachability becomes security-relevant when it violates the intended network or trust boundary.

---

# References

## InternalAllTheThings

[InternalAllTheThings](https://swisskyrepo.github.io/InternalAllTheThings/){ target="_blank" rel="noopener noreferrer" }

Useful reference for internal network discovery, protocol enumeration, Active Directory assessment, pivoting and red-team network techniques.

---

## Nmap

[Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }

[Nmap Network Scanning](https://nmap.org/book/){ target="_blank" rel="noopener noreferrer" }

[Nmap NSE Documentation](https://nmap.org/nsedoc/){ target="_blank" rel="noopener noreferrer" }

---

## ProjectDiscovery httpx

[ProjectDiscovery httpx](https://github.com/projectdiscovery/httpx){ target="_blank" rel="noopener noreferrer" }

---

## Wireshark

[Wireshark Documentation](https://www.wireshark.org/docs/){ target="_blank" rel="noopener noreferrer" }

[Wireshark Display Filters](https://www.wireshark.org/docs/man-pages/wireshark-filter.html){ target="_blank" rel="noopener noreferrer" }

---

## tcpdump

[tcpdump Documentation](https://www.tcpdump.org/manpages/tcpdump.1.html){ target="_blank" rel="noopener noreferrer" }

---

## OpenSSL

[OpenSSL Documentation](https://docs.openssl.org/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft Networking

[Microsoft Learn - Windows Networking](https://learn.microsoft.com/en-us/windows-server/networking/){ target="_blank" rel="noopener noreferrer" }

---

## PowerShell Networking

[Microsoft Learn - NetTCPIP Module](https://learn.microsoft.com/en-us/powershell/module/nettcpip/){ target="_blank" rel="noopener noreferrer" }

[Microsoft Learn - Test-NetConnection](https://learn.microsoft.com/en-us/powershell/module/nettcpip/test-netconnection){ target="_blank" rel="noopener noreferrer" }

---

## Chisel

[Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }

---

## Ligolo-ng

[Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

For local network awareness:

```bash
ip addr
ip route
ip neigh
ss -tulpn
cat /etc/resolv.conf
```

On Windows:

```powershell
Get-NetIPConfiguration
Get-NetRoute
Get-NetNeighbor
Get-NetTCPConnection -State Listen
Get-DnsClientServerAddress
```

For connectivity:

```text
DNS
 |
 v
Route
 |
 v
TCP / UDP
 |
 v
TLS
 |
 v
Application
```

Test each layer independently.

For discovery:

```text
Host
 |
 v
Port
 |
 v
Protocol
 |
 v
Service
 |
 v
Configuration
 |
 v
Security Boundary
```

For internal assessments, begin with information already available from the host before generating additional network traffic.

For segmentation assessments:

```text
Expected
   |
   v
Test
   |
   v
Actual
   |
   v
Difference
   |
   v
Impact
```

For pivoting:

```text
Reachability
    |
    v
Authorised Pivot
    |
    v
Controlled Tunnel
    |
    v
Approved Destination
    |
    v
Cleanup
```

The goal is not simply to discover as many open ports as possible.

The goal is to understand:

```text
What can communicate?
Why can it communicate?
Should it communicate?
What security boundary exists?
Can that boundary be crossed?
```

That turns basic network enumeration into meaningful security assessment.
