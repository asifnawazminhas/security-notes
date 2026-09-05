---
title: Red Team Infrastructure
description: Red team infrastructure architecture, VPS hardening, domains, DNS, TLS, redirectors, command-and-control infrastructure, payload hosting, logging, firewalling, operational security, and cleanup for authorised security assessments.
---

# Red Team Infrastructure

Red team infrastructure is the collection of systems and services used to support an authorised security assessment.

Depending on the engagement, infrastructure can include:

```text
Operator Workstations
        |
        v
VPN / Management Network
        |
        v
Team Server
        |
        +--------------------+
        |                    |
        v                    v
 C2 Redirector         Payload Server
        |                    |
        v                    v
     Internet             Internet
        |                    |
        +---------+----------+
                  |
                  v
         Authorised Targets
```

Infrastructure should be designed before an engagement begins.

A poorly secured red team server can expose:

```text
Customer information
Credentials
Payloads
Infrastructure addresses
Operator activity
Assessment evidence
Internal network information
C2 configuration
Attack paths
```

Treat red team infrastructure as sensitive production infrastructure for the duration of the engagement.


---

# Infrastructure Principles

A useful infrastructure design follows several principles:

```text
Isolation
Least Privilege
Minimal Exposure
Strong Authentication
Encryption
Logging
Segmentation
Recoverability
Attribution Control
Cleanup
```

The objective is not simply to make infrastructure difficult to discover.

The infrastructure must also remain secure, controllable, auditable, and removable.


---

# High-Level Architecture

A simple architecture can look like:

```text
                    RED TEAM

                Operator Workstation
                        |
                        |
                 Encrypted Access
                        |
                        v
                +---------------+
                |  Team Server  |
                +---------------+
                        |
                        |
              Internal C2 Traffic
                        |
                        v
                +---------------+
                | C2 Redirector |
                +---------------+
                        |
                        |
                     HTTPS
                        |
                        v
                    Internet
                        |
                        v
               Authorised Target
```

A more complete environment may separate multiple infrastructure functions:

```text
                         Operators
                             |
                             v
                     Management VPN
                             |
              +--------------+--------------+
              |                             |
              v                             v
        Team Server                    Logging Server
              |
              |
      +-------+-------+
      |               |
      v               v
 C2 Redirector   Payload Redirector
      |               |
      v               v
  c2.example      files.example
      |               |
      +-------+-------+
              |
              v
           Internet
              |
              v
      Authorised Environment
```


---

# Infrastructure Roles

It is useful to separate infrastructure by purpose.

| Component | Purpose |
|---|---|
| Operator workstation | Assessment operations |
| Management VPN | Restricted administrative access |
| Team server | C2 backend or collaboration service |
| C2 redirector | Internet-facing communication relay |
| Payload server | Controlled delivery of assessment files |
| Web redirector | HTTP routing and filtering |
| DNS infrastructure | Domain resolution |
| Logging server | Central infrastructure telemetry |
| Repository | Configuration and controlled scripts |
| Evidence storage | Assessment evidence |
| Monitoring | Infrastructure availability and security |

Not every engagement requires every component.


---

# Separate Management and Operational Traffic

Where practical, separate:

```text
Management Traffic
        |
        +--> SSH
        +--> VPN
        +--> Administration

Operational Traffic
        |
        +--> HTTPS
        +--> C2
        +--> Payload Delivery
        +--> Redirectors
```

Do not expose administrative interfaces publicly unless necessary.


---

# Management Network

A management network provides a controlled path between operators and red team infrastructure.

Example:

```text
Operator
   |
   v
VPN
   |
   v
Management Network
   |
   +--> Team Server
   |
   +--> Redirector
   |
   +--> Logging
   |
   +--> Payload Server
```

Potential technologies include:

```text
WireGuard
OpenVPN
Cloud private networking
SSH bastion
Provider VPN
```

Administrative services should preferably only accept connections from trusted management addresses.


---

# VPS Infrastructure

Virtual private servers are commonly used for temporary assessment infrastructure.

Potential uses include:

```text
C2 team server
Redirector
Payload server
VPN server
Logging server
DNS infrastructure
Web server
Testing utilities
```

Infrastructure should be provisioned specifically for the engagement where practical.


---

# VPS Baseline

Before installing assessment tooling:

```text
Update operating system
Create administrative user
Configure SSH
Configure firewall
Disable unnecessary services
Configure logging
Configure time synchronisation
Verify DNS
Configure automatic security updates where appropriate
Document installed services
```

Example Debian/Kali update:

```bash
sudo apt update
```

```bash
sudo apt full-upgrade -y
```


---

# Administrative User

Avoid routine direct root login where practical.

Create a dedicated administrative account:

```bash
sudo adduser operator
```

Add appropriate administrative privileges where required:

```bash
sudo usermod -aG sudo operator
```

Verify:

```bash
id operator
```


---

# SSH Hardening

SSH is commonly used to administer red team infrastructure.

Important controls include:

```text
Public-key authentication
Restricted source addresses
No unnecessary root login
No weak passwords
Modern cryptography
Logging
Rate limiting where appropriate
```

Generate a dedicated engagement key where required:

```bash
ssh-keygen -t ed25519
```

Example:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/redteam-engagement
```

Connect:

```bash
ssh -i ~/.ssh/redteam-engagement operator@SERVER
```


---

# SSH Configuration

Server configuration is commonly located at:

```text
/etc/ssh/sshd_config
```

Review the effective configuration:

```bash
sudo sshd -T
```

Useful settings to review include:

```text
PermitRootLogin
PasswordAuthentication
PubkeyAuthentication
AllowUsers
AllowGroups
MaxAuthTries
LogLevel
```

After changing SSH configuration, validate before restarting:

```bash
sudo sshd -t
```

Do not close the existing administrative session until a second session has successfully connected using the new configuration.


---

# Firewall

Expose only services required for the engagement.

A simple model:

```text
Internet
   |
   +--> 443/tcp  Redirector
   |
   X--> 22/tcp  Team Server
   |
   X--> Other Management Ports
```

Administrative access should preferably originate from:

```text
Known operator IP
Management VPN
Bastion
Private cloud network
```


---

# UFW

Example baseline:

```bash
sudo ufw default deny incoming
```

```bash
sudo ufw default allow outgoing
```

Allow SSH from an authorised management address:

```bash
sudo ufw allow from 203.0.113.10 to any port 22 proto tcp
```

Allow HTTPS:

```bash
sudo ufw allow 443/tcp
```

Enable:

```bash
sudo ufw enable
```

Review:

```bash
sudo ufw status numbered
```

Use addresses and ports appropriate for the actual engagement.


---

# nftables

Modern Linux systems may use nftables.

Inspect:

```bash
sudo nft list ruleset
```

Also understand whether another firewall manager is generating the ruleset.

Potential managers include:

```text
UFW
firewalld
Docker
Cloud firewall
Provider firewall
```


---

# Cloud Firewall

Do not rely exclusively on the host firewall where the provider supports an external firewall.

A useful layered model is:

```text
Internet
   |
   v
Provider Firewall
   |
   v
Host Firewall
   |
   v
Application
```

If one layer is accidentally changed, another still limits exposure.


---

# Service Exposure

Check listening services:

```bash
ss -lntup
```

Alternative:

```bash
sudo ss -lntup
```

Review:

```text
Listening address
Port
Protocol
Process
Expected exposure
Firewall rule
```

Unexpected listeners should be investigated.


---

# Domain Strategy

Domains can provide stable names for assessment infrastructure.

A simple structure might be:

```text
example-assessment.net
        |
        +--> c2.example-assessment.net
        |
        +--> files.example-assessment.net
        |
        +--> vpn.example-assessment.net
        |
        +--> logs.example-assessment.net
```

Avoid using production organisational domains for temporary assessment infrastructure unless explicitly planned.


---

# DNS

DNS records commonly include:

```text
A
AAAA
CNAME
TXT
MX
CAA
```

For a basic HTTPS service:

```text
c2.example-assessment.net
        |
        v
A Record
        |
        v
203.0.113.20
```

Check:

```bash
dig c2.example-assessment.net
```

```bash
dig +short c2.example-assessment.net
```

Alternative:

```bash
nslookup c2.example-assessment.net
```


---

# DNS Operational Security

DNS can reveal infrastructure relationships.

Consider whether multiple services unnecessarily resolve to the same address.

Example:

```text
c2.example.net   ----+
files.example.net ---+--> Same VPS
vpn.example.net  ----+
```

This may be acceptable for a small lab but creates stronger infrastructure correlation.

A more separated architecture might use:

```text
c2.example.net
      |
      v
Redirector A

files.example.net
      |
      v
Redirector B

vpn.example.net
      |
      v
Management Host
```


---

# TLS

Internet-facing HTTP infrastructure should normally use TLS.

```text
Target
   |
   v
HTTPS
   |
   v
Redirector
```

TLS provides:

```text
Transport encryption
Server authentication
Integrity
Normal HTTPS transport
```

Certificates should be valid for the configured hostname.


---

# Certificate Management

Certificate automation can be performed using tools such as:

```text
Certbot
acme.sh
Caddy
Traefik
Cloud provider certificate services
```

Certificate renewal should be tested before an engagement starts.

Check certificate information:

```bash
openssl s_client -connect example-assessment.net:443 -servername example-assessment.net
```


---

# Redirectors

A redirector separates internet-facing traffic from backend infrastructure.

```text
Authorised Target
       |
       v
   Redirector
       |
       v
   Team Server
```

Benefits can include:

```text
Backend isolation
Reduced direct exposure
Traffic filtering
Central TLS termination
Logging
Infrastructure replacement
Separation of responsibilities
```


---

# Why Use Redirectors?

Without a redirector:

```text
Target
   |
   v
Team Server
```

The backend service is directly exposed.

With a redirector:

```text
Target
   |
   v
Redirector
   |
   v
Backend
```

The backend can be restricted so that only the redirector is permitted to connect to the relevant service.


---

# Redirector Security Model

A useful design is:

```text
                    Internet
                       |
                       v
                +-------------+
                | Redirector  |
                +-------------+
                       |
             Restricted Route
                       |
                       v
                +-------------+
                | Team Server |
                +-------------+
                       |
                       v
                Management VPN
```

The team server should not accept arbitrary internet connections where avoidable.


---

# Reverse Proxy

Common reverse-proxy technologies include:

```text
Nginx
Apache
Caddy
HAProxy
Traefik
Cloud load balancers
```

A reverse proxy can provide:

```text
TLS termination
Request filtering
Access logging
Backend routing
Rate limiting
Header handling
Health checks
```


---

# Nginx Baseline

A minimal generic HTTPS reverse proxy may resemble:

```nginx
server {
    listen 443 ssl;
    server_name example-assessment.net;

    ssl_certificate /etc/letsencrypt/live/example-assessment.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example-assessment.net/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Validate configuration:

```bash
sudo nginx -t
```

Reload:

```bash
sudo systemctl reload nginx
```

This is only a generic reverse-proxy example. Actual routing depends on the authorised service being proxied.


---

# Redirector Filtering

Redirectors can reject traffic that does not match expected engagement characteristics.

Possible controls include:

```text
Allowed paths
Expected methods
Expected Host header
Source restrictions
Request size limits
Rate limits
Known engagement identifiers
Backend authentication
```

Filtering should be designed carefully so that it does not create an availability issue for legitimate infrastructure.


---

# Backend Restriction

The backend should preferably accept operational traffic only from known redirectors.

Conceptually:

```text
Internet
   |
   X
Team Server

Redirector
   |
   v
Team Server
```

Firewall logic:

```text
ALLOW Redirector -> Backend Port
DENY  Internet   -> Backend Port
```


---

# Command-and-Control Infrastructure

C2 infrastructure is one component of the overall red team infrastructure.

```text
Operator
   |
   v
Team Server
   |
   v
Redirector
   |
   v
Authorised Test Host
```

The team server may maintain:

```text
Agent state
Tasking
Operator sessions
Assessment metadata
Logs
Configuration
```

Because of this, the team server should receive stronger protection than a disposable public redirector.


---

# C2 Separation

Where practical:

```text
                    Internet
                       |
                       v
                  Redirector
                       |
                       v
                Restricted Port
                       |
                       v
                  Team Server
                       |
                       v
                 Management VPN
                       |
                       v
                    Operator
```

Avoid exposing the C2 administrative interface directly to the internet.


---

# C2 Frameworks

Common authorised security testing and adversary simulation frameworks include:

```text
Cobalt Strike
Sliver
Mythic
Havoc
Metasploit
CALDERA
```

Each framework has different:

```text
Architecture
Listener models
Agent formats
Authentication
Logging
Network behaviour
Extensibility
Operational requirements
```

Framework selection should be based on engagement requirements rather than familiarity alone.


---

# C2 Is Covered Separately

This infrastructure page focuses on the systems supporting C2.

The dedicated C2 page should cover:

```text
C2 architecture
Team server
Listeners
Agents
Transport
HTTP / HTTPS
DNS concepts
Redirectors
Profiles
Tasking
Sleep and jitter
Operational security
Detection surfaces
Logging
Cleanup
Framework comparison
```

See:

[Command and Control](command-and-control.md)


---

# Payload Infrastructure

Payload delivery should preferably be separated from management infrastructure.

Example:

```text
Payload Repository
       |
       v
Payload Server
       |
       v
HTTPS
       |
       v
Authorised Target
```

The server should expose only the files required for the engagement.


---

# Simple HTTP Server

For a temporary lab or controlled transfer:

```bash
python3 -m http.server 8000
```

Bind to a specific interface where appropriate:

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

For internet-facing engagement infrastructure, a properly configured HTTPS web server is preferable to an unauthenticated temporary development server.


---

# Payload Directory

Use a dedicated directory:

```text
/srv/redteam-files/
```

Example structure:

```text
/srv/redteam-files/
├── tools/
├── scripts/
├── test-files/
└── checksums/
```

Do not expose:

```text
SSH keys
Operator credentials
Customer evidence
C2 configuration
Internal notes
Source repositories
API tokens
```


---

# File Integrity

Record hashes for important assessment files.

Linux:

```bash
sha256sum file.bin
```

PowerShell:

```powershell
Get-FileHash .\file.bin -Algorithm SHA256
```

This helps establish exactly which file was delivered during the assessment.


---

# Payload Tracking

Maintain a simple inventory:

| File | Purpose | SHA-256 | Target | Cleanup Required |
|---|---|---|---|---|
| `test.bin` | Controlled validation | `<hash>` | Test host | Yes |
| `enum.ps1` | Enumeration | `<hash>` | Test host | Yes |

Tracking becomes increasingly important during larger engagements.


---

# Infrastructure Logging

Infrastructure should produce enough telemetry to reconstruct what occurred.

Potential sources include:

```text
SSH logs
VPN logs
Firewall logs
Nginx logs
Apache logs
C2 logs
System journal
Authentication logs
Cloud audit logs
DNS logs
Provider logs
```

On systemd systems:

```bash
journalctl
```

SSH events may be available through:

```bash
journalctl -u ssh
```

or:

```bash
journalctl -u sshd
```

depending on the distribution.


---

# Web Logs

Nginx commonly stores logs under:

```text
/var/log/nginx/access.log
/var/log/nginx/error.log
```

Monitor:

```bash
sudo tail -f /var/log/nginx/access.log
```

These logs can help distinguish:

```text
Assessment traffic
Internet scanning
Search-engine crawlers
Automated exploitation
Unexpected third-party traffic
```


---

# Central Logging

For larger engagements:

```text
Redirector A ----+
                 |
Redirector B ----+----> Logging Server
                 |
Payload Host ----+
                 |
Team Server -----+
```

Centralisation reduces dependence on ephemeral hosts.


---

# Time Synchronisation

Accurate timestamps are critical for comparing red team activity with defensive telemetry.

Check:

```bash
timedatectl
```

A useful standard is:

```text
UTC for infrastructure logs
UTC for operator timeline
UTC for evidence
```

If local time is used, document the timezone explicitly.


---

# Operator Timeline

Record significant activity.

Example:

```text
2026-09-05 08:32 UTC
Operator: A
Source: Redirector-01
Target: TEST-WKS-01
Action: Connectivity validation
Result: Successful
```

This allows blue-team telemetry to be correlated later.


---

# Infrastructure Inventory

Maintain an inventory.

| Host | Role | Public IP | Management | Exposed Services |
|---|---|---|---|---|
| `rt-team-01` | Team server | Restricted | VPN | Backend only |
| `rt-redir-01` | C2 redirector | Public | VPN/SSH | 443 |
| `rt-files-01` | Payload server | Public | VPN/SSH | 443 |
| `rt-log-01` | Logging | Restricted | VPN | Internal |

Avoid storing real passwords in the inventory.


---

# Secrets Management

Infrastructure secrets can include:

```text
SSH private keys
VPN keys
API tokens
Cloud credentials
DNS provider tokens
TLS private keys
C2 credentials
Repository tokens
```

Do not store them directly in source-controlled configuration files.


---

# Environment Files

If environment files are required:

```text
.env
```

Ensure they are excluded from Git:

```gitignore
.env
*.key
*.pem
secrets/
credentials/
```

Verify:

```bash
git status
```

Also check repository history if a secret was accidentally committed.


---

# Repository Security

Red team repositories may contain sensitive operational information.

Repositories should be:

```text
Private where appropriate
Access controlled
Protected with MFA
Free from credentials
Free from customer data
Reviewed before publication
```

Never assume deleting a secret from the latest commit removes it from repository history.


---

# Backups

Infrastructure configuration should be recoverable.

Useful items to back up include:

```text
Firewall configuration
Reverse-proxy configuration
Infrastructure inventory
DNS configuration
C2 configuration
Logging configuration
Deployment scripts
```

Do not create unnecessary backups of customer-derived sensitive information.


---

# Monitoring Infrastructure

Red team infrastructure is exposed to the internet and can itself be attacked.

Monitor:

```text
Unexpected SSH attempts
Unexpected web traffic
Port scanning
Authentication failures
CPU usage
Disk usage
Memory usage
Certificate expiry
Service failures
Unexpected processes
Unexpected listeners
```

Check processes:

```bash
ps aux
```

Check listening ports:

```bash
ss -lntup
```


---

# Health Checks

Simple infrastructure checks can include:

```bash
systemctl status nginx
```

```bash
systemctl status ssh
```

```bash
df -h
```

```bash
free -h
```

```bash
uptime
```

```bash
ss -lntup
```


---

# External Validation

After applying firewall rules, verify exposure externally.

For example:

```bash
nmap -Pn -p 22,80,443 SERVER
```

The expected result should match the infrastructure design.

Example:

```text
22/tcp   filtered
80/tcp   closed
443/tcp  open
```

Do not rely only on local firewall output.


---

# Cloud Metadata

If infrastructure runs in a cloud environment, protect cloud credentials and metadata access.

Understand:

```text
Instance roles
Metadata service
API credentials
Security groups
Firewall rules
Snapshots
Object storage
Cloud audit logs
IAM permissions
```


---

# Infrastructure Segmentation

Avoid putting every function on one unrestricted VPS for substantial engagements.

Instead:

```text
              Internet
                 |
          +------+------+
          |             |
          v             v
      Redirector     Payload Host
          |
          v
      Team Server
          |
          v
      Management
```

Segmentation reduces the consequences of compromise of one component.


---

# Small Engagement Architecture

A small authorised lab may reasonably use:

```text
             VPS
              |
      +-------+-------+
      |               |
     SSH             HTTPS
      |               |
 Operator          Test Host
```

The simpler design is easier to manage but provides less isolation.


---

# Medium Engagement Architecture

```text
                       Internet
                          |
             +------------+------------+
             |                         |
             v                         v
       C2 Redirector              Payload Host
             |
             v
         Team Server
             |
             v
       Management VPN
             |
             v
          Operators
```


---

# Larger Engagement Architecture

```text
                            Internet
                               |
                +--------------+--------------+
                |                             |
                v                             v
          Redirector A                  Redirector B
                |                             |
                +--------------+--------------+
                               |
                               v
                          Team Server
                               |
                  +------------+------------+
                  |                         |
                  v                         v
             Logging                    Storage
                  |                         |
                  +------------+------------+
                               |
                               v
                        Management VPN
                               |
                    +----------+----------+
                    |                     |
                    v                     v
                Operator A            Operator B
```


---

# Infrastructure Attribution

Infrastructure naturally leaves observable information.

Examples include:

```text
IP addresses
Hosting provider
ASN
Domain registration
DNS history
TLS certificates
HTTP headers
Server banners
Open ports
Favicon hashes
Certificate transparency
Shared infrastructure
```

This is relevant when assessing how infrastructure may be identified or correlated.

The objective should not be to impersonate unrelated organisations or deceive uninvolved third parties.


---

# HTTP Headers

Inspect:

```bash
curl -I https://example-assessment.net/
```

Unnecessary headers can expose:

```text
Server software
Framework
Version information
Proxy technology
Backend behaviour
```

Reduce unnecessary information where practical.


---

# Server Banners

Review:

```bash
curl -I https://example-assessment.net/
```

and:

```bash
nmap -sV SERVER
```

Ensure the exposed services match the intended architecture.


---

# Redirector Failure

Plan for redirector loss.

```text
Redirector Fails
      |
      v
DNS Change
      |
      v
Replacement Redirector
      |
      v
Backend Restored
```

Document enough configuration to rebuild disposable infrastructure quickly.


---

# Team Server Failure

Team-server loss can be more serious.

Consider:

```text
Configuration backup
Engagement logs
Operator state
Infrastructure documentation
Recovery procedure
Access credentials
```

Backups must themselves be protected.


---

# Kill Switch

The engagement should have a method to rapidly stop operational infrastructure.

Possible actions include:

```text
Disable listener
Stop redirector
Block backend
Remove DNS record
Revoke credentials
Stop payload hosting
Disable cloud resource
```

The exact mechanism depends on the architecture.


---

# Emergency Shutdown

A simple shutdown model:

```text
Emergency
   |
   v
Stop Operational Services
   |
   v
Block External Traffic
   |
   v
Preserve Required Logs
   |
   v
Notify Engagement Lead
   |
   v
Investigate
```


---

# Cleanup Tracking

Every temporary infrastructure component should have an owner and cleanup requirement.

Example:

| Resource | Created | Purpose | Cleanup |
|---|---|---|---|
| VPS | Yes | Redirector | Destroy |
| Domain | Yes | Assessment | Review/retire |
| DNS record | Yes | C2 | Remove |
| TLS certificate | Yes | HTTPS | Revoke/expire |
| Firewall rule | Yes | Management | Remove |
| Cloud token | Yes | Automation | Revoke |
| SSH key | Yes | Administration | Revoke/archive appropriately |


---

# Infrastructure Decommissioning

At the end of an engagement:

```text
Stop operational services
        |
        v
Collect required logs
        |
        v
Remove assessment files
        |
        v
Revoke temporary credentials
        |
        v
Remove DNS records
        |
        v
Remove firewall exceptions
        |
        v
Destroy temporary servers
        |
        v
Verify cleanup
```


---

# Evidence Retention

Retain only information required by:

```text
Engagement agreement
Reporting requirements
Legal requirements
Customer policy
Evidence policy
```

Sensitive material should not remain indefinitely on disposable infrastructure.


---

# Infrastructure Checklist

## Planning

- [ ] Infrastructure requirements defined
- [ ] Engagement scope reviewed
- [ ] Required services identified
- [ ] Hosting provider selected
- [ ] Domains prepared
- [ ] DNS plan prepared
- [ ] Logging requirements defined
- [ ] Cleanup process defined

## VPS

- [ ] Operating system updated
- [ ] Administrative account created
- [ ] SSH hardened
- [ ] Root login policy reviewed
- [ ] Password authentication policy reviewed
- [ ] Unnecessary services disabled
- [ ] Time synchronisation verified

## Firewall

- [ ] Default-deny inbound policy considered
- [ ] Management ports restricted
- [ ] Public services explicitly allowed
- [ ] Provider firewall configured
- [ ] Host firewall configured
- [ ] External exposure verified

## DNS and TLS

- [ ] DNS records correct
- [ ] TLS certificates valid
- [ ] Certificate renewal tested
- [ ] Backend addresses not unnecessarily exposed
- [ ] DNS relationships reviewed

## Redirectors

- [ ] Redirector isolated from backend
- [ ] Backend restricted to redirector
- [ ] TLS configured
- [ ] Access logging enabled
- [ ] Filtering reviewed
- [ ] Recovery procedure documented

## C2

- [ ] Team server restricted
- [ ] Administrative interface protected
- [ ] Operator authentication configured
- [ ] Redirector architecture verified
- [ ] C2 logs protected
- [ ] Emergency stop procedure documented

## Payload Hosting

- [ ] Dedicated directory used
- [ ] Only required files exposed
- [ ] File hashes recorded
- [ ] Customer evidence excluded
- [ ] Cleanup inventory maintained

## Logging

- [ ] SSH logging available
- [ ] Firewall logging considered
- [ ] Web logs enabled
- [ ] C2 logs retained as required
- [ ] Clock synchronisation verified
- [ ] Operator timeline maintained

## Secrets

- [ ] Secrets excluded from Git
- [ ] SSH keys protected
- [ ] API tokens protected
- [ ] DNS credentials protected
- [ ] Cloud credentials protected
- [ ] Temporary credentials tracked

## Cleanup

- [ ] Temporary accounts removed
- [ ] Temporary keys revoked
- [ ] DNS records removed
- [ ] Firewall exceptions removed
- [ ] Payloads removed
- [ ] Required logs collected
- [ ] VPS instances destroyed where appropriate
- [ ] Cleanup verified


---

# Infrastructure Decision Model

```text
                    Engagement
                        |
                        v
               Infrastructure Needed?
                   /           \
                 No             Yes
                 |               |
                 |               v
                 |        Determine Services
                 |               |
                 |               v
                 |        Publicly Exposed?
                 |          /         \
                 |        No           Yes
                 |        |             |
                 |        |             v
                 |        |        Redirector?
                 |        |          /      \
                 |        |        No        Yes
                 |        |        |          |
                 |        +--------+----------+
                 |                 |
                 |                 v
                 |           Firewall Rules
                 |                 |
                 |                 v
                 |            TLS / DNS
                 |                 |
                 |                 v
                 |             Logging
                 |                 |
                 |                 v
                 |             Validate
                 |                 |
                 +-----------------+
                                   |
                                   v
                              Engagement
                                   |
                                   v
                                Cleanup
```


---

# Final Infrastructure Model

A mature infrastructure design can be represented as:

```text
                    Operators
                        |
                        v
                Management VPN
                        |
                        v
                  Team Server
                        |
              +---------+---------+
              |                   |
              v                   v
       C2 Redirector        Logging System
              |
              v
           Internet
              |
              v
       Authorised Target


Security Controls

Management:
    Restricted access
    Strong authentication
    SSH keys
    VPN

Network:
    Provider firewall
    Host firewall
    Segmentation

Transport:
    TLS
    Valid certificates

Operations:
    Logging
    Monitoring
    Timeline
    Inventory

Recovery:
    Configuration backup
    Replacement infrastructure
    Kill switch

End of Engagement:
    Revoke
    Remove
    Destroy
    Verify
```


---

# Related Notes

- [Red Teaming](./)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Lateral Movement](lateral-movement.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Active Directory](../active-directory/)
- [PrivEsc Explorer](../privesc/)


---

# References

- [MITRE ATT&CK - Command and Control](https://attack.mitre.org/tactics/TA0011/){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [Nginx Documentation](https://nginx.org/en/docs/){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [WireGuard](https://www.wireguard.com/){ target="_blank" rel="noopener noreferrer" }
- [Let's Encrypt](https://letsencrypt.org/){ target="_blank" rel="noopener noreferrer" }
- [UFW Manual](https://manpages.ubuntu.com/manpages/jammy/en/man8/ufw.8.html){ target="_blank" rel="noopener noreferrer" }
- [nftables](https://www.netfilter.org/projects/nftables/){ target="_blank" rel="noopener noreferrer" }
- [Sliver](https://github.com/BishopFox/sliver){ target="_blank" rel="noopener noreferrer" }
- [Mythic](https://github.com/its-a-feature/Mythic){ target="_blank" rel="noopener noreferrer" }
- [MITRE CALDERA](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [Metasploit Framework](https://github.com/rapid7/metasploit-framework){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Red team infrastructure should only be used to support explicitly authorised security assessments. Restrict infrastructure to approved targets and activities, protect customer information and credentials, maintain appropriate logging, and remove temporary infrastructure when the engagement ends.
