---
title: Wireshark and tshark Cheatsheet
description: Practical Wireshark and tshark reference for authorised security assessments covering packet capture, display filters, capture filters, TCP, UDP, DNS, HTTP, TLS, SMB, Kerberos, LDAP, authentication, traffic analysis, evidence collection and troubleshooting.
---

# Wireshark and tshark Cheatsheet

Wireshark and `tshark` provide packet-level visibility into network communications.

They are useful when you need to answer questions such as:

```text
Did the connection reach the target?

Which protocol is actually being used?

What DNS queries were generated?

Did the server respond?

Was the TCP handshake completed?

Was the connection reset?

Was HTTP redirected?

Which TLS certificate was presented?

Which SMB dialect was negotiated?

Which Kerberos messages were exchanged?

Is authentication repeatedly failing?

Is traffic leaving through the expected interface?

What actually happened on the wire?
```

Wireshark provides the graphical interface.

`tshark` provides command-line packet capture and analysis using Wireshark's protocol dissectors.

A practical workflow is:

```text
Define Question
      |
      v
Choose Capture Point
      |
      v
Select Interface
      |
      v
Start Focused Capture
      |
      v
Reproduce Activity
      |
      v
Stop Capture
      |
      v
Apply Display Filters
      |
      v
Follow Conversation
      |
      v
Interpret Packets
      |
      v
Correlate With Host/Application Logs
      |
      v
Capture Evidence
```

!!! warning "Authorised Security Testing"

    Capture network traffic only where you are authorised to do so. Packet captures can contain credentials, authentication material, cookies, tokens, personal information, internal hostnames and other sensitive data. Treat PCAP files as sensitive assessment evidence.


# Quick Start

List interfaces with tshark:

```bash
tshark -D
```

Capture on an interface:

```bash
sudo tshark -i eth0
```

Capture to file:

```bash
sudo tshark -i eth0 -w capture.pcapng
```

Read capture:

```bash
tshark -r capture.pcapng
```

Filter DNS:

```bash
tshark -r capture.pcapng -Y 'dns'
```

Filter HTTP:

```bash
tshark -r capture.pcapng -Y 'http'
```

Filter TLS:

```bash
tshark -r capture.pcapng -Y 'tls'
```

Filter one IP:

```bash
tshark -r capture.pcapng -Y 'ip.addr == 192.168.1.10'
```

Filter TCP port:

```bash
tshark -r capture.pcapng -Y 'tcp.port == 443'
```

Extract selected fields:

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -e frame.time \
  -e ip.src \
  -e dns.qry.name
```


# Installation

Kali/Debian:

```bash
sudo apt update
sudo apt install wireshark tshark
```

Check Wireshark:

```bash
wireshark --version
```

Check tshark:

```bash
tshark --version
```

Locate:

```bash
which wireshark
```

```bash
which tshark
```


# Start Wireshark

```bash
wireshark
```

When using a graphical Kali environment:

```text
Applications
    |
    v
Sniffing & Spoofing
    |
    v
Wireshark
```

The exact desktop menu structure may vary.


# tshark Help

```bash
tshark -h
```

Manual:

```bash
man tshark
```


# Interfaces

Before capturing, identify the correct interface.

Linux:

```bash
ip addr
```

Routes:

```bash
ip route
```

tshark interfaces:

```bash
tshark -D
```

Representative output:

```text
1. eth0
2. lo
3. tun0
```

During a VPN-based assessment, traffic may traverse:

```text
tun0
```

instead of:

```text
eth0
```

Always confirm the actual route.


# Determine Interface for a Target

```bash
ip route get 192.168.1.10
```

Representative output:

```text
192.168.1.10 dev tun0 src 10.10.14.20
```

Interpretation:

```text
Traffic to 192.168.1.10 is expected to leave through tun0.
```

This is useful before starting a packet capture.


# Capture With Wireshark

Select the relevant interface and start the capture.

Typical workflow:

```text
Select Interface
      |
      v
Start Capture
      |
      v
Reproduce Test
      |
      v
Stop Capture
      |
      v
Apply Display Filter
      |
      v
Inspect Conversation
```


# Capture With tshark

Basic:

```bash
sudo tshark -i eth0
```

Specific interface:

```bash
sudo tshark -i tun0
```

Write directly to file:

```bash
sudo tshark -i tun0 -w assessment.pcapng
```


# Capture a Limited Number of Packets

```bash
sudo tshark -i eth0 -c 100
```

Write 100 packets:

```bash
sudo tshark -i eth0 -c 100 -w capture.pcapng
```


# Capture for a Fixed Duration

Capture for 60 seconds:

```bash
sudo tshark -i eth0 -a duration:60 -w capture.pcapng
```


# Capture File Size Limit

Example:

```bash
sudo tshark -i eth0 -a filesize:100000 -w capture.pcapng
```

Review local tshark help for the units and behaviour supported by the installed version.


# Capture Filters vs Display Filters

This distinction is extremely important.

```text
CAPTURE FILTER
     |
     v
Controls what is recorded

DISPLAY FILTER
     |
     v
Controls what recorded traffic is displayed
```


# Capture Filter

Capture filters use BPF-style syntax.

Example:

```bash
sudo tshark -i eth0 -f 'host 192.168.1.10'
```

Only matching traffic is captured.


# Display Filter

Display filters use Wireshark syntax.

Example:

```bash
tshark -r capture.pcapng -Y 'ip.addr == 192.168.1.10'
```

The entire capture remains intact, but only matching packets are displayed.


# Why the Difference Matters

If you use an overly restrictive capture filter:

```text
Uncaptured traffic is gone.
```

If you use a display filter:

```text
Other packets remain available in the PCAP.
```

For investigative work, a broader capture followed by focused display filtering is often safer when storage and privacy constraints permit.


# Common Capture Filters

Single host:

```text
host 192.168.1.10
```

Source host:

```text
src host 192.168.1.10
```

Destination host:

```text
dst host 192.168.1.10
```

TCP:

```text
tcp
```

UDP:

```text
udp
```

Port:

```text
port 443
```

TCP port:

```text
tcp port 443
```

UDP port:

```text
udp port 53
```

Network:

```text
net 192.168.1.0/24
```


# Combine Capture Filters

Host and port:

```text
host 192.168.1.10 and port 443
```

HTTP or HTTPS:

```text
tcp port 80 or tcp port 443
```

Exclude SSH management traffic:

```text
not port 22
```

Example:

```bash
sudo tshark -i eth0 -f 'host 192.168.1.10 and not port 22'
```


# Common Display Filters

IPv4:

```text
ip
```

IPv6:

```text
ipv6
```

TCP:

```text
tcp
```

UDP:

```text
udp
```

DNS:

```text
dns
```

HTTP:

```text
http
```

TLS:

```text
tls
```

SMB:

```text
smb
```

SMB2/3:

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

ICMP:

```text
icmp
```


# Filter by IP

Either source or destination:

```text
ip.addr == 192.168.1.10
```

Source:

```text
ip.src == 192.168.1.10
```

Destination:

```text
ip.dst == 192.168.1.10
```


# Filter by TCP Port

```text
tcp.port == 443
```

Source:

```text
tcp.srcport == 443
```

Destination:

```text
tcp.dstport == 443
```


# Filter by UDP Port

```text
udp.port == 53
```


# Combine Display Filters

AND:

```text
ip.addr == 192.168.1.10 && tcp.port == 443
```

OR:

```text
tcp.port == 80 || tcp.port == 443
```

NOT:

```text
!(tcp.port == 22)
```


# TCP Analysis

TCP analysis is one of the most valuable uses of Wireshark.


# TCP Handshake

Normal handshake:

```text
Client                         Server
  |                              |
  | -------- SYN -------------> |
  |                              |
  | <------ SYN/ACK ------------ |
  |                              |
  | -------- ACK -------------> |
  |                              |
  |       Connection Ready       |
```


# SYN Filter

```text
tcp.flags.syn == 1
```


# Initial SYN Without ACK

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

Useful for identifying connection attempts.


# SYN/ACK

```text
tcp.flags.syn == 1 && tcp.flags.ack == 1
```


# Reset

```text
tcp.flags.reset == 1
```

A reset may indicate:

```text
Closed port

Application rejection

Connection termination

Firewall behaviour

Protocol mismatch
```

Context matters.


# FIN

```text
tcp.flags.fin == 1
```


# TCP Retransmissions

```text
tcp.analysis.retransmission
```

Retransmissions can result from:

```text
Packet loss

Congestion

Delayed responses

Network path problems

Capture artefacts
```

Do not automatically interpret retransmissions as a security issue.


# Duplicate ACK

```text
tcp.analysis.duplicate_ack
```


# Lost Segment

```text
tcp.analysis.lost_segment
```

Remember that a capture taken at only one network position may itself miss packets.


# TCP Stream

A TCP stream represents a conversation.

Wireshark:

```text
Right-click packet
    |
    v
Follow
    |
    v
TCP Stream
```

This can reconstruct application traffic where the protocol is not encrypted.


# Filter a TCP Stream

```text
tcp.stream == 5
```

The stream number depends on the capture.


# tshark TCP Stream

List stream values:

```bash
tshark -r capture.pcapng \
  -T fields \
  -e tcp.stream | sort -n | uniq
```

Follow a selected stream:

```bash
tshark -r capture.pcapng -q -z follow,tcp,ascii,0
```


# Connection Troubleshooting

Suppose:

```text
Client -> SYN -> Server
```

but no SYN/ACK returns.

Possible explanations:

```text
Firewall silently dropping traffic

Target offline

Routing problem

Packet lost

Capture point cannot see return traffic
```

Do not conclude:

```text
Port is closed.
```

A closed TCP port often produces a reset, while silent filtering may produce no response.


# DNS Analysis

Display DNS:

```text
dns
```


# DNS Queries

```text
dns.flags.response == 0
```


# DNS Responses

```text
dns.flags.response == 1
```


# Query Name

```text
dns.qry.name
```

Example filter:

```text
dns.qry.name == "example.com"
```


# Query Contains Text

```text
dns.qry.name contains "example"
```


# A Record Queries

```text
dns.qry.type == 1
```


# AAAA Queries

```text
dns.qry.type == 28
```


# DNS Response Code

```text
dns.flags.rcode
```


# NXDOMAIN

```text
dns.flags.rcode == 3
```

This can help identify failed hostname resolution.


# Extract DNS Queries With tshark

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -e frame.time \
  -e ip.src \
  -e dns.qry.name
```


# Unique DNS Queries

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -e dns.qry.name | sort -u
```


# DNS Troubleshooting Workflow

```text
Application Request
       |
       v
DNS Query Generated?
      / \
    No   Yes
    |     |
    v     v
Client   DNS Response?
Issue      / \
         No   Yes
         |     |
         v     v
      Network  Correct IP?
      / DNS      / \
                No  Yes
                |    |
                v    v
              DNS   Continue
             Issue  Connection
```


# HTTP Analysis

Display:

```text
http
```

Requests:

```text
http.request
```

Responses:

```text
http.response
```


# HTTP Request Method

```text
http.request.method
```

GET:

```text
http.request.method == "GET"
```

POST:

```text
http.request.method == "POST"
```


# HTTP Host

```text
http.host
```

Example:

```text
http.host == "example.com"
```


# HTTP URI

```text
http.request.uri
```

Contains:

```text
http.request.uri contains "/api/"
```


# HTTP Status

```text
http.response.code
```

Example:

```text
http.response.code == 403
```


# HTTP Error Responses

```text
http.response.code >= 400
```

This can quickly identify:

```text
400

401

403

404

429

500
```

responses in unencrypted HTTP traffic.


# Extract HTTP Requests

```bash
tshark -r capture.pcapng \
  -Y 'http.request' \
  -T fields \
  -e frame.time \
  -e ip.src \
  -e http.request.method \
  -e http.host \
  -e http.request.uri
```


# HTTP Credentials

Unencrypted HTTP traffic may expose:

```text
Cookies

Authorization headers

Form data

Tokens

Application data
```

Treat packet captures containing these values as highly sensitive.


# HTTPS

For HTTPS:

```text
Application Data
      |
      v
TLS Encryption
      |
      v
TCP
      |
      v
Network
```

Without decryption material, Wireshark normally cannot display the encrypted HTTP payload.


# TLS Filter

```text
tls
```


# TLS Handshake

```text
tls.handshake
```


# Client Hello

```text
tls.handshake.type == 1
```


# Server Hello

```text
tls.handshake.type == 2
```


# TLS Handshake Model

```text
Client                         Server
  |                              |
  | ------ ClientHello --------> |
  |                              |
  | <------ ServerHello -------- |
  |                              |
  | <----- Certificate ---------- |
  |                              |
  |       Key Establishment       |
  |                              |
  | ===== Encrypted Data =======> |
```


# TLS Server Name

Depending on protocol version and capture conditions, SNI can be visible in the ClientHello.

Useful filter:

```text
tls.handshake.extensions_server_name
```

Example:

```text
tls.handshake.extensions_server_name == "example.com"
```


# Extract TLS SNI

```bash
tshark -r capture.pcapng \
  -Y 'tls.handshake.extensions_server_name' \
  -T fields \
  -e ip.dst \
  -e tls.handshake.extensions_server_name
```


# TLS Certificate Information

Wireshark can dissect certificates exchanged during appropriate TLS handshakes.

For certificate-focused CLI validation, also use:

```bash
openssl s_client -connect example.com:443 -servername example.com
```

and the [curl Cheatsheet](curl.md).


# TLS Failure Analysis

A failed TLS connection may involve:

```text
Protocol mismatch

Certificate problem

Cipher incompatibility

Client authentication requirement

Application gateway

Connection reset

TLS alert
```


# TLS Alerts

Filter:

```text
tls.alert_message
```

An alert provides useful protocol evidence but must be interpreted in context.


# SMB Analysis

SMB2 and SMB3 traffic is commonly displayed using:

```text
smb2
```


# SMB Ports

Common:

```text
TCP/445
```

Legacy NetBIOS-based SMB may involve:

```text
TCP/139
```


# Filter SMB to a Host

```text
smb2 && ip.addr == 192.168.1.10
```


# SMB Commands

Wireshark can display SMB command types and responses.

This can help investigate:

```text
Session setup

Tree connections

File access

Authentication

Protocol negotiation
```


# SMB Negotiation

A typical sequence:

```text
Client
  |
  v
SMB Negotiate Request
  |
  v
Server
  |
  v
SMB Negotiate Response
  |
  v
Session Setup
```


# SMB Interpretation

Seeing:

```text
TCP/445

SMB negotiation
```

supports:

```text
SMB communication occurred.
```

It does not automatically prove:

```text
Anonymous access

Administrative access

Signing weakness

Credential compromise
```


# SMB Signing

Protocol negotiation may provide information relevant to SMB signing.

For focused security validation, combine packet analysis with tools such as:

```text
NetExec

Nmap

smbclient
```

See the [NetExec Cheatsheet](netexec.md).


# Kerberos Analysis

Display:

```text
kerberos
```

Kerberos traffic commonly uses:

```text
TCP/88

UDP/88
```


# Kerberos High-Level Flow

```text
Client
  |
  | AS-REQ
  v
KDC
  |
  | AS-REP
  v
Client
  |
  | TGS-REQ
  v
KDC
  |
  | TGS-REP
  v
Client
  |
  v
Service
```


# Kerberos Message Types

Wireshark can distinguish messages such as:

```text
AS-REQ

AS-REP

TGS-REQ

TGS-REP

KRB-ERROR
```


# Kerberos Errors

Filter:

```text
kerberos.error_code
```

Errors can help investigate:

```text
Authentication failures

Clock problems

Principal problems

Ticket issues

Encryption compatibility
```

Do not interpret an error code without understanding the Kerberos exchange around it.


# Active Directory Authentication Troubleshooting

A useful sequence:

```text
DNS
 |
 v
Domain Controller Discovery
 |
 v
Kerberos
 |
 v
LDAP / SMB
 |
 v
Application Protocol
```

If domain authentication fails, packet capture can help identify where the process stopped.


# LDAP Analysis

Display:

```text
ldap
```

Common ports:

```text
389/tcp

636/tcp

3268/tcp

3269/tcp
```


# LDAP vs LDAPS

Conceptually:

```text
LDAP
 |
 +--> TCP/389
 |
 +--> May use StartTLS

LDAPS
 |
 +--> TLS-protected LDAP
 |
 +--> Commonly TCP/636
```

Do not assume encryption solely from the port number. Validate the observed protocol.


# LDAP Operations

Wireshark may expose operations such as:

```text
Bind

Search

Search Result

Modify

Unbind
```

when traffic is not protected by TLS or another mechanism that prevents payload inspection.


# NTLM

NTLM authentication may appear inside protocols such as:

```text
SMB

HTTP

LDAP

RPC
```

Wireshark may dissect relevant NTLMSSP messages.


# NTLMSSP Filter

A commonly useful display filter is:

```text
ntlmssp
```


# NTLM Authentication Flow

High level:

```text
Client                     Server
  |                           |
  | ---- Negotiate ---------> |
  |                           |
  | <--- Challenge ---------- |
  |                           |
  | ---- Authenticate ------> |
```


# Security Interpretation

Seeing NTLM authentication establishes:

```text
NTLM was involved in the observed authentication exchange.
```

It does not automatically establish:

```text
NTLM relay is possible.

Credentials were compromised.

SMB signing is disabled.

The authentication is vulnerable.
```

Those require additional context and validation.


# ICMP

Filter:

```text
icmp
```

Echo request:

```text
icmp.type == 8
```

Echo reply:

```text
icmp.type == 0
```


# ICMP Destination Unreachable

```text
icmp.type == 3
```

This can provide useful information during UDP and routing troubleshooting.


# ARP

Filter:

```text
arp
```

ARP is useful for understanding local-layer communication.


# ARP Request

Typical:

```text
Who has 192.168.1.10?
```

Response:

```text
192.168.1.10 is at <MAC>
```


# ARP Analysis

ARP can help answer:

```text
Is the target local?

Is address resolution working?

Which MAC address responded?

Is there unexpected ARP behaviour?
```


# DHCP

Filter:

```text
dhcp
```

Depending on Wireshark version/dissector naming, BOOTP-related fields may also appear.

Typical DHCP flow:

```text
Discover
   |
   v
Offer
   |
   v
Request
   |
   v
ACK
```


# SSH

SSH traffic:

```text
tcp.port == 22
```

SSH payload is encrypted after protocol negotiation.

You can still inspect:

```text
Connection establishment

Endpoints

Timing

Packet sizes

Connection termination
```

but not normal encrypted session content.


# RDP

Common filter:

```text
tcp.port == 3389
```

Packet analysis can help determine:

```text
Was TCP established?

Did TLS negotiation begin?

Was the connection reset?

Did the target respond?
```

Application-level authentication may require additional tooling and logs.


# WinRM

HTTP WinRM commonly uses:

```text
5985/tcp
```

HTTPS WinRM commonly uses:

```text
5986/tcp
```

Filter:

```text
tcp.port == 5985 || tcp.port == 5986
```

For unencrypted HTTP-level traffic where applicable:

```text
http && tcp.port == 5985
```


# MSSQL

Common:

```text
tcp.port == 1433
```

SQL Server may also use dynamic ports, so use actual observed traffic rather than relying only on standard port numbers.


# PostgreSQL

```text
tcp.port == 5432
```


# MySQL

```text
tcp.port == 3306
```


# Redis

```text
tcp.port == 6379
```


# NFS

Commonly associated with:

```text
2049/tcp

2049/udp
```

Filter:

```text
tcp.port == 2049 || udp.port == 2049
```


# Follow Conversations

One of Wireshark's most useful features is reconstructing conversations.

Possible follow options include:

```text
TCP Stream

UDP Stream

HTTP Stream
```

depending on the selected packet and protocol.


# Follow TCP Stream

Wireshark:

```text
Right-click
    |
    v
Follow
    |
    v
TCP Stream
```

This isolates the conversation.


# Stream Filter

After selecting a stream, Wireshark applies a filter similar to:

```text
tcp.stream eq 0
```


# Conversation Statistics

Wireshark:

```text
Statistics
    |
    v
Conversations
```

Useful views include:

```text
Ethernet

IPv4

IPv6

TCP

UDP
```


# Endpoints

Wireshark:

```text
Statistics
    |
    v
Endpoints
```

This helps identify:

```text
Active IP addresses

MAC addresses

Conversation volume
```


# Protocol Hierarchy

Wireshark:

```text
Statistics
    |
    v
Protocol Hierarchy
```

Useful for quickly understanding the protocols present in a capture.


# Expert Information

Wireshark:

```text
Analyze
    |
    v
Expert Information
```

This can highlight:

```text
Warnings

Errors

Retransmissions

Protocol anomalies
```

Expert Information is a diagnostic aid, not an automatic vulnerability scanner.


# tshark Protocol Hierarchy

```bash
tshark -r capture.pcapng -q -z io,phs
```


# tshark Conversations

TCP:

```bash
tshark -r capture.pcapng -q -z conv,tcp
```

UDP:

```bash
tshark -r capture.pcapng -q -z conv,udp
```

IP:

```bash
tshark -r capture.pcapng -q -z conv,ip
```


# tshark Endpoints

IPv4:

```bash
tshark -r capture.pcapng -q -z endpoints,ip
```

TCP:

```bash
tshark -r capture.pcapng -q -z endpoints,tcp
```


# Extract Fields

`tshark` becomes particularly powerful when extracting structured fields.

General model:

```bash
tshark -r capture.pcapng \
  -Y '<filter>' \
  -T fields \
  -e <field1> \
  -e <field2>
```


# Extract Source and Destination

```bash
tshark -r capture.pcapng \
  -T fields \
  -e frame.number \
  -e ip.src \
  -e ip.dst
```


# Extract TCP Connections

```bash
tshark -r capture.pcapng \
  -Y 'tcp' \
  -T fields \
  -e frame.time \
  -e ip.src \
  -e tcp.srcport \
  -e ip.dst \
  -e tcp.dstport
```


# Extract HTTP Requests

```bash
tshark -r capture.pcapng \
  -Y 'http.request' \
  -T fields \
  -e ip.src \
  -e http.request.method \
  -e http.host \
  -e http.request.uri
```


# Extract DNS

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -e ip.src \
  -e dns.qry.name
```


# Extract TLS SNI

```bash
tshark -r capture.pcapng \
  -Y 'tls.handshake.extensions_server_name' \
  -T fields \
  -e ip.src \
  -e ip.dst \
  -e tls.handshake.extensions_server_name
```


# CSV-Style Output

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -E separator=, \
  -E quote=d \
  -e frame.time \
  -e ip.src \
  -e dns.qry.name
```

Redirect:

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -E separator=, \
  -E quote=d \
  -e frame.time \
  -e ip.src \
  -e dns.qry.name > dns.csv
```


# JSON Output

For automation:

```bash
tshark -r capture.pcapng -T json > capture.json
```

Be aware that large captures can produce very large JSON files.


# Packet Timestamps

Display frame time:

```text
frame.time
```

Epoch:

```text
frame.time_epoch
```

Example:

```bash
tshark -r capture.pcapng \
  -T fields \
  -e frame.time_epoch \
  -e ip.src \
  -e ip.dst
```


# Why Timestamps Matter

During an assessment, timestamps allow correlation with:

```text
Firewall logs

EDR

Windows Event Logs

Linux logs

Web server logs

SIEM

Proxy logs

Identity logs
```


# Correlation Model

```text
Test ID
   |
   v
Timestamp
   |
   +--> PCAP
   |
   +--> Firewall
   |
   +--> EDR
   |
   +--> SIEM
   |
   +--> Application Log
   |
   v
Unified Timeline
```


# Nmap and Wireshark

Wireshark can show what an Nmap scan looks like on the network.

Example:

```text
Nmap
 |
 v
SYN -> 22
SYN -> 80
SYN -> 443
SYN -> 445
 |
 v
Target Responses
```

Capture:

```bash
sudo tshark -i eth0 -f 'host 192.168.1.10' -w nmap-test.pcapng
```

Then run the authorised scan separately.


# Analyse SYN Activity

```text
tcp.flags.syn == 1 && tcp.flags.ack == 0
```

This can help visualise port-scanning behaviour.


# Nmap Detection Exercise

```text
Assessment Host
      |
      v
Nmap Scan
      |
      v
Packet Capture
      |
      v
Firewall / NDR / SIEM
      |
      v
Compare Visibility
```


# curl and Wireshark

Capture:

```bash
sudo tshark -i eth0 -w curl-test.pcapng
```

Generate a request:

```bash
curl http://example.com/
```

Then filter:

```text
http
```

For HTTPS:

```text
tls
```

The HTTP body is normally encrypted when TLS is used.


# Web Assessment Workflow

```text
Nmap
 |
 v
Web Port
 |
 v
curl
 |
 v
HTTP Behaviour
 |
 v
Burp Suite
 |
 v
Application Testing
 |
 v
Wireshark
 |
 v
Network-Level Validation
```

Wireshark is not a replacement for Burp Suite. They answer different questions.


# Burp vs Wireshark

```text
Burp Suite
    |
    v
HTTP/Application Layer

Wireshark
    |
    v
Packet/Protocol Layer
```

Use Burp for:

```text
Requests

Responses

Parameters

Sessions

Application behaviour
```

Use Wireshark for:

```text
Network connections

DNS

TCP

TLS

Protocol negotiation

Packet-level troubleshooting
```


# Troubleshooting - No Packets

Check interfaces:

```bash
tshark -D
```

Check routes:

```bash
ip route
```

Check target route:

```bash
ip route get 192.168.1.10
```

You may simply be capturing on the wrong interface.


# Troubleshooting - Only Outbound Packets

Possible causes:

```text
No server response

Wrong capture point

Asymmetric routing

Firewall drop

Capture interface problem
```


# Troubleshooting - Traffic Is Encrypted

This is expected for protocols such as:

```text
HTTPS

SSH

LDAPS

Encrypted SMB sessions

Many modern application protocols
```

Packet capture still provides metadata and protocol-handshake information.


# Troubleshooting - Wireshark Shows TCP Instead of Protocol

Possible causes:

```text
Non-standard port

Incomplete capture

Encrypted protocol

Dissector not selected

Protocol not recognised
```

Wireshark can sometimes manually decode traffic using:

```text
Analyze
    |
    v
Decode As
```

Only do this when you have reason to believe the traffic is a specific protocol.


# Troubleshooting - Checksum Errors

Packet captures taken on the sending host can show apparent checksum errors due to checksum offloading.

Conceptually:

```text
Application
    |
    v
Operating System
    |
    v
Packet Capture
    |
    v
NIC Adds Final Checksum
    |
    v
Network
```

The capture may occur before the NIC calculates the final checksum.

Therefore:

```text
Bad checksum in local capture
```

does not automatically mean malformed traffic was transmitted.


# Troubleshooting - Retransmissions Everywhere

Possible explanations:

```text
Actual packet loss

Capture loss

Asymmetric visibility

High system load

Congestion

Incorrect capture point
```

Correlate with network and host telemetry.


# Capture Loss

Large or high-speed captures can drop packets.

This can create misleading analysis.

Consider:

```text
Capture interface capacity

Disk speed

Capture filters

Buffer size

Host load
```


# Packet Capture Security

PCAPs may contain:

```text
Credentials

NTLM authentication material

Kerberos traffic

Session cookies

Bearer tokens

API keys

Internal hostnames

Email addresses

Usernames

File contents

Application data
```

Store captures according to the engagement's evidence-handling requirements.


# Avoid Capturing More Than Necessary

A good principle:

```text
Capture enough to answer the question.
```

Not:

```text
Capture the entire corporate network indefinitely.
```


# Evidence Capture

For an important network test record:

```text
Test ID

Timestamp

Capture host

Capture interface

Capture point

Source IP

Destination IP

Protocol

Relevant ports

Capture filter

Display filter

PCAP filename

Relevant frame numbers

Interpretation
```


# Example Evidence Record

```text
Test ID:
NET-PCAP-012

Objective:
Determine why HTTPS connectivity from the assessment
workstation to APP01 failed.

Capture Point:
Assessment workstation

Interface:
tun0

Source:
10.10.14.20

Destination:
10.10.10.25

Destination Port:
443/tcp

Display Filter:
ip.addr == 10.10.10.25 && tcp.port == 443

Observation:
Repeated TCP SYN packets were transmitted toward APP01.
No SYN/ACK or RST response was observed in the capture.

Interpretation:
The capture demonstrates that the assessment host attempted
the connection. The capture alone does not determine whether
the missing response resulted from filtering, routing,
packet loss, the target being unavailable, or incomplete
visibility of the return path.
```


# Strong vs Weak Conclusions

Weak:

```text
No response, therefore firewall blocked it.
```

Better:

```text
No response was observed at the assessment capture point.
```

Then investigate:

```text
Firewall logs

Routing

Target availability

Capture location
```


# Another Example - DNS

Observed:

```text
Client -> DNS Query -> DNS Server

DNS Server -> NXDOMAIN -> Client
```

Defensible conclusion:

```text
The DNS server responded and indicated that the requested
name did not exist according to the queried DNS context.
```

Not:

```text
The network is broken.
```


# Example - TCP Refused

Observed:

```text
SYN
 |
 v
RST/ACK
```

This supports:

```text
The target responded but did not accept the TCP connection
on the tested port at that time.
```

This is different from:

```text
No response.
```


# Example - HTTP Redirect

Observed unencrypted HTTP:

```text
GET / HTTP/1.1

HTTP/1.1 301 Moved Permanently
Location: https://example.com/
```

This supports:

```text
The HTTP endpoint redirected the tested request to HTTPS.
```

Further testing should determine whether HTTPS is consistently enforced across relevant application paths.


# Example - TLS

Observed:

```text
ClientHello
   |
   v
ServerHello
   |
   v
Certificate
   |
   v
Encrypted Application Data
```

This supports:

```text
TLS negotiation occurred and encrypted application
communication followed.
```

It does not by itself prove:

```text
TLS configuration is secure.
```


# Example - SMB

Observed:

```text
TCP/445 connection

SMB2 negotiation

Session setup
```

This supports:

```text
The client established SMB communication with the target.
```

Further security analysis may require:

```text
Signing validation

Authentication context

Share permissions

Protocol versions

Authorisation
```


# Reporting

Packet capture is usually supporting evidence rather than the vulnerability itself.

Avoid:

> Wireshark showed TCP/445.

Prefer:

> Network validation demonstrated that SMB over TCP/445 was directly reachable from the corporate user network to the management server. This exposure was confirmed at the packet level and did not align with the documented segmentation requirement restricting management protocols to the administrative network.


# Reporting Authentication Failure

Avoid:

> Kerberos is broken.

Prefer:

> During the controlled authentication attempt, the client reached the domain controller and received a Kerberos error response. Packet analysis confirms network connectivity to the KDC; further investigation is required at the identity and Kerberos configuration layers.


# Retesting

Packet captures are particularly useful for comparing before and after remediation.

Before:

```text
User VLAN
   |
   | SYN
   v
Management Server
   |
   | SYN/ACK
   v
User VLAN
```

After segmentation change:

```text
User VLAN
   |
   | SYN
   v
Firewall
   |
   X
```

The retest must still consider where the capture was taken.


# Retest Workflow

```text
Original Test
     |
     v
Original PCAP
     |
     v
Remediation
     |
     v
Repeat Same Test
     |
     v
New PCAP
     |
     v
Compare
```


# Detection Engineering

Packet capture is valuable for understanding what security controls can observe.

Example:

```text
Technique
   |
   v
Network Traffic
   |
   v
Packet Capture
   |
   v
NDR / IDS
   |
   v
SIEM
   |
   v
Detection
```


# Purple Team Validation

For a controlled exercise:

```text
Test ID:
PT-NET-001

Technique:
Internal service discovery

Source:
Authorised test workstation

Target:
Dedicated test subnet

Expected Network Signal:
Multiple TCP SYN packets from one source to multiple
destination ports.

Expected Detection:
Internal port scanning alert.

Evidence:
PCAP + NDR event + SIEM alert.
```


# Questions for Defenders

```text
Was the traffic visible?

Was the source identified?

Was the destination identified?

Was the protocol identified?

Was an alert generated?

Was the alert enriched?

Was the behaviour correlated with endpoint telemetry?

Did the analyst reach the correct conclusion?
```


# Wireshark Display Filter Quick Reference

| Objective | Filter |
|---|---|
| IPv4 | `ip` |
| IPv6 | `ipv6` |
| One host | `ip.addr == 192.168.1.10` |
| Source IP | `ip.src == 192.168.1.10` |
| Destination IP | `ip.dst == 192.168.1.10` |
| TCP | `tcp` |
| UDP | `udp` |
| TCP port 443 | `tcp.port == 443` |
| UDP port 53 | `udp.port == 53` |
| SYN | `tcp.flags.syn == 1` |
| Initial SYN | `tcp.flags.syn == 1 && tcp.flags.ack == 0` |
| SYN/ACK | `tcp.flags.syn == 1 && tcp.flags.ack == 1` |
| TCP reset | `tcp.flags.reset == 1` |
| Retransmission | `tcp.analysis.retransmission` |
| DNS | `dns` |
| DNS query | `dns.flags.response == 0` |
| NXDOMAIN | `dns.flags.rcode == 3` |
| HTTP | `http` |
| HTTP request | `http.request` |
| HTTP response | `http.response` |
| HTTP GET | `http.request.method == "GET"` |
| HTTP 403 | `http.response.code == 403` |
| TLS | `tls` |
| TLS handshake | `tls.handshake` |
| TLS ClientHello | `tls.handshake.type == 1` |
| TLS SNI | `tls.handshake.extensions_server_name` |
| SMB2/3 | `smb2` |
| Kerberos | `kerberos` |
| LDAP | `ldap` |
| NTLMSSP | `ntlmssp` |
| ICMP | `icmp` |
| ARP | `arp` |


# Capture Filter Quick Reference

| Objective | Capture Filter |
|---|---|
| One host | `host 192.168.1.10` |
| Source host | `src host 192.168.1.10` |
| Destination host | `dst host 192.168.1.10` |
| Network | `net 192.168.1.0/24` |
| TCP | `tcp` |
| UDP | `udp` |
| Port 443 | `port 443` |
| TCP/443 | `tcp port 443` |
| UDP/53 | `udp port 53` |
| HTTP or HTTPS | `tcp port 80 or tcp port 443` |
| Exclude SSH | `not port 22` |
| Host and HTTPS | `host 192.168.1.10 and tcp port 443` |


# tshark Quick Reference

## Interfaces

```bash
tshark -D
```

## Capture

```bash
sudo tshark -i eth0
```

## Save Capture

```bash
sudo tshark -i eth0 -w capture.pcapng
```

## Capture 60 Seconds

```bash
sudo tshark -i eth0 -a duration:60 -w capture.pcapng
```

## Read

```bash
tshark -r capture.pcapng
```

## Display Filter

```bash
tshark -r capture.pcapng -Y 'dns'
```

## Capture Filter

```bash
sudo tshark -i eth0 -f 'host 192.168.1.10'
```

## HTTP

```bash
tshark -r capture.pcapng -Y 'http'
```

## DNS

```bash
tshark -r capture.pcapng -Y 'dns'
```

## TLS

```bash
tshark -r capture.pcapng -Y 'tls'
```

## SMB

```bash
tshark -r capture.pcapng -Y 'smb2'
```

## Kerberos

```bash
tshark -r capture.pcapng -Y 'kerberos'
```

## LDAP

```bash
tshark -r capture.pcapng -Y 'ldap'
```

## Conversations

```bash
tshark -r capture.pcapng -q -z conv,tcp
```

## Protocol Hierarchy

```bash
tshark -r capture.pcapng -q -z io,phs
```

## DNS Names

```bash
tshark -r capture.pcapng \
  -Y 'dns.flags.response == 0' \
  -T fields \
  -e dns.qry.name
```

## HTTP Requests

```bash
tshark -r capture.pcapng \
  -Y 'http.request' \
  -T fields \
  -e http.request.method \
  -e http.host \
  -e http.request.uri
```

## TLS SNI

```bash
tshark -r capture.pcapng \
  -Y 'tls.handshake.extensions_server_name' \
  -T fields \
  -e tls.handshake.extensions_server_name
```


# Protocol Quick Reference

| Protocol | Common Port | Useful Filter |
|---|---:|---|
| DNS | 53 | `dns` |
| HTTP | 80 | `http` |
| HTTPS/TLS | 443 | `tls` |
| Kerberos | 88 | `kerberos` |
| RPC | 135 | `tcp.port == 135` |
| SMB | 445 | `smb2` |
| LDAP | 389 | `ldap` |
| LDAPS | 636 | `tcp.port == 636` |
| MSSQL | 1433 | `tcp.port == 1433` |
| NFS | 2049 | `tcp.port == 2049 || udp.port == 2049` |
| RDP | 3389 | `tcp.port == 3389` |
| PostgreSQL | 5432 | `tcp.port == 5432` |
| WinRM HTTP | 5985 | `tcp.port == 5985` |
| WinRM HTTPS | 5986 | `tcp.port == 5986` |
| Redis | 6379 | `tcp.port == 6379` |


# Interpretation Quick Reference

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| SYN sent | Connection attempt occurred | Target received it |
| SYN/ACK received | TCP port accepted connection attempt | Application is secure |
| RST received | Connection was rejected/reset | Firewall blocked it |
| No response | No response visible at capture point | Firewall definitely blocked it |
| DNS query | Client attempted name resolution | DNS succeeded |
| NXDOMAIN | DNS server reported name absent | Network failure |
| HTTP 200 | HTTP request succeeded | Authorisation is correct |
| HTTP 403 | Server refused request | Resource does not exist |
| TLS handshake | TLS negotiation occurred | TLS configuration is secure |
| SMB negotiation | SMB communication occurred | SMB is vulnerable |
| NTLMSSP observed | NTLM used in exchange | Relay is possible |
| Kerberos exchange | Kerberos communication occurred | Authentication succeeded |
| Retransmission | Packet appears retransmitted | Network is necessarily faulty |
| Checksum warning | Capture sees checksum discrepancy | Packet left host malformed |


# Assessment Workflow

```text
                     SECURITY QUESTION
                            |
                            v
                     CAPTURE LOCATION
                            |
                            v
                       INTERFACE
                            |
                            v
                    START CAPTURE
                            |
                            v
                    REPRODUCE EVENT
                            |
                            v
                     STOP CAPTURE
                            |
                            v
                    DISPLAY FILTER
                            |
               +------------+------------+
               |                         |
               v                         v
           NETWORK                   PROTOCOL
           BEHAVIOUR                 BEHAVIOUR
               |                         |
               +------------+------------+
                            |
                            v
                     FOLLOW STREAM
                            |
                            v
                      INTERPRET
                            |
                            v
                  CORRELATE TELEMETRY
                            |
                            v
                        EVIDENCE
```


# Packet Analysis Checklist

## Preparation

- [ ] Capture authorised
- [ ] Objective defined
- [ ] Correct source identified
- [ ] Correct destination identified
- [ ] Correct interface identified
- [ ] Route verified
- [ ] Sensitive-data handling understood

## Capture

- [ ] Capture started before test
- [ ] Test timestamp recorded
- [ ] Test reproduced once where sufficient
- [ ] Capture stopped after relevant activity
- [ ] PCAP saved
- [ ] Capture filename meaningful

## Network

- [ ] DNS reviewed
- [ ] TCP handshake reviewed
- [ ] Resets reviewed
- [ ] Retransmissions interpreted carefully
- [ ] ICMP reviewed where relevant
- [ ] Source and destination verified
- [ ] Ports verified

## Protocol

- [ ] Actual protocol identified
- [ ] Protocol negotiation reviewed
- [ ] Authentication exchange reviewed where relevant
- [ ] TLS considered
- [ ] Application data reviewed only where visible and authorised

## Interpretation

- [ ] Observation separated from assumption
- [ ] Capture-point limitations considered
- [ ] Asymmetric routing considered
- [ ] Packet loss considered
- [ ] Encryption considered
- [ ] Host/application logs correlated where needed

## Evidence

- [ ] Test ID recorded
- [ ] Timestamp recorded
- [ ] Capture point recorded
- [ ] Interface recorded
- [ ] PCAP retained securely
- [ ] Relevant frame numbers recorded
- [ ] Display filter recorded
- [ ] Interpretation documented
- [ ] Sensitive information protected

## Retest

- [ ] Same capture point used where possible
- [ ] Same source used
- [ ] Same target used
- [ ] Same action reproduced
- [ ] New PCAP captured
- [ ] Before/after behaviour compared


# Final Testing Principle

Packet capture provides visibility into what was observable **at a specific point on the network**.

That qualification matters.

Do not use:

```text
Packet Not Visible
      |
      v
Event Did Not Happen
```

Use:

```text
Packet Not Visible
      |
      v
Was Capture Point Correct?
      |
      v
Was Interface Correct?
      |
      v
Could Routing Be Asymmetric?
      |
      v
Could Capture Have Dropped Packets?
      |
      v
What Do Other Telemetry Sources Show?
```

Likewise, do not stop at:

```text
Packet
  |
  v
Protocol
```

Continue:

```text
Packet
  |
  v
Conversation
  |
  v
Protocol State
  |
  v
Application / Authentication Context
  |
  v
Expected Behaviour
  |
  v
Observed Behaviour
  |
  v
Security Meaning
```

For every important packet-analysis result ask:

```text
Where was this captured?

Which interface was used?

Who sent the packet?

Who received it?

Did the other side respond?

Was the TCP handshake completed?

Which protocol was negotiated?

Was the traffic encrypted?

What can actually be observed?

What cannot be determined from this capture?

Does another telemetry source confirm the interpretation?

What evidence should be preserved?

How would I reproduce the test?
```


# Related Cheatsheets

- [Networking Cheatsheet](networking.md)
- [Nmap Cheatsheet](nmap.md)
- [curl Cheatsheet](curl.md)
- [Web Application Security Cheatsheet](web.md)
- [Active Directory Cheatsheet](active-directory.md)
- [NetExec Cheatsheet](netexec.md)
- [PowerShell Cheatsheet](powershell.md)
- [Windows Cheatsheet](windows.md)
- [Linux Cheatsheet](linux.md)


# Detailed Notes

- [Web Application Security](../web/index.md)
- [Active Directory](../active-directory/index.md)
- [Windows](../windows/index.md)
- [Linux](../linux/index.md)
- [Red Teaming](../red-teaming/index.md)
- [Purple Teaming](../purple-teaming/index.md)


# References

- [Wireshark](https://www.wireshark.org/){ target="_blank" rel="noopener noreferrer" }
- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/){ target="_blank" rel="noopener noreferrer" }
- [Wireshark Display Filters](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html){ target="_blank" rel="noopener noreferrer" }
- [Wireshark Capture Filters](https://wiki.wireshark.org/CaptureFilters){ target="_blank" rel="noopener noreferrer" }
- [Wireshark Display Filter Reference](https://www.wireshark.org/docs/dfref/){ target="_blank" rel="noopener noreferrer" }
- [tshark Manual](https://www.wireshark.org/docs/man-pages/tshark.html){ target="_blank" rel="noopener noreferrer" }
- [TCPDump and libpcap Filter Syntax](https://www.tcpdump.org/manpages/pcap-filter.7.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Start with a question"
    Do not open a large PCAP and randomly browse packets. Define the question first - for example, "Did the TCP handshake complete?" or "Which DNS response did the client receive?" - and build the analysis around that question.


!!! tip "Record the display filter"
    The filter used to isolate the relevant traffic is useful assessment evidence because another tester can reopen the PCAP and reproduce your analysis.


!!! tip "Correlate timestamps"
    Packet timestamps become substantially more useful when correlated with firewall, EDR, SIEM, authentication and application logs.


!!! warning "A PCAP only represents its capture point"
    Absence of a packet does not necessarily prove that the packet never existed elsewhere on the network. Capture location, asymmetric routing, dropped packets and interface selection must be considered.


!!! warning "PCAP files can contain secrets"
    Packet captures can contain authentication material, cookies, tokens, usernames, internal infrastructure details and application data. Store and share them according to the engagement's evidence-handling requirements.
