---
title: Nmap Cheatsheet
description: Detailed practical Nmap reference for authorised security assessments covering host discovery, TCP and UDP scanning, service detection, NSE, output, performance, firewall interpretation, validation, evidence collection and troubleshooting.
---

# Nmap Cheatsheet

Nmap is one of the primary tools used during network reconnaissance and security assessments.

It can help answer:

```text
Which hosts are reachable?

Which TCP ports are exposed?

Which UDP services are available?

What services appear to be listening?

Which versions are reported?

Which network paths are filtered?

Which protocols require deeper investigation?
```

A good Nmap workflow is not:

```text
nmap <target>
```

followed immediately by:

```text
Start testing everything.
```

Instead:

```text
Define Scope
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
Focused Enumeration
    |
    v
Manual Validation
    |
    v
Interpret Exposure
    |
    v
Capture Evidence
```

!!! warning "Authorised Security Testing"

    Only scan systems and networks that you are explicitly authorised to assess. Network scanning can generate significant traffic, trigger monitoring systems, affect fragile services, and violate assessment rules if performed outside the agreed scope.


# Quick Start

A practical external or internal assessment often follows:

```text
Target
  |
  v
Confirm Scope
  |
  v
Discover Hosts
  |
  v
Discover TCP Ports
  |
  v
Identify Services
  |
  v
Check UDP Where Relevant
  |
  v
Run Focused NSE
  |
  v
Manually Validate
  |
  v
Document Exposure
```


# Installation

Kali Linux:

```bash
sudo apt update
sudo apt install nmap
```

Check:

```bash
nmap --version
```

Locate:

```bash
which nmap
```


# Help

```bash
nmap -h
```

Manual:

```bash
man nmap
```

Always check the locally installed version when relying on less common options or NSE behaviour.


# Target Formats

Single IP:

```bash
nmap 192.168.1.10
```

Hostname:

```bash
nmap server.example.com
```

Multiple targets:

```bash
nmap 192.168.1.10 192.168.1.20
```

CIDR:

```bash
nmap 192.168.1.0/24
```

Range:

```bash
nmap 192.168.1.10-50
```

Input file:

```bash
nmap -iL targets.txt
```


# Excluding Targets

Exclude one host:

```bash
nmap 192.168.1.0/24 --exclude 192.168.1.1
```

Exclude multiple:

```bash
nmap 192.168.1.0/24 --exclude 192.168.1.1,192.168.1.254
```

Exclude from file:

```bash
nmap 192.168.1.0/24 --excludefile exclude.txt
```


# Scope First

Before scanning:

```text
[ ] IP range authorised
[ ] Hostnames authorised
[ ] Cloud assets included if relevant
[ ] Third-party systems excluded
[ ] Production restrictions understood
[ ] Scan windows understood
[ ] Rate restrictions understood
[ ] UDP testing permitted
[ ] NSE restrictions understood
```


# Host Discovery

Before performing large port scans, determine which systems appear reachable.

Basic discovery:

```bash
nmap -sn 192.168.1.0/24
```

This performs host discovery without a port scan.


# Representative Output

```text
Nmap scan report for 192.168.1.10
Host is up (0.0021s latency).

Nmap scan report for 192.168.1.20
Host is up (0.0034s latency).
```

Interpretation:

```text
Nmap received sufficient responses to classify the hosts as up.
```

It does not prove:

```text
Other hosts are definitely offline.
```


# Why Host Discovery Can Miss Systems

Discovery may be affected by:

```text
Firewall rules

ICMP filtering

Network segmentation

Host firewall

Cloud security groups

Routing

Probe type

Network ACLs
```

A system that appears down may simply not respond to the discovery probes used.


# Skip Host Discovery

When you already know the target exists or discovery probes are blocked:

```bash
nmap -Pn 192.168.1.10
```

`-Pn` tells Nmap to treat the target as online and proceed with scanning.

Use this carefully across large ranges because every address will be treated as a scan target.


# ARP Discovery

On a local Ethernet network, Nmap can use ARP discovery.

A local-network scan may identify hosts even when ICMP is filtered.

This is one reason internal discovery behaviour can differ from remote scanning.


# TCP SYN Discovery

Host discovery can also use TCP probes.

For example:

```bash
nmap -PS80,443 192.168.1.0/24
```

This can be useful when ICMP-based discovery is restricted.


# TCP ACK Discovery

```bash
nmap -PA80,443 192.168.1.0/24
```

The usefulness depends on network architecture and filtering.


# ICMP Echo Discovery

```bash
nmap -PE 192.168.1.0/24
```

Do not assume lack of ICMP response means the system does not exist.


# Basic TCP Scan

```bash
nmap 192.168.1.10
```

By default, Nmap scans a selection of commonly used TCP ports.


# SYN Scan

With suitable privileges:

```bash
sudo nmap -sS 192.168.1.10
```

SYN scanning is commonly used for TCP port discovery.


# TCP Connect Scan

```bash
nmap -sT 192.168.1.10
```

A TCP connect scan completes the operating system's normal TCP connection process.

This is useful when raw packet privileges are unavailable.


# SYN vs Connect

Conceptually:

```text
SYN Scan

SYN
 |
 v
Target
 |
 +--> SYN/ACK -> Open
 |
 +--> RST     -> Closed
```

A connect scan uses the host operating system's normal TCP connection mechanism.


# Specific Port

```bash
nmap -p 443 192.168.1.10
```

Multiple:

```bash
nmap -p 22,80,443,445,3389 192.168.1.10
```

Range:

```bash
nmap -p 1-1000 192.168.1.10
```


# All TCP Ports

```bash
nmap -p- 192.168.1.10
```

This scans TCP ports:

```text
1-65535
```


# Why Full-Port Scanning Matters

A default Nmap scan does not test every TCP port.

Applications may listen on:

```text
8080

8443

8888

9000

9443

10000

Custom high ports
```

A common mistake is:

```text
Default Scan
     |
     v
No Interesting Ports
     |
     v
Assume No Services
```

A better workflow is:

```text
Initial Scan
     |
     v
Full TCP Port Discovery
     |
     v
Focused Service Enumeration
```


# Fast Scan

```bash
nmap -F 192.168.1.10
```

This scans fewer ports than the default selection.

Useful for:

```text
Quick triage

Large networks

Initial discovery
```

It is not a replacement for comprehensive port discovery where that is required.


# Top Ports

```bash
nmap --top-ports 100 192.168.1.10
```

or:

```bash
nmap --top-ports 1000 192.168.1.10
```

Useful when balancing:

```text
Coverage

Time

Network impact
```


# Open Ports Only

```bash
nmap --open 192.168.1.10
```

This reduces output clutter by focusing on open or potentially open ports.


# Port States

Nmap can report states such as:

```text
open

closed

filtered

unfiltered

open|filtered

closed|filtered
```


# Open

Example:

```text
443/tcp open https
```

Generally means:

```text
A service accepted or responded to the probe in a way consistent
with an open port.
```


# Closed

Example:

```text
443/tcp closed https
```

Generally means:

```text
The target is reachable, but no service is accepting connections
on that port.
```


# Filtered

Example:

```text
445/tcp filtered microsoft-ds
```

This means Nmap cannot determine whether the port is open because packet filtering prevents a conclusive response.

Possible causes:

```text
Firewall

ACL

Security group

Packet filter

Network device
```


# Filtered Does Not Mean Closed

This distinction matters:

```text
closed
```

and:

```text
filtered
```

represent different observations.

Do not report:

> SMB is disabled.

solely because:

```text
445/tcp filtered
```

The correct conclusion may simply be:

> TCP/445 could not be directly assessed from the tested network position because traffic appeared to be filtered.


# Open or Filtered

Commonly seen with UDP:

```text
53/udp open|filtered domain
```

This means Nmap cannot distinguish between:

```text
An open service that did not respond
```

and:

```text
Filtering that silently dropped the probe
```


# Service Detection

After finding ports:

```bash
nmap -sV -p 22,80,443 192.168.1.10
```

Example:

```text
PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH ...
80/tcp  open  http    nginx
443/tcp open  ssl/http nginx
```


# What `-sV` Does

Service detection sends additional probes to identify:

```text
Protocol

Product

Version

Additional service information
```

It is more active than basic port discovery.


# Do Not Treat Version Detection as Absolute

Example:

```text
Apache httpd 2.x
```

may be influenced by:

```text
Banner configuration

Reverse proxy

Backported patches

Custom builds

Middleboxes

Incomplete fingerprints
```

Use the result as evidence for further validation, not automatic proof of vulnerability.


# Default Scripts and Version Detection

A commonly used focused scan is:

```bash
nmap -sC -sV -p 22,80,443 192.168.1.10
```

Where:

```text
-sC
```

runs the default NSE script set.

And:

```text
-sV
```

performs service/version detection.


# Understand `-sC`

Do not use `-sC` blindly against fragile or sensitive production systems.

Review the assessment rules and understand the scripts being invoked.


# Operating System Detection

```bash
sudo nmap -O 192.168.1.10
```

OS detection uses network-stack characteristics to estimate the operating system.


# OS Detection Interpretation

Example:

```text
Running: Linux
```

should generally be interpreted as:

```text
Network fingerprint appears consistent with Linux.
```

Not necessarily:

```text
Operating system definitively confirmed.
```


# Aggressive Detection

```bash
nmap -A 192.168.1.10
```

`-A` enables several advanced detection features.

It is convenient but can be substantially noisier than a focused scan.


# Prefer Focused Enumeration

Instead of automatically:

```bash
nmap -A target
```

consider:

```bash
nmap -sV -p <identified-ports> target
```

followed by protocol-specific testing.

This gives better control over traffic and assessment scope.


# UDP Scanning

UDP is frequently overlooked.

Basic UDP scan:

```bash
sudo nmap -sU 192.168.1.10
```


# Specific UDP Ports

```bash
sudo nmap -sU -p 53,67,68,69,123,161,500,514,1900 192.168.1.10
```


# Common UDP Services

| Port | Service |
|---:|---|
| 53 | DNS |
| 67/68 | DHCP |
| 69 | TFTP |
| 88 | Kerberos |
| 123 | NTP |
| 137 | NetBIOS |
| 161 | SNMP |
| 162 | SNMP Trap |
| 500 | IKE |
| 514 | Syslog |
| 1900 | SSDP |
| 4500 | IPsec NAT-T |


# UDP Is Different

UDP has no TCP-style handshake.

Conceptually:

```text
Probe
 |
 v
UDP Service
 |
 +--> Application Response -> Open
 |
 +--> ICMP Unreachable     -> Closed
 |
 +--> No Response          -> Open or Filtered
```


# Faster UDP Triage

Instead of scanning every UDP port immediately:

```bash
sudo nmap -sU --top-ports 100 192.168.1.10
```

Then expand where justified.


# TCP and UDP Together

For selected ports:

```bash
sudo nmap -sS -sU -p T:22,80,443,U:53,161 192.168.1.10
```


# Protocol-Focused Enumeration

After discovery, switch from:

```text
Which ports exist?
```

to:

```text
What is this service?
```


# HTTP

```bash
nmap -sV -p 80,443,8080,8443 192.168.1.10
```

Useful NSE discovery:

```bash
nmap --script http-title -p 80,443,8080,8443 192.168.1.10
```

Headers:

```bash
nmap --script http-headers -p 80,443 192.168.1.10
```


# HTTPS and TLS

Certificate information:

```bash
nmap --script ssl-cert -p 443 192.168.1.10
```

Cipher enumeration:

```bash
nmap --script ssl-enum-ciphers -p 443 192.168.1.10
```

Use TLS results as the starting point for configuration analysis.


# SSH

```bash
nmap -sV -p 22 192.168.1.10
```

Algorithms:

```bash
nmap --script ssh2-enum-algos -p 22 192.168.1.10
```

Host keys:

```bash
nmap --script ssh-hostkey -p 22 192.168.1.10
```


# SMB

```bash
nmap -sV -p 139,445 192.168.1.10
```

Protocol information:

```bash
nmap --script smb-protocols -p 445 192.168.1.10
```

Security mode:

```bash
nmap --script smb-security-mode -p 445 192.168.1.10
```

For detailed AD/SMB testing, continue with the [Active Directory Cheatsheet](active-directory.md) and [NetExec Cheatsheet](netexec.md).


# LDAP

```bash
nmap -sV -p 389,636,3268,3269 192.168.1.10
```

LDAP exposure should be interpreted in the context of:

```text
Authentication

TLS

Directory role

Network location
```


# Kerberos

```bash
nmap -sV -p 88 192.168.1.10
```

In Active Directory environments, Kerberos exposure is normally expected on domain controllers.

The existence of port 88 is not a vulnerability.


# RDP

```bash
nmap -sV -p 3389 192.168.1.10
```

RDP-related NSE scripts available locally can be found with:

```bash
ls /usr/share/nmap/scripts/rdp*
```


# WinRM

```bash
nmap -sV -p 5985,5986 192.168.1.10
```

Common interpretation:

```text
5985 -> HTTP WinRM

5986 -> HTTPS WinRM
```

Validate actual protocol behaviour rather than relying solely on port number.


# MSSQL

```bash
nmap -sV -p 1433 192.168.1.10
```

SQL Server may also use:

```text
Dynamic ports

Named instances
```

so do not assume:

```text
1433 closed = no MSSQL
```


# MySQL

```bash
nmap -sV -p 3306 192.168.1.10
```


# PostgreSQL

```bash
nmap -sV -p 5432 192.168.1.10
```


# DNS

TCP:

```bash
nmap -sV -p 53 192.168.1.10
```

UDP:

```bash
sudo nmap -sU -sV -p 53 192.168.1.10
```


# SNMP

```bash
sudo nmap -sU -sV -p 161 192.168.1.10
```

SNMP exposure can reveal substantial infrastructure information depending on configuration and access controls.


# NTP

```bash
sudo nmap -sU -sV -p 123 192.168.1.10
```


# FTP

```bash
nmap -sV -p 21 192.168.1.10
```

Identify:

```text
Product

Version

TLS support

Authentication requirements
```


# SMTP

```bash
nmap -sV -p 25,465,587 192.168.1.10
```


# Common Enterprise Ports

| Port | Typical Service |
|---:|---|
| 21 | FTP |
| 22 | SSH |
| 25 | SMTP |
| 53 | DNS |
| 80 | HTTP |
| 88 | Kerberos |
| 110 | POP3 |
| 111 | RPC |
| 123 | NTP |
| 135 | MSRPC |
| 139 | NetBIOS |
| 143 | IMAP |
| 389 | LDAP |
| 443 | HTTPS |
| 445 | SMB |
| 465 | SMTPS |
| 587 | SMTP submission |
| 636 | LDAPS |
| 1433 | MSSQL |
| 1521 | Oracle |
| 2049 | NFS |
| 3268 | Global Catalog |
| 3269 | Global Catalog TLS |
| 3306 | MySQL |
| 3389 | RDP |
| 5432 | PostgreSQL |
| 5985 | WinRM HTTP |
| 5986 | WinRM HTTPS |
| 6379 | Redis |
| 8080 | Alternate HTTP |
| 8443 | Alternate HTTPS |
| 9200 | Elasticsearch |


# NSE

Nmap Scripting Engine scripts extend Nmap beyond basic scanning.

Locate scripts:

```bash
ls /usr/share/nmap/scripts/
```

Search:

```bash
ls /usr/share/nmap/scripts/ | grep http
```

or:

```bash
ls /usr/share/nmap/scripts/ | grep smb
```


# NSE Help

```bash
nmap --script-help http-title
```

This is particularly important before running unfamiliar scripts.


# Run One Script

```bash
nmap --script http-title -p 80 192.168.1.10
```


# Multiple Scripts

```bash
nmap --script http-title,http-headers -p 80,443 192.168.1.10
```


# Script Categories

NSE scripts can belong to categories such as:

```text
auth

broadcast

brute

default

discovery

dos

exploit

external

fuzzer

intrusive

malware

safe

version

vuln
```


# Do Not Treat NSE Categories Equally

There is a major difference between:

```text
safe
```

and:

```text
dos
```

or:

```text
intrusive
```

Do not run broad script categories against production environments without understanding their behaviour and having explicit authorisation.


# Review Script Before Running

Script files are commonly stored under:

```text
/usr/share/nmap/scripts/
```

Inspect:

```bash
less /usr/share/nmap/scripts/<script>.nse
```

This is useful when operational impact is unclear.


# Default Scripts

```bash
nmap -sC 192.168.1.10
```

Equivalent to using the default NSE script category in typical Nmap usage.

Use deliberately rather than mechanically.


# Vulnerability Scripts

Nmap includes scripts associated with vulnerability detection.

List locally:

```bash
ls /usr/share/nmap/scripts/ | grep vuln
```

Or review script categories through Nmap's documentation.

Do not assume:

```text
NSE says VULNERABLE
```

equals:

```text
Confirmed exploitable vulnerability
```

Manual validation and version/configuration analysis may still be necessary.


# NSE Result Interpretation

Treat NSE output as:

```text
Automated Observation
        |
        v
Check Script Logic
        |
        v
Understand Detection Method
        |
        v
Verify Target State
        |
        v
Manual Validation
        |
        v
Conclusion
```


# Scan Timing

Nmap supports timing templates:

```text
-T0

-T1

-T2

-T3

-T4

-T5
```


# Typical Default

```text
-T3
```

is the normal timing template.


# Faster Scanning

A common assessment command may use:

```bash
nmap -T4 192.168.1.10
```

But faster is not automatically better.


# Timing Trade-Off

```text
Faster Scan
    |
    +--> Less Time
    |
    +--> More Traffic
    |
    +--> Potential Accuracy Impact
    |
    +--> More Monitoring Visibility
    |
    +--> Greater Risk to Fragile Systems
```


# Rate Control

Minimum packet rate:

```bash
nmap --min-rate 1000 192.168.1.10
```

Maximum rate:

```bash
nmap --max-rate 100 192.168.1.10
```

Do not use aggressive rate settings simply because a copied command contains them.


# Large Network Scanning

For large environments:

```text
Start with discovery

Prioritise known subnets

Control scan rate

Separate discovery from enumeration

Save output

Avoid repeatedly rescanning everything
```


# Recommended Large-Network Model

```text
CIDR
 |
 v
Host Discovery
 |
 v
Alive Targets
 |
 v
Port Discovery
 |
 v
Interesting Services
 |
 v
Focused Enumeration
```


# Output Formats

Nmap supports several useful output formats.


# Normal Output

```bash
nmap 192.168.1.10 -oN scan.txt
```


# XML

```bash
nmap 192.168.1.10 -oX scan.xml
```

Useful for:

```text
Automation

Parsing

Import into other tools

Long-term evidence
```


# Grepable Output

```bash
nmap 192.168.1.10 -oG scan.gnmap
```

This format is useful for some legacy parsing workflows.


# All Major Formats

```bash
nmap 192.168.1.10 -oA scans/server01
```

This produces several output files with the same basename.


# Create Output Directory

```bash
mkdir -p scans
```

Then:

```bash
nmap -sV -p- 192.168.1.10 -oA scans/server01
```


# Why Save Raw Output

Raw scan output provides:

```text
Evidence

Reproducibility

Comparison

Reporting support

Retest baseline
```


# Useful Naming Convention

```text
YYYYMMDD_target_scan-type
```

Example:

```text
20260906_192.168.1.10_tcp-full
```


# Verbose Output

```bash
nmap -v 192.168.1.10
```

More:

```bash
nmap -vv 192.168.1.10
```


# Show Reasons

```bash
nmap --reason 192.168.1.10
```

This helps explain why Nmap assigned a particular host or port state.


# Example

```text
PORT    STATE    SERVICE REASON
443/tcp filtered https   no-response
```

This provides useful context for interpretation.


# Packet Trace

For troubleshooting:

```bash
sudo nmap --packet-trace -p 443 192.168.1.10
```

This can generate substantial output but is useful for understanding probe/response behaviour.


# Scan Through a Specific Interface

List interfaces:

```bash
ip addr
```

Nmap interface information:

```bash
nmap --iflist
```

Specify interface:

```bash
sudo nmap -e eth0 192.168.1.10
```


# Source Port

Nmap supports selecting a source port where appropriate:

```bash
sudo nmap --source-port 53 -p 443 192.168.1.10
```

This should only be used when there is a legitimate assessment reason, such as validating firewall policy behaviour.

Do not assume changing the source port will bypass a firewall.


# IPv6

Scan IPv6:

```bash
nmap -6 <IPv6-address>
```

Example:

```bash
nmap -6 2001:db8::10
```

Do not forget IPv6 during internal assessments when the environment uses it.


# DNS Resolution

Disable DNS resolution:

```bash
nmap -n 192.168.1.10
```

This can improve speed and avoid unnecessary DNS queries.


# Force DNS Resolution

```bash
nmap -R 192.168.1.10
```

Use only when name resolution is useful to the assessment.


# Traceroute

```bash
nmap --traceroute 192.168.1.10
```

This may help understand network position and routing.


# Firewall Analysis

Nmap can provide evidence of filtering, but interpreting firewall policy requires care.

Example:

```text
22/tcp  open
80/tcp  filtered
443/tcp open
445/tcp filtered
```

A reasonable observation:

```text
The tested source could establish connectivity to TCP/22 and
TCP/443, while TCP/80 and TCP/445 appeared filtered.
```

Do not automatically claim:

```text
Firewall correctly configured.
```

A firewall assessment requires comparison against intended policy.


# Same Host, Different Source

A valuable validation method is scanning from different authorised network positions.

Example:

```text
Internet
   |
   v
443 only

Internal User VLAN
   |
   v
443,445,3389

Admin VLAN
   |
   v
22,443,445,5985
```

This can reveal segmentation behaviour.


# Segmentation Validation

```text
Source Zone
    |
    v
Target Zone
    |
    v
Expected Policy
    |
    v
Nmap Observation
    |
    v
Compare
```


# Do Not Equate Reachability with Authorisation

If:

```text
445/tcp open
```

that proves network reachability to SMB.

It does not prove:

```text
Anonymous access

Authenticated access

Administrative access

Sensitive share access
```


# Manual Validation

Nmap should often be followed by protocol-specific tools.

Example:

```text
Nmap
 |
 v
445/tcp open
 |
 v
NetExec / smbclient
 |
 v
Authentication and Share Validation
```


# HTTP Validation

Nmap:

```text
443/tcp open https
```

Follow with:

```bash
curl -k -I https://192.168.1.10/
```

where appropriate.

Then continue with browser/Burp-based application analysis.


# TLS Validation

Nmap may identify TLS.

Continue with appropriate TLS analysis and certificate inspection rather than treating:

```text
443 open
```

as sufficient security evidence.


# SMB Validation

Nmap:

```text
445/tcp open microsoft-ds
```

Continue with:

```bash
nxc smb 192.168.1.10
```

or other authorised SMB tooling.

See [NetExec Cheatsheet](netexec.md).


# RDP Validation

Nmap:

```text
3389/tcp open ms-wbt-server
```

Next determine:

```text
Is RDP actually reachable?

Is NLA enabled?

Who can log on?

Is exposure expected?
```


# WinRM Validation

Nmap:

```text
5985/tcp open
```

Continue with appropriate Windows or Active Directory testing.

See:

- [Windows Cheatsheet](windows.md)
- [PowerShell Cheatsheet](powershell.md)
- [NetExec Cheatsheet](netexec.md)


# Common Scan Workflow

## Phase 1 - Discovery

```bash
nmap -sn 192.168.1.0/24 -oA scans/discovery
```


# Phase 2 - TCP Discovery

For a known authorised host:

```bash
nmap -p- --open 192.168.1.10 -oA scans/192.168.1.10_tcp
```


# Phase 3 - Service Enumeration

Suppose discovery returned:

```text
22
80
443
445
```

Then:

```bash
nmap -sV -sC -p 22,80,443,445 192.168.1.10 -oA scans/192.168.1.10_services
```


# Phase 4 - UDP

```bash
sudo nmap -sU --top-ports 100 192.168.1.10 -oA scans/192.168.1.10_udp
```


# Phase 5 - Focused Enumeration

Example:

```bash
nmap --script ssl-cert,ssl-enum-ciphers -p 443 192.168.1.10
```

or:

```bash
nmap --script smb-protocols,smb-security-mode -p 445 192.168.1.10
```


# Phase 6 - Manual Validation

Use the appropriate protocol-specific tooling rather than continuing to stack Nmap scripts indefinitely.


# Web Server Example

Initial:

```bash
nmap -p- 192.168.1.50
```

Representative result:

```text
22/tcp   open ssh
8080/tcp open http-proxy
8443/tcp open https-alt
```

Focused:

```bash
nmap -sV -sC -p 22,8080,8443 192.168.1.50
```

Interpretation:

```text
The host exposes SSH and two web-related TCP services.
```

Next:

```text
Open web applications in browser/Burp.

Identify virtual hosts.

Review HTTP headers.

Identify application technology.

Perform content discovery.
```

Do not spend the entire web assessment inside Nmap.


# Active Directory Example

Initial:

```bash
nmap -sV -p 53,88,135,139,389,445,464,636,3268,3269,3389,5985,5986 10.10.10.10
```

Representative result:

```text
53/tcp   open domain
88/tcp   open kerberos-sec
135/tcp  open msrpc
389/tcp  open ldap
445/tcp  open microsoft-ds
636/tcp  open ldaps
3268/tcp open globalcatLDAP
```

This pattern is consistent with Active Directory infrastructure.

It does not by itself prove:

```text
Domain Controller definitively confirmed

Anonymous LDAP available

SMB misconfigured

Kerberos vulnerable
```

Continue with AD-specific enumeration.


# Database Example

Nmap:

```bash
nmap -sV -p 1433,3306,5432 192.168.1.30
```

Representative:

```text
1433/tcp open ms-sql-s
```

Next determine:

```text
Is remote database exposure expected?

Which authentication methods are supported?

Which network zones can reach it?

Does the service reveal unnecessary version information?

Are credentials available within scope?
```


# Scan Result Classification

A useful model:

```text
OPEN PORT
   |
   v
SERVICE IDENTIFIED?
   |
  / \
 No   Yes
 |     |
 v     v
Manual  VERSION
Probe     |
          v
    EXPECTED SERVICE?
        /      \
      Yes       No
      |          |
      v          v
 Config       Investigate
 Review       Exposure
```


# Observation vs Finding

Example observation:

```text
TCP/3389 is reachable from the user network.
```

This is not automatically a vulnerability.

A finding may exist if:

```text
Policy requires RDP to be restricted to an admin network
```

but testing demonstrates:

```text
User VLAN -> TCP/3389 -> Management Server
```

The vulnerability is then the segmentation/access-control weakness, not simply:

```text
RDP open.
```


# Service Version vs Vulnerability

Nmap:

```text
22/tcp open ssh OpenSSH <version>
```

Do not immediately:

```text
Search CVE
    |
    v
Report Critical
```

Instead:

```text
Reported Version
      |
      v
Verify Product
      |
      v
Verify Actual Version
      |
      v
Check Vendor Packaging
      |
      v
Check Backported Fixes
      |
      v
Confirm Vulnerable Configuration
      |
      v
Determine Reachability
      |
      v
Controlled Validation
```


# Backported Patches

Linux distributions frequently backport security fixes without changing the upstream version in the way vulnerability scanners expect.

Therefore banner-based version matching can produce false positives.


# Common False Positives

## Version Detection

Possible reasons:

```text
Custom banner

Reverse proxy

Backported patch

Load balancer

Middlebox

Incomplete fingerprint
```


## Filtered Port

Possible reasons:

```text
Firewall

Host firewall

Cloud ACL

Packet loss

Routing issue
```


## Host Down

Possible reasons:

```text
Discovery probes blocked

ICMP filtered

Firewall

Network path

Host actually offline
```


## Open or Filtered UDP

Possible reasons:

```text
Silent UDP service

Firewall silently dropping probes

Application does not respond to Nmap probe
```


# Common Mistakes

## Only Running Default Scan

```bash
nmap target
```

and stopping.

Problem:

```text
High ports may be missed.
```


## Ignoring UDP

Problem:

```text
DNS, SNMP, NTP, IKE and other UDP services may be missed.
```


## Running `-A` Everywhere

Problem:

```text
Unnecessary probes and noise.
```


## Running Every NSE Script

Problem:

```text
Some scripts are intrusive, brute-force, exploit, fuzzing or DoS related.
```


## Treating `filtered` as `closed`

Problem:

```text
Different network observations.
```


## Treating Version as Confirmed Vulnerability

Problem:

```text
Version identification is not vulnerability confirmation.
```


## Not Saving Output

Problem:

```text
Poor reproducibility and weak evidence.
```


## Scanning Out-of-Scope Addresses

Problem:

```text
Authorisation violation.
```


# Troubleshooting

# Host Appears Down

Try against a known authorised target:

```bash
nmap -Pn 192.168.1.10
```

Then verify routing:

```bash
ip route get 192.168.1.10
```

Check connectivity with appropriate protocol-specific tools.


# Everything Is Filtered

Possible causes:

```text
Firewall

Wrong network

VPN issue

Routing

Cloud ACL

Source restrictions
```

Check:

```bash
ip addr
```

```bash
ip route
```

```bash
nmap --iflist
```


# Nmap Uses Wrong Interface

Check:

```bash
nmap --iflist
```

Then where justified:

```bash
sudo nmap -e <interface> <target>
```


# DNS Is Slow

Disable reverse DNS:

```bash
nmap -n 192.168.1.0/24
```


# Service Detection Takes Too Long

Limit it to identified ports:

```bash
nmap -sV -p 22,80,443 192.168.1.10
```

rather than performing service detection against every port unnecessarily.


# UDP Takes Too Long

Start with:

```bash
sudo nmap -sU --top-ports 100 192.168.1.10
```

Then expand based on the assessment objective.


# Nmap Needs Root

Some scan types require raw-packet privileges.

Use:

```bash
sudo nmap ...
```

when required and authorised.

Do not assume every Nmap feature behaves identically as an unprivileged user.


# Evidence Collection

For important scans record:

```text
Test ID

Timestamp

Nmap version

Source host

Source IP

Source network zone

Target

Target IP

Scan type

Ports

Options

Output

Interpretation
```


# Example Evidence Record

```text
Test ID:
NET-NMAP-004

Timestamp:
2026-09-06 18:30 UTC

Tool:
Nmap

Version:
<installed version>

Source:
Assessment workstation

Source Zone:
Corporate User VLAN

Target:
SRV01

Target IP:
10.10.10.20

Objective:
Identify network services reachable from the user network.

Result:
TCP/443 and TCP/445 were reachable.
TCP/3389 appeared filtered.

Interpretation:
HTTPS and SMB were directly reachable from the assessment
source. RDP could not be conclusively assessed because the
traffic appeared filtered.
```


# Reporting Port Exposure

Avoid:

> Port 445 is open and vulnerable.

Prefer:

> TCP/445 was reachable from the tested user-network segment and responded as an SMB service. Whether this exposure represents a security weakness depends on the intended network-access policy and the authentication and authorisation controls protecting the service.


# Reporting Segmentation

Example:

> Testing from the corporate user VLAN demonstrated direct TCP connectivity to the management interface on `SRV01` over TCP/5985. According to the intended segmentation model, WinRM administration should only be accessible from the administrative network. The observed exposure therefore indicates insufficient network segmentation between the user and management zones.


# Reporting Unsupported Protocol

Example:

> The server accepted SMB connections using an outdated protocol version. Protocol negotiation was independently validated after Nmap identified SMB exposure. Legacy SMB versions should be disabled where no operational dependency remains.

The finding should focus on:

```text
Protocol configuration
```

rather than:

```text
Nmap result
```


# Retesting

Use the same source position whenever possible.

Example before remediation:

```text
User VLAN
   |
   v
TCP/5985
   |
   v
SRV01
   |
   v
open
```

After remediation:

```bash
nmap -Pn -p 5985 --reason 10.10.10.20
```

Then compare against the expected network policy.


# Retest Interpretation

If the result becomes:

```text
5985/tcp filtered
```

and filtering is the intended control, this supports successful remediation.

But also verify:

```text
Same source network

Same target

Same route

Firewall change applied

No alternate management port remains exposed
```


# Compare Before and After

Before:

```text
22/tcp   open
443/tcp  open
445/tcp  open
3389/tcp open
5985/tcp open
```

After:

```text
443/tcp open
```

Then determine whether the reduced exposure matches the intended architecture.


# Detection Perspective

Nmap scanning can be visible through:

```text
Firewall logs

IDS/IPS

NDR

EDR

Host firewall logs

Application logs

SIEM
```


# SYN Scan Telemetry

A broad SYN scan may generate:

```text
One source

Many destination ports

Short time window

Incomplete TCP handshakes
```


# Service Detection Telemetry

`-sV` may generate:

```text
Multiple protocol probes

Unexpected request formats

Application responses

Banner requests
```


# NSE Telemetry

NSE traffic depends entirely on the selected script.

This is why defenders and testers should understand the script rather than treating all NSE activity as equivalent.


# Purple Team Scan Exercise

Objective:

```text
Can defenders detect broad internal network scanning?
```

Controlled procedure:

```text
Authorised Source
      |
      v
Known Test Subnet
      |
      v
Controlled Port Scan
      |
      v
Review Firewall / NDR / SIEM
      |
      v
Determine Detection Coverage
```


# Detection Questions

Ask:

```text
Was the source IP identified?

Was the target range identified?

Was scan behaviour detected?

Was the protocol identified?

Was an alert generated?

How quickly?

Did the SOC investigate?

Could analysts distinguish authorised scanning from suspicious scanning?
```


# Quick Commands

## Discovery

```bash
nmap -sn 192.168.1.0/24
```

## Treat Host as Online

```bash
nmap -Pn 192.168.1.10
```

## Default TCP

```bash
nmap 192.168.1.10
```

## SYN

```bash
sudo nmap -sS 192.168.1.10
```

## Connect

```bash
nmap -sT 192.168.1.10
```

## Full TCP

```bash
nmap -p- 192.168.1.10
```

## Top 100

```bash
nmap --top-ports 100 192.168.1.10
```

## Service Detection

```bash
nmap -sV 192.168.1.10
```

## Default Scripts

```bash
nmap -sC 192.168.1.10
```

## Focused Services

```bash
nmap -sC -sV -p 22,80,443 192.168.1.10
```

## OS Detection

```bash
sudo nmap -O 192.168.1.10
```

## UDP Top Ports

```bash
sudo nmap -sU --top-ports 100 192.168.1.10
```

## Open Only

```bash
nmap --open 192.168.1.10
```

## No DNS

```bash
nmap -n 192.168.1.10
```

## Reason

```bash
nmap --reason 192.168.1.10
```

## Save All Formats

```bash
nmap 192.168.1.10 -oA scans/target
```

## IPv6

```bash
nmap -6 <IPv6-address>
```


# Quick Service Commands

## HTTP

```bash
nmap -sV --script http-title,http-headers -p 80,443,8080,8443 192.168.1.10
```

## TLS

```bash
nmap --script ssl-cert,ssl-enum-ciphers -p 443 192.168.1.10
```

## SSH

```bash
nmap -sV --script ssh2-enum-algos,ssh-hostkey -p 22 192.168.1.10
```

## SMB

```bash
nmap -sV --script smb-protocols,smb-security-mode -p 445 192.168.1.10
```

## LDAP

```bash
nmap -sV -p 389,636,3268,3269 192.168.1.10
```

## Kerberos

```bash
nmap -sV -p 88 192.168.1.10
```

## RDP

```bash
nmap -sV -p 3389 192.168.1.10
```

## WinRM

```bash
nmap -sV -p 5985,5986 192.168.1.10
```

## MSSQL

```bash
nmap -sV -p 1433 192.168.1.10
```

## DNS

```bash
sudo nmap -sU -sV -p 53 192.168.1.10
```

## SNMP

```bash
sudo nmap -sU -sV -p 161 192.168.1.10
```


# Quick Interpretation Table

| Nmap Result | Supports | Does Not Automatically Prove |
|---|---|---|
| `Host is up` | Host responded to discovery | Every service is reachable |
| `open` | Port responded as open | Service is vulnerable |
| `closed` | Host reachable, port not accepting connection | Firewall exists |
| `filtered` | Scan could not determine state because of filtering/no response | Port is closed |
| `open|filtered` | State cannot be distinguished | Service definitely open |
| `-sV` identifies product | Probe matched service fingerprint | Exact patch state |
| OS guess | Network fingerprint resembles OS | Definitive OS identification |
| NSE finding | Script observed expected condition | Vulnerability always confirmed |
| TCP/445 open | SMB network exposure | Anonymous/admin access |
| TCP/3389 open | RDP reachable | User can authenticate |
| TCP/5985 open | Service reachable on expected WinRM port | Remote administration permitted |


# Scan Selection Matrix

| Objective | Starting Command |
|---|---|
| Discover hosts | `nmap -sn <range>` |
| Scan known host despite discovery filtering | `nmap -Pn <host>` |
| Quick TCP scan | `nmap <host>` |
| Full TCP discovery | `nmap -p- <host>` |
| Identify services | `nmap -sV -p <ports> <host>` |
| Run default NSE | `nmap -sC -p <ports> <host>` |
| Top UDP ports | `sudo nmap -sU --top-ports 100 <host>` |
| TLS review | `nmap --script ssl-cert,ssl-enum-ciphers -p 443 <host>` |
| SMB protocol review | `nmap --script smb-protocols -p 445 <host>` |
| Save evidence | `nmap ... -oA <basename>` |


# Practical Assessment Workflow

```text
                       AUTHORISED SCOPE
                              |
                              v
                        TARGET RANGE
                              |
                              v
                        HOST DISCOVERY
                              |
                              v
                       RESPONSIVE HOSTS
                              |
                              v
                    TCP PORT DISCOVERY
                              |
                              v
                      OPEN TCP PORTS
                              |
                    +---------+---------+
                    |                   |
                    v                   v
             SERVICE DETECTION      UDP TRIAGE
                    |                   |
                    +---------+---------+
                              |
                              v
                    PROTOCOL ENUMERATION
                              |
                              v
                      MANUAL VALIDATION
                              |
                              v
                     SECURITY CONTEXT
                              |
                              v
                         EVIDENCE
                              |
                              v
                          REPORT
```


# Nmap Assessment Checklist

## Scope

- [ ] Target IP authorised
- [ ] Target range authorised
- [ ] Exclusions identified
- [ ] Third-party infrastructure excluded
- [ ] Production restrictions reviewed
- [ ] Rate restrictions reviewed
- [ ] NSE restrictions reviewed

## Discovery

- [ ] Host discovery performed where appropriate
- [ ] Discovery limitations understood
- [ ] Known systems tested with `-Pn` where justified
- [ ] DNS considered
- [ ] IPv6 considered where relevant

## TCP

- [ ] Common ports reviewed
- [ ] Full TCP range considered
- [ ] Open ports recorded
- [ ] Closed vs filtered distinguished
- [ ] Service detection performed on relevant ports

## UDP

- [ ] UDP considered
- [ ] Important UDP services prioritised
- [ ] `open|filtered` interpreted correctly
- [ ] Protocol-specific validation performed

## Services

- [ ] HTTP/HTTPS reviewed
- [ ] SSH reviewed
- [ ] SMB reviewed
- [ ] LDAP/Kerberos reviewed where relevant
- [ ] RDP reviewed
- [ ] WinRM reviewed
- [ ] Database services reviewed
- [ ] DNS/SNMP/NTP reviewed where relevant

## NSE

- [ ] Script purpose understood
- [ ] Script help reviewed
- [ ] Intrusive scripts avoided unless authorised
- [ ] DoS scripts not run casually
- [ ] Automated results manually interpreted

## Evidence

- [ ] Nmap version recorded
- [ ] Source IP recorded
- [ ] Source zone recorded
- [ ] Target recorded
- [ ] Timestamp recorded
- [ ] Command recorded
- [ ] Raw output saved
- [ ] Important results interpreted
- [ ] Limitations documented

## Reporting

- [ ] Open port not automatically called vulnerability
- [ ] Version not automatically called vulnerable
- [ ] Filtering interpreted correctly
- [ ] Intended architecture considered
- [ ] Root cause identified
- [ ] Security consequence explained

## Retest

- [ ] Same network position used where possible
- [ ] Same target used
- [ ] Relevant port rescanned
- [ ] Intended policy compared
- [ ] Alternative exposure checked
- [ ] Evidence saved


# Final Testing Principle

Nmap is best used as a **discovery and validation tool**, not as a substitute for understanding the service behind the port.

Do not stop at:

```text
PORT
 |
 v
SERVICE
```

Continue:

```text
PORT
 |
 v
SERVICE
 |
 v
PROTOCOL
 |
 v
CONFIGURATION
 |
 v
ACCESS CONTROL
 |
 v
APPLICATION
 |
 v
SECURITY CONSEQUENCE
```

For every important Nmap result ask:

```text
Why is this port reachable?

From which network position?

Is the exposure intended?

What service actually responds?

How confident is the fingerprint?

What authentication protects it?

What protocol configuration is in use?

Does the result require manual validation?

What does this exposure enable?

What would remediation change?

How will I prove the change during retesting?
```


# Related Cheatsheets

- [Networking Cheatsheet](networking.md)
- [Web Application Security Cheatsheet](web.md)
- [Active Directory Cheatsheet](active-directory.md)
- [NetExec Cheatsheet](netexec.md)
- [Impacket Cheatsheet](impacket.md)
- [Windows Cheatsheet](windows.md)
- [Linux Cheatsheet](linux.md)


# Detailed Notes

- [Web Application Security](../web/index.md)
- [Active Directory](../active-directory/index.md)
- [Windows](../windows/index.md)
- [Linux](../linux/index.md)
- [Red Teaming](../red-teaming/index.md)


# References

- [Nmap Official Website](https://nmap.org/){ target="_blank" rel="noopener noreferrer" }
- [Nmap Reference Guide](https://nmap.org/book/man.html){ target="_blank" rel="noopener noreferrer" }
- [Nmap Network Scanning](https://nmap.org/book/){ target="_blank" rel="noopener noreferrer" }
- [Nmap Scripting Engine](https://nmap.org/book/nse.html){ target="_blank" rel="noopener noreferrer" }
- [NSE Script Documentation](https://nmap.org/nsedoc/){ target="_blank" rel="noopener noreferrer" }
- [Nmap Port Scanning Basics](https://nmap.org/book/man-port-scanning-basics.html){ target="_blank" rel="noopener noreferrer" }
- [Nmap Service and Version Detection](https://nmap.org/book/man-version-detection.html){ target="_blank" rel="noopener noreferrer" }
- [Nmap Host Discovery](https://nmap.org/book/man-host-discovery.html){ target="_blank" rel="noopener noreferrer" }
- [Nmap Output](https://nmap.org/book/man-output.html){ target="_blank" rel="noopener noreferrer" }


!!! tip "Discover broadly, enumerate narrowly"
    Port discovery and detailed service enumeration do not need to be the same scan. First identify the exposed attack surface, then run focused service detection and protocol-specific checks against the ports that actually matter.


!!! tip "Use --reason when the result is unclear"
    `--reason` can make `open`, `closed`, `filtered` and host-discovery results easier to understand because it exposes the response or lack of response that contributed to Nmap's classification.


!!! tip "Save the raw scan"
    Use `-oA` or another appropriate output option for important assessment scans. The raw result is far more useful during reporting and retesting than relying on terminal history or screenshots alone.


!!! warning "An open port is an observation, not automatically a vulnerability"
    The security significance depends on the exposed service, intended network architecture, authentication, protocol configuration and what the reachable service actually permits.


!!! warning "NSE scripts have different operational impacts"
    Before running unfamiliar scripts, inspect their documentation and category. Discovery and safe scripts are operationally different from brute-force, intrusive, exploit, fuzzing and denial-of-service scripts.
