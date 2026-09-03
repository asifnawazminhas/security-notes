# Active Directory Pivoting - Tunnelling, Port Forwarding and Network Access

Pivoting is the process of using an already accessible system as an intermediary to reach another network, host or service that cannot be reached directly from the operator's current position.

In an Active Directory assessment, a compromised or authorised foothold may have access to:

```text
Internal Subnets
Management Networks
Server VLANs
Domain Controllers
Database Networks
Backup Networks
Legacy Networks
Cloud-Connected Networks
Isolated Application Segments
```

that are not directly reachable from the testing system.

The basic relationship is:

```text
Operator
   |
   X
   |
Internal Target
```

but:

```text
Operator
   |
   v
Pivot Host
   |
   v
Internal Target
```

may be possible.

Pivoting does not inherently provide additional privileges.

It provides:

```text
Network Reachability
```

which may allow other authorised assessment techniques to operate across previously inaccessible network boundaries.

!!! warning "Authorised testing only"
    Pivoting can extend testing into network segments that were not directly reachable from the original assessment system. Confirm that every destination network and target remains within the authorised scope. Use restrictive routes and listeners wherever possible, avoid exposing tunnels to unnecessary interfaces, and remove all temporary forwarding configuration when testing is complete.

---

# Pivoting at a Glance

A simple pivot is:

```text
Kali
 |
 v
Host A
 |
 v
Host B
```

A more realistic Active Directory path may be:

```text
Assessment Host
      |
      v
Workstation
      |
      v
Server Network
      |
      v
Application Server
      |
      v
Management Network
      |
      v
Domain Controller
```

The security assessment should determine:

```text
Why Is the Path Possible?

Which Network Boundary Was Crossed?

Which Host Provided the Route?

Which Services Became Reachable?

Was the Access Intended?
```

---

# Pivoting vs Lateral Movement

These concepts are related but different.

Lateral movement normally means:

```text
Identity / Credential
        |
        v
Remote Service
        |
        v
Another Host
```

Pivoting normally means:

```text
Network Position
      |
      v
Intermediate Host
      |
      v
Previously Unreachable Network
```

For example:

```text
WMI to SRV01
```

may be lateral movement.

Using SRV01 to reach:

```text
10.20.30.0/24
```

may be pivoting.

---

# Pivoting vs Remote Execution

Remote execution answers:

```text
Can I execute something on the remote host?
```

Pivoting answers:

```text
Can I route or proxy traffic through the remote host?
```

A host may provide one capability without the other.

---

# Pivoting vs Tunnelling

Pivoting is the overall objective.

Tunnelling is one mechanism for achieving it.

```text
Pivoting
   |
   +--> Port Forwarding
   |
   +--> SOCKS Proxy
   |
   +--> Reverse Tunnel
   |
   +--> TUN Interface
   |
   +--> Native Routing
```

---

# Pivoting vs Port Forwarding

Port forwarding exposes or redirects a specific network connection.

Example:

```text
localhost:8445
      |
      v
Pivot
      |
      v
10.20.30.10:445
```

This provides access to one destination service.

Pivoting can be broader and may provide access to:

```text
Multiple Hosts
Multiple Ports
Entire Subnets
```

---

# Pivoting vs SOCKS

A SOCKS proxy provides application-level proxying.

Example:

```text
Tool
 |
 v
SOCKS5
 |
 v
Pivot
 |
 v
Internal Network
```

Applications that support SOCKS directly, or that can operate through ProxyChains, can use the tunnel.

---

# Pivoting vs TUN

A TUN interface creates a virtual Layer 3 network interface.

Conceptually:

```text
Application
    |
    v
Operating-System Routing Table
    |
    v
TUN Interface
    |
    v
Tunnel
    |
    v
Pivot
    |
    v
Internal Network
```

This can be more transparent than SOCKS because many tools can use the operating system's normal routing table.

---

# Why Pivoting Matters in Active Directory

Active Directory environments are rarely flat.

A typical architecture may contain:

```text
User Network
Server Network
Domain Controller Network
Management Network
Database Network
Backup Network
DMZ
Cloud Network
```

A compromised system may have access to several of these zones.

Example:

```text
Internet
   |
   v
DMZ
   |
   X
   |
Internal Network
```

But a DMZ host may itself have:

```text
DMZ Host
   |
   +--> Internal DNS
   +--> Database Server
   +--> Domain Services
   +--> Management Server
```

These relationships should be carefully evaluated.

---

# The Pivot Host

A pivot host is an intermediate system through which traffic passes.

Examples include:

```text
Windows Workstation
Windows Server
Linux Server
Jump Host
Application Server
Web Server
Management Server
```

The host does not necessarily need to be domain joined.

---

# Identify Network Interfaces

Before creating any tunnel, understand the pivot's existing network connectivity.

Windows:

```powershell
Get-NetIPConfiguration
```

Alternative:

```cmd
ipconfig /all
```

Linux:

```bash
ip addr
```

---

# Windows Routing Table

```powershell
Get-NetRoute
```

Focused output:

```powershell
Get-NetRoute |
    Select-Object DestinationPrefix,NextHop,InterfaceAlias,RouteMetric
```

Legacy view:

```cmd
route print
```

---

# Linux Routing Table

```bash
ip route
```

Example:

```text
default via 192.168.1.1 dev eth0
10.20.30.0/24 dev eth1 proto kernel scope link
192.168.1.0/24 dev eth0 proto kernel scope link
```

This host may provide a path between:

```text
192.168.1.0/24
```

and:

```text
10.20.30.0/24
```

depending on firewall and routing controls.

---

# Identify Listening Services

Windows:

```powershell
Get-NetTCPConnection -State Listen |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

Linux:

```bash
ss -lntup
```

This helps identify:

```text
Existing Management Services
Potential Tunnel Ports
Unexpected Exposures
```

---

# Identify Reachable Networks

Do not immediately perform broad scanning through a pivot.

Start with:

```text
Interfaces
Routes
DNS Configuration
Known Application Dependencies
Active Directory Information
Configuration Files
Approved Architecture Documentation
```

Then perform targeted validation.

---

# Windows DNS Configuration

```powershell
Get-DnsClientServerAddress |
    Where-Object ServerAddresses |
    Select-Object InterfaceAlias,AddressFamily,ServerAddresses
```

This can reveal internal DNS infrastructure accessible from the pivot.

---

# Linux DNS Configuration

Depending on the system:

```bash
cat /etc/resolv.conf
```

or:

```bash
resolvectl status
```

---

# Active Directory Context

On a domain-joined Windows host:

```powershell
$env:USERDNSDOMAIN
```

```powershell
$env:LOGONSERVER
```

```cmd
nltest /dsgetdc:corp.example
```

These can help identify domain infrastructure visible from the pivot.

---

# Basic Pivoting Decision Model

Before selecting a tool, determine:

```text
What Can the Operator Reach?

What Can the Pivot Reach?

What Must Be Reached?

Which Direction Can Connections Be Established?

Which Protocols Must Traverse the Tunnel?
```

The decision flow is:

```text
Destination
    |
    v
Single Service?
    |
    +--> Yes --> Port Forward
    |
    v
Multiple TCP Services?
    |
    +--> Yes --> SOCKS
    |
    v
Need Broad IP Routing?
    |
    +--> Yes --> TUN
```

Then determine:

```text
Can Operator Connect to Pivot?
```

or:

```text
Can Pivot Connect Back to Operator?
```

This determines whether a:

```text
Forward
```

or:

```text
Reverse
```

tunnel is more suitable.

---

# Pivoting Method Selection

| Requirement | Common Approach |
|---|---|
| One remote TCP service | Local port forwarding |
| Expose one service from pivot side | Remote port forwarding |
| Multiple TCP destinations | SOCKS proxy |
| SOCKS-aware tooling | SOCKS5 |
| Broad Layer 3 access | TUN interface |
| Outbound-only pivot | Reverse tunnel |
| Existing SSH access | SSH forwarding |
| Complex multi-hop routing | Ligolo-ng or chained tunnels |

The correct approach depends on:

```text
Scope
Network Controls
Available Software
Privileges
Protocols
Operational Risk
```

---

# Local Port Forwarding

Local forwarding maps a local port to a remote destination.

Conceptually:

```text
Operator
localhost:8445
      |
      v
Tunnel
      |
      v
Pivot
      |
      v
10.20.30.10:445
```

The operator then connects to:

```text
127.0.0.1:8445
```

while the pivot reaches:

```text
10.20.30.10:445
```

---

# SSH Local Port Forwarding

If legitimate SSH access to the pivot already exists:

```bash
ssh -L 8445:10.20.30.10:445 user@pivot.example
```

The mapping becomes:

```text
127.0.0.1:8445
      |
      v
SSH
      |
      v
Pivot
      |
      v
10.20.30.10:445
```

---

# Bind Locally Only

By default, prefer forwarding listeners bound to:

```text
127.0.0.1
```

rather than:

```text
0.0.0.0
```

unless there is a specific authorised reason to expose the listener to other systems.

This reduces accidental exposure.

---

# SSH Forward Without Interactive Shell

Where supported:

```bash
ssh -N -L 8445:10.20.30.10:445 user@pivot.example
```

`-N` tells SSH not to execute a remote command.

This is useful when only forwarding is required.

---

# Remote Port Forwarding

Remote forwarding works in the opposite direction.

Conceptually:

```text
Remote Side
localhost:8080
      |
      v
SSH Tunnel
      |
      v
Operator-Side Destination
```

Example:

```bash
ssh -N -R 8080:127.0.0.1:8000 user@pivot.example
```

The exact exposure of the remote listening port depends on the SSH server configuration.

---

# Remote Forwarding Security

Do not assume a remote forwarded port is bound only to loopback.

Review:

```text
GatewayPorts
Bind Address
Firewall
SSH Server Configuration
```

before using remote forwarding in sensitive environments.

---

# Dynamic SSH Forwarding

SSH can provide a SOCKS proxy using:

```bash
ssh -N -D 1080 user@pivot.example
```

This creates a SOCKS listener on:

```text
127.0.0.1:1080
```

The flow becomes:

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
Destination
```

---

# SOCKS Proxy

SOCKS provides a flexible way to proxy multiple TCP connections.

Example:

```text
Browser
   |
   v
SOCKS
   |
   v
Pivot
   |
   +--> Web Server
   |
   +--> SMB Server
   |
   +--> LDAP Server
   |
   +--> Database
```

Tool compatibility varies.

---

# SOCKS4 vs SOCKS5

SOCKS5 provides capabilities beyond SOCKS4 and is generally preferred where supported.

Important differences can include:

```text
Authentication Support
Addressing
DNS Handling
Protocol Features
```

Always verify which version the selected tunnelling tool provides.

---

# ProxyChains

ProxyChains can force many TCP client applications through a SOCKS proxy.

Common configuration file:

```text
/etc/proxychains4.conf
```

A typical SOCKS5 entry is:

```text
socks5 127.0.0.1 1080
```

---

# Test ProxyChains

For a known authorised HTTP service:

```bash
proxychains4 curl http://10.20.30.20/
```

This provides a low-impact connectivity test.

---

# ProxyChains and Nmap

Nmap does not behave transparently through ProxyChains for every scan type.

Raw packet techniques such as:

```text
SYN Scan
ICMP Discovery
OS Detection
```

cannot simply be proxied through a normal SOCKS TCP proxy.

Where TCP connect scanning is explicitly required:

```bash
proxychains4 nmap -sT -Pn -p80,443 10.20.30.20
```

Keep scans tightly scoped.

---

# Why `-sT` Matters

A SOCKS proxy operates at a higher level than raw packet generation.

Therefore:

```text
SYN Scan
```

requires packet-level access that SOCKS does not provide.

TCP connect scanning:

```text
-sT
```

uses normal socket connections and is more compatible with SOCKS proxying.

---

# Why `-Pn` Matters

Host discovery mechanisms such as ICMP may not traverse a SOCKS proxy.

Using:

```text
-Pn
```

tells Nmap to treat the target as online and test the specified ports directly.

This does not mean:

```text
The Host Is Definitely Online
```

It simply skips normal host discovery.

---

# DNS Through a Proxy

DNS deserves special attention during pivoting.

A tool may resolve:

```text
srv01.corp.example
```

on the operator's system rather than through the pivot.

If the internal DNS name is only resolvable inside the target network, this can fail.

---

# Proxy DNS

ProxyChains supports proxy-based DNS behaviour depending on configuration.

Review:

```text
proxy_dns
```

in:

```text
/etc/proxychains4.conf
```

before relying on internal hostnames.

---

# DNS Leakage

A common operational mistake is:

```text
Internal Hostname
      |
      v
Operator's Normal DNS Resolver
```

instead of:

```text
Internal Hostname
      |
      v
Tunnel
      |
      v
Internal DNS Resolver
```

This can:

```text
Fail Resolution
Leak Internal Names
Produce Misleading Results
```

---

# Chisel

Chisel is a TCP tunnelling tool that operates over HTTP and uses SSH internally for transport security.

It can provide:

```text
Port Forwarding
Reverse Port Forwarding
SOCKS
```

and is useful where an authorised pivot can make outbound HTTP connections.

Project:

[Chisel](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }

Always verify current syntax with:

```bash
chisel --help
```

---

# Chisel Architecture

A common reverse-pivot architecture is:

```text
Operator
Chisel Server
    ^
    |
    | Outbound Connection
    |
Pivot
Chisel Client
    |
    v
Internal Network
```

This can be useful when:

```text
Operator -> Pivot
```

connections are blocked but:

```text
Pivot -> Operator
```

connections are permitted.

---

# Start a Chisel Server

In an authorised lab, a server capable of reverse tunnels can be started with:

```bash
chisel server --reverse --port 8080
```

Check the installed version first:

```bash
chisel server --help
```

---

# Chisel Reverse SOCKS

From the pivot:

```bash
chisel client OPERATOR_IP:8080 R:socks
```

The exact SOCKS listener behaviour and defaults should be verified against the installed Chisel version.

The conceptual flow is:

```text
Internal Target
      ^
      |
Pivot
      |
      | Outbound Tunnel
      v
Operator
      |
      v
SOCKS
```

---

# Chisel Security

Treat the Chisel server as temporary assessment infrastructure.

Restrict:

```text
Source Addresses
Listening Interfaces
Firewall Rules
Assessment Duration
```

where possible.

Do not leave an unrestricted tunnelling server running after the engagement.

---

# Chisel Authentication

Where appropriate, configure Chisel authentication rather than exposing an unauthenticated tunnelling service.

Check current options:

```bash
chisel server --help
```

because authentication and configuration options may change between versions.

---

# Ligolo-ng

Ligolo-ng provides a tunnelling approach based around:

```text
Agent
Proxy
TUN Interface
```

Project:

[Ligolo-ng](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }

Its major advantage is that many tools can interact with the routed network without requiring ProxyChains.

---

# Ligolo-ng Architecture

```text
Assessment Host
      |
      v
Ligolo Proxy
      |
      v
TUN Interface
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

# Why TUN Is Useful

With a TUN interface:

```text
Tool
 |
 v
Operating-System Route
 |
 v
TUN
 |
 v
Tunnel
 |
 v
Pivot
```

Many applications can operate normally because the routing occurs at the operating-system level.

This can simplify use of tools that do not support SOCKS.

---

# Check Ligolo-ng Version

Before using syntax from notes:

```bash
./proxy -h
```

and:

```bash
./agent -h
```

Ligolo-ng has changed its interface across versions, so current built-in help should be treated as authoritative for the installed release.

---

# Ligolo-ng Proxy

A typical assessment begins by starting the proxy component on the operator system.

The exact command depends on the installed release.

Verify:

```bash
./proxy -h
```

and identify:

```text
Listen Address
Listen Port
TLS Options
Authentication Options
```

before starting the service.

---

# Ligolo-ng Agent

The agent is started on the authorised pivot and connects to the proxy.

Conceptually:

```text
Pivot Agent
    |
    | Outbound
    v
Operator Proxy
```

Verify current connection syntax using:

```bash
./agent -h
```

---

# Ligolo-ng Route

Once the tunnel interface and session are established, a route is added on the assessment host for the network reachable through the pivot.

Conceptually:

```bash
sudo ip route add 10.20.30.0/24 dev ligolo
```

The interface name must match the interface actually created for the assessment.

---

# Check Routes

```bash
ip route
```

Verify that only the intended in-scope networks are routed through the tunnel.

---

# Route Specificity

Prefer:

```text
10.20.30.0/24
```

over:

```text
0.0.0.0/0
```

when only one internal network is required.

This reduces accidental routing of unrelated traffic through the pivot.

---

# TUN vs SOCKS

SOCKS:

```text
Application
    |
    v
Proxy Configuration
    |
    v
SOCKS
```

TUN:

```text
Application
    |
    v
Normal Network Stack
    |
    v
Routing Table
    |
    v
TUN
```

---

# TUN Advantages

Potential advantages include:

```text
Broader Tool Compatibility
Normal Routing Semantics
No ProxyChains Requirement
Simpler Multi-Service Access
```

---

# TUN Considerations

Potential considerations include:

```text
Route Conflicts
Local Privileges
DNS Configuration
Overlapping Networks
Accidental Traffic Routing
Cleanup
```

---

# Overlapping Networks

A common problem is:

```text
Operator Network:
10.0.0.0/24

Target Internal Network:
10.0.0.0/24
```

The local operating system may route traffic to the wrong interface.

Possible solutions depend on the tunnelling technology and environment.

Do not blindly replace the operator's normal route.

---

# Route Inspection

Before adding routes:

```bash
ip route
```

Record existing entries.

After adding routes:

```bash
ip route
```

confirm the intended result.

After testing, remove only the routes created for the assessment.

---

# Remove a Linux Route

Example:

```bash
sudo ip route del 10.20.30.0/24 dev ligolo
```

Use the actual interface and route configured during testing.

---

# SSH as a Pivot

SSH is often the simplest option when legitimate SSH access already exists.

Supported approaches include:

```text
Local Forwarding
Remote Forwarding
Dynamic SOCKS
```

This avoids introducing another tunnelling utility when SSH already provides the required functionality.

---

# SSH Local Forward

```bash
ssh -N -L 8445:10.20.30.10:445 user@pivot.example
```

---

# SSH Dynamic SOCKS

```bash
ssh -N -D 1080 user@pivot.example
```

---

# SSH Remote Forward

```bash
ssh -N -R 8080:127.0.0.1:8000 user@pivot.example
```

---

# SSH Bind Address

A local forward can explicitly bind to loopback:

```bash
ssh -N -L 127.0.0.1:8445:10.20.30.10:445 user@pivot.example
```

This is preferable to unnecessarily exposing the listener externally.

---

# SSH Keepalive

Long-running assessment tunnels may benefit from SSH keepalive configuration.

For example:

```bash
ssh -N -o ServerAliveInterval=30 -L 127.0.0.1:8445:10.20.30.10:445 user@pivot.example
```

This can help detect broken sessions.

---

# Windows SSH

Modern Windows systems may have:

```text
OpenSSH Client
OpenSSH Server
```

installed as optional capabilities.

Check:

```powershell
Get-Command ssh.exe -ErrorAction SilentlyContinue
```

Do not install additional Windows features without explicit authorisation.

---

# Windows Portproxy

Windows includes:

```text
netsh interface portproxy
```

which can configure TCP forwarding.

This modifies persistent operating-system configuration and should therefore be used carefully.

---

# View Existing Portproxy Rules

```cmd
netsh interface portproxy show all
```

This is safe for inspection.

---

# Portproxy Concept

```text
Client
 |
 v
Pivot:8445
 |
 v
Windows Portproxy
 |
 v
10.20.30.10:445
```

---

# Portproxy Modification Warning

Creating a portproxy rule changes the host configuration and may persist after the assessment.

Prefer temporary tunnelling mechanisms unless:

```text
Portproxy Testing Is Explicitly Required
```

---

# Example Portproxy Rule

In a controlled lab:

```cmd
netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=8445 connectaddress=10.20.30.10 connectport=445
```

This requires suitable privileges.

---

# Verify Portproxy

```cmd
netsh interface portproxy show all
```

---

# Remove Portproxy

```cmd
netsh interface portproxy delete v4tov4 listenaddress=127.0.0.1 listenport=8445
```

Always verify cleanup:

```cmd
netsh interface portproxy show all
```

---

# Windows Firewall and Portproxy

Creating a portproxy rule does not automatically guarantee that the listener is reachable through Windows Firewall.

Do not weaken firewall rules merely to make a pivot work unless firewall changes are explicitly part of the approved test.

---

# Native Linux Forwarding

Linux can route traffic between interfaces when:

```text
IP Forwarding
Routing
Firewall
```

are configured appropriately.

Check current forwarding state:

```bash
sysctl net.ipv4.ip_forward
```

---

# Do Not Enable Routing Automatically

Changing:

```text
net.ipv4.ip_forward
```

modifies the host's networking behaviour.

Do not enable it on a production pivot merely to facilitate testing unless explicitly authorised.

A user-space tunnel may be less intrusive.

---

# Socat

Socat can relay connections between network endpoints.

Project documentation:

[Socat](http://www.dest-unreach.org/socat/){ target="_blank" rel="noopener noreferrer" }

It can be useful for simple single-port forwarding where already installed.

---

# Socat Forwarding Concept

```text
Client
 |
 v
Pivot:8445
 |
 v
socat
 |
 v
10.20.30.10:445
```

---

# Socat Example

In an authorised lab:

```bash
socat TCP-LISTEN:8445,bind=127.0.0.1,reuseaddr,fork TCP:10.20.30.10:445
```

This keeps the listener on loopback.

---

# Verify Socat Listener

```bash
ss -lntp
```

---

# Stop Socat

Terminate the assessment process when testing is complete.

Do not leave forwarding listeners running.

---

# Reverse Tunnels

A reverse tunnel is useful when:

```text
Operator
   |
   X
   |
Pivot
```

but:

```text
Pivot
   |
   v
Operator
```

is permitted.

The pivot initiates the connection outward.

---

# Reverse Tunnel Model

```text
Internal Network
      ^
      |
Pivot Host
      |
      | Outbound Connection
      v
Assessment Host
```

The established connection is then used to carry traffic back through the pivot.

---

# Why Reverse Tunnels Work

Network security frequently permits:

```text
Outbound Connections
```

more broadly than:

```text
Inbound Connections
```

A reverse tunnel uses that asymmetry.

This does not mean the control is automatically vulnerable.

The security question is whether the allowed outbound path enables an unintended trust-boundary bypass.

---

# Egress Filtering

Strong egress controls can restrict:

```text
Pivot -> Internet
```

or:

```text
Server -> Arbitrary External Host
```

connections.

Assess:

```text
Allowed Destinations
Allowed Ports
Proxy Requirements
TLS Inspection
DNS Restrictions
Application Controls
```

---

# Do Not Bypass Controls Unnecessarily

If a tunnel is blocked by:

```text
Firewall
Proxy
Application Control
EDR
Egress Filtering
```

do not immediately attempt increasingly evasive techniques.

First determine whether the control itself answers the assessment question.

---

# Double Pivoting

Sometimes the desired target is reachable only through multiple systems.

Example:

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
   |
   v
Target
```

This is commonly called:

```text
Double Pivoting
```

or:

```text
Multi-Hop Pivoting
```

---

# Multi-Hop Risks

Every additional pivot increases:

```text
Complexity
Latency
Detection Surface
Cleanup Requirements
Route Conflicts
Failure Points
Scope Risk
```

Use the minimum number of pivots required.

---

# SSH Multi-Hop

SSH supports jump hosts through:

```text
ProxyJump
```

Example:

```bash
ssh -J user@jump01.example admin@srv01.internal.example
```

This is often cleaner than manually creating several forwarding layers when SSH access already exists.

---

# SSH Config

For repeated authorised administration:

```text
Host jump01
    HostName jump01.example
    User audituser

Host srv01
    HostName srv01.internal.example
    User auditadmin
    ProxyJump jump01
```

Then:

```bash
ssh srv01
```

Do not store passwords in SSH configuration.

---

# ProxyChains Multi-Hop

ProxyChains can chain proxies depending on configuration.

However, each additional proxy adds complexity and can make:

```text
DNS
Timeouts
Authentication
Tool Compatibility
```

harder to troubleshoot.

---

# Routing Through Multiple Pivots

For complex networks, a TUN-based solution may be easier to reason about than multiple application-level SOCKS proxies.

The important principle is:

```text
Understand Every Route
```

before adding another one.

---

# Pivoting and SMB

Suppose:

```text
10.20.30.10:445
```

is reachable only from the pivot.

A tunnel may make SMB accessible to the assessment system.

However, SMB tools can depend on:

```text
Hostname Resolution
Kerberos SPNs
Multiple Connections
RPC
Named Pipes
```

so a single forwarded port may not reproduce full native network access.

See:

[SMB](smb.md)

---

# Pivoting and Kerberos

Kerberos can be particularly sensitive to tunnelling configuration.

Requirements may include:

```text
Correct DNS
Correct Hostname
Reachable KDC
Reachable Service
Correct SPN
Time Synchronisation
```

---

# Kerberos Through a Pivot

Conceptually:

```text
Assessment Host
      |
      +--> KDC
      |
      +--> Target Service
```

Both paths may need to be available.

Forwarding only:

```text
Target:445
```

may not be sufficient if the assessment host also needs access to:

```text
Domain Controller:88
```

---

# Kerberos Ports

Common Kerberos-related connectivity includes:

```text
88/TCP
88/UDP
464/TCP
464/UDP
```

depending on the operation.

DNS may also require:

```text
53/TCP
53/UDP
```

---

# LDAP Through a Pivot

Active Directory enumeration may require:

```text
389/TCP
636/TCP
3268/TCP
3269/TCP
```

depending on whether the workflow uses:

```text
LDAP
LDAPS
Global Catalog
Global Catalog over TLS
```

---

# DNS Through a Pivot

Internal Active Directory names often require the domain's DNS servers.

A useful architecture is:

```text
Assessment Tool
      |
      v
Tunnel
      |
      v
Internal DNS
      |
      v
AD Name Resolution
```

Incorrect DNS configuration is one of the most common reasons that:

```text
IP Connectivity Works
```

but:

```text
Active Directory Tooling Fails
```

---

# Pivoting and BloodHound

BloodHound data collection can require access to multiple services across domain systems.

See:

[BloodHound](bloodhound.md)

Before collecting through a pivot, determine which protocols the selected collector requires.

Avoid unnecessarily routing the entire assessment system through the target network.

---

# Pivoting and NetExec

NetExec can operate against multiple protocols.

See:

[NetExec](netexec.md)

When using it through a pivot, verify whether the tunnel supports the required:

```text
TCP Connections
DNS
Kerberos
RPC
SMB
LDAP
```

behaviour.

---

# Pivoting and Impacket

Impacket tools can require different combinations of:

```text
SMB
RPC
Kerberos
LDAP
HTTP
DNS
```

See:

[Impacket](impacket.md)

Do not assume that because one Impacket tool works through a tunnel, every Impacket tool will.

---

# Pivoting and WMI

Traditional remote WMI requires:

```text
135/TCP
+
Dynamic RPC
```

A single port forward to:

```text
135/TCP
```

does not provide the dynamic RPC connectivity required for normal WMI operation.

See:

[WMI](wmi.md)

---

# Pivoting and DCOM

DCOM has the same general RPC consideration:

```text
135/TCP
      |
      v
Dynamic RPC Port
```

A route-based tunnel is often easier to use for RPC-heavy protocols than a collection of individual port forwards.

See:

[DCOM](dcom.md)

---

# Pivoting and WinRM

WinRM commonly uses:

```text
5985/TCP
5986/TCP
```

Because these are fixed ports, simple forwarding may be sufficient for some WinRM workflows.

See:

[WinRM](winrm.md)

---

# Pivoting and RDP

RDP commonly uses:

```text
3389/TCP
```

A local forward can expose an internal RDP service to the assessment host.

Conceptually:

```text
127.0.0.1:13389
      |
      v
Tunnel
      |
      v
10.20.30.20:3389
```

Interactive logon should only be used when required by the test objective.

---

# Pivoting and Web Applications

Internal web applications are often straightforward to access through:

```text
SOCKS
Port Forwarding
TUN
```

For example:

```text
Browser
   |
   v
SOCKS
   |
   v
Internal Web Application
```

Browser proxy configuration may be preferable to routing all system traffic through the pivot.

---

# Browser SOCKS

A browser can be configured to use:

```text
127.0.0.1:1080
```

as a SOCKS proxy.

Where internal DNS is required, ensure DNS requests are also resolved through the intended network path.

---

# Burp Suite Through a Pivot

A useful assessment chain can be:

```text
Browser
   |
   v
Burp Suite
   |
   v
SOCKS Proxy
   |
   v
Pivot
   |
   v
Internal Web Application
```

Burp Suite supports upstream SOCKS proxy configuration.

This allows:

```text
Browser -> Burp -> Pivot -> Internal Application
```

while preserving normal web-testing functionality.

---

# Do Not Expose Internal Services Publicly

Avoid creating:

```text
0.0.0.0:445
      |
      v
Internal SMB
```

or similar public listeners.

Prefer:

```text
127.0.0.1
```

for local assessment forwarding whenever possible.

---

# Bind Address Matters

Compare:

```text
127.0.0.1:8445
```

with:

```text
0.0.0.0:8445
```

The first is reachable only locally.

The second may be reachable from other network interfaces.

This can unintentionally expose internal services.

---

# Privilege Requirements

Some pivoting techniques require elevated privileges.

Examples can include:

```text
Creating TUN Interfaces
Changing Routes
Enabling IP Forwarding
Changing Firewall Rules
Configuring Windows Portproxy
```

Others may operate entirely in user space.

Prefer the least invasive method that satisfies the test objective.

---

# User-Space Tunnels

User-space tunnelling can avoid modifying:

```text
Kernel Forwarding
NAT
Persistent Routing
System Firewall
```

on the pivot.

This often simplifies cleanup.

---

# Network Address Translation

Some native routing designs require:

```text
NAT
```

to allow return traffic.

However, adding NAT rules changes network behaviour and may affect other traffic.

Do not modify production NAT or firewall configuration unless explicitly authorised.

---

# Return Routes

Routing requires bidirectional communication.

Suppose:

```text
Assessment Host
      |
      v
Pivot
      |
      v
10.20.30.10
```

The destination must have a valid return path.

Tunnelling tools often solve this by carrying responses back through the established connection.

Native routing may require explicit:

```text
Routes
NAT
```

depending on the topology.

---

# Tunnel Direction

Determine connection direction before selecting the tool.

## Forward Connection

```text
Operator
   |
   v
Pivot
```

Useful options may include:

```text
SSH Local Forward
SSH Dynamic Forward
Direct Agent Connection
```

## Reverse Connection

```text
Pivot
   |
   v
Operator
```

Useful options may include:

```text
Reverse SSH
Chisel Reverse Tunnel
Ligolo-ng Agent
```

---

# Firewall Considerations

Ask:

```text
Can Operator Reach Pivot?

Can Pivot Reach Operator?

Which Ports Are Allowed?

Is an HTTP Proxy Required?

Is DNS Allowed?

Is TLS Inspection Present?

Are Unknown Binaries Blocked?
```

The answers determine the appropriate pivoting design.

---

# Application Proxies

Some enterprise environments require outbound traffic through:

```text
HTTP Proxy
```

A tunnelling tool may not automatically inherit system proxy configuration.

Do not modify enterprise proxy configuration merely to force a tunnel through it.

---

# TLS Inspection

Outbound TLS may be inspected by enterprise security controls.

This can affect:

```text
Certificate Validation
Unknown Protocols over TLS
Tunnel Reliability
Detection
```

Do not disable enterprise TLS controls during an assessment unless explicitly authorised.

---

# Pivoting OPSEC

Pivoting can produce significant network telemetry.

Potential indicators include:

```text
Long-Lived Connections
Unusual Outbound Connections
High Fan-Out Internal Connections
Unexpected SOCKS Traffic
Unusual SSH Connections
New Listening Ports
TUN Interfaces
Route Changes
Portproxy Rules
Unknown Tunnel Processes
```

---

# High Fan-Out Traffic

A tunnel may transform:

```text
One Connection to Pivot
```

into:

```text
Pivot
 |
 +--> Host 1
 +--> Host 2
 +--> Host 3
 +--> Host 4
 +--> Host 5
```

From the internal network's perspective, all traffic may appear to originate from:

```text
Pivot Host
```

This is important for detection and evidence interpretation.

---

# Source Attribution

When traffic is proxied:

```text
Assessment Host
      |
      v
Pivot
      |
      v
Target
```

the target may log:

```text
Pivot IP
```

rather than:

```text
Assessment Host IP
```

Document this clearly in the assessment timeline.

---

# Pivoting Detection

Detection should combine:

```text
Process Telemetry
Network Telemetry
Firewall Logs
Route Changes
Listening Ports
Authentication
EDR
Proxy Logs
DNS
```

---

# Process Detection

Potential processes requiring context can include:

```text
ssh.exe
ssh
chisel
socat
Custom Tunnel Agents
```

These tools can also be legitimate.

Do not detect solely by executable name.

---

# Command-Line Telemetry

Where process command-line auditing is enabled, look for unusual use of:

```text
-L
-R
-D
```

with SSH or unusual forwarding parameters in other networking tools.

---

# Network Detection

Look for:

```text
Long-Lived External Connections
Unexpected Outbound Server Connections
Unexpected High-Volume Internal Connections
New Listening Ports
Unusual Destination Networks
```

---

# Route Changes

Unexpected changes to:

```text
Routing Table
IP Forwarding
Network Interfaces
```

may indicate tunnelling or unauthorised network bridging.

---

# Windows Portproxy Detection

Review:

```cmd
netsh interface portproxy show all
```

Unexpected entries should be investigated.

---

# Linux Forwarding Detection

Check:

```bash
sysctl net.ipv4.ip_forward
```

and review:

```bash
ip route
```

as part of system-baseline monitoring where appropriate.

---

# New Network Interfaces

TUN-based tunnelling may create interfaces.

Linux:

```bash
ip link
```

and:

```bash
ip addr
```

Unexpected interfaces should be investigated in context.

---

# Firewall Telemetry

Network and host firewalls can identify:

```text
New Outbound Connections
Unexpected East-West Traffic
RPC Fan-Out
SMB Fan-Out
LDAP Access
RDP Connections
```

originating from systems that normally do not perform administrative activity.

---

# EDR Telemetry

Modern EDR platforms may detect:

```text
Tunnel Tools
Unusual Process Execution
Network Connections
Port Listeners
Route Modification
Persistence
Binary Introduction
```

Pivoting should not be assumed to be invisible.

---

# Detection Correlation

A useful model is:

```text
New Process
    |
    v
Long-Lived Connection
    |
    v
New Internal Fan-Out
    |
    v
Previously Unusual Network Segment
```

This correlation is stronger than any single signal.

---

# Pivot Host Context

Compare:

```text
Network Management Server
       |
       v
Many Internal Connections
```

with:

```text
User Workstation
       |
       v
Many Server-Segment Connections
```

The second pattern is usually more suspicious.

---

# Pivoting Hardening

A strong defensive model includes:

```text
Network Segmentation
Host Firewalls
Egress Filtering
Least Privilege
Administrative Tiering
Application Control
EDR
Proxy Restrictions
Network Monitoring
DNS Monitoring
Restricted Management Paths
```

---

# Network Segmentation

Segmentation should control:

```text
Which Source
Can Reach
Which Destination
On Which Port
For Which Purpose
```

rather than simply creating VLANs.

---

# Segmentation Is Not Just VLANs

A network may contain:

```text
User VLAN
Server VLAN
Management VLAN
```

but if:

```text
User VLAN -> All Server Ports
```

is permitted, the security boundary may provide limited protection.

---

# Host Firewalls

Host-based firewall policy remains important even when network firewalls exist.

Example:

```text
Server
 |
 +--> Allow WinRM from Admin Network
 |
 +--> Allow Monitoring from Monitoring Network
 |
 +--> Deny Workstation Network
```

---

# Egress Filtering

Servers should not automatically be permitted to connect to:

```text
Any Internet Address
Any Port
```

unless required.

Restricting outbound connectivity can make reverse tunnelling more difficult and improve detection.

---

# Application Control

Application control can reduce the ability to introduce arbitrary tunnelling binaries.

Examples include:

```text
WDAC
AppLocker
```

This should complement rather than replace network controls.

---

# Administrative Tiering

A strong administrative model limits:

```text
Who Can Administer What
```

and:

```text
From Which Systems
```

Example:

```text
Privileged Identity
       |
       v
Privileged Workstation
       |
       v
Management Network
       |
       v
Tier 0 System
```

---

# Restrict Peer-to-Peer Traffic

Where not required:

```text
Workstation
    |
    X
    |
Workstation
```

can significantly reduce lateral-movement and pivoting opportunities.

---

# Restrict Server Egress

Application servers often need only specific outbound destinations.

Example:

```text
Application Server
      |
      +--> DNS
      +--> Database
      +--> Update Service
      +--> Monitoring
      |
      X
      |
      +--> Arbitrary Internet
```

---

# Safe Pivoting Workflow

A controlled assessment should follow:

```text
Understand Topology
      |
      v
Confirm Scope
      |
      v
Identify Pivot Interfaces
      |
      v
Inspect Routes
      |
      v
Identify Required Destination
      |
      v
Choose Minimum Tunnel
      |
      v
Restrict Listener
      |
      v
Validate One Service
      |
      v
Expand Only if Required
      |
      v
Collect Evidence
      |
      v
Remove Tunnel
      |
      v
Verify Cleanup
```

---

# Step 1 - Understand the Pivot

Windows:

```powershell
Get-NetIPConfiguration
```

Linux:

```bash
ip addr
```

---

# Step 2 - Understand Routes

Windows:

```powershell
Get-NetRoute |
    Select-Object DestinationPrefix,NextHop,InterfaceAlias,RouteMetric
```

Linux:

```bash
ip route
```

---

# Step 3 - Identify the Required Destination

Avoid:

```text
Tunnel Entire Internal Network
```

when the objective requires only:

```text
10.20.30.10:443
```

---

# Step 4 - Select the Minimum Mechanism

Example:

```text
One Web Service
      |
      v
Local Port Forward
```

rather than:

```text
Full TUN Route
```

---

# Step 5 - Bind Safely

Prefer:

```text
127.0.0.1
```

for assessment listeners.

---

# Step 6 - Validate Connectivity

For HTTP:

```bash
curl http://127.0.0.1:8080/
```

For a direct routed target:

```bash
curl http://10.20.30.20/
```

Use the least intrusive validation appropriate for the target service.

---

# Step 7 - Record Traffic Path

Document:

```text
Assessment Host
      |
      v
Pivot Host
      |
      v
Target Host
```

including IP addresses and tunnel type.

---

# Step 8 - Remove Tunnel

Stop:

```text
SSH Forward
Chisel
Ligolo-ng
Socat
Other Tunnel Processes
```

and remove temporary routes or configuration.

---

# Step 9 - Verify Cleanup

Check:

```text
Listening Ports
Processes
Routes
Portproxy Rules
Temporary Files
Network Interfaces
```

---

# Cleanup Checklist

## Operator

- [ ] Stop proxy
- [ ] Stop tunnel server
- [ ] Remove temporary routes
- [ ] Remove temporary TUN interface if applicable
- [ ] Remove temporary proxy configuration
- [ ] Restore DNS configuration
- [ ] Close listeners

## Pivot

- [ ] Stop tunnel process
- [ ] Remove temporary binaries where required
- [ ] Remove marker files
- [ ] Remove temporary portproxy rules
- [ ] Restore modified routing only if it was explicitly changed
- [ ] Restore modified forwarding only if it was explicitly changed
- [ ] Verify no tunnel process remains

---

# Evidence Checklist

Record:

```text
Assessment Host
Assessment IP
Pivot Host
Pivot IP
Pivot Interfaces
Pivot Routes
Destination Network
Destination Host
Destination Port
Tunnel Type
Tunnel Direction
Tool
Tool Version
Listening Address
Listening Port
Route Added
DNS Configuration
Authentication Used
Start Time
Stop Time
Files Introduced
Configuration Modified
Cleanup Performed
```

---

# Sensitive Evidence

Do not unnecessarily include:

```text
Passwords
NTLM Hashes
Kerberos Tickets
Private Keys
Tunnel Authentication Secrets
```

in screenshots or reports.

Where sensitive material must be retained:

```text
Restrict Access
Encrypt Storage
Minimise Retention
Redact Reports
```

---

# Reporting Pivoting Findings

Do not report:

```text
Pivoting Is Possible
```

without explaining the underlying security weakness.

The actual issue may be:

```text
Insufficient Network Segmentation
```

or:

```text
Unrestricted Server Egress
```

or:

```text
Workstation-to-Server Administrative Access
```

or:

```text
Management Network Reachable from Lower-Trust Host
```

or:

```text
Broad East-West Connectivity
```

---

# Example Finding - Insufficient Network Segmentation

```text
Finding:
Compromised Workstation Can Reach Restricted Server Network

Description:
A workstation in the standard user network had direct network
connectivity to management services within the server network.

The workstation could therefore be used as an intermediary to access
systems that were not directly reachable from the external assessment
position.

A temporary assessment tunnel was used to validate the network path.
No persistence was created.

Impact:
Compromise of a standard workstation could provide an attacker with a
network foothold from which additional internal systems and
administrative services could be reached.

This reduces the effectiveness of network segmentation as a
lateral-movement control.

Recommendation:
Restrict workstation-to-server connectivity to explicitly required
application services.

Administrative protocols should be reachable only from approved
management networks, jump hosts and privileged administrative
workstations.
```

---

# Example Finding - Unrestricted Server Egress

```text
Finding:
Internal Server Permits Unrestricted Outbound Internet Connectivity

Description:
The tested server was able to establish arbitrary outbound network
connections to Internet-hosted systems.

The server's documented application role did not require unrestricted
Internet access.

Impact:
If the server is compromised, unrestricted outbound connectivity may
facilitate command-and-control communication, reverse tunnelling and
data exfiltration.

Recommendation:
Apply egress filtering based on the server's documented business
requirements.

Permit only required destinations, protocols and services and monitor
blocked outbound connection attempts.
```

---

# Example Finding - Management Network Reachability

```text
Finding:
Lower-Trust Application Server Can Reach Management Network

Description:
An application server in a lower-trust network segment had network
connectivity to systems within the administrative management network.

The application did not require this connectivity for normal business
operation.

Impact:
Compromise of the application server could provide an attacker with a
network pivot into a higher-trust management segment.

This may expose administrative services and increase the impact of an
initial application compromise.

Recommendation:
Block lower-trust systems from initiating connections into the
management network.

Permit management traffic only from explicitly approved
administrative systems.
```

---

# Example Finding - Workstation-to-Workstation Connectivity

```text
Finding:
Unrestricted Peer-to-Peer Workstation Connectivity

Description:
Standard workstations were able to initiate connections to
administrative and file-sharing services on other workstation systems.

Impact:
Compromise of one workstation may provide an attacker with direct
network paths for credential reuse, remote administration and lateral
movement to additional endpoints.

Recommendation:
Restrict unnecessary peer-to-peer workstation traffic using host and
network firewall controls.

Allow only explicitly required workstation-to-workstation services.
```

---

# Example Finding - Excessive Internal Reachability

```text
Finding:
Application Server Has Excessive East-West Network Reachability

Description:
The tested application server could initiate connections to multiple
internal networks unrelated to its documented application
dependencies.

The reachable networks included administrative and infrastructure
services.

Impact:
Compromise of the application server could allow an attacker to use
the host as a network pivot and significantly expand access within the
internal environment.

Recommendation:
Implement application-specific network allowlisting.

Permit the server to communicate only with systems and ports required
for its documented function.
```

---

# Pivoting Assessment Checklist

## Scope

- [ ] Confirm pivot host is in scope
- [ ] Confirm destination network is in scope
- [ ] Confirm destination hosts are in scope
- [ ] Confirm permitted testing hours
- [ ] Confirm prohibited network segments
- [ ] Confirm whether tunnel software may be introduced

## Discovery

- [ ] Enumerate pivot interfaces
- [ ] Enumerate pivot IP addresses
- [ ] Enumerate routing table
- [ ] Identify DNS servers
- [ ] Identify default gateway
- [ ] Identify reachable internal networks
- [ ] Identify existing listeners
- [ ] Identify firewall boundaries
- [ ] Identify required destination only

## Method Selection

- [ ] Determine single-port vs multi-host requirement
- [ ] Determine SOCKS suitability
- [ ] Determine TUN suitability
- [ ] Determine connection direction
- [ ] Determine whether SSH already exists
- [ ] Prefer existing legitimate tooling
- [ ] Minimise introduced software
- [ ] Minimise configuration changes

## Port Forwarding

- [ ] Use local forwarding for individual services where suitable
- [ ] Bind to loopback
- [ ] Avoid unnecessary public listeners
- [ ] Record source port
- [ ] Record destination
- [ ] Remove forward after testing

## SOCKS

- [ ] Identify SOCKS version
- [ ] Bind proxy to loopback
- [ ] Configure ProxyChains where required
- [ ] Review proxy DNS
- [ ] Prevent DNS leakage
- [ ] Use TCP-compatible tools
- [ ] Avoid unsupported raw-packet scans

## TUN

- [ ] Record existing routes
- [ ] Create only required routes
- [ ] Avoid default-route replacement
- [ ] Check overlapping networks
- [ ] Verify TUN interface
- [ ] Remove routes after testing
- [ ] Remove temporary interface if required

## SSH

- [ ] Prefer existing authorised SSH
- [ ] Use `-N` when no shell is required
- [ ] Bind local forwards to loopback
- [ ] Review remote-forward bind behaviour
- [ ] Protect SSH keys
- [ ] Stop tunnel after testing

## Chisel

- [ ] Verify current version
- [ ] Run `chisel --help`
- [ ] Restrict server exposure
- [ ] Configure authentication where appropriate
- [ ] Record listening port
- [ ] Record reverse tunnel configuration
- [ ] Stop server after testing
- [ ] Remove temporary client binary where required

## Ligolo-ng

- [ ] Verify current version
- [ ] Review proxy help
- [ ] Review agent help
- [ ] Record proxy listener
- [ ] Record agent connection
- [ ] Record TUN interface
- [ ] Add only required routes
- [ ] Remove routes
- [ ] Stop agent
- [ ] Stop proxy
- [ ] Remove temporary artifacts

## Windows

- [ ] Review `Get-NetIPConfiguration`
- [ ] Review `Get-NetRoute`
- [ ] Review listening ports
- [ ] Review portproxy
- [ ] Avoid modifying firewall
- [ ] Avoid enabling routing without approval
- [ ] Remove temporary portproxy entries

## Linux

- [ ] Review `ip addr`
- [ ] Review `ip route`
- [ ] Review `ss -lntup`
- [ ] Review IP forwarding state
- [ ] Avoid changing forwarding without approval
- [ ] Avoid persistent NAT changes
- [ ] Remove temporary routes

## Active Directory

- [ ] Determine KDC reachability
- [ ] Determine DNS reachability
- [ ] Determine LDAP reachability
- [ ] Determine SMB reachability
- [ ] Determine RPC reachability
- [ ] Determine WinRM reachability
- [ ] Preserve hostname-based Kerberos where required
- [ ] Avoid unnecessary broad routing

## Detection

- [ ] Monitor new tunnel processes
- [ ] Monitor long-lived outbound connections
- [ ] Monitor new listeners
- [ ] Monitor unusual SSH forwarding
- [ ] Monitor high fan-out traffic
- [ ] Monitor unusual east-west traffic
- [ ] Monitor route changes
- [ ] Monitor new interfaces
- [ ] Review Windows portproxy
- [ ] Monitor unexpected server egress
- [ ] Monitor DNS anomalies
- [ ] Correlate source process and network traffic

## Hardening

- [ ] Enforce network segmentation
- [ ] Enforce host firewalls
- [ ] Restrict workstation-to-workstation traffic
- [ ] Restrict workstation-to-server administration
- [ ] Restrict server egress
- [ ] Protect management networks
- [ ] Use administrative tiering
- [ ] Use privileged administrative workstations
- [ ] Deploy application control
- [ ] Deploy EDR
- [ ] Monitor east-west traffic
- [ ] Review firewall rules regularly

## Cleanup

- [ ] Stop tunnel processes
- [ ] Stop tunnel servers
- [ ] Remove temporary binaries
- [ ] Remove temporary routes
- [ ] Remove temporary interfaces
- [ ] Remove portproxy entries
- [ ] Restore temporary DNS changes
- [ ] Close listeners
- [ ] Verify no tunnel remains
- [ ] Record cleanup time

## Reporting

- [ ] Identify underlying network weakness
- [ ] Identify trust boundary crossed
- [ ] Identify pivot host
- [ ] Identify destination network
- [ ] Identify affected systems
- [ ] Document tunnel type
- [ ] Document minimal validation
- [ ] Explain lateral-movement impact
- [ ] Avoid exposing credentials
- [ ] Provide targeted segmentation recommendation

---

# Pivoting Testing Model

The basic model is:

```text
Operator
   |
   v
Pivot
   |
   v
Target
```

The segmentation model is:

```text
Operator
   |
   X
   |
Target

Operator
   |
   v
Pivot
   |
   v
Target
```

The local-forward model is:

```text
127.0.0.1:8445
      |
      v
Tunnel
      |
      v
Pivot
      |
      v
Target:445
```

The SOCKS model is:

```text
Application
    |
    v
SOCKS
    |
    v
Tunnel
    |
    v
Pivot
    |
    v
Internal Network
```

The TUN model is:

```text
Application
    |
    v
Routing Table
    |
    v
TUN
    |
    v
Tunnel
    |
    v
Pivot
    |
    v
Internal Network
```

The reverse-tunnel model is:

```text
Internal Network
      ^
      |
Pivot
      |
      | Outbound
      v
Assessment Host
```

The double-pivot model is:

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
   |
   v
Target
```

The Active Directory model is:

```text
Assessment Host
      |
      v
Pivot
      |
      +--> DNS
      |
      +--> Kerberos
      |
      +--> LDAP
      |
      +--> SMB
      |
      +--> RPC
      |
      v
Active Directory
```

The detection model is:

```text
Tunnel Process
      |
      v
Long-Lived Connection
      |
      v
Internal Fan-Out
      |
      v
Previously Unusual Destination
```

The defensive model is:

```text
Network Segmentation
       +
Host Firewalls
       +
Egress Filtering
       +
Administrative Tiering
       +
Application Control
       +
EDR
       +
Network Monitoring
       =
Reduced Pivoting Opportunity
```

For penetration testers:

```text
Do Not Ask:
"How can I tunnel everything?"

Ask:
"What minimum network path is required
to validate the identified trust boundary?"
```

For defenders:

```text
Do Not Ask:
"Can an attacker install Chisel?"

Ask:
"If this system is compromised,
which additional networks become reachable?"
```

The complete relationship is:

```text
Initial Access
     |
     v
Network Position
     |
     v
Pivot Host
     |
     v
Additional Reachability
     |
     v
Remote Services
     |
     v
Potential Lateral Movement
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Active Directory Enumeration:

[Enumeration](enumeration.md)

Lateral Movement:

[Lateral Movement](lateral-movement.md)

SMB:

[SMB](smb.md)

WinRM:

[WinRM](winrm.md)

WMI:

[WMI](wmi.md)

DCOM:

[DCOM](dcom.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

BloodHound:

[BloodHound](bloodhound.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

Pass-the-Hash:

[Pass-the-Hash](pass-the-hash.md)

NTLM:

[NTLM](ntlm.md)

The next Active Directory section should cover domain and forest trust relationships:

```text
docs/active-directory/trusts.md
```

---

# References

## MITRE ATT&CK - Proxy

[MITRE ATT&CK - T1090 Proxy](https://attack.mitre.org/techniques/T1090/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - External Proxy

[MITRE ATT&CK - T1090.002 External Proxy](https://attack.mitre.org/techniques/T1090/002/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Multi-Hop Proxy

[MITRE ATT&CK - T1090.003 Multi-Hop Proxy](https://attack.mitre.org/techniques/T1090/003/){ target="_blank" rel="noopener noreferrer" }

---

## OpenSSH - Port Forwarding

[OpenSSH Manual](https://man.openbsd.org/ssh){ target="_blank" rel="noopener noreferrer" }

---

## Chisel

[Chisel - GitHub](https://github.com/jpillora/chisel){ target="_blank" rel="noopener noreferrer" }

Verify installed syntax with:

```bash
chisel --help
```

---

## Ligolo-ng

[Ligolo-ng - GitHub](https://github.com/nicocha30/ligolo-ng){ target="_blank" rel="noopener noreferrer" }

Verify the installed version using:

```bash
./proxy -h
./agent -h
```

---

## ProxyChains-ng

[ProxyChains-ng - GitHub](https://github.com/rofl0r/proxychains-ng){ target="_blank" rel="noopener noreferrer" }

---

## Socat

[Socat](http://www.dest-unreach.org/socat/){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Netsh Interface Portproxy

[Microsoft - Netsh Interface Portproxy](https://learn.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-interface-portproxy){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Windows Defender Firewall

[Microsoft - Windows Firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Pivoting should be understood as:

```text
Network Reachability
```

rather than:

```text
Privilege Escalation
```

The key question is not:

```text
Can I Start a SOCKS Proxy?
```

It is:

```text
What Additional Security Boundary
Does This Host Allow Me to Cross?
```

A good assessment starts with:

```text
Interfaces
Routes
DNS
Network Architecture
Scope
```

before creating any tunnel.

Choose the smallest mechanism that satisfies the test objective:

```text
One Service
    |
    v
Port Forward
```

```text
Several TCP Services
    |
    v
SOCKS
```

```text
Multiple Protocols / Broad Routing
    |
    v
TUN
```

Do not unnecessarily route:

```text
0.0.0.0/0
```

through an assessment tunnel.

Prefer explicit routes such as:

```text
10.20.30.0/24
```

or even narrower destinations where possible.

Pay particular attention to Active Directory dependencies:

```text
DNS
Kerberos
LDAP
SMB
RPC
```

because a tunnel that provides basic IP connectivity may still be insufficient for domain-aware tooling.

Finally, treat cleanup as part of the assessment rather than an optional final step.

Verify:

```text
Processes
Listeners
Routes
Interfaces
Portproxy Rules
Temporary Files
Proxy Configuration
```

after the tunnel is removed.

The defensive goal is not merely:

```text
Block Chisel
```

or:

```text
Block Ligolo-ng
```

It is to build an architecture where compromise of one system does not automatically provide:

```text
A Route to Everything Else
```

A mature design should look more like:

```text
User Network
     |
     X
     |
Management Network

Application Server
     |
     +--> Required Database
     +--> Required DNS
     |
     X
     |
Unrelated Internal Networks

Privileged Workstation
     |
     v
Management Network
     |
     v
Administrative Services
```

The next section moves from network reachability into one of the most important Active Directory security boundaries:

```text
Domain and Forest Trusts
```
