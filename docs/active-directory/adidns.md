# Active Directory Integrated DNS

Active Directory Integrated DNS, commonly referred to as ADIDNS, stores DNS zone information inside Active Directory rather than only in traditional DNS zone files.

In most Active Directory environments, DNS is a critical dependency for:

```text
Domain Controller Discovery
Kerberos
LDAP
Global Catalog Discovery
Service Location
Domain Joins
Group Policy
Replication
Authentication
```

The relationship can be viewed as:

```text
Active Directory
      |
      v
DNS
      |
      +--> Domain Controllers
      +--> Kerberos
      +--> LDAP
      +--> Global Catalog
      +--> Services
      |
      v
Authentication and Management
```

Because Active Directory depends heavily on DNS, ADIDNS should be included in both penetration-testing enumeration and defensive review.

The important security questions are not simply:

```text
Can DNS be queried?
```

but:

```text
Who Can Create DNS Records?
Who Can Modify Existing Records?
Which Zones Permit Dynamic Updates?
Are Stale Records Present?
Can DNS Changes Influence Authentication?
Can DNS Changes Redirect Network Traffic?
Are DNS Changes Monitored?
```

!!! warning "Authorised testing only"
    DNS modifications can affect authentication, service discovery and production traffic across an Active Directory environment. Prefer read-only enumeration. Do not create, modify or delete production DNS records unless explicitly authorised and an agreed cleanup procedure exists.

---

# ADIDNS at a Glance

Traditional DNS can be represented as:

```text
DNS Server
    |
    v
Zone File
    |
    +--> A
    +--> AAAA
    +--> CNAME
    +--> MX
    +--> SRV
```

With Active Directory Integrated DNS:

```text
Active Directory
      |
      v
DNS Application Partition
      |
      v
DNS Zone
      |
      v
DNS Node
      |
      v
DNS Record
```

The DNS information is stored as Active Directory objects and can be replicated using Active Directory replication.

---

# Why Active Directory Needs DNS

Active Directory clients use DNS to discover services.

For example, a client looking for a domain controller may query:

```text
_ldap._tcp.dc._msdcs.corp.example
```

Kerberos discovery may involve:

```text
_kerberos._tcp.corp.example
```

Global Catalog discovery may involve:

```text
_ldap._tcp.gc._msdcs.corp.example
```

The simplified discovery model is:

```text
Client
  |
  v
DNS Query
  |
  v
SRV Record
  |
  v
Domain Controller
  |
  v
LDAP / Kerberos
```

---

# DNS as Identity Infrastructure

DNS should therefore be considered part of the Active Directory identity infrastructure.

A failure or compromise of DNS can affect:

```text
Authentication
Service Discovery
Domain Controller Selection
Application Connectivity
Management Traffic
```

---

# Active Directory Integrated Zones

A DNS zone can be stored in Active Directory when:

```text
Zone Type
=
Active Directory Integrated
```

Instead of relying on a single writable zone file, DNS information can be replicated between authorised DNS servers through Active Directory.

---

# Benefits of AD Integrated DNS

Common benefits include:

```text
Multi-Master Updates
Active Directory Replication
Secure Dynamic Updates
Integrated Access Control
Improved Availability
```

---

# DNS Application Partitions

Modern Active Directory environments commonly store DNS data in application directory partitions.

Common partitions include:

```text
DomainDnsZones
ForestDnsZones
```

---

# DomainDnsZones

Conceptually:

```text
DC=DomainDnsZones,DC=corp,DC=example
```

contains DNS information intended for DNS servers within the domain.

---

# ForestDnsZones

Conceptually:

```text
DC=ForestDnsZones,DC=corp,DC=example
```

contains DNS information that can be replicated across DNS servers in the forest.

---

# Legacy DNS Storage

Older configurations may store DNS information beneath:

```text
CN=MicrosoftDNS,CN=System
```

The exact location depends on:

```text
Windows Version
Zone Configuration
Migration History
Replication Scope
```

Do not assume every environment uses the same storage location.

---

# DNS Object Model

A simplified ADIDNS structure is:

```text
DNS Zone
   |
   v
dnsZone
   |
   v
dnsNode
   |
   v
dnsRecord
```

---

# dnsZone

A DNS zone is represented by a directory object associated with the DNS namespace.

Example:

```text
corp.example
```

---

# dnsNode

Individual DNS names can be represented using:

```text
dnsNode
```

objects.

Example conceptual node:

```text
files01
```

inside:

```text
corp.example
```

represents:

```text
files01.corp.example
```

---

# dnsRecord

The DNS data itself is stored in the:

```text
dnsRecord
```

attribute.

This attribute uses a binary structure rather than ordinary human-readable DNS text.

---

# Common DNS Record Types

During Active Directory assessments, commonly encountered record types include:

```text
A
AAAA
CNAME
SRV
NS
SOA
PTR
MX
TXT
```

---

# A Record

Maps a hostname to an IPv4 address:

```text
files01.corp.example
        |
        v
10.20.30.40
```

---

# AAAA Record

Maps a hostname to an IPv6 address.

```text
files01.corp.example
        |
        v
2001:db8::10
```

---

# CNAME Record

Creates an alias:

```text
portal.corp.example
        |
        v
web01.corp.example
```

---

# SRV Record

Service records are extremely important in Active Directory.

Example:

```text
_ldap._tcp.dc._msdcs.corp.example
```

can identify domain controllers providing LDAP.

---

# Domain Controller Discovery

Query using Linux:

```bash
dig _ldap._tcp.dc._msdcs.corp.example SRV
```

Windows:

```powershell
Resolve-DnsName -Type SRV '_ldap._tcp.dc._msdcs.corp.example'
```

---

# Kerberos Discovery

Linux:

```bash
dig _kerberos._tcp.corp.example SRV
```

Windows:

```powershell
Resolve-DnsName -Type SRV '_kerberos._tcp.corp.example'
```

---

# Global Catalog Discovery

```bash
dig _ldap._tcp.gc._msdcs.corp.example SRV
```

---

# Discover Domain Controller

Native Windows:

```cmd
nltest /dsgetdc:corp.example
```

This can reveal information such as:

```text
Domain Controller
Address
Domain
Forest
Site
Flags
```

---

# PowerShell DNS Enumeration

Basic DNS resolution:

```powershell
Resolve-DnsName 'corp.example'
```

---

# Query A Records

```powershell
Resolve-DnsName -Name 'files01.corp.example' -Type A
```

---

# Query AAAA Records

```powershell
Resolve-DnsName -Name 'files01.corp.example' -Type AAAA
```

---

# Query NS Records

```powershell
Resolve-DnsName -Name 'corp.example' -Type NS
```

---

# Query SOA Record

```powershell
Resolve-DnsName -Name 'corp.example' -Type SOA
```

---

# Query MX Records

```powershell
Resolve-DnsName -Name 'corp.example' -Type MX
```

---

# Query TXT Records

```powershell
Resolve-DnsName -Name 'corp.example' -Type TXT
```

---

# DNS Server PowerShell Module

Where the DNS Server module is available and the user has appropriate permissions:

```powershell
Get-DnsServerZone
```

This typically requires execution on a DNS server or remote management access to one.

---

# Query Zone Records

Where authorised:

```powershell
Get-DnsServerResourceRecord -ZoneName 'corp.example'
```

This can provide a structured view of records in a zone.

---

# Remote DNS Server Query

If administrative access is explicitly authorised:

```powershell
Get-DnsServerZone -ComputerName 'dc01.corp.example'
```

Do not assume ordinary domain users have access to DNS Server management APIs.

---

# Linux DNS Enumeration

Common tools include:

```text
dig
host
nslookup
dnsrecon
dnsenum
```

---

# dig

Name server enumeration:

```bash
dig corp.example NS
```

SOA:

```bash
dig corp.example SOA
```

A record:

```bash
dig files01.corp.example A
```

SRV:

```bash
dig _ldap._tcp.dc._msdcs.corp.example SRV
```

---

# host

```bash
host corp.example
```

Specific record:

```bash
host -t SRV _ldap._tcp.dc._msdcs.corp.example
```

---

# nslookup

Interactive:

```bash
nslookup
```

Then:

```text
set type=SRV
_ldap._tcp.dc._msdcs.corp.example
```

---

# Zone Transfer

DNS zone transfer uses:

```text
AXFR
```

A zone transfer can reveal a large portion of a DNS namespace if the DNS server permits it.

Test only against authorised DNS servers.

Example:

```bash
dig AXFR corp.example @10.20.30.10
```

or:

```bash
dig @10.20.30.10 corp.example AXFR
```

---

# Zone Transfer Result

A successful transfer may reveal:

```text
Domain Controllers
File Servers
Application Servers
Mail Servers
Management Systems
Legacy Hosts
Internal Naming Conventions
```

---

# Zone Transfer Security

A successful AXFR is not automatically critical.

Impact depends on:

```text
Information Exposed
Network Accessibility
Environment Sensitivity
Whether Transfer Was Intended
```

However, unnecessary unauthenticated zone transfers can significantly improve attacker reconnaissance.

---

# DNSRecon

DNSRecon can assist with DNS enumeration.

Check installed syntax:

```bash
dnsrecon -h
```

Basic domain enumeration:

```bash
dnsrecon -d corp.example
```

Zone transfer testing:

```bash
dnsrecon -d corp.example -t axfr
```

Use only within the authorised DNS namespace.

---

# DNS Enumeration Workflow

A useful initial workflow is:

```text
Domain
  |
  v
Name Servers
  |
  v
SOA
  |
  v
Domain Controllers
  |
  v
Kerberos
  |
  v
LDAP
  |
  v
Global Catalog
  |
  v
Known Hosts
```

---

# ADIDNS Enumeration Through LDAP

Because AD Integrated DNS information exists in Active Directory, LDAP can also expose DNS objects when the querying identity has permission to read them.

This is different from ordinary DNS protocol enumeration.

---

# Discover Naming Contexts

LDAP RootDSE can identify naming contexts.

Example:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -s base \
  -b '' \
  defaultNamingContext namingContexts
```

Potential output may include:

```text
DC=corp,DC=example

DC=DomainDnsZones,DC=corp,DC=example

DC=ForestDnsZones,DC=corp,DC=example
```

---

# DomainDnsZones Search Base

A common search base is:

```text
CN=MicrosoftDNS,DC=DomainDnsZones,DC=corp,DC=example
```

---

# ForestDnsZones Search Base

A common forest-wide DNS search base is:

```text
CN=MicrosoftDNS,DC=ForestDnsZones,DC=corp,DC=example
```

---

# Enumerate DNS Nodes with LDAP

Example:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=MicrosoftDNS,DC=DomainDnsZones,DC=corp,DC=example' \
  '(objectClass=dnsNode)' \
  distinguishedName name
```

This performs read-only enumeration.

---

# Enumerate DNS Zones

Example:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=MicrosoftDNS,DC=DomainDnsZones,DC=corp,DC=example' \
  '(objectClass=dnsZone)' \
  distinguishedName name
```

---

# DNS Record Binary Data

Requesting:

```text
dnsRecord
```

through LDAP may return binary data.

Example:

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=MicrosoftDNS,DC=DomainDnsZones,DC=corp,DC=example' \
  '(objectClass=dnsNode)' \
  name dnsRecord
```

Dedicated ADIDNS-aware tooling can make this easier to interpret.

---

# ADIDNS Tooling

Several security tools can interact with Active Directory Integrated DNS.

One commonly encountered project is:

```text
adidnsdump
```

It is designed to enumerate and dump DNS information from AD Integrated DNS using LDAP.

---

# adidnsdump

Project:

```text
https://github.com/dirkjanm/adidnsdump
```

Install according to the project's current documentation.

Check syntax:

```bash
adidnsdump -h
```

Because command-line behaviour can change between versions, use the installed help output as the authoritative reference.

---

# Read-Only ADIDNS Dumping

A typical assessment goal is:

```text
LDAP Authentication
      |
      v
DNS Partition
      |
      v
DNS Nodes
      |
      v
Host Inventory
```

This can reveal records that are not necessarily discoverable through simple DNS brute forcing.

---

# Why LDAP DNS Enumeration Matters

Normal DNS enumeration asks:

```text
Does this hostname resolve?
```

ADIDNS enumeration may instead ask:

```text
Which DNS objects exist in the directory?
```

These approaches can produce different visibility.

---

# Tombstoned and Stale Data

Directory-backed DNS may contain:

```text
Stale Records
Aging Records
Tombstoned Objects
Legacy Names
```

depending on configuration and lifecycle.

Do not assume every discovered DNS object represents a currently active system.

---

# DNS Records Are Not Proof of Live Hosts

Always distinguish:

```text
DNS Record Exists
```

from:

```text
Host Is Alive
```

A safer validation flow is:

```text
DNS Record
    |
    v
Resolve
    |
    v
Approved Connectivity Test
    |
    v
Service Validation
```

---

# Dynamic DNS Updates

Active Directory environments frequently use dynamic DNS updates.

A client may register or update DNS records automatically.

Conceptually:

```text
Domain Client
     |
     v
Dynamic DNS Update
     |
     v
DNS Server
     |
     v
AD Integrated Zone
```

---

# Secure Dynamic Updates

AD Integrated zones can be configured to accept:

```text
Secure Only
```

dynamic updates.

This allows Active Directory authentication and ACLs to control record updates.

---

# Dynamic Update Modes

Depending on zone configuration, dynamic updates may be:

```text
None
Nonsecure and Secure
Secure Only
```

For AD Integrated production zones:

```text
Secure Only
```

is generally the preferred configuration.

---

# Why Nonsecure Dynamic Updates Matter

If a zone permits unauthenticated dynamic updates, an unauthorised system may potentially register or alter DNS information.

The risk model is:

```text
Unauthorised Client
       |
       v
DNS Update
       |
       v
Name Resolution
       |
       v
Traffic Redirection
```

---

# Secure Does Not Mean Every Update Is Safe

Even with secure dynamic updates, permissions still matter.

The important question becomes:

```text
Which Authenticated Principal
Can Modify Which DNS Object?
```

---

# DNS Record Ownership

Dynamically registered DNS records can have security descriptors and ownership.

Conceptually:

```text
Computer Account
      |
      v
Creates DNS Node
      |
      v
Becomes Associated with Object
      |
      v
ACL Controls Future Changes
```

The exact behaviour depends on how the record was created and DNS configuration.

---

# DNS ACLs

Because DNS objects are stored in Active Directory, they can have:

```text
Owner
DACL
ACEs
```

like other directory objects.

This makes DNS permissions part of the broader Active Directory ACL attack surface.

See:

[ACL and ACE](acl-ace.md)

---

# DNS Record Permission Review

A high-value assessment asks:

```text
Can Low-Privilege Users Create Records?

Can Users Modify Records They Do Not Own?

Can Broad Groups Modify Sensitive DNS Nodes?

Can Delegated Administrators Modify Critical Records?

Can Stale Objects Be Reclaimed?
```

---

# Record Creation vs Record Modification

These are different security questions.

```text
Create New Name
```

may be permitted while:

```text
Modify Existing Name
```

is denied.

Do not assume that permission to create a DNS record provides control over existing DNS records.

---

# Existing Record

Suppose:

```text
portal.corp.example
```

already exists.

The relevant question is:

```text
Who Owns the dnsNode?

What Does Its DACL Permit?
```

---

# Nonexistent Name

If:

```text
unused-name.corp.example
```

does not exist, zone-level permissions may determine whether an authenticated identity can create it.

This distinction is important during ADIDNS security testing.

---

# DNS Record Creation Risk

Record creation becomes security relevant when another system attempts to resolve a predictable but currently nonexistent name.

Conceptually:

```text
Application
    |
    v
Resolve Missing Name
    |
    v
Attacker-Controlled DNS Record
    |
    v
Attacker-Controlled Address
```

This can redirect traffic.

---

# DNS Name Collision

A potentially dangerous pattern is:

```text
Application Expects Name
        |
        v
DNS Name Does Not Exist
        |
        v
Another Principal Registers Name
        |
        v
Application Resolves New Record
```

This is sometimes referred to as:

```text
DNS Name Takeover
```

or:

```text
DNS Record Hijacking
```

depending on the exact condition.

---

# DNS Hijacking vs DNS Spoofing

These concepts should be distinguished.

DNS spoofing often means:

```text
Forged DNS Response
```

whereas ADIDNS record abuse may involve:

```text
Legitimate DNS Infrastructure
       |
       v
Unauthorised or Excessive Record Permission
       |
       v
Malicious Record
```

The second scenario can be more persistent because the authoritative DNS infrastructure itself serves the record.

---

# ADIDNS and NTLM

DNS redirection can become particularly important when Windows systems authenticate automatically to network services.

Conceptually:

```text
Victim
 |
 v
Resolve Name
 |
 v
Controlled Address
 |
 v
Network Service
 |
 v
Authentication Attempt
```

Depending on:

```text
Protocol
Application
Security Configuration
Credentials
NTLM Policy
```

this may result in NTLM authentication.

See:

[NTLM](ntlm.md)

---

# ADIDNS and NTLM Relay

The broader risk can become:

```text
DNS Control
    |
    v
Traffic Redirection
    |
    v
Authentication
    |
    v
Relay Opportunity
```

if all other relay prerequisites exist.

See:

[NTLM Relay](ntlm-relay.md)

DNS control alone does not guarantee relay.

---

# DNS Control Does Not Equal Credential Capture

Avoid reporting:

```text
Can Create DNS Record
=
Credentials Can Be Captured
```

The actual chain requires:

```text
Relevant Name Resolution
Reachable Controlled Service
Authentication Behaviour
Suitable Protocol
Victim Interaction
Security Controls
```

Each stage should be established separately.

---

# ADIDNS and Authentication Coercion

Authentication coercion and DNS manipulation can sometimes intersect.

Conceptually:

```text
Coercion Primitive
      |
      v
Target Resolves Name
      |
      v
DNS
      |
      v
Controlled Destination
      |
      v
Authentication Attempt
```

See:

[Authentication Coercion](authentication-coercion.md)

Do not combine intrusive coercion and DNS modification unless explicitly authorised.

---

# ADIDNS and Kerberos

Kerberos depends heavily on correct DNS and SPN resolution.

However:

```text
DNS Control
```

does not automatically mean:

```text
Kerberos Impersonation
```

Kerberos still validates the requested service and cryptographic ticket information.

---

# ADIDNS and LDAP

Domain controllers advertise LDAP through DNS SRV records.

Example:

```text
_ldap._tcp.dc._msdcs.corp.example
```

These records are highly important to Active Directory operation.

Do not modify infrastructure SRV records during penetration testing.

---

# ADIDNS and Domain Controllers

Critical DNS records can include those associated with:

```text
Domain Controllers
Kerberos
LDAP
Global Catalog
PDC
Forest Services
```

Modification of these records can cause significant disruption.

Treat them as production-critical infrastructure.

---

# _msdcs Zone

Active Directory commonly uses:

```text
_msdcs
```

for domain controller and forest-related DNS information.

Example:

```text
_msdcs.corp.example
```

This namespace should receive particularly careful monitoring and access control.

---

# Domain Controller GUID Records

Active Directory replication and domain controller location can depend on DNS records associated with domain controller GUIDs.

Do not modify or remove these records during security testing.

---

# DNS Scavenging

DNS aging and scavenging can automatically remove stale dynamically registered records.

The lifecycle is broadly:

```text
Record Created
     |
     v
Record Refreshed
     |
     v
No Refresh
     |
     v
Aging
     |
     v
Scavenging
```

---

# Why Scavenging Matters

Without appropriate lifecycle management:

```text
Old Systems
   |
   v
Stale DNS Records
   |
   v
Incorrect Resolution
```

can persist.

Stale records can create:

```text
Operational Confusion
Information Disclosure
Name-Reuse Risk
Unexpected Traffic
```

---

# Stale Record Risk

Suppose:

```text
legacy-app.corp.example
```

still resolves to an address that has been reassigned.

The resulting model may be:

```text
Legacy Name
    |
    v
Reassigned Address
    |
    v
Unexpected System
```

This can create both operational and security issues.

---

# Dangling CNAME Records

A CNAME may reference a target that no longer exists.

Example:

```text
portal.corp.example
        |
        v
old-app.internal.example
        |
        X
```

Whether this creates an exploitable condition depends on whether the missing target can be legitimately claimed or controlled.

Do not label every dangling CNAME as a takeover vulnerability.

---

# DNS Wildcards

Wildcard DNS records may cause unexpected names to resolve.

Example:

```text
*.corp.example
```

This can affect:

```text
Enumeration
Application Routing
Certificate Validation
Virtual Hosting
Security Testing
```

Check whether apparent hostnames are simply wildcard responses.

---

# Wildcard Detection

Example:

```bash
dig definitely-does-not-exist-938472.corp.example A
```

If arbitrary names resolve identically, a wildcard may exist.

Use a random, clearly non-production test label.

---

# DNSSEC

DNSSEC provides integrity protection for DNS data using cryptographic signatures.

Its use in internal Active Directory environments varies.

DNSSEC should not be confused with:

```text
Secure Dynamic Updates
```

They address different security properties.

---

# DNSSEC vs Secure Dynamic Updates

```text
DNSSEC
=
Authenticity / Integrity of DNS Data
```

while:

```text
Secure Dynamic Updates
=
Authorisation for DNS Record Changes
```

---

# DNS Recursion

DNS servers may provide recursive resolution.

During assessment, determine whether recursion is:

```text
Internal Only
Restricted
Internet Exposed
Unrestricted
```

An internal AD DNS server generally should not provide unnecessary recursion to untrusted networks.

---

# DNS Forwarders

Active Directory DNS servers commonly forward unresolved requests to:

```text
Internal Resolvers
Security DNS Services
Upstream DNS
Internet Resolvers
```

Review:

```text
Forwarder Security
Logging
Availability
Trust
```

---

# Conditional Forwarders

Conditional forwarders are especially common with:

```text
Trusted Domains
Separate Forests
Partner Networks
```

Example:

```text
partner.example
      |
      v
Partner DNS Servers
```

These relationships can reveal trust and infrastructure dependencies.

---

# Trust Relationships and DNS

Active Directory trusts frequently require cross-domain name resolution.

See:

[Trust Relationships](trust-relationships.md)

A trust can be healthy while authentication still fails because:

```text
DNS Resolution
```

is broken.

---

# DNS and Pivoting

Internal DNS may not be directly accessible from the tester's original network location.

A pivot can introduce additional complexity:

```text
Operator
   |
   v
Pivot
   |
   v
Internal DNS
```

See:

[Pivoting](pivoting.md)

---

# DNS Through SOCKS

SOCKS-based pivoting requires particular attention to where DNS resolution occurs.

Potential problem:

```text
Tool
 |
 v
Local DNS Resolver
 |
 X
 |
Internal Name
```

even though the target TCP service is reachable through the proxy.

---

# Remote DNS Resolution

When using proxy tooling, determine whether:

```text
DNS Resolution Is Local
```

or:

```text
DNS Resolution Is Proxied
```

Incorrect DNS behaviour can:

```text
Leak Internal Queries
Cause False Negatives
Break Kerberos
```

---

# ADIDNS and BloodHound

BloodHound focuses primarily on Active Directory relationships rather than acting as a DNS inventory platform.

However, DNS information can help resolve and contextualise:

```text
Computers
Domain Controllers
Services
Domains
Forests
```

identified during graph analysis.

See:

[BloodHound](bloodhound.md)

---

# ADIDNS and NetExec

NetExec can help validate systems discovered through DNS.

See:

[NetExec](netexec.md)

A safe workflow is:

```text
DNS Record
    |
    v
Approved Host
    |
    v
Minimal Service Check
```

rather than immediately scanning every discovered address.

---

# ADIDNS and Impacket

Impacket tools depend heavily on:

```text
Correct Hostnames
DNS
Kerberos Realm Resolution
Domain Controller Selection
```

See:

[Impacket](impacket.md)

When Kerberos tooling fails, verify DNS before assuming credentials or tickets are invalid.

---

# Kerberos Troubleshooting

A useful sequence is:

```text
Hostname Correct?
      |
      v
DNS Resolves?
      |
      v
KDC Discoverable?
      |
      v
Time Correct?
      |
      v
SPN Correct?
      |
      v
Ticket Valid?
```

---

# DNS Server Enumeration

From Windows:

```powershell
Get-DnsClientServerAddress
```

This identifies configured DNS resolvers.

---

# IP Configuration

```powershell
Get-NetIPConfiguration
```

or:

```cmd
ipconfig /all
```

Review:

```text
DNS Servers
DNS Suffix
Connection-Specific Suffix
Primary DNS Suffix
```

---

# DNS Suffix Search List

```powershell
Get-DnsClientGlobalSetting
```

This can help explain why short hostnames resolve.

---

# Linux Resolver Configuration

```bash
cat /etc/resolv.conf
```

On systems using `systemd-resolved`:

```bash
resolvectl status
```

---

# DNS Cache

Windows:

```cmd
ipconfig /displaydns
```

This may reveal recently resolved names.

Treat cached entries as historical observations rather than proof that services are currently active.

---

# Clear DNS Cache

Windows supports:

```cmd
ipconfig /flushdns
```

However, this changes host state.

Do not flush production caches merely for enumeration.

---

# Safe DNS Assessment Workflow

A recommended workflow is:

```text
Identify Domain
      |
      v
Identify DNS Servers
      |
      v
Enumerate NS / SOA
      |
      v
Enumerate AD SRV Records
      |
      v
Identify DNS Partitions
      |
      v
Read ADIDNS Objects
      |
      v
Review Dynamic Update Configuration
      |
      v
Review ACLs
      |
      v
Identify Stale / Interesting Records
      |
      v
Validate Only Approved Targets
      |
      v
Report
```

---

# Step 1 - Identify Domain

Windows:

```cmd
whoami
```

```cmd
echo %USERDNSDOMAIN%
```

PowerShell:

```powershell
$env:USERDNSDOMAIN
```

---

# Step 2 - Identify DNS Servers

```powershell
Get-DnsClientServerAddress
```

or:

```cmd
ipconfig /all
```

---

# Step 3 - Enumerate Name Servers

```bash
dig corp.example NS
```

---

# Step 4 - Enumerate SOA

```bash
dig corp.example SOA
```

---

# Step 5 - Enumerate Domain Controllers

```bash
dig _ldap._tcp.dc._msdcs.corp.example SRV
```

---

# Step 6 - Enumerate Kerberos

```bash
dig _kerberos._tcp.corp.example SRV
```

---

# Step 7 - Enumerate Global Catalog

```bash
dig _ldap._tcp.gc._msdcs.corp.example SRV
```

---

# Step 8 - Test Zone Transfer

Only against an authorised DNS server:

```bash
dig @10.20.30.10 corp.example AXFR
```

---

# Step 9 - Discover DNS Application Partitions

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -s base \
  -b '' \
  namingContexts
```

---

# Step 10 - Enumerate ADIDNS Objects

```bash
ldapsearch -x -H ldap://dc01.corp.example \
  -D 'audituser@corp.example' -W \
  -b 'CN=MicrosoftDNS,DC=DomainDnsZones,DC=corp,DC=example' \
  '(objectClass=dnsNode)' \
  distinguishedName name
```

---

# Step 11 - Review Permissions

Where appropriate and authorised, inspect the security descriptors associated with relevant DNS objects.

Focus on:

```text
Sensitive Records
Broad Write Permissions
Unexpected Owners
Delegated Groups
```

---

# Step 12 - Validate Minimum Impact

If a suspicious DNS permission is identified:

```text
Permission
    |
    v
Potential DNS Change
    |
    v
Affected Resolution Path
    |
    v
Potential Security Impact
```

Prefer proving the permission and dependency without changing the record.

---

# Safe DNS Write Validation

Production DNS changes should generally be avoided.

If explicit write testing is required, use:

```text
Dedicated Test Zone
```

or:

```text
Pre-Approved Unique Test Record
```

Example conceptual name:

```text
pentest-validation-<random>.corp.example
```

The test should include:

```text
Create
Verify
Delete
Verify Deletion
```

with timestamps and DNS owner approval.

---

# Never Use Existing Production Names

Do not overwrite:

```text
Domain Controllers
Applications
File Servers
Web Servers
Management Systems
Authentication Services
```

to prove DNS write access.

The permission itself may already provide sufficient evidence.

---

# DNS Evidence

Record:

```text
Domain
DNS Server
Zone
Zone Type
Replication Scope
Dynamic Update Mode
DNS Node
Record Type
Record Value
Object Owner
Relevant ACE
Test Identity
Resolution Result
Timestamp
Tool
Tool Version
```

---

# DNS Evidence Example

```text
Zone:
corp.example

Zone Type:
Active Directory Integrated

Dynamic Updates:
Secure Only

Object:
CN=test-record,CN=MicrosoftDNS,DC=DomainDnsZones,DC=corp,DC=example

Observation:
The assessment account had permission to create child objects within
the approved test area of the DNS zone.

Validation:
A uniquely named test record was created and removed with prior
approval.

Production records were not modified.
```

---

# ADIDNS Detection

Defensive monitoring should focus on:

```text
DNS Record Creation
DNS Record Modification
DNS Record Deletion
Zone Configuration Changes
Dynamic Update Changes
Unexpected DNS Ownership
Unusual DNS Queries
Sensitive Record Changes
```

---

# DNS Server Logging

Windows DNS Server provides logging capabilities including:

```text
DNS Server Event Logs
Analytical Logging
Debug Logging
```

The exact configuration should balance:

```text
Visibility
Performance
Storage
Operational Requirements
```

---

# DNS Server Event Logs

Review:

```text
Applications and Services Logs
    |
    v
Microsoft
    |
    v
Windows
    |
    v
DNS-Server
```

Available channels depend on Windows Server version and configuration.

---

# Active Directory Object Monitoring

Because ADIDNS records are directory objects, Active Directory auditing can also contribute visibility.

Event:

```text
5136
```

may identify directory object modification when appropriate auditing and SACLs are configured.

---

# Event 5136

Event 5136 indicates:

```text
A directory service object was modified
```

For ADIDNS monitoring, correlate:

```text
Actor
Object DN
Attribute
Time
Domain Controller
```

---

# DNS Change Correlation

A useful detection model is:

```text
Directory Change
      |
      v
DNS Node
      |
      v
New Resolution
      |
      v
Client Connections
      |
      v
Authentication
```

This provides more context than alerting on a DNS change alone.

---

# Detect New Records

Newly created records deserve additional attention when:

```text
Creator Is Unexpected
Name Resembles Infrastructure
Address Is External
Address Is Unusual
Name Was Previously Missing
Record Appears Shortly Before Authentication Activity
```

---

# Detect Sensitive Record Modification

High-value records include those related to:

```text
Domain Controllers
Kerberos
LDAP
Global Catalog
AD CS
ADFS
Management Infrastructure
Backup Infrastructure
```

Changes should normally correspond to known administrative activity.

---

# External IP Addresses

An internal AD zone suddenly resolving a sensitive hostname to:

```text
Public IP
```

or an unexpected network segment should be investigated.

However, some organisations legitimately use:

```text
Split DNS
Cloud Services
Reverse Proxies
Hybrid Infrastructure
```

so context is essential.

---

# DNS Query Monitoring

DNS telemetry can help identify:

```text
Unusual Host Discovery
High-Volume Enumeration
Random Name Queries
Known Tool Patterns
Unexpected External Resolution
```

Do not assume every burst of DNS queries is malicious.

Inventory systems and monitoring platforms can generate similar behaviour.

---

# ADIDNS Hardening

A strong ADIDNS security model includes:

```text
Secure Dynamic Updates
Least-Privilege ACLs
Protected Infrastructure Records
DNS Aging and Scavenging
Restricted Zone Transfers
Restricted Recursion
Network Segmentation
DNS Logging
Change Monitoring
Lifecycle Management
```

---

# Secure Dynamic Updates

For Active Directory Integrated production zones, prefer:

```text
Secure Only
```

where operationally appropriate.

Avoid:

```text
Nonsecure and Secure
```

unless a documented legacy requirement exists.

---

# Restrict Zone Transfers

Zone transfers should be limited to:

```text
Authorised Secondary DNS Servers
```

when transfers are required.

Avoid exposing AXFR unnecessarily.

---

# Restrict DNS Administration

Membership in:

```text
DNSAdmins
```

and other DNS management roles should be tightly controlled.

DNS administration can be security sensitive and should not be treated as routine low-level infrastructure access.

---

# DNSAdmins

Enumerate:

```powershell
Get-ADGroupMember -Identity 'DNSAdmins'
```

Review:

```text
Users
Nested Groups
Service Accounts
Legacy Administrators
```

Do not assume that membership is harmless simply because the group name refers to DNS.

---

# DNSAdmins Security Context

Historically, excessive DNS Server administrative rights have been security sensitive because DNS services commonly run on domain controllers.

The exact risk depends on:

```text
Windows Version
DNS Architecture
Server Role
Permissions
Current Hardening
```

Assess the actual environment rather than relying on historical attack assumptions.

---

# Protect Critical DNS Objects

Critical infrastructure records should not be writable by broad groups.

Review permissions for:

```text
Domain Controller Records
_msdcs
Kerberos SRV Records
LDAP SRV Records
Global Catalog Records
Critical Applications
```

---

# Least Privilege

Avoid broad ACLs such as:

```text
Authenticated Users - GenericAll
```

or equivalent excessive write permissions on sensitive DNS objects.

The exact permissions required depend on the DNS design.

---

# DNS Aging

Configure appropriate aging where dynamic DNS is heavily used.

The objective is to reduce:

```text
Stale Dynamic Records
```

without accidentally deleting valid static infrastructure records.

---

# Scavenging

Scavenging should be designed carefully.

Poorly configured scavenging can cause:

```text
Service Outages
Unexpected Record Removal
```

so remediation should follow DNS operational guidance rather than simply enabling aggressive cleanup.

---

# Static Records

Critical infrastructure may use static DNS records.

These require their own:

```text
Ownership
Change Management
Lifecycle Review
```

because scavenging will not necessarily remove them.

---

# Monitor Delegated DNS Permissions

DNS management is frequently delegated.

Review:

```text
Who Can Create Records?
Who Can Delete Records?
Who Can Modify Zone Settings?
Who Can Manage DNS Servers?
```

---

# Restrict DNS Network Exposure

DNS servers should be reachable only from networks that require the service.

External clients should not normally have direct access to internal Active Directory DNS infrastructure.

---

# Split DNS

Organisations may use separate:

```text
Internal DNS
External DNS
```

for the same namespace.

This is commonly called:

```text
Split DNS
```

or:

```text
Split-Horizon DNS
```

Ensure internal records are not unintentionally published externally.

---

# Internal Information Disclosure

External DNS should generally not reveal unnecessary internal details such as:

```text
Domain Controller Names
Internal IP Addresses
Management Systems
Internal Service Names
```

unless there is a specific requirement.

---

# DNS Backup and Recovery

DNS recovery should be included in Active Directory disaster recovery planning.

For AD Integrated zones, recovery is closely connected to:

```text
Active Directory Recovery
Replication
Domain Controller Recovery
```

---

# Reporting ADIDNS Findings

Do not report:

```text
Active Directory Integrated DNS Is Enabled
```

as a vulnerability.

AD integration is normal and generally desirable.

Report the actual security weakness.

Examples:

```text
Unauthenticated DNS Zone Transfer Exposes Internal Infrastructure
```

```text
Nonsecure Dynamic Updates Permitted on Active Directory DNS Zone
```

```text
Excessive DNS Object Permissions Permit Unauthorised Record Creation
```

```text
Sensitive DNS Record Writable by Low-Privilege Principal
```

```text
Stale DNS Records Create Unnecessary Name-Reuse Risk
```

```text
Internal Active Directory DNS Exposed to Untrusted Networks
```

---

# Example Finding - Zone Transfer

```text
Finding:
Internal DNS Zone Transfer Permitted to Unauthorised Clients

Description:
The authoritative DNS server permitted a full zone transfer for the
internal Active Directory DNS zone from the assessment network.

The transfer disclosed hostnames and infrastructure records including
domain controllers, application systems and internal service names.

Impact:
An unauthorised user with network access to the DNS server can obtain
a detailed inventory of the internal DNS namespace.

This significantly reduces the effort required for infrastructure
reconnaissance and can reveal high-value systems.

Recommendation:
Restrict zone transfers to explicitly authorised secondary DNS
servers.

Review DNS access controls and network segmentation to ensure that
untrusted clients cannot request full zone transfers.
```

---

# Example Finding - Nonsecure Dynamic Updates

```text
Finding:
Active Directory DNS Zone Permits Nonsecure Dynamic Updates

Description:
The internal DNS zone accepted dynamic DNS updates without requiring
Active Directory authentication.

Impact:
A system with network access to the DNS service may potentially
register DNS information without possessing an authorised domain
identity.

Depending on the affected names and application behaviour, this could
redirect network traffic or influence authentication flows.

Recommendation:
Where operationally supported, configure the Active Directory
Integrated zone to permit secure dynamic updates only.

Identify and remediate legacy systems that require unauthenticated
updates before enforcing the change.
```

---

# Example Finding - Excessive DNS Write Permission

```text
Finding:
Low-Privilege Domain Users Can Create DNS Records in Sensitive Namespace

Description:
The assessment identified permissions that allowed a low-privilege
domain identity to create DNS objects within a production Active
Directory Integrated DNS namespace.

A uniquely named test record was used for validation with prior
approval. Existing production records were not modified.

Impact:
An attacker controlling a permitted domain identity may be able to
register names that are currently unused.

If applications or users subsequently resolve one of those names,
traffic may be directed to an attacker-controlled system.

The practical impact depends on the names available for registration
and the authentication behaviour of affected clients.

Recommendation:
Review DNS zone ACLs and determine whether broad record-creation
permissions are required.

Apply least privilege while preserving legitimate secure dynamic DNS
registration for domain systems.
```

---

# Example Finding - Sensitive Record Modification

```text
Finding:
Delegated DNS Group Can Modify Critical Infrastructure Record

Description:
A delegated DNS administration group had write permission over a DNS
record associated with a security-sensitive internal service.

The group's business role did not require control of the affected
record.

Impact:
Compromise of a member of the delegated group could allow DNS traffic
for the affected service to be redirected.

Depending on the service, this could result in denial of service,
traffic interception or authentication exposure.

Recommendation:
Remove unnecessary write permissions from the sensitive DNS object.

Separate routine DNS administration from control of Tier 0 and other
security-critical infrastructure records.
```

---

# Example Finding - Stale DNS

```text
Finding:
Stale Active Directory DNS Records Remain After System Decommissioning

Description:
Multiple DNS records referenced systems that had been decommissioned.

The records remained present after the associated hosts were removed
from service.

Impact:
Stale records increase infrastructure ambiguity and may cause traffic
to be directed toward addresses that are later reassigned.

They can also expose historical naming information useful during
reconnaissance.

Recommendation:
Implement a documented DNS lifecycle process.

Review aging and scavenging for dynamic records and ensure static
records are removed through the system decommissioning process.
```

---

# ADIDNS Assessment Checklist

## Environment

- [ ] Identify Active Directory domain
- [ ] Identify forest
- [ ] Identify DNS suffix
- [ ] Identify configured DNS servers
- [ ] Identify authoritative DNS servers
- [ ] Identify DNS server roles
- [ ] Confirm scope

## DNS Discovery

- [ ] Query NS
- [ ] Query SOA
- [ ] Query LDAP SRV
- [ ] Query Kerberos SRV
- [ ] Query Global Catalog SRV
- [ ] Identify `_msdcs`
- [ ] Identify conditional forwarders where authorised
- [ ] Identify split DNS

## Zone Transfer

- [ ] Test AXFR only against authorised DNS servers
- [ ] Record whether transfer succeeds
- [ ] Record source network
- [ ] Record information exposed
- [ ] Avoid unnecessary repeated transfers

## AD Integration

- [ ] Determine whether zone is AD Integrated
- [ ] Identify `DomainDnsZones`
- [ ] Identify `ForestDnsZones`
- [ ] Identify legacy DNS storage if present
- [ ] Enumerate `dnsZone`
- [ ] Enumerate `dnsNode`
- [ ] Understand `dnsRecord`

## Dynamic Updates

- [ ] Identify update mode
- [ ] Identify secure-only zones
- [ ] Identify nonsecure updates
- [ ] Review legacy requirements
- [ ] Review record ownership
- [ ] Review record lifecycle

## Permissions

- [ ] Review zone ACLs
- [ ] Review sensitive node ACLs
- [ ] Review object owners
- [ ] Identify broad write permissions
- [ ] Identify delegated DNS groups
- [ ] Review DNSAdmins membership
- [ ] Identify unexpected privileged identities

## Records

- [ ] Review A records
- [ ] Review AAAA records
- [ ] Review CNAME records
- [ ] Review SRV records
- [ ] Review NS records
- [ ] Review critical infrastructure names
- [ ] Identify stale records
- [ ] Identify dangling records
- [ ] Identify wildcard DNS

## Authentication Risk

- [ ] Identify names used by applications
- [ ] Identify automatic authentication behaviour
- [ ] Review NTLM exposure
- [ ] Review relay prerequisites separately
- [ ] Review Kerberos dependencies
- [ ] Do not equate DNS control with credential compromise

## Safe Validation

- [ ] Prefer read-only enumeration
- [ ] Do not modify production records
- [ ] Use unique approved test record if required
- [ ] Record original state
- [ ] Create only approved record
- [ ] Verify expected resolution
- [ ] Delete test record
- [ ] Verify cleanup
- [ ] Record timestamps

## Detection

- [ ] Monitor DNS Server logs
- [ ] Monitor directory changes
- [ ] Review 5136 where applicable
- [ ] Monitor new DNS nodes
- [ ] Monitor sensitive record changes
- [ ] Monitor unexpected external addresses
- [ ] Correlate DNS changes with authentication
- [ ] Baseline legitimate dynamic updates

## Hardening

- [ ] Use secure dynamic updates where appropriate
- [ ] Restrict zone transfers
- [ ] Restrict recursion
- [ ] Apply least-privilege DNS ACLs
- [ ] Protect critical records
- [ ] Review DNSAdmins
- [ ] Review delegated DNS permissions
- [ ] Configure appropriate aging
- [ ] Configure appropriate scavenging
- [ ] Remove stale static records
- [ ] Segment DNS infrastructure
- [ ] Monitor DNS changes
- [ ] Maintain DNS recovery procedures

## Reporting

- [ ] Do not report AD Integrated DNS itself as a vulnerability
- [ ] Identify exact DNS weakness
- [ ] Record affected zone
- [ ] Record affected record
- [ ] Record affected principal
- [ ] Explain realistic traffic path
- [ ] Explain authentication dependency
- [ ] Avoid overstating theoretical impact
- [ ] Provide DNS-specific remediation

---

# ADIDNS Testing Model

The Active Directory dependency model is:

```text
Active Directory
      |
      v
DNS
      |
      v
Service Discovery
      |
      v
Authentication
```

The storage model is:

```text
Active Directory
      |
      v
DNS Application Partition
      |
      v
dnsZone
      |
      v
dnsNode
      |
      v
dnsRecord
```

The domain-controller discovery model is:

```text
Client
  |
  v
DNS SRV Query
  |
  v
Domain Controller
  |
  +--> Kerberos
  +--> LDAP
```

The dynamic update model is:

```text
Client
  |
  v
Authenticated DNS Update
  |
  v
AD Integrated Zone
  |
  v
DNS Record
```

The permission model is:

```text
Principal
   |
   v
DNS Object ACL
   |
   +--> Read
   +--> Create
   +--> Modify
   +--> Delete
```

The potential abuse model is:

```text
Excessive DNS Permission
        |
        v
Controlled DNS Name
        |
        v
Victim Resolution
        |
        v
Traffic Redirection
        |
        v
Potential Authentication Exposure
```

The important qualification is:

```text
DNS Write
   !=
Automatic Credential Compromise
```

The stale-record model is:

```text
System Decommissioned
       |
       v
DNS Record Remains
       |
       v
Address Reassigned
       |
       v
Unexpected Resolution
```

The trust model is:

```text
Forest A
   |
   v
DNS Resolution
   |
   v
Trust
   |
   v
Forest B
```

The detection model is:

```text
DNS Object Change
       |
       v
Resolution Change
       |
       v
Network Connection
       |
       v
Authentication
```

The defensive model is:

```text
Secure Dynamic Updates
        +
Least-Privilege ACLs
        +
Restricted AXFR
        +
Protected Infrastructure Records
        +
Aging and Scavenging
        +
Network Segmentation
        +
Monitoring
        =
Reduced ADIDNS Risk
```

For penetration testers:

```text
Do Not Ask:
"Can I change a DNS record?"

Ask:
"Which DNS permissions are excessive,
what dependency relies on the affected
name, and can the impact be demonstrated
without disrupting production?"
```

For defenders:

```text
Do Not Ask:
"Does DNS resolve correctly?"

Ask:
"Who can change our DNS namespace,
which records are security critical,
and would we detect an unauthorised
change?"
```

The complete model is:

```text
Identity
   |
   v
DNS Permission
   |
   v
DNS Object
   |
   v
Name Resolution
   |
   v
Network Destination
   |
   v
Authentication / Application
   |
   v
Security Impact
```

---

# Related Notes

Active Directory:

[Active Directory](index.md)

Enumeration:

[Enumeration](enumeration.md)

ACL and ACE:

[ACL and ACE](acl-ace.md)

Kerberos:

[Kerberos](kerberos.md)

NTLM:

[NTLM](ntlm.md)

NTLM Relay:

[NTLM Relay](ntlm-relay.md)

Authentication Coercion:

[Authentication Coercion](authentication-coercion.md)

BloodHound:

[BloodHound](bloodhound.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

Trust Relationships:

[Trust Relationships](trust-relationships.md)

SID History:

[SID History](sid-history.md)

Trust Tickets:

[Trust Tickets](trust-tickets.md)

Pivoting:

[Pivoting](pivoting.md)

The next infrastructure page is:

```text
docs/active-directory/shares.md
```

followed by:

```text
docs/active-directory/sccm.md
docs/active-directory/wsus.md
docs/active-directory/mdt.md
docs/active-directory/scom.md
docs/active-directory/adfs.md
docs/active-directory/rodc.md
```

---

# References

## Microsoft - DNS and AD DS

[Microsoft - DNS and AD DS](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/dns-and-ad-ds){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DNS Zones

[Microsoft - DNS Zones](https://learn.microsoft.com/en-us/windows-server/networking/dns/zone-types){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Active Directory Integrated DNS Zones

[Microsoft - DNS Zones](https://learn.microsoft.com/en-us/windows-server/networking/dns/zone-types){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Dynamic DNS Updates

[Microsoft - Dynamic Update](https://learn.microsoft.com/en-us/windows-server/networking/dns/dynamic-update){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DNS Aging and Scavenging

[Microsoft - DNS Aging and Scavenging](https://learn.microsoft.com/en-us/windows-server/networking/dns/aging-scavenging){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Resolve-DnsName

[Microsoft - Resolve-DnsName](https://learn.microsoft.com/en-us/powershell/module/dnsclient/resolve-dnsname){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-DnsServerZone

[Microsoft - Get-DnsServerZone](https://learn.microsoft.com/en-us/powershell/module/dnsserver/get-dnsserverzone){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Get-DnsServerResourceRecord

[Microsoft - Get-DnsServerResourceRecord](https://learn.microsoft.com/en-us/powershell/module/dnsserver/get-dnsserverresourcerecord){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DNS Server Security

[Microsoft - DNS Security](https://learn.microsoft.com/en-us/windows-server/networking/dns/dns-security){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - DNSAdmins Group

[Microsoft - Active Directory Security Groups](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Event 5136

[Microsoft - 5136: A Directory Service Object Was Modified](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## adidnsdump

[GitHub - dirkjanm/adidnsdump](https://github.com/dirkjanm/adidnsdump){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Network Service Discovery

[MITRE ATT&CK - T1049 System Network Connections Discovery](https://attack.mitre.org/techniques/T1049/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK - Remote System Discovery

[MITRE ATT&CK - T1018 Remote System Discovery](https://attack.mitre.org/techniques/T1018/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Active Directory Integrated DNS is fundamental Active Directory infrastructure.

The normal relationship is:

```text
Active Directory
      |
      v
DNS
      |
      v
Domain and Service Discovery
      |
      v
Authentication
```

ADIDNS itself is not a vulnerability.

The security assessment should instead determine:

```text
Who Controls DNS?
      |
      v
Which Names Can They Control?
      |
      v
Which Systems Resolve Those Names?
      |
      v
What Traffic Follows?
      |
      v
What Security Impact Results?
```

A strong assessment begins with:

```text
Read-Only Enumeration
```

and only progresses to DNS modification when:

```text
Explicitly Authorised
```

and necessary.

The most important distinction is:

```text
DNS Write Permission
        !=
Confirmed Authentication Compromise
```

A complete attack path requires additional conditions.

The defensive objective is:

```text
Secure Dynamic Updates
      |
      v
Least-Privilege DNS Permissions
      |
      v
Protected Critical Records
      |
      v
Controlled DNS Lifecycle
      |
      v
Monitoring
```

DNS should ultimately be treated as part of the identity security boundary rather than merely a supporting network service.

The next infrastructure page covers another major source of Active Directory reconnaissance and credential exposure:

```text
Windows and Active Directory Shares
```
