---
title: Lateral Movement
description: Lateral movement methodology for authorised red team assessments, covering Windows and Linux remote administration, SMB, WinRM, RDP, WMI, DCOM, SSH, credential reuse, Kerberos, NTLM, pivoting, Ligolo-ng, Chisel, SSH tunnelling, SOCKS, proxychains, detection, evidence, and remediation.
---

# Lateral Movement

Lateral movement is the process of using an existing authorised foothold to access another system, identity, application, or network segment during a security assessment.

A typical attack path can be represented as:

```text
Initial Access
      |
      v
Workstation A
      |
      v
Credential / Trust
      |
      v
Server B
      |
      v
Additional Network Access
      |
      v
Server C
```

Lateral movement should answer more than:

```text
Can I reach another machine?
```

A useful assessment should determine:

```text
Why was the movement possible?
Which identity enabled it?
Which protocol was used?
Which trust boundary was crossed?
What privilege was obtained?
Which segmentation controls were bypassed or correctly enforced?
Was the activity logged?
Was it detected?
How far could the attack path reasonably continue?
```

Lateral movement should always remain within the approved scope and Rules of Engagement.


---

# Lateral Movement Objectives

Potential objectives include:

```text
Validate credential reuse
Validate administrative access
Test network segmentation
Evaluate remote-management controls
Evaluate identity boundaries
Test east-west monitoring
Validate privileged access design
Evaluate detection and response
Reach an approved assessment objective
```

The objective should not be to access every reachable host.

Stop once sufficient evidence exists to demonstrate the relevant attack path.


---

# Lateral Movement Model

```text
Current Foothold
      |
      v
Identify Identity
      |
      v
Identify Reachable Systems
      |
      v
Identify Trust
      |
      v
Identify Authentication Material
      |
      v
Select Remote Access Method
      |
      v
Confirm Scope
      |
      v
Minimal Validation
      |
      v
New Security Context
      |
      v
Record Detection
```


---

# Lateral Movement vs Pivoting

These concepts are related but different.

## Lateral Movement

Lateral movement establishes access to another system or security context.

```text
Host A
  |
  | Authentication / Remote Administration
  v
Host B
```

Examples:

```text
SMB
WinRM
RDP
SSH
WMI
DCOM
Remote service administration
Application administration
```

## Pivoting

Pivoting uses one system as a network path to reach another network or host.

```text
Operator
   |
   v
Host A
   |
   v
Internal Network
   |
   v
Host B
```

Tools such as:

```text
Ligolo-ng
Chisel
SSH
SOCKS proxies
proxychains
Framework-specific pivots
```

primarily provide network reachability.

They do not by themselves provide authentication to the destination system.

A common attack path therefore combines both concepts:

```text
Pivot
  +
Credential
  +
Remote Protocol
  =
Lateral Movement
```


---

# Before Lateral Movement

Before moving to another system, verify:

```text
Destination is in scope
Identity use is authorised
Credential use is authorised
Protocol is permitted
Testing window permits the activity
Availability requirements are understood
Third-party boundaries are understood
Expected security controls are known
```

Technical reachability does not establish authorisation.


---

# Establish Current Context

Before lateral movement, understand the existing foothold.

On Windows:

```cmd
whoami
```

```cmd
whoami /all
```

```cmd
hostname
```

```cmd
ipconfig /all
```

```cmd
route print
```

PowerShell:

```powershell
Get-NetIPConfiguration
```

```powershell
Get-NetRoute
```

On Linux:

```bash
whoami
```

```bash
id
```

```bash
hostname
```

```bash
ip addr
```

```bash
ip route
```

Determine:

```text
Current identity
Privilege
Network interfaces
Routes
DNS configuration
Domain membership
Reachable networks
Security controls
```


---

# Network Reachability

Lateral movement requires a usable network path.

Conceptually:

```text
Source Host
    |
    v
Network Control
    |
    +--> Allowed
    |
    +--> Blocked
```

Useful questions include:

```text
Can the source reach the destination?
Which ports are reachable?
Does a firewall restrict east-west traffic?
Does the destination accept remote administration?
Does authentication work from this source?
```


---

# Windows Connectivity Testing

PowerShell:

```powershell
Test-NetConnection SERVER -Port 445
```

WinRM:

```powershell
Test-NetConnection SERVER -Port 5985
```

RDP:

```powershell
Test-NetConnection SERVER -Port 3389
```

SSH:

```powershell
Test-NetConnection SERVER -Port 22
```

A successful TCP connection only confirms network reachability.

It does not confirm authentication or authorisation.


---

# Linux Connectivity Testing

Useful options include:

```bash
nc -vz SERVER 22
```

```bash
nc -vz SERVER 445
```

```bash
nc -vz SERVER 3389
```

```bash
nc -vz SERVER 5985
```

Nmap can be useful where scanning the internal segment is permitted:

```bash
nmap -Pn -p 22,135,139,445,3389,5985,5986 SERVER
```

Keep internal scanning proportional to the assessment objective.


---

# Common Lateral Movement Protocols

Common remote-access mechanisms include:

| Method | Common Port | Typical Platform |
|---|---:|---|
| SMB | TCP 445 | Windows |
| WinRM HTTP | TCP 5985 | Windows |
| WinRM HTTPS | TCP 5986 | Windows |
| RDP | TCP 3389 | Windows |
| WMI/DCOM | TCP 135 + dynamic RPC | Windows |
| SSH | TCP 22 | Windows/Linux |
| VNC | TCP 5900+ | Windows/Linux |
| Application administration | Varies | Both |

Ports can differ from defaults.


---

# Credential Reuse

Credential reuse is one of the most important lateral movement conditions.

```text
Host A
   |
   v
Credential
   |
   +--> Host B
   |
   +--> Host C
   |
   +--> Host D
```

Examples include:

```text
Reused local administrator password
Reused service-account credential
Domain account with access to multiple hosts
Shared SSH key
Shared application credential
Cloud identity with access to multiple systems
```

Credential reuse increases the blast radius of a single compromise.


---

# Local Administrator Password Reuse

Consider:

```text
HOST-A
Administrator : Password-A

HOST-B
Administrator : Password-A

HOST-C
Administrator : Password-A
```

Compromise of one local administrator credential can potentially affect multiple systems.

Controls such as Windows LAPS are designed to reduce this risk.

See:

[LAPS](../active-directory/laps.md)


---

# Windows Lateral Movement

Windows environments commonly expose several remote-management mechanisms.

```text
SMB
WinRM
RDP
WMI
DCOM
Remote services
Scheduled administration
PowerShell remoting
SSH
```


---

# SMB

Server Message Block is used for:

```text
File sharing
Administrative shares
Named pipes
Remote administration
Authentication
```

Common port:

```text
TCP 445
```

Basic reachability:

```powershell
Test-NetConnection SERVER -Port 445
```


---

# SMB Shares

From Windows:

```cmd
net view \\SERVER
```

Access an authorised share:

```cmd
dir \\SERVER\SHARE
```

PowerShell:

```powershell
Get-ChildItem \\SERVER\SHARE
```

Access to a share does not automatically imply administrative access.


---

# Administrative Shares

Windows commonly provides administrative shares such as:

```text
ADMIN$
C$
IPC$
```

Their accessibility can indicate elevated remote privileges.

Example validation:

```cmd
dir \\SERVER\C$
```

Use only where the supplied identity is authorised for the target.


---

# NetExec

NetExec can help validate authorised authentication across Windows services.

General SMB syntax:

```bash
nxc smb TARGET -u USER -p 'PASSWORD'
```

For a domain account:

```bash
nxc smb TARGET -d DOMAIN -u USER -p 'PASSWORD'
```

Against an approved host list:

```bash
nxc smb targets.txt -d DOMAIN -u USER -p 'PASSWORD'
```

Avoid broad credential testing unless the engagement explicitly permits it.

See:

[NetExec Cheatsheet](../cheatsheets/netexec.md)


---

# WinRM

Windows Remote Management provides remote management using WS-Management.

Common ports:

```text
5985 - HTTP
5986 - HTTPS
```

Check reachability:

```powershell
Test-NetConnection SERVER -Port 5985
```

PowerShell can test whether WinRM responds:

```powershell
Test-WSMan SERVER
```


---

# PowerShell Remoting

Where authorised and configured:

```powershell
Enter-PSSession -ComputerName SERVER
```

With an approved credential object:

```powershell
$cred = Get-Credential
Enter-PSSession -ComputerName SERVER -Credential $cred
```

For remote command execution:

```powershell
Invoke-Command -ComputerName SERVER -ScriptBlock { hostname }
```

This provides a clean validation of remote administrative access.


---

# Evil-WinRM

Evil-WinRM is commonly used during authorised Windows assessments where WinRM access is available.

Typical syntax:

```bash
evil-winrm -i SERVER -u USER -p 'PASSWORD'
```

It should be treated as a remote administration client rather than proof of a vulnerability.

The finding should explain why the identity had inappropriate remote access if that is the actual issue.


---

# RDP

Remote Desktop Protocol provides interactive graphical access to Windows systems.

Default port:

```text
TCP 3389
```

Check:

```powershell
Test-NetConnection SERVER -Port 3389
```

RDP access can be constrained by:

```text
Firewall
Network Level Authentication
User rights
Remote Desktop Users group
MFA
RD Gateway
Conditional access
Network segmentation
```


---

# Linux RDP Client

FreeRDP can connect to an authorised Windows host:

```bash
xfreerdp /v:SERVER /u:USER
```

Domain identity:

```bash
xfreerdp /v:SERVER /d:DOMAIN /u:USER
```

Prefer interactive password entry rather than placing passwords directly in shell history.


---

# WMI

Windows Management Instrumentation supports remote management.

Conceptually:

```text
Source
  |
  v
RPC Endpoint Mapper
  |
  v
WMI
  |
  v
Target
```

WMI commonly involves:

```text
TCP 135
Dynamic RPC ports
```

PowerShell can query a remote authorised system using CIM where the environment permits it:

```powershell
Get-CimInstance Win32_OperatingSystem -ComputerName SERVER
```

A successful remote query can be sufficient to demonstrate that the identity has remote-management access.


---

# Impacket WMIExec

Impacket includes remote administration utilities frequently used in authorised assessments.

A common WMI authentication form is:

```bash
impacket-wmiexec DOMAIN/USER@SERVER
```

The tool will request the password interactively when needed.

See:

[Impacket Cheatsheet](../cheatsheets/impacket.md)


---

# DCOM

Distributed Component Object Model is another Windows remote-management technology.

It relies heavily on RPC and Windows permissions.

Conceptually:

```text
Source Host
     |
     v
RPC / DCOM
     |
     v
Remote COM Object
     |
     v
Destination
```

DCOM availability does not automatically indicate a vulnerability.

Evaluate:

```text
Which identity can activate remote objects?
Why is that permission required?
Which network segments can access RPC?
Is the activity monitored?
```


---

# Remote Services

Windows service management can provide remote administrative functionality when an identity has appropriate rights.

Conceptually:

```text
Administrator
     |
     v
Service Control Manager
     |
     v
Remote Host
```

From a defensive perspective, remote service creation or modification is highly relevant telemetry.


---

# PsExec Model

PsExec-style administration commonly involves:

```text
Administrative Authentication
        |
        v
SMB
        |
        v
Service Control Manager
        |
        v
Temporary / Remote Service
```

Sysinternals PsExec is a legitimate administrative tool and should not automatically be treated as malicious.

The context determines whether its use is expected.


---

# Impacket PsExec

Impacket provides a PsExec-style remote administration utility:

```bash
impacket-psexec DOMAIN/USER@SERVER
```

Use interactive password entry where possible.

Remote service-based execution is generally noisy and can produce useful defensive telemetry.


---

# SMBExec

Impacket also provides SMB-based remote execution:

```bash
impacket-smbexec DOMAIN/USER@SERVER
```

Different remote administration methods can produce different telemetry.

Choose the method appropriate to the assessment objective rather than attempting every available technique.


---

# Kerberos-Based Lateral Movement

In Active Directory environments, Kerberos can provide authentication to remote services.

Relevant material can include:

```text
Password
NT hash
Kerberos key
TGT
Service ticket
Certificate-derived authentication
```

Kerberos authentication should be understood separately from the remote protocol itself.

For example:

```text
Kerberos Credential
       |
       v
SMB
```

or:

```text
Kerberos Credential
       |
       v
WinRM
```

Use the dedicated notes:

[Kerberos](../active-directory/kerberos.md)

[Kerberos Tickets](../active-directory/kerberos-tickets.md)


---

# Pass-the-Ticket

Where an authorised Kerberos ticket is available, it may be possible to authenticate without using the account password.

Conceptually:

```text
Kerberos Ticket
      |
      v
Target Service
      |
      v
Authenticated Session
```

Use:

[Pass-the-Ticket](../active-directory/pass-the-ticket.md)


---

# Pass-the-Hash

NTLM authentication may permit authentication using password-derived NT hash material in environments where the protocol and service support it.

Conceptually:

```text
NT Hash
   |
   v
NTLM Authentication
   |
   v
Remote Service
```

Use:

[Pass-the-Hash](../active-directory/pass-the-hash.md)

The defensive objective should include reducing NTLM usage, protecting privileged credentials, and limiting where privileged identities can authenticate.


---

# Overpass-the-Hash

Another Active Directory concept involves using password-derived key material to obtain Kerberos authentication material.

Use:

[Overpass-the-Hash](../active-directory/overpass-the-hash.md)


---

# Linux Lateral Movement

SSH is the primary remote-administration protocol on many Linux systems.

Potential access material includes:

```text
Password
SSH private key
SSH certificate
Agent-forwarded identity
Kerberos authentication
Application credential
```


---

# SSH

Basic connection:

```bash
ssh user@SERVER
```

Specific private key:

```bash
ssh -i ~/.ssh/id_ed25519 user@SERVER
```

Specific port:

```bash
ssh -p 2222 user@SERVER
```

Verbose troubleshooting:

```bash
ssh -v user@SERVER
```

Avoid copying private keys unnecessarily between assessment systems.


---

# SSH Key Reuse

A private key may be trusted by multiple systems.

```text
Private Key
    |
    +--> Server A
    |
    +--> Server B
    |
    +--> Server C
```

This can create a lateral movement path if the same identity and key are trusted broadly.

The finding should focus on the actual trust and key-management weakness.


---

# SSH Configuration

SSH configuration can reveal intended relationships:

```bash
cat ~/.ssh/config
```

Potential information includes:

```text
Host aliases
Usernames
Identity files
Jump hosts
Ports
Internal systems
```

This can help identify legitimate administration paths that may also become attack paths after credential compromise.


---

# SSH Agent Forwarding

SSH agent forwarding allows authentication through an intermediate system without placing the private key on that system.

Conceptually:

```text
Operator
   |
   | SSH Agent
   v
Jump Host
   |
   v
Destination
```

It is operationally useful but creates security considerations if the intermediate system is compromised.

Prefer safer architecture such as explicit jump-host configuration where possible and avoid unnecessary agent forwarding.


---

# Pivoting

A foothold may have access to networks that the operator cannot reach directly.

Example:

```text
Operator
   |
   X
10.20.30.0/24


Operator
   |
   v
Compromised / Test Host
   |
   v
10.20.30.0/24
```

A pivot creates a controlled route through the authorised foothold.

Common options include:

```text
Ligolo-ng
Chisel
SSH port forwarding
SOCKS proxying
proxychains
Framework-native pivots
```


---

# Pivoting Decision Model

```text
Destination
    |
    v
Directly Reachable?
   /        \
 Yes         No
  |           |
  |           v
  |       Foothold Has
  |        Route?
  |       /     \
  |     No       Yes
  |     |         |
  |    STOP       v
  |          Pivot Permitted?
  |            /       \
  |          No         Yes
  |          |           |
  |         STOP         v
  |                  Create Pivot
  |                       |
  +-----------------------+
                          |
                          v
                    Validate Route
```


---

# Ligolo-ng

Ligolo-ng is a tunnelling and pivoting tool that can create network access through an authorised agent.

Its major advantage is that it can expose a routed network interface to the operator rather than requiring every application to support a SOCKS proxy.

Conceptually:

```text
Kali / Operator
      |
      v
Ligolo Proxy
      |
      v
Encrypted Tunnel
      |
      v
Ligolo Agent
      |
      v
Internal Network
```


---

# Ligolo-ng Architecture

```text
                   Operator System
                         |
                         v
                  +--------------+
                  | Ligolo Proxy |
                  +------+-------+
                         |
                         | Tunnel
                         |
                  +------+-------+
                  | Ligolo Agent |
                  +------+-------+
                         |
                         v
                  Internal Network
                         |
              +----------+----------+
              |                     |
              v                     v
           Server A              Server B
```


---

# Ligolo-ng Use Case

Suppose:

```text
Operator:
192.0.2.10

Foothold:
10.10.10.25

Internal network reachable by foothold:
172.16.20.0/24
```

The operator cannot directly reach:

```text
172.16.20.0/24
```

but the foothold can.

Ligolo-ng can provide a controlled network path:

```text
Operator
   |
   v
Foothold
   |
   v
172.16.20.0/24
```


---

# Ligolo-ng Proxy

The proxy component runs on the operator-controlled infrastructure.

Exact command-line options can change between releases, so verify the installed version:

```bash
./proxy -h
```

The proxy waits for an authorised Ligolo agent to connect.


---

# Ligolo-ng Agent

The agent runs on the authorised pivot system.

Check available options:

```text
agent -h
```

After the agent establishes a connection to the operator-controlled proxy, the session can be selected from the proxy interface.


---

# Ligolo Interface

Ligolo-ng commonly uses a TUN interface on Linux.

A typical Linux preparation model is:

```bash
sudo ip tuntap add user "$(whoami)" mode tun ligolo
```

Bring it up:

```bash
sudo ip link set ligolo up
```

Verify:

```bash
ip addr show ligolo
```


---

# Ligolo Route

After establishing the authorised session, add only the required internal route.

Example:

```bash
sudo ip route add 172.16.20.0/24 dev ligolo
```

Verify:

```bash
ip route
```

Conceptually:

```text
172.16.20.0/24
      |
      v
ligolo
      |
      v
Pivot Agent
```

Do not add broad routes when only a small authorised network is required.


---

# Ligolo Validation

Once the tunnel is active, normal applications can use the route.

For example:

```bash
nc -vz 172.16.20.10 445
```

or, where internal scanning is permitted:

```bash
nmap -Pn -p 22,445,3389 172.16.20.10
```

The important distinction is:

```text
Ligolo provides network reachability.

It does not provide authentication.
```


---

# Ligolo Double Pivot Concept

Multiple network layers can exist:

```text
Operator
   |
   v
Pivot A
   |
   v
Network B
   |
   v
Pivot B
   |
   v
Network C
```

Multi-hop pivoting increases complexity and should only be used when necessary for the authorised objective.

Record every route and pivot host.


---

# Ligolo Detection

Potential defensive indicators include:

```text
Unexpected outbound connection from pivot host
Long-lived connection
New process
Unusual executable
Unexpected internal connections originating from pivot host
Connection patterns inconsistent with host role
Endpoint security alerts
```

Network routing through a host can make that host appear to initiate connections to systems it does not normally access.


---

# Ligolo Cleanup

After testing:

```text
Stop Ligolo session
Remove temporary agent
Remove TUN route
Remove TUN interface if created for assessment
Verify no process remains
Record cleanup
```

Example route removal:

```bash
sudo ip route del 172.16.20.0/24 dev ligolo
```

Interface removal:

```bash
sudo ip link delete ligolo
```


---

# Chisel

Chisel is a TCP tunnelling tool that operates over HTTP and uses SSH for tunnel security.

It is useful when a SOCKS or specific TCP forwarding model is more appropriate than routed TUN access.

Conceptually:

```text
Operator
   |
   v
Chisel Server
   |
   v
HTTP Transport
   |
   v
Chisel Client
   |
   v
Internal Network
```


---

# Chisel Architecture

```text
                 Operator System
                       |
                       v
                +-------------+
                | Chisel      |
                | Server      |
                +------+------+
                       |
                       | Tunnel
                       |
                +------+------+
                | Chisel      |
                | Client      |
                +------+------+
                       |
                       v
                Internal Network
```


---

# Chisel Reverse SOCKS Concept

A useful authorised pivot model is:

```text
Operator
   |
   v
SOCKS Proxy
   |
   v
Chisel Tunnel
   |
   v
Pivot Host
   |
   v
Internal Network
```

The SOCKS proxy can then be used by proxy-aware applications.


---

# Chisel Server

Review the installed options:

```bash
chisel server --help
```

A reverse-capable server can be configured on operator-controlled infrastructure.

For example, when appropriate for the lab or engagement:

```bash
chisel server --reverse --port 8000
```

Ensure the listening port is permitted by the infrastructure firewall.


---

# Chisel Client

The authorised pivot host connects back to the controlled Chisel server.

Review:

```text
chisel client --help
```

A reverse SOCKS tunnel can be established using the syntax supported by the installed Chisel release.

A commonly used model is:

```text
Pivot Host
    |
    v
Operator Chisel Server
    |
    v
SOCKS Listener
```

Verify the exact release syntax before use rather than assuming options remain unchanged.


---

# Chisel and proxychains

Once a SOCKS listener is available, tools that support SOCKS can use it directly.

Other TCP clients can sometimes be routed using proxychains.

Conceptually:

```text
Application
    |
    v
proxychains
    |
    v
SOCKS
    |
    v
Chisel
    |
    v
Pivot
    |
    v
Target
```


---

# proxychains

ProxyChains can force many TCP applications through a configured proxy.

Configuration is commonly stored under:

```text
/etc/proxychains4.conf
```

or:

```text
/etc/proxychains.conf
```

A SOCKS entry conceptually looks like:

```text
socks5 127.0.0.1 1080
```

Check the local configuration before use.


---

# proxychains Example

After the approved SOCKS pivot is active:

```bash
proxychains4 nc -vz 172.16.20.10 445
```

For a single authorised host:

```bash
proxychains4 nmap -sT -Pn -p 445 172.16.20.10
```

When using Nmap through a SOCKS proxy, TCP connect scanning is generally more appropriate than raw-packet scan types because proxychains operates at the socket API layer.


---

# proxychains Limitations

Not every application or protocol works cleanly through proxychains.

Potential limitations include:

```text
UDP support
ICMP
Raw sockets
DNS behaviour
High-volume scanning
Application-specific networking
Performance
```

A routed TUN approach such as Ligolo-ng can be more convenient when broad TCP reachability is required.


---

# Ligolo-ng vs Chisel

| Feature | Ligolo-ng | Chisel |
|---|---|---|
| Primary model | Routed/TUN pivot | TCP/SOCKS tunnelling |
| Application changes | Usually none after route | Proxy-aware or proxychains |
| Routing experience | Similar to normal network route | Proxy based |
| Specific port forwarding | Possible depending on design | Strong fit |
| SOCKS workflow | Not primary requirement | Common |
| Multi-network testing | Convenient | Possible but more proxy-oriented |

Both can be useful.

Select the tool based on the network architecture and assessment objective.


---

# SSH Local Port Forwarding

SSH can provide simple port forwarding without additional tunnelling software.

Local forwarding:

```bash
ssh -L LOCAL_PORT:DESTINATION:DESTINATION_PORT user@PIVOT
```

Conceptually:

```text
Operator:8443
     |
     v
SSH Tunnel
     |
     v
Pivot
     |
     v
Internal:443
```

Example:

```bash
ssh -L 8443:172.16.20.10:443 user@PIVOT
```

The operator can then connect to:

```text
127.0.0.1:8443
```

and SSH forwards the connection to the authorised internal destination.


---

# SSH Dynamic Port Forwarding

SSH can also create a local SOCKS proxy.

Syntax:

```bash
ssh -D 1080 user@PIVOT
```

Conceptually:

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
Internal Network
```

Configure proxy-aware tools or proxychains to use the local SOCKS listener.


---

# SSH Remote Port Forwarding

Remote forwarding exposes a port on the remote SSH side and forwards it toward a destination reachable from the local side.

General syntax:

```bash
ssh -R REMOTE_PORT:DESTINATION:DESTINATION_PORT user@SERVER
```

Use remote forwarding carefully because it can create a new listening service on the remote side depending on SSH configuration.


---

# SSH Jump Hosts

OpenSSH supports jump hosts using `ProxyJump`.

Example:

```bash
ssh -J user@PIVOT user@DESTINATION
```

Conceptually:

```text
Operator
   |
   v
Jump Host
   |
   v
Destination
```

This is often preferable to unnecessary agent forwarding.


---

# SOCKS Proxying

SOCKS provides an application-level proxy model.

```text
Tool
 |
 v
SOCKS Proxy
 |
 v
Pivot
 |
 v
Destination
```

Common SOCKS versions include:

```text
SOCKS4
SOCKS5
```

SOCKS5 supports additional capabilities, but actual behaviour depends on the proxy implementation.


---

# DNS Through Proxies

DNS deserves particular attention during proxy-based pivoting.

A common mistake is:

```text
Application traffic -> Proxy

DNS query -> Local network
```

This can cause:

```text
Failed hostname resolution
Information leakage
Incorrect routing
Unexpected DNS telemetry
```

Where hostname resolution must occur through the pivot, configure the selected proxy tooling appropriately.


---

# Framework-Native Pivoting

Some C2 frameworks provide their own pivoting capabilities.

Depending on the framework, concepts can include:

```text
SOCKS proxies
Port forwarding
Peer-to-peer agents
Internal listeners
Route management
```

Use the framework's current documentation because implementations and syntax change over time.

Do not deploy a second tunnelling tool when the existing authorised framework already provides the required functionality without unnecessary complexity.


---

# Choosing a Pivot Method

A simple decision model:

```text
Need One Internal TCP Service?
          |
         Yes
          |
          v
   SSH Local Forward
       or Chisel


Need Multiple Proxy-Aware Tools?
          |
         Yes
          |
          v
    SOCKS / Chisel
          |
          v
     proxychains


Need Broad Routed Access?
          |
         Yes
          |
          v
      Ligolo-ng


Already Have C2 Pivot Support?
          |
         Yes
          |
          v
 Consider Framework-Native Pivot
```


---

# Pivot Route Inventory

Record pivot routes during an engagement.

Example:

| Pivot | Source | Reachable Network | Tool | Cleanup |
|---|---|---|---|---|
| `PIVOT-01` | `TEST-WKS01` | `172.16.20.0/24` | Ligolo-ng | Required |
| `PIVOT-02` | `LINUX-JUMP01` | `10.30.5.0/24` | SSH SOCKS | Required |

This becomes especially important when multiple operators are active.


---

# Network Segmentation

Lateral movement frequently reveals segmentation weaknesses.

A strong model might look like:

```text
User Workstations
       |
       X
Domain Controllers


User Workstations
       |
       X
Management Network


Admin Workstations
       |
       v
Management Network
```

Segmentation should follow business and administrative requirements.


---

# Flat Network

A flat network may permit unnecessary east-west connectivity:

```text
Workstation A
     |
     +--> Workstation B
     |
     +--> Server A
     |
     +--> Database
     |
     +--> Management Server
```

Reachability alone is not necessarily a vulnerability.

The assessment should determine whether the access violates the intended security architecture.


---

# Administrative Tiering

Privileged identities should not routinely authenticate to lower-trust systems.

Conceptually:

```text
Tier 0
Domain Controllers
Identity Infrastructure
        |
        X
        |
Tier 2 Workstations
```

If highly privileged credentials are exposed on a normal workstation, the problem may originate from administrative workflow rather than the workstation itself.


---

# Privileged Access Workstations

Dedicated administrative workstations can reduce credential exposure.

```text
Normal Workstation
       |
       X
Tier 0 Administration


Privileged Workstation
       |
       v
Tier 0 Administration
```

The goal is to reduce where privileged credentials and sessions appear.


---

# Windows Firewall

Host firewalls can significantly restrict lateral movement.

For example:

```text
Workstation
   |
   X--> SMB from peer workstations
   |
   X--> WinRM from user networks
   |
   X--> RDP from arbitrary sources
   |
   v
Management traffic from approved admin network
```

Host-based segmentation remains valuable even inside trusted networks.


---

# Authentication Restrictions

Remote access can also be restricted through:

```text
User rights
Local group membership
Authentication policy
MFA
Network Level Authentication
SSH AllowUsers
SSH AllowGroups
Sudo policy
Conditional access
Privileged access management
```


---

# Detection Opportunities

Lateral movement can produce telemetry at several layers.

```text
Source Endpoint
      |
      v
Network
      |
      v
Authentication
      |
      v
Destination Endpoint
      |
      v
EDR
      |
      v
SIEM
```


---

# Windows Authentication Telemetry

Relevant Windows events can include successful and failed logons.

Commonly investigated event IDs include:

```text
4624 - Successful logon
4625 - Failed logon
4648 - Logon using explicit credentials
4672 - Special privileges assigned
```

The usefulness of an event depends on logon type, source, identity, destination, and surrounding activity.


---

# Logon Types

Windows logon types provide useful context.

Examples include:

| Logon Type | Meaning |
|---:|---|
| 2 | Interactive |
| 3 | Network |
| 10 | RemoteInteractive |

Do not interpret the event ID without considering the logon type.


---

# RDP Detection

Potential telemetry includes:

```text
Authentication events
RemoteInteractive logon
Terminal Services logs
Network connection
Source IP
User identity
Session creation
EDR telemetry
```


---

# WinRM Detection

WinRM activity can produce:

```text
Authentication events
WinRM operational logs
PowerShell logs
Process creation
Network connections
EDR telemetry
```

PowerShell remoting can also produce useful script and process telemetry depending on logging configuration.


---

# SMB Detection

Potential SMB lateral movement indicators include:

```text
Network logons
Administrative share access
Remote service activity
Named pipe access
Unusual workstation-to-workstation SMB
Authentication failures
EDR telemetry
```


---

# WMI Detection

WMI-based remote administration can produce:

```text
WMI operational logs
Authentication events
RPC connections
Process creation
EDR alerts
Source-to-destination relationships
```


---

# SSH Detection

Linux SSH telemetry can include:

```text
Successful authentication
Failed authentication
Source address
Username
Public-key fingerprint
Session creation
sudo activity
Command history where applicable
Audit events
```

Logs may be available through:

```bash
journalctl -u ssh
```

or:

```bash
journalctl -u sshd
```

depending on the distribution.


---

# Pivot Detection

Pivoting can alter normal network relationships.

Example:

```text
Normal:

Workstation A ---> Application Server


During Pivot:

Workstation A ---> Database Server
Workstation A ---> Management Server
Workstation A ---> Internal Web Server
```

Useful indicators include:

```text
Unexpected outbound tunnel
Long-lived external connection
New tunnelling process
Unexpected internal connection fan-out
Host contacting unusual network segments
Proxy process creation
New listening ports
```


---

# Ligolo-ng Detection

Potential indicators include:

```text
Ligolo agent process
Unexpected executable
Long-lived connection to external infrastructure
Unusual internal traffic originating from the pivot
EDR alerts
File creation
Network connection telemetry
```

Defenders should correlate:

```text
Process
   +
External Connection
   +
Internal Connection
```


---

# Chisel Detection

Potential indicators include:

```text
Chisel process
Long-lived HTTP connection
SOCKS listener
Unexpected outbound connection
Internal connections originating from pivot
Command-line telemetry
EDR detection
```

Renaming an executable does not remove its behavioural indicators.


---

# SSH Tunnel Detection

SSH tunnelling can be investigated through:

```text
Long-lived SSH sessions
Unusual SSH source/destination relationships
Unexpected local listeners
Unexpected remote listeners
Connection fan-out from jump host
sshd configuration
Process command line
```


---

# Detection Validation

Track whether each lateral movement stage is observed.

Example:

| Activity | Logged | Alerted | Prevented | Investigated |
|---|---|---|---|---|
| SMB authentication | Yes | No | No | No |
| WinRM session | Yes | Yes | No | Yes |
| RDP logon | Yes | Yes | No | Yes |
| Ligolo tunnel | Yes | Yes | No | Yes |
| Internal connection through pivot | Yes | No | No | No |

This creates measurable defensive outcomes.


---

# Lateral Movement Evidence

For each meaningful movement event, record:

```text
Timestamp
Source host
Source identity
Destination host
Protocol
Authentication material type
Privilege obtained
Pivot used
Result
Detection result
Evidence reference
```


---

# Example Evidence

```text
Timestamp:
2026-09-05 13:40 UTC

Source:
TEST-WKS01

Destination:
TEST-SRV02

Identity:
CORP\test-admin

Protocol:
WinRM

Result:
Remote authentication successful

Privilege:
Local administrator

Detection:
Authentication event recorded.
EDR alert generated.
SOC investigation observed.
```


---

# Pivot Evidence

For pivoting, additionally record:

```text
Pivot host
Tool
Tunnel direction
Operator endpoint
Internal route
Destination network
Start time
Stop time
Cleanup
```

Example:

```text
Pivot:
TEST-WKS01

Tool:
Ligolo-ng

Authorised route:
172.16.20.0/24

Purpose:
Reach approved internal test server

Cleanup:
Route removed and temporary agent deleted
```


---

# Candidate vs Confirmed

## Candidate

A possible lateral movement path exists.

Examples:

```text
Port reachable
Credential discovered
User belongs to remote-access group
SSH key discovered
Administrative share visible
```


## Likely

Multiple conditions support practical movement.

Examples:

```text
Credential appears valid
Destination is reachable
Remote service is available
Identity has relevant permissions
```


## Confirmed

Controlled testing demonstrates successful access to the authorised destination.


---

# Lateral Movement Severity

Severity depends on:

```text
Source privilege
Destination privilege
Identity privilege
Credential reuse
Number of reachable systems
Network segmentation
Administrative tier crossed
Detection
Business impact
Attack chaining
```

A single permitted SSH connection between two expected administration systems should not automatically be considered a vulnerability.


---

# Reporting

A useful finding should identify the root cause.

Weak:

```text
WinRM allowed lateral movement.
```

Better:

```text
A domain service account held local administrator privileges on
multiple servers and was permitted to authenticate remotely using
WinRM.

After the account credential became available from the authorised
source host, it was minimally validated against a second in-scope
server, where it provided local administrative access.
```


---

# Reporting Pivoting

Avoid reporting:

```text
Ligolo bypassed the network.
```

unless the evidence actually supports that conclusion.

Better:

```text
The compromised workstation had network connectivity to the
restricted server segment that was not directly reachable from
the assessment infrastructure.

A controlled tunnel through the workstation demonstrated that
this existing network path could be used to reach the approved
server segment.
```

The underlying issue is usually:

```text
Segmentation
Trust
Host access
Firewall policy
```

not the tunnelling tool itself.


---

# Remediation Model

```text
Lateral Movement Path
        |
        v
Identify Root Cause
        |
        +--> Credential Reuse
        |
        +--> Excessive Privilege
        |
        +--> Flat Network
        |
        +--> Remote Management Exposure
        |
        +--> Weak Authentication
        |
        +--> Privileged Session Exposure
        |
        v
Reduce Trust
        |
        v
Improve Detection
        |
        v
Retest
```


---

# Credential Controls

Potential mitigations include:

```text
Windows LAPS
gMSA
Unique credentials
Credential rotation
Managed identities
MFA
Privileged access management
Reduced service-account privilege
Short-lived credentials
```


---

# Network Controls

Potential improvements include:

```text
Host firewall
Network segmentation
Management VLANs
Administrative jump hosts
Privileged access workstations
Restricted east-west SMB
Restricted WinRM
Restricted RDP
Restricted SSH
Zero-trust access controls
```


---

# Remote Administration Controls

Remote administration should be limited to:

```text
Required identities
Required source networks
Required destination systems
Required protocols
Required time periods
```

Avoid:

```text
Any user
   |
   v
Any workstation
   |
   v
Any server
```


---

# Administrative Access Model

Prefer:

```text
Administrator
     |
     v
Privileged Workstation
     |
     v
Management Network
     |
     v
Managed Server
```

rather than:

```text
Administrator
     |
     v
Normal User Workstation
     |
     v
Any Server
```


---

# Pivoting Controls

Reduce unnecessary pivot opportunities through:

```text
Network segmentation
Host firewalls
Outbound filtering
Application control
EDR
Proxy controls
Restricted administration
Network monitoring
DNS monitoring
Least privilege
```


---

# Lateral Movement Checklist

## Context

- [ ] Written authorisation confirmed
- [ ] Current identity known
- [ ] Current privilege known
- [ ] Source host documented
- [ ] Destination scope confirmed
- [ ] Credential use permitted
- [ ] Remote protocol permitted

## Reachability

- [ ] Routes reviewed
- [ ] Network interfaces reviewed
- [ ] Required ports tested
- [ ] Segmentation boundaries understood
- [ ] Third-party networks excluded
- [ ] Scanning remained within scope

## Windows

- [ ] SMB considered
- [ ] WinRM considered
- [ ] RDP considered
- [ ] WMI considered
- [ ] DCOM considered where relevant
- [ ] Remote service administration considered
- [ ] Local administrator reuse considered
- [ ] Kerberos authentication considered
- [ ] NTLM authentication considered
- [ ] Host firewall considered

## Linux

- [ ] SSH considered
- [ ] SSH keys considered
- [ ] SSH configuration considered
- [ ] Agent forwarding considered
- [ ] Jump hosts considered
- [ ] Credential reuse considered
- [ ] Sudo privilege considered after access

## Pivoting

- [ ] Direct route tested first
- [ ] Pivot genuinely required
- [ ] Pivot host in scope
- [ ] Destination network in scope
- [ ] Ligolo-ng considered
- [ ] Chisel considered
- [ ] SSH forwarding considered
- [ ] SOCKS/proxychains considered
- [ ] Framework-native pivot considered
- [ ] Routes kept as narrow as possible
- [ ] Pivot inventory maintained

## Detection

- [ ] Source endpoint telemetry considered
- [ ] Authentication telemetry considered
- [ ] Network telemetry considered
- [ ] Destination endpoint telemetry considered
- [ ] SMB telemetry considered
- [ ] WinRM telemetry considered
- [ ] RDP telemetry considered
- [ ] SSH telemetry considered
- [ ] Tunnel telemetry considered
- [ ] Alerts recorded
- [ ] Response recorded

## Evidence

- [ ] Timestamp recorded
- [ ] Source recorded
- [ ] Destination recorded
- [ ] Identity recorded
- [ ] Protocol recorded
- [ ] Privilege recorded
- [ ] Pivot route recorded where applicable
- [ ] Detection recorded
- [ ] Sensitive credentials redacted

## Cleanup

- [ ] Remote sessions closed
- [ ] Temporary files removed
- [ ] Pivot processes stopped
- [ ] Ligolo routes removed
- [ ] Temporary TUN interfaces removed
- [ ] SOCKS listeners stopped
- [ ] SSH tunnels closed
- [ ] Temporary credentials revoked where applicable
- [ ] Cleanup verified


---

# Lateral Movement Decision Model

```text
                   Current Foothold
                          |
                          v
                  Destination In Scope?
                     /          \
                   No            Yes
                   |              |
                  STOP            v
                           Directly Reachable?
                            /            \
                          Yes             No
                          |                |
                          |                v
                          |          Pivot Available?
                          |           /          \
                          |         No            Yes
                          |         |              |
                          |        STOP            v
                          |                   Establish
                          |                    Pivot
                          |                      |
                          +----------+-----------+
                                     |
                                     v
                              Remote Service?
                               /          \
                             No            Yes
                             |              |
                          Reassess           v
                                      Credential /
                                      Trust Exists?
                                       /        \
                                     No          Yes
                                     |            |
                                  Reassess         v
                                            Validation
                                             Permitted?
                                            /        \
                                          No          Yes
                                          |            |
                                         STOP          v
                                                Minimal Access
                                                     |
                                                     v
                                              Record Context
                                                     |
                                                     v
                                              Objective Proven?
                                                /          \
                                              Yes           No
                                              |              |
                                             STOP       Continue Only
                                                         if Required
```


---

# Lateral Movement Attack Path

```text
Initial Access
      |
      v
Workstation
      |
      v
Credential Access
      |
      v
Reusable Identity
      |
      v
Network Reachability
      |
      +------------------+
      |                  |
      v                  v
 Direct Access         Pivot
      |                  |
      +--------+---------+
               |
               v
        Remote Protocol
               |
               v
          Second Host
               |
               v
       New Security Context
               |
               v
         Further Objective
```


---

# Pivoting Model

```text
                      Operator
                         |
                         |
                  Direct Route?
                    /       \
                  Yes        No
                  |           |
                  |           v
                  |       Pivot Host
                  |           |
                  |     +-----+-----+
                  |     |           |
                  |     v           v
                  |  Ligolo      Chisel
                  |     |           |
                  |     +-----+-----+
                  |           |
                  |           v
                  |      SOCKS / Route
                  |           |
                  +-----------+
                              |
                              v
                       Internal Target
                              |
                              v
                     Remote Authentication
                              |
                              v
                       Lateral Movement
```


---

# Defensive Lateral Movement Model

```text
                        Identity
                           |
                           v
                     Least Privilege
                           |
                           v
                Unique / Managed Credentials
                           |
                           v
                    Network Segmentation
                           |
                           v
                 Restricted Remote Access
                           |
                           v
                      Host Firewall
                           |
                           v
                    Endpoint Security
                           |
                           v
                    Network Monitoring
                           |
                           v
                          SIEM
                           |
                           v
                    Incident Response
```


---

# Final Testing Model

```text
Authorisation
      |
      v
Establish Source Context
      |
      v
Identify Destination
      |
      v
Confirm Scope
      |
      v
Test Reachability
      |
      v
Pivot if Required
      |
      v
Identify Remote Protocol
      |
      v
Identify Credential / Trust
      |
      v
Minimal Authentication
      |
      v
Establish New Context
      |
      v
Measure Detection
      |
      v
Collect Evidence
      |
      v
Stop When Objective Proven
      |
      v
Remove Tunnels and Artifacts
      |
      v
Verify Cleanup
```


---

# Quick Reference

## Windows Reachability

```powershell
Test-NetConnection SERVER -Port 445
Test-NetConnection SERVER -Port 3389
Test-NetConnection SERVER -Port 5985
Test-NetConnection SERVER -Port 5986
Test-NetConnection SERVER -Port 22
```

## Windows Context

```cmd
whoami
whoami /all
hostname
ipconfig /all
route print
```

## SMB

```cmd
net view \\SERVER
dir \\SERVER\SHARE
```

## WinRM

```powershell
Test-WSMan SERVER
Enter-PSSession -ComputerName SERVER
```

## Linux Context

```bash
whoami
id
hostname
ip addr
ip route
```

## SSH

```bash
ssh user@SERVER
```

```bash
ssh -i ~/.ssh/id_ed25519 user@SERVER
```

## SSH Jump Host

```bash
ssh -J user@PIVOT user@DESTINATION
```

## SSH Local Forward

```bash
ssh -L 8443:172.16.20.10:443 user@PIVOT
```

## SSH SOCKS

```bash
ssh -D 1080 user@PIVOT
```

## Ligolo TUN

```bash
sudo ip tuntap add user "$(whoami)" mode tun ligolo
sudo ip link set ligolo up
```

## Ligolo Route

```bash
sudo ip route add 172.16.20.0/24 dev ligolo
```

## Ligolo Cleanup

```bash
sudo ip route del 172.16.20.0/24 dev ligolo
sudo ip link delete ligolo
```

## Chisel Help

```bash
chisel server --help
```

```text
chisel client --help
```

## Chisel Reverse Server

```bash
chisel server --reverse --port 8000
```

## proxychains

```bash
proxychains4 nc -vz 172.16.20.10 445
```

## Nmap Through SOCKS

```bash
proxychains4 nmap -sT -Pn -p 445 172.16.20.10
```


---

# Related Notes

- [Red Teaming](./)
- [Infrastructure](infrastructure.md)
- [Initial Access](initial-access.md)
- [Command and Control](command-and-control.md)
- [Credential Access](credential-access.md)
- [Persistence](persistence.md)
- [Defence Evasion](defence-evasion.md)
- [Windows](../windows/)
- [Linux](../linux/)
- [Active Directory](../active-directory/)
- [Kerberos](../active-directory/kerberos.md)
- [Kerberos Tickets](../active-directory/kerberos-tickets.md)
- [Pass-the-Hash](../active-directory/pass-the-hash.md)
- [Pass-the-Ticket](../active-directory/pass-the-ticket.md)
- [Overpass-the-Hash](../active-directory/overpass-the-hash.md)
- [WinRM](../active-directory/winrm.md)
- [WMI](../active-directory/wmi.md)
- [DCOM](../active-directory/dcom.md)
- [SMB](../active-directory/smb.md)
- [Pivoting](../active-directory/pivoting.md)
- [NetExec Cheatsheet](../cheatsheets/netexec.md)
- [Impacket Cheatsheet](../cheatsheets/impacket.md)
- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)


---

# References

- [MITRE ATT&CK - Lateral Movement](https://attack.mitre.org/tactics/TA0008/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Remote Services](https://attack.mitre.org/techniques/T1021/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - SMB/Windows Admin Shares](https://attack.mitre.org/techniques/T1021/002/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Windows Remote Management](https://attack.mitre.org/techniques/T1021/006/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Remote Desktop Protocol](https://attack.mitre.org/techniques/T1021/001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - SSH](https://attack.mitre.org/techniques/T1021/004/){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Windows Remote Management](https://learn.microsoft.com/windows/win32/winrm/portal){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - PowerShell Remoting](https://learn.microsoft.com/powershell/scripting/security/remoting/powershell-remoting-faq){ target="_blank" rel="noopener noreferrer" }
- [Microsoft - Remote Desktop Services](https://learn.microsoft.com/windows-server/remote/remote-desktop-services/){ target="_blank" rel="noopener noreferrer" }
- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [NetExec](https://github.com/Pennyw0rth/NetExec){ target="_blank" rel="noopener noreferrer" }
- [Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }
- [Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }
- [Ligolo-ng Documentation](https://docs.ligolo.ng/){ target="_blank" rel="noopener noreferrer" }
- [Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }
- [ProxyChains-NG](https://github.com/rofl0r/proxychains-ng){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Lateral movement and pivoting can provide access to systems and network segments that were not visible from the original assessment infrastructure. Confirm that every destination system, identity, subnet, protocol, and credential remains within the approved scope before interacting with it. Keep tunnels and routes as narrow as practical, minimise authentication attempts, avoid unnecessary data access, record deployed pivot infrastructure, and remove temporary agents, routes, proxies, tunnels, and assessment artifacts when testing is complete.
