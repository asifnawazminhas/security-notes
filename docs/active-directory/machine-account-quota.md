# Active Directory Machine Account Quota

Machine Account Quota is an Active Directory setting that controls how many computer accounts an ordinary domain user can create in the domain using the default computer-join mechanism.

The relevant domain attribute is:

```text
ms-DS-MachineAccountQuota
```

It is commonly abbreviated:

```text
MAQ
```

The default value in a newly created Active Directory domain has traditionally been:

```text
10
```

This means that, unless the environment has changed the configuration or otherwise restricted the operation, ordinary authenticated domain users may be able to create computer accounts.

From a security perspective, this matters because a newly created computer object is not merely a directory entry.

It is a security principal with:

```text
Computer Account
      |
      +--> SID
      |
      +--> Password / Kerberos Keys
      |
      +--> Group Membership
      |
      +--> Kerberos Authentication
      |
      +--> Potential SPNs
      |
      +--> Directory Permissions
```

A simplified security model is:

```text
Domain User
    |
    v
Machine Account Quota
    |
    v
Create Computer Account
    |
    v
Control Computer Credentials
    |
    v
New Domain Security Principal
```

Machine Account Quota becomes especially important when combined with other Active Directory weaknesses.

For example:

```text
Machine Account Quota
        |
        v
Controlled Computer Account
        |
        +
Write Access to Target Computer
        |
        v
RBCD
        |
        v
S4U
        |
        v
Delegated Service Ticket
```

Therefore:

```text
MAQ > 0
```

should not automatically be reported as a critical vulnerability.

Instead:

```text
MAQ
 +
Ability to Create Computer
 +
Additional Directory Rights
 +
Reachable Privileged Target
 =
Potential Attack Path
```

!!! warning "Authorised testing only"
    Creating computer accounts changes Active Directory. During assessments, enumerate `ms-DS-MachineAccountQuota` and relevant ACLs first. Only create a test computer account where explicitly authorised. Use a clearly identifiable test object, record the original directory state, avoid modifying production computer objects unless specifically approved, and remove all test objects and related delegation settings after validation.

---

# What Is a Machine Account?

Computers joined to an Active Directory domain normally have corresponding computer objects.

Example:

```text
SERVER01$
```

The trailing:

```text
$
```

is conventionally present in the computer account's `sAMAccountName`.

Conceptually:

```text
Windows Computer
       |
       v
Active Directory
       |
       v
Computer Object
       |
       v
SERVER01$
```

The computer account is a security principal.

---

# Computer Accounts Are Security Principals

A computer account has properties such as:

```text
sAMAccountName
objectSid
objectGUID
userAccountControl
servicePrincipalName
dNSHostName
msDS-SupportedEncryptionTypes
msDS-AllowedToActOnBehalfOfOtherIdentity
```

and other attributes depending on configuration.

The computer account also possesses authentication material.

Conceptually:

```text
Computer Password
      |
      v
Kerberos Keys
      |
      v
Computer Authentication
```

Therefore control of a computer account can be security-relevant even when no physical or virtual computer corresponding to the account exists.

---

# Machine Account Quota

The domain attribute:

```text
ms-DS-MachineAccountQuota
```

defines the number of computer accounts that a non-privileged principal can create through the relevant default mechanism.

Conceptually:

```text
Authenticated Domain User
          |
          v
ms-DS-MachineAccountQuota
          |
          v
Create Computer Objects
```

---

# Default Value

The commonly documented default is:

```text
10
```

However, never assume the value during an assessment.

Always enumerate it.

The environment may have:

```text
0
1
5
10
20
```

or another value.

---

# Why Machine Account Quota Exists

Machine Account Quota supports environments where ordinary users are permitted to join workstations to the domain without requiring a domain administrator for every join operation.

Conceptually:

```text
Employee
   |
   v
Join Computer to Domain
   |
   v
Computer Account Created
```

This can be operationally convenient.

However, the same capability can become useful to an attacker who has compromised a normal domain user.

---

# MAQ Is a Domain Attribute

Machine Account Quota is stored on the domain object.

Example domain:

```text
DC=corp,DC=example
```

Relevant attribute:

```text
ms-DS-MachineAccountQuota
```

---

# Enumerate MAQ with PowerShell

Using the Active Directory PowerShell module:

```powershell
Get-ADDomain |
    Select-Object \
        DNSRoot,
        DistinguishedName
```

Then query the domain object:

```powershell
Get-ADObject \
    -Identity 'DC=corp,DC=example' \
    -Properties ms-DS-MachineAccountQuota |
    Select-Object \
        DistinguishedName,
        ms-DS-MachineAccountQuota
```

Example:

```text
DistinguishedName          ms-DS-MachineAccountQuota
-----------------          -------------------------
DC=corp,DC=example         10
```

---

# Dynamic Domain Query

Avoid hardcoding the domain DN:

```powershell
$domain = Get-ADDomain

Get-ADObject \
    -Identity $domain.DistinguishedName \
    -Properties ms-DS-MachineAccountQuota |
    Select-Object \
        DistinguishedName,
        ms-DS-MachineAccountQuota
```

---

# Enumerate MAQ with ADSI

Where the Active Directory module is unavailable:

```powershell
$root = [ADSI]'LDAP://RootDSE'
$domainDN = $root.defaultNamingContext

$domain = [ADSI]("LDAP://" + $domainDN)

$domain.'ms-DS-MachineAccountQuota'
```

---

# Enumerate with ldapsearch

From Linux:

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    -s base \
    '(objectClass=domain)' \
    ms-DS-MachineAccountQuota
```

Example output:

```text
dn: DC=corp,DC=example
ms-DS-MachineAccountQuota: 10
```

---

# Anonymous LDAP

Do not assume anonymous LDAP queries are permitted.

If anonymous bind is disabled, use authorised domain credentials.

---

# NetExec

NetExec can assist with LDAP and Active Directory enumeration.

Because modules and command-line options can change between versions, inspect the installed version:

```bash
nxc --version
```

and:

```bash
nxc ldap --help
```

before relying on version-specific MAQ modules or options.

For general usage:

[NetExec](netexec.md)

---

# PowerView

PowerView can query domain objects and attributes.

Exact commands depend on the PowerView version.

Useful starting points include:

```powershell
Get-Domain
```

and:

```powershell
Get-DomainObject
```

Check:

```powershell
Get-Help Get-DomainObject -Full
```

before using version-specific property syntax.

Native LDAP or the Active Directory module is usually sufficient for MAQ enumeration.

---

# BloodHound

BloodHound can help determine whether the ability to create or control computer objects contributes to a larger attack path.

The important question is not merely:

```text
Can Alice create a computer?
```

but:

```text
What can a computer controlled by Alice influence?
```

Potential relationships include:

```text
Computer Creation
      |
      v
Controlled Computer Principal
      |
      +--> RBCD
      |
      +--> ACL Relationships
      |
      +--> Group Membership
      |
      +--> Kerberos Authentication
      |
      +--> Other Attack Paths
```

---

# MAQ vs Computer Object ACLs

These concepts must be separated.

```text
Machine Account Quota
```

is not the same as:

```text
CreateChild on an OU
```

A principal may be able to create computer accounts because of:

```text
MAQ
```

or because administrators explicitly delegated:

```text
Create Computer Objects
```

on an OU.

These are different mechanisms.

---

# Delegated Computer Creation

An organisation may set:

```text
ms-DS-MachineAccountQuota = 0
```

while intentionally delegating computer creation to a provisioning group.

Example:

```text
Workstation Provisioning
        |
        v
CreateChild
        |
        v
Workstations OU
```

This can be more controlled than broad default MAQ-based creation.

---

# MAQ Zero Does Not Mean No One Can Create Computers

This is a critical distinction.

```text
MAQ = 0
```

means the default quota mechanism is disabled for ordinary users.

It does not mean:

```text
No Non-Admin Can Create Computer Objects
```

because delegated ACLs may still permit creation.

Therefore test both:

```text
Machine Account Quota
```

and:

```text
OU ACLs
```

---

# Computer Creation Rights

When assessing computer creation, consider:

```text
ms-DS-MachineAccountQuota
CreateChild
GenericAll
GenericWrite
Delegated Join Rights
Pre-Staged Computer Objects
```

The effective capability depends on the directory configuration.

---

# Domain Join vs Computer Object Creation

These are related but not identical concepts.

A domain join typically involves:

```text
Computer
   |
   v
Create or Reuse Computer Object
   |
   v
Establish Machine Password
   |
   v
Configure Domain Membership
```

During security testing, it may be possible to create a computer object without actually joining a Windows system to the domain.

---

# Controlled Computer Account

If an authorised test creates:

```text
PENTEST01$
```

and the tester knows the password used for the account, the tester controls that computer security principal.

Conceptually:

```text
Known Machine Password
        |
        v
Known Kerberos Keys
        |
        v
Controlled Computer Principal
```

---

# Computer Account Authentication

A computer account can authenticate using Kerberos.

Conceptually:

```text
PENTEST01$
    |
    v
AS-REQ
    |
    v
KDC
    |
    v
TGT
```

The resulting identity is:

```text
CORP\PENTEST01$
```

not the user who created it.

---

# Computer Account Group Membership

Domain computer accounts are commonly members of:

```text
Domain Computers
```

This matters where resources grant permissions to:

```text
Domain Computers
```

Example:

```text
Domain Computers
       |
       v
Read Application Share
```

A newly controlled computer principal may therefore inherit access available to that group.

---

# Enumerate Domain Computers Permissions

Do not assume:

```text
Domain Computers
```

has no useful permissions.

Investigate:

```text
Shares
Applications
ACLs
Certificate Templates
Directory Objects
Services
```

that trust the group.

---

# Computer Account SPNs

Domain-joined computer accounts commonly possess Service Principal Names.

Examples can include:

```text
HOST/SERVER01
HOST/SERVER01.corp.example
RestrictedKrbHost/SERVER01
RestrictedKrbHost/SERVER01.corp.example
```

and service-specific SPNs depending on the host and services.

A manually created computer object may not automatically have the exact same SPN set as a normally joined Windows machine.

Always enumerate the actual object.

---

# Enumerate Computer Account

PowerShell:

```powershell
Get-ADComputer \
    -Identity 'PENTEST01' \
    -Properties * |
    Select-Object \
        Name,
        SamAccountName,
        DistinguishedName,
        Enabled,
        DNSHostName,
        ServicePrincipalName,
        UserAccountControl,
        ObjectSID
```

---

# Enumerate All Computer Accounts

```powershell
Get-ADComputer \
    -Filter * \
    -Properties \
        DNSHostName,
        OperatingSystem,
        ServicePrincipalName,
        whenCreated |
    Select-Object \
        Name,
        SamAccountName,
        DNSHostName,
        OperatingSystem,
        whenCreated
```

---

# Recently Created Computer Accounts

Recent computer accounts may deserve review.

Example:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties whenCreated |
    Sort-Object whenCreated -Descending |
    Select-Object \
        -First 20 \
        Name,
        SamAccountName,
        DistinguishedName,
        whenCreated
```

This is useful for both assessment and detection.

---

# Creator Tracking

Computer accounts created through the quota mechanism can contain information that helps identify the creator.

One particularly relevant attribute is:

```text
ms-DS-CreatorSID
```

This can be present when a non-administrative principal creates an object using the quota mechanism.

Conceptually:

```text
Alice
 |
 v
Creates Computer
 |
 v
PENTEST01$
 |
 v
ms-DS-CreatorSID
 |
 v
Alice SID
```

---

# Enumerate ms-DS-CreatorSID

PowerShell:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties ms-DS-CreatorSID |
    Where-Object {
        $_.'ms-DS-CreatorSID'
    } |
    Select-Object \
        Name,
        SamAccountName,
        ms-DS-CreatorSID
```

Depending on how PowerShell renders the binary SID, additional conversion may be useful.

---

# Convert Creator SID

Example:

```powershell
Get-ADComputer \
    -Filter * \
    -Properties ms-DS-CreatorSID |
    ForEach-Object {

        if ($_.'ms-DS-CreatorSID') {

            $sid = New-Object \
                System.Security.Principal.SecurityIdentifier(
                    $_.'ms-DS-CreatorSID',
                    0
                )

            [PSCustomObject]@{
                Computer   = $_.SamAccountName
                CreatorSID = $sid.Value
            }
        }
    }
```

---

# Resolve Creator SID

Once a SID is obtained:

```powershell
$sid = New-Object \
    System.Security.Principal.SecurityIdentifier(
        'S-1-5-21-111111111-222222222-333333333-1105'
    )

$sid.Translate(
    [System.Security.Principal.NTAccount]
)
```

This may identify the principal associated with the SID.

---

# Important CreatorSID Caveat

Do not treat:

```text
ms-DS-CreatorSID
```

as a universal audit trail for every computer object.

Its presence and behaviour depend on how the object was created and the privileges involved.

Use security event logs and directory auditing for authoritative historical investigation where available.

---

# Quota Accounting

The quota is not simply:

```text
Number of computers currently visible
```

in the directory.

Active Directory uses ownership/creator-related information as part of the quota mechanism.

During testing, do not assume deleting one test computer immediately restores every quota-related condition exactly as expected without verification.

---

# Computer Account Password

Computer accounts normally maintain passwords used for domain authentication.

On legitimately joined Windows systems, machine passwords are automatically managed.

For an intentionally created test computer object where the tester controls the initial password:

```text
Known Password
      |
      v
Computer Account Authentication
```

This is why controlled computer creation can provide a useful security principal.

---

# Computer Password vs User Password

The two should not be confused.

```text
User:
CORP\alice

Computer:
CORP\PENTEST01$
```

They are separate security principals with separate credentials.

---

# Computer Account Naming

A computer account commonly has:

```text
name:
PENTEST01

sAMAccountName:
PENTEST01$
```

The trailing `$` is important when specifying the account to many tools.

---

# Safe Naming

During authorised testing use an unmistakable test name such as:

```text
PENTEST01$
SECURITYTEST01$
AUDIT-MAQ-01$
```

subject to the organisation's naming rules.

Avoid names that resemble:

```text
Domain Controllers
Production Servers
Management Systems
Backup Servers
```

---

# Creating a Computer Account

Creating a computer object is a directory write operation.

Only perform this where explicitly authorised.

A common Linux tool used in Active Directory testing is Impacket's:

```text
addcomputer.py
```

Depending on installation, the command may be exposed as:

```text
impacket-addcomputer
```

Check the installed version:

```bash
impacket-addcomputer -h
```

---

# Impacket addcomputer

A typical authorised test pattern is:

```bash
impacket-addcomputer \
    'corp.example/alice:<PASSWORD>' \
    -computer-name 'PENTEST01$' \
    -computer-pass '<STRONG_TEST_PASSWORD>' \
    -dc-host dc01.corp.example
```

Exact options can vary with Impacket versions.

Always verify:

```bash
impacket-addcomputer -h
```

before execution.

---

# Do Not Use Predictable Production Passwords

For a controlled test account, use a strong temporary password generated specifically for the assessment.

Do not use:

```text
Password1!
Welcome123!
Company2026!
```

or reuse real credentials.

---

# Verify Computer Creation

From Windows:

```powershell
Get-ADComputer \
    -Identity 'PENTEST01' \
    -Properties \
        whenCreated,
        ms-DS-CreatorSID,
        ServicePrincipalName |
    Select-Object \
        Name,
        SamAccountName,
        DistinguishedName,
        whenCreated,
        ms-DS-CreatorSID,
        ServicePrincipalName
```

---

# Verify with ldapsearch

```bash
ldapsearch \
    -x \
    -H ldap://dc01.corp.example \
    -D 'CORP\alice' \
    -W \
    -b 'DC=corp,DC=example' \
    '(&(objectCategory=computer)(sAMAccountName=PENTEST01$))' \
    distinguishedName \
    sAMAccountName \
    objectSid \
    ms-DS-CreatorSID \
    servicePrincipalName \
    userAccountControl
```

---

# Verify Kerberos Authentication

If the controlled computer account was legitimately created for the assessment, Kerberos authentication can be tested.

For example, Impacket's `getTGT.py` may be available as:

```text
impacket-getTGT
```

Check:

```bash
impacket-getTGT -h
```

A password-based test can use:

```bash
impacket-getTGT \
    'corp.example/PENTEST01$:<STRONG_TEST_PASSWORD>'
```

A successful result demonstrates that the created object is a usable domain security principal.

No further privilege escalation is required merely to prove that fact.

---

# Kerberos Cache

A successful TGT request may produce a credential cache such as:

```text
PENTEST01$.ccache
```

It can be inspected with:

```bash
export KRB5CCNAME="$PWD/PENTEST01$.ccache"
klist
```

This should be treated as sensitive assessment evidence.

---

# MAQ and RBCD

One of the best-known security relationships involving Machine Account Quota is Resource-Based Constrained Delegation.

The important model is:

```text
Compromised User
      |
      v
MAQ Allows Computer Creation
      |
      v
Controlled Computer Account
      |
      +
Write Access to Target Computer
      |
      v
Configure RBCD
      |
      v
S4U
      |
      v
Access Target Service
```

Machine Account Quota supplies:

```text
Controlled Security Principal
```

but does not by itself supply:

```text
Write Access to Target Computer
```

Both conditions matter.

See:

[Resource-Based Constrained Delegation](rbcd.md)

---

# MAQ Alone Does Not Equal RBCD

This distinction should appear clearly in reports.

Incorrect:

```text
MAQ is 10, therefore any user can compromise servers using RBCD.
```

Correct:

```text
MAQ allows ordinary domain users to create controlled computer
principals.

This capability becomes security-relevant where those users also have
sufficient rights over another computer object or resource to establish
a further attack path such as RBCD.
```

---

# Example RBCD Prerequisites

Conceptually:

```text
Alice
 |
 +--> Can Create PENTEST01$
 |
 +--> GenericWrite over SERVER01$
 |
 v
Potential RBCD Path
```

Without the second relationship:

```text
Alice
 |
 +--> Can Create PENTEST01$
 |
 X
No Control over Target
```

the classic RBCD chain is incomplete.

---

# MAQ and GenericWrite

Suppose BloodHound identifies:

```text
Alice
 |
 v
GenericWrite
 |
 v
SERVER01$
```

and:

```text
MAQ = 10
```

Then investigate whether Alice can create a controlled computer principal that can participate in the RBCD chain.

The critical path becomes:

```text
Alice
 |
 +--> Create PENTEST01$
 |
 +--> GenericWrite SERVER01$
 |
 v
Potential Delegation Configuration
```

---

# MAQ and GenericAll

Similarly:

```text
Alice
 |
 v
GenericAll
 |
 v
SERVER01$
```

provides broad control over the target computer object.

If Alice can also create or otherwise control a suitable security principal, this may support additional attack paths.

---

# MAQ and WriteDACL

An indirect path can be:

```text
Alice
 |
 v
WriteDACL
 |
 v
SERVER01$
 |
 v
Grant Required Right
 |
 v
Modify Relevant Attribute
```

The complete ACL path should be documented.

See:

[Active Directory ACL and ACE Abuse](acl-ace.md)

---

# MAQ and Existing Computer Accounts

Creating a new computer account is not always necessary.

An attacker may already control:

```text
Existing Computer Account
```

through:

```text
Machine Credential Compromise
Computer Object ACL
Known Machine Password
Other Directory Weakness
```

Therefore:

```text
MAQ = 0
```

does not automatically prevent attack paths requiring a controlled computer principal.

---

# MAQ and Computer Account Reuse

A pre-existing computer object may be reusable during legitimate domain join operations if the requesting principal has the required permissions and the environment permits it.

This area has received additional security hardening in modern Windows environments.

Do not assume historical computer-account reuse behaviour remains applicable to a current domain.

Evaluate the actual permissions and current Microsoft domain-join hardening behaviour.

---

# Domain Join Hardening

Microsoft has introduced additional protections around domain join and computer-account reuse.

This is particularly relevant when analysing:

```text
Pre-Created Computer Accounts
Computer Object Ownership
Domain Join Reuse
```

Machine Account Quota should therefore not be evaluated using old assumptions alone.

---

# MAQ and sAMAccountName

Computer accounts normally use a `sAMAccountName` ending in:

```text
$
```

Historical Active Directory attack research has demonstrated that unusual computer-account naming and account-name manipulation could interact with other vulnerabilities or protocol behaviour.

Do not assume those historical chains remain exploitable on patched systems.

Assess:

```text
Current Patch Level
Current Domain Configuration
Actual Attribute Permissions
```

rather than reproducing obsolete exploit chains by default.

---

# MAQ and noPac

Historical attack chains such as:

```text
noPac
```

combined computer-account manipulation with vulnerabilities including:

```text
CVE-2021-42278
CVE-2021-42287
```

These vulnerabilities should be treated as separate patch-management issues.

A non-zero Machine Account Quota does not mean a domain is vulnerable to noPac.

The correct model is:

```text
MAQ
 +
Specific Vulnerability
 +
Required Conditions
 =
Historical Attack Chain
```

not:

```text
MAQ > 0
 =
noPac Vulnerable
```

---

# MAQ and Kerberos

Computer accounts are Kerberos principals.

Therefore Machine Account Quota connects directly to the Kerberos security model.

```text
Created Computer
      |
      v
Known Machine Key
      |
      v
Kerberos Authentication
      |
      v
TGT
```

See:

[Kerberos](kerberos.md)

and:

[Kerberos Tickets](kerberos-tickets.md)

---

# MAQ and Pass-the-Key

If computer-account Kerberos key material is known, it can potentially be used directly for Kerberos authentication.

This is conceptually related to:

[Pass-the-Key](pass-the-key.md)

The fact that the account is a computer rather than a user does not remove the importance of its long-term Kerberos keys.

---

# MAQ and Pass-the-Ticket

Tickets issued to a controlled computer account are credentials and should be protected accordingly.

See:

[Pass-the-Ticket](pass-the-ticket.md)

---

# MAQ and AD CS

Computer accounts may be eligible to enrol in certificate templates depending on:

```text
Template Permissions
Subject Requirements
Authentication Requirements
CA Configuration
```

Therefore a newly controlled computer account may expose certificate-enrolment paths if templates grant rights broadly to:

```text
Domain Computers
```

This does not automatically make MAQ an AD CS vulnerability.

The complete certificate-template configuration must be assessed.

---

# AD CS Example

Conceptually:

```text
MAQ
 |
 v
Controlled Computer
 |
 v
MemberOf Domain Computers
 |
 v
Certificate Template Enrollment
 |
 v
Certificate
```

The resulting security impact depends entirely on the template and certificate configuration.

Dedicated AD CS notes should analyse this separately.

---

# MAQ and Group Membership

New computer accounts commonly inherit membership associated with domain computers.

The assessment should therefore ask:

```text
What can Domain Computers access?
```

Possible resources include:

```text
Shares
Applications
Certificate Templates
Directory Objects
Deployment Services
Management Systems
```

---

# MAQ and Network Shares

Example:

```text
Domain Computers
       |
       v
Read
       |
       v
Software Deployment Share
```

A controlled computer account may therefore obtain access not available to a normal user account.

This is environment-specific and should be validated.

---

# MAQ and SCCM

Enterprise management platforms such as Microsoft Configuration Manager may assign permissions or expose content based on computer identity.

Machine Account Quota does not automatically compromise SCCM.

However, a controlled computer security principal may become relevant in environments where:

```text
Domain Computers
```

or computer-specific authentication is trusted.

SCCM should be assessed separately.

---

# MAQ and WSUS

The same principle applies to Windows Server Update Services and other infrastructure.

Do not assume that a newly created computer account is automatically enrolled, managed, or trusted.

Determine the actual authentication and authorization model.

---

# MAQ and LDAP Signing

LDAP signing does not disable Machine Account Quota.

These are different controls.

```text
LDAP Signing
     |
     v
Protect LDAP Integrity
```

versus:

```text
MAQ
 |
 v
Control Computer Creation Quota
```

Both can be important but address different threats.

---

# MAQ and SMB Signing

Similarly:

```text
SMB Signing
```

does not prevent legitimate Active Directory computer-account creation.

Do not recommend unrelated controls as remediation for MAQ.

---

# MAQ and NTLM

Machine Account Quota itself is a directory authorization setting.

It is not an NTLM weakness.

Computer accounts may authenticate through supported domain authentication mechanisms, but the root issue remains:

```text
Who is permitted to create and control computer principals?
```

---

# MAQ and Password Spraying

Machine Account Quota should not be confused with user-account credential attacks.

A user account obtained through:

```text
Password Spraying
```

may provide the initial authenticated principal that can exercise MAQ.

The attack chain could therefore be:

```text
Password Spray
      |
      v
Compromised User
      |
      v
MAQ
      |
      v
Controlled Computer
```

See:

[Password Spraying](password-spraying.md)

---

# MAQ and BloodHound Attack Paths

BloodHound should be used to answer:

```text
Does the compromised principal control a target
that becomes exploitable when combined with
a controlled computer account?
```

Potentially interesting relationships include:

```text
GenericAll
GenericWrite
WriteDacl
WriteOwner
Owns
AddMember
RBCD-related relationships
```

depending on BloodHound version and collection.

---

# BloodHound Analysis Model

```text
Controlled User
      |
      v
Outbound Object Control
      |
      v
Target Computer
      |
      +
Controlled Computer Principal
      |
      v
Potential Delegation / ACL Path
```

---

# Do Not Stop at MAQ

Finding:

```text
ms-DS-MachineAccountQuota: 10
```

should trigger:

```text
Enumerate Target ACLs
        |
        v
Enumerate Domain Computers Permissions
        |
        v
Review Delegation Paths
        |
        v
Review AD CS
        |
        v
Review Infrastructure Trust
```

rather than immediately assigning high severity.

---

# Safe Validation Strategy

A safe validation hierarchy is:

```text
Level 1
Read MAQ

Level 2
Analyse Computer Creation ACLs

Level 3
Map Potential Attack Paths

Level 4
Create Dedicated Test Computer

Level 5
Authenticate as Test Computer

Level 6
Use Test Computer in Further Attack Path
```

Only progress as far as required.

---

# Level 1 - Read MAQ

Read:

```text
ms-DS-MachineAccountQuota
```

This is non-invasive.

---

# Level 2 - Analyse ACLs

Determine:

```text
Can the user create computer objects through ACLs?
Can the user modify target computers?
Can the user modify delegation attributes?
```

This may be sufficient to prove the risk.

---

# Level 3 - Map the Attack Path

Example:

```text
CORP\alice
     |
     +--> MAQ = 10
     |
     +--> GenericWrite
            |
            v
        SERVER01$
```

If the prerequisites are independently confirmed, active exploitation may not be necessary.

---

# Level 4 - Create a Test Computer

Where authorised:

```text
CORP\alice
     |
     v
Create
     |
     v
PENTEST01$
```

Record:

```text
DN
SID
Creator SID
Creation Time
Password
```

The password itself should be stored securely and should not be unnecessarily included in the final report.

---

# Level 5 - Authenticate as the Test Computer

A Kerberos TGT request can demonstrate:

```text
Created Object
     +
Known Credential
     =
Controlled Security Principal
```

No production target needs to be modified.

---

# Level 6 - Further Attack Path

Only where explicitly authorised:

```text
Controlled Computer
       |
       v
Delegation / ACL Chain
       |
       v
Target
```

Prefer a dedicated test target rather than a production server.

---

# Creating Computer Objects Is Not Always Necessary

If:

```text
MAQ = 10
```

and the engagement only requires configuration review, simply recording the value may be sufficient.

If:

```text
Alice has GenericWrite over SERVER01$
```

and all prerequisites for a known attack path are confirmed, directory modification may also be unnecessary.

Choose the least intrusive evidence.

---

# Detection

Defenders should monitor:

```text
Computer Account Creation
Computer Account Modification
Computer Account Deletion
Unusual Computer Names
Unexpected Computer Creators
Delegation Attribute Changes
Computer Account Authentication
Computer Accounts Created Outside Provisioning Workflows
```

---

# Event 4741

Security event:

```text
4741
```

records:

```text
A computer account was created
```

when the appropriate auditing is enabled.

This is one of the most important events for MAQ monitoring.

---

# Event 4742

Event:

```text
4742
```

records:

```text
A computer account was changed
```

This can be useful when investigating unusual changes to computer objects.

---

# Event 4743

Event:

```text
4743
```

records:

```text
A computer account was deleted
```

A suspicious sequence may therefore look like:

```text
4741
 |
 v
Computer Created
 |
 v
Attack Activity
 |
 v
4743
 |
 v
Computer Deleted
```

Short-lived computer accounts deserve attention.

---

# Event 5136

Where Directory Service Changes auditing is enabled:

```text
5136
```

may record modifications to directory object attributes.

This can be especially important for changes involving:

```text
msDS-AllowedToActOnBehalfOfOtherIdentity
servicePrincipalName
userAccountControl
dNSHostName
```

depending on the configured SACL and auditing.

---

# Event 5137

Event:

```text
5137
```

can record creation of a directory service object where appropriate auditing is configured.

This can complement:

```text
4741
```

during investigation.

---

# Event 5141

Event:

```text
5141
```

can record deletion of a directory service object where appropriate auditing is configured.

---

# Kerberos Events

A newly created computer account may subsequently authenticate using Kerberos.

Relevant events include:

```text
4768
4769
```

A useful detection sequence is:

```text
4741
 |
 v
New Computer
 |
 v
4768
 |
 v
TGT Requested
 |
 v
4769
 |
 v
Service Ticket Requested
```

The sequence itself may be legitimate, so correlate it with provisioning processes.

---

# Detect Non-Standard Creators

In many mature environments, computer creation should originate from:

```text
Provisioning Service
IT Administration
Deployment Platform
Approved Join Process
```

Alert when a computer is created by:

```text
Ordinary Employee Account
Unexpected Service Account
Recently Compromised Account
```

subject to the organisation's legitimate workflow.

---

# Detect Suspicious Names

Look for names that:

```text
Do Not Match Naming Standards
Mimic Domain Controllers
Mimic Servers
Contain Random Strings
Are Created and Deleted Quickly
```

However, naming anomalies alone are weak indicators.

---

# Detect CreatorSID

Where:

```text
ms-DS-CreatorSID
```

is present, it can help identify objects created through non-administrative quota-based mechanisms.

A useful review is:

```text
Computer
 |
 +--> CreatorSID
 |
 +--> Creation Time
 |
 +--> OU
 |
 +--> SPNs
 |
 +--> Authentication Activity
```

---

# Detect RBCD Follow-On Activity

A particularly important chain is:

```text
Computer Created
      |
      v
Target Computer Modified
      |
      v
msDS-AllowedToActOnBehalfOfOtherIdentity
      |
      v
Kerberos Service Tickets
```

This is more suspicious than computer creation alone.

---

# Detection Model

```text
4741 / 5137
      |
      v
New Computer Object
      |
      v
Identify Creator
      |
      v
Validate Provisioning Process
      |
      v
Monitor Object Changes
      |
      v
Monitor Kerberos Activity
      |
      v
Monitor Target ACL / Delegation Changes
```

---

# Purple Team Exercise

A controlled MAQ exercise can be designed as:

```text
Dedicated Test User
      |
      v
Read MAQ
      |
      v
Create PENTEST01$
      |
      v
Request Kerberos TGT
      |
      v
Defender Detects Creation
      |
      v
Defender Identifies Creator
      |
      v
Delete Test Computer
```

This validates detection without modifying a production target.

---

# Extended Purple Team Exercise

Where RBCD testing is explicitly in scope:

```text
Test User
   |
   v
Create Test Computer
   |
   v
Controlled Test Target
   |
   v
Configure RBCD
   |
   v
S4U Validation
   |
   v
Detection
   |
   v
Cleanup
```

Use:

```text
Test Computer
Test Target
Test User
```

rather than production administrative accounts.

---

# Purple Team Questions

Defenders should answer:

```text
Who created the computer?

Was the creator authorised?

What was the computer name?

Where was it created?

Was ms-DS-CreatorSID present?

Did the computer authenticate?

Which services did it access?

Was another computer object modified?

Was RBCD configured?

Was an SPN changed?

Was the object deleted shortly afterwards?
```

---

# Purple Team Metrics

Useful metrics include:

```text
Time to detect computer creation
Time to identify creator
Time to classify creation as unauthorised
Time to detect Kerberos authentication
Time to detect delegation modification
Time to correlate the attack chain
Time to contain the user
Time to remove the rogue computer
```

---

# Hardening

The primary defensive question is:

```text
Do ordinary users actually need to create
computer accounts?
```

If the answer is no, consider reducing:

```text
ms-DS-MachineAccountQuota
```

to:

```text
0
```

after validating operational dependencies.

---

# Set MAQ to Zero

An administrator can modify the domain attribute using appropriate Active Directory administration mechanisms.

Example PowerShell:

```powershell
Set-ADDomain \
    -Identity 'corp.example' \
    -Replace @{
        'ms-DS-MachineAccountQuota' = 0
    }
```

This is an administrative change.

Test it carefully before deployment because existing domain-join workflows may depend on the current behaviour.

---

# Verify MAQ

After a legitimate change:

```powershell
$domain = Get-ADDomain

Get-ADObject \
    -Identity $domain.DistinguishedName \
    -Properties ms-DS-MachineAccountQuota |
    Select-Object \
        ms-DS-MachineAccountQuota
```

Expected:

```text
ms-DS-MachineAccountQuota
-------------------------
0
```

---

# Prefer Explicit Delegation

Instead of allowing every domain user to create computer accounts:

```text
Domain Users
     |
     v
MAQ
     |
     v
Create Computers
```

prefer a controlled model where appropriate:

```text
Workstation Provisioning Team
          |
          v
Delegated Create Rights
          |
          v
Workstations OU
```

This reduces the number of principals capable of creating computer objects.

---

# Restrict Join Workflows

Define:

```text
Who may join computers?
Which OUs may they use?
Which provisioning platform performs joins?
Which naming standards apply?
Who approves exceptions?
```

---

# Review OU ACLs

Setting:

```text
MAQ = 0
```

is incomplete if broad principals still have:

```text
CreateChild
```

over computer-containing OUs.

Review:

```text
Domain Root
Workstations OU
Servers OU
Staging OUs
Legacy OUs
```

---

# Review Computer Object ACLs

Attack paths such as RBCD frequently depend on weak ACLs over existing computer objects.

Review:

```text
GenericAll
GenericWrite
WriteDACL
WriteOwner
Validated Writes
Specific Attribute Writes
```

on sensitive computers.

---

# Protect Tier 0 Computer Objects

Computer objects representing:

```text
Domain Controllers
Certificate Authorities
Identity Servers
Management Servers
Privileged Access Systems
```

should be treated as highly sensitive directory objects.

Unexpected write permissions over these objects should receive immediate attention.

---

# Monitor Computer Creation

Create alerts for:

```text
4741
```

where computer creation is uncommon or tightly controlled.

In larger environments, baseline legitimate provisioning systems and alert on deviations.

---

# Review Existing CreatorSID Objects

Periodically identify computer accounts containing:

```text
ms-DS-CreatorSID
```

and verify that their creators and purpose remain legitimate.

---

# Review Stale Computer Accounts

Machine Account Quota is only one part of computer-account security.

Also review:

```text
Stale Computers
Disabled Computers
Old Operating Systems
Unused SPNs
Unexpected Delegation
Weak ACLs
```

---

# Protect Computer Credentials

Computer-account credentials should be treated as secrets.

Compromise can enable:

```text
Machine Authentication
Kerberos Ticket Requests
Access as Computer Principal
Additional Attack Paths
```

---

# Domain Computers Least Privilege

Review resources that grant permissions to:

```text
Domain Computers
```

Ask:

```text
Does every domain computer require this access?
```

If not, use more narrowly scoped groups.

---

# AD CS Hardening

Review certificate templates available to:

```text
Domain Computers
```

and ensure they do not provide unintended privilege escalation.

This belongs within the broader AD CS assessment.

---

# RBCD Hardening

Machine Account Quota reduction should be combined with:

```text
Computer Object ACL Review
RBCD Attribute Monitoring
Tiering
Least Privilege
```

Reducing MAQ alone does not eliminate RBCD attack paths.

---

# Incident Response

If an unauthorised computer account is discovered:

```text
Rogue Computer Detected
        |
        v
Record Object
        |
        v
Identify Creator
        |
        v
Review Object ACL
        |
        v
Review SPNs
        |
        v
Review Delegation
        |
        v
Review Kerberos Activity
        |
        v
Review Target Computer Changes
        |
        v
Contain Creator
        |
        v
Remove Rogue Object
        |
        v
Hunt for Persistence
```

---

# Capture Before Deletion

Before deleting a suspicious computer object, capture:

```text
Distinguished Name
SID
GUID
sAMAccountName
dNSHostName
userAccountControl
servicePrincipalName
ms-DS-CreatorSID
msDS-AllowedToActOnBehalfOfOtherIdentity
whenCreated
whenChanged
Object ACL
Group Membership
```

where relevant.

---

# Review Creator

If:

```text
ms-DS-CreatorSID
```

identifies a user, investigate that identity.

Review:

```text
Authentication History
Password Reset History
Group Membership
Privilege Changes
Other Computer Objects Created
Target ACL Access
```

---

# Review Other Created Computers

If Alice created one suspicious computer:

```text
PENTEST01$
```

search for other computer objects associated with the same creator SID.

Conceptually:

```text
Alice SID
 |
 +--> COMPUTER-A$
 +--> COMPUTER-B$
 +--> COMPUTER-C$
```

This can reveal a broader compromise.

---

# Review Delegation

For the rogue computer and potential targets, review:

```text
msDS-AllowedToDelegateTo
msDS-AllowedToActOnBehalfOfOtherIdentity
TrustedForDelegation
TrustedToAuthForDelegation
```

depending on the object type and scenario.

---

# Review Kerberos Activity

Search for:

```text
4768
4769
```

associated with the rogue computer account.

Determine:

```text
When did it authenticate?
Which services were requested?
Which systems were contacted?
```

---

# Review Computer Deletion

Attackers may delete temporary computer accounts to reduce visible artefacts.

Therefore:

```text
No Rogue Computer Exists Now
```

does not prove:

```text
No Rogue Computer Was Created
```

Historical event logs remain important.

---

# Reporting

Possible finding titles include:

```text
Default Machine Account Quota Allows Domain Users to Create Computer Accounts
```

```text
Machine Account Quota Contributes to Resource-Based Constrained Delegation Attack Path
```

```text
Unrestricted Computer Account Creation Increases Active Directory Attack Surface
```

```text
Domain Users Can Create Controlled Computer Security Principals
```

```text
Machine Account Quota and Weak Computer ACL Enable Privilege Escalation
```

---

# Do Not Overstate the Finding

Avoid:

```text
Machine Account Quota is 10 and therefore the domain can be compromised.
```

Prefer:

```text
The domain retains the default Machine Account Quota value of 10,
allowing ordinary authenticated domain users to create computer
accounts through the applicable default mechanism.

A created computer account is a domain security principal controlled
by the creator and can participate in Kerberos authentication and
other directory relationships.

This configuration increases attack surface and can contribute to
privilege-escalation chains when combined with weaknesses such as
write access over computer objects or unsafe delegation configuration.
```

---

# Example Informational Finding

```text
Finding:
Domain Users Can Create Computer Accounts Through Machine Account Quota

Affected Object:
DC=corp,DC=example

Attribute:
ms-DS-MachineAccountQuota

Value:
10

Description:
The Active Directory domain is configured with a Machine Account Quota
of 10.

This allows ordinary authenticated domain users, subject to the
applicable Active Directory computer-creation rules, to create computer
accounts without requiring domain administrative privileges.

A newly created computer account is a domain security principal whose
credentials can be controlled by its creator.

The configuration does not independently provide administrative access.
However, controlled computer principals can contribute to other Active
Directory attack paths when combined with additional permissions or
misconfigurations.

Impact:
The configuration increases the number of security principals that can
be introduced by a compromised domain user and may increase the impact
of weaknesses involving computer-object ACLs, Kerberos delegation,
certificate services, or resources that trust Domain Computers.

Recommendation:
Determine whether ordinary users require the ability to create computer
accounts.

If this functionality is not required, consider setting
ms-DS-MachineAccountQuota to 0 after validating domain-join workflows.

Delegate computer creation explicitly to approved provisioning
identities or groups and appropriate OUs where required.

Review existing computer-object ACLs and monitor computer-account
creation events.
```

---

# Example Chained Finding

```text
Finding:
Machine Account Quota and Weak Computer ACL Enable RBCD Attack Path

Source Principal:
CORP\alice

Machine Account Quota:
10

Target:
CORP\SERVER01$

Target Permission:
GenericWrite

Description:
The CORP\alice account can create a controlled computer account because
the domain's Machine Account Quota is configured to 10.

The same account has GenericWrite permission over the SERVER01$
computer object.

These conditions can potentially be combined to establish a
Resource-Based Constrained Delegation relationship using a controlled
computer principal.

The Machine Account Quota value, target ACL, and resulting attack path
were confirmed during the assessment.

Production delegation settings were not modified.

Impact:
Successful exploitation could allow the controlled principal to obtain
Kerberos service tickets representing authorised users to services on
the affected target, subject to the remaining Kerberos and authorization
conditions.

This could result in privilege escalation and administrative access to
SERVER01.

Recommendation:
Remove the unnecessary GenericWrite permission over SERVER01$.

Determine whether ordinary domain users require computer-account
creation and reduce ms-DS-MachineAccountQuota to 0 where operationally
appropriate.

Review computer-object ACLs throughout the environment and monitor
changes to resource-based constrained delegation attributes.
```

---

# Severity

Machine Account Quota alone is often best treated as:

```text
Configuration / Attack Surface
```

rather than automatically:

```text
High
Critical
```

Severity should be based on the complete path.

Example:

```text
MAQ = 10
 +
No Useful Target Rights
 =
Limited Direct Impact
```

versus:

```text
MAQ = 10
 +
GenericWrite over Tier 1 Server
 +
RBCD Preconditions
 =
Significant Privilege Escalation Path
```

---

# Evidence Checklist

Record:

```text
Domain
Domain DN
MAQ Value
Source User
Source SID
Computer Creation Mechanism
Test Computer Name
Test Computer DN
Test Computer SID
Creator SID
Creation Time
Computer ACL
Computer Group Membership
SPNs
Kerberos Validation
Target Computer
Target ACL
Potential Delegation Path
Validation Performed
Cleanup Performed
Relevant Events
Timestamp
```

---

# Machine Account Quota Assessment Checklist

## Preparation

- [ ] Confirm MAQ enumeration is authorised
- [ ] Confirm computer creation is authorised
- [ ] Confirm computer deletion is authorised
- [ ] Confirm RBCD testing restrictions
- [ ] Select dedicated test computer name
- [ ] Generate strong temporary machine password
- [ ] Record cleanup requirements

## Enumeration

- [ ] Identify domain DN
- [ ] Read `ms-DS-MachineAccountQuota`
- [ ] Enumerate computer accounts
- [ ] Enumerate recently created computers
- [ ] Enumerate `ms-DS-CreatorSID`
- [ ] Enumerate computer OUs
- [ ] Enumerate computer-creation ACLs
- [ ] Enumerate delegated provisioning groups
- [ ] Identify computer accounts with unusual owners
- [ ] Identify stale computer accounts

## Computer Security

- [ ] Review `Domain Computers`
- [ ] Review permissions granted to `Domain Computers`
- [ ] Review computer SPNs
- [ ] Review computer-object ACLs
- [ ] Review Tier 0 computer ACLs
- [ ] Review computer delegation configuration
- [ ] Review certificate-template access

## ACL Analysis

- [ ] Review `CreateChild`
- [ ] Review `GenericAll`
- [ ] Review `GenericWrite`
- [ ] Review `WriteDACL`
- [ ] Review `WriteOwner`
- [ ] Review validated writes
- [ ] Review specific attribute write permissions
- [ ] Review inherited permissions

## RBCD Analysis

- [ ] Identify controlled computer principals
- [ ] Identify writable target computers
- [ ] Review `msDS-AllowedToActOnBehalfOfOtherIdentity`
- [ ] Review BloodHound RBCD paths
- [ ] Confirm target service requirements
- [ ] Confirm Kerberos prerequisites
- [ ] Avoid active production delegation changes unless approved

## Active Validation

- [ ] Use dedicated test user
- [ ] Create dedicated test computer only if authorised
- [ ] Record computer DN
- [ ] Record computer SID
- [ ] Record creator SID
- [ ] Verify computer account exists
- [ ] Verify Kerberos authentication if required
- [ ] Avoid unnecessary target modification
- [ ] Remove test computer after validation

## Detection

- [ ] Monitor 4741
- [ ] Monitor 4742
- [ ] Monitor 4743
- [ ] Monitor 5136
- [ ] Monitor 5137
- [ ] Monitor 5141
- [ ] Monitor 4768
- [ ] Monitor 4769
- [ ] Identify unusual creators
- [ ] Identify unusual computer names
- [ ] Identify short-lived computer accounts
- [ ] Monitor RBCD attribute changes
- [ ] Correlate new computers with Kerberos activity

## Hardening

- [ ] Determine whether MAQ is required
- [ ] Consider setting MAQ to 0
- [ ] Validate domain-join workflows first
- [ ] Delegate computer creation explicitly
- [ ] Restrict creation to approved OUs
- [ ] Review OU ACLs
- [ ] Review computer-object ACLs
- [ ] Protect Tier 0 computer objects
- [ ] Review `Domain Computers` permissions
- [ ] Review AD CS templates
- [ ] Monitor computer creation
- [ ] Review existing CreatorSID objects

## Cleanup

- [ ] Remove test RBCD configuration
- [ ] Remove test SPNs if created
- [ ] Delete test computer account
- [ ] Confirm object deletion
- [ ] Remove local Kerberos caches
- [ ] Remove temporary credentials
- [ ] Verify target ACL unchanged
- [ ] Verify target delegation unchanged
- [ ] Secure evidence

---

# Machine Account Quota Testing Model

The basic model is:

```text
Domain User
    |
    v
Machine Account Quota
    |
    v
Computer Creation
    |
    v
Controlled Computer Principal
```

The authentication model is:

```text
Controlled Computer
       |
       v
Known Machine Credential
       |
       v
Kerberos AS-REQ
       |
       v
KDC
       |
       v
Computer TGT
```

The group-membership model is:

```text
Controlled Computer
       |
       v
Domain Computers
       |
       v
Resources Trusting Domain Computers
```

The ACL model is:

```text
Controlled User
      |
      v
Create Computer
      |
      +
Control Target Object
      |
      v
Potential Attack Path
```

The RBCD model is:

```text
Compromised User
      |
      v
MAQ
      |
      v
Create ATTACKER01$
      |
      +
Write Access to SERVER01$
      |
      v
RBCD
      |
      v
S4U
      |
      v
Service Ticket
      |
      v
SERVER01
```

The MAQ-zero model is:

```text
MAQ = 0
   |
   X
Default Quota Creation
```

but:

```text
Delegated CreateChild
        |
        v
Computer Creation
```

may still remain.

Therefore:

```text
MAQ = 0
```

does not mean:

```text
No Computer Creation Attack Surface
```

The defensive model is:

```text
Determine Business Need
        |
        v
Reduce MAQ
        |
        v
Delegate Creation Explicitly
        |
        v
Protect Computer ACLs
        |
        v
Monitor Creation
        |
        v
Monitor Delegation Changes
```

The detection model is:

```text
Computer Created
      |
      v
Identify Creator
      |
      v
Check Provisioning Process
      |
      v
Monitor Authentication
      |
      v
Monitor Object Changes
      |
      v
Detect Follow-On Attack
```

A mature assessment should answer:

```text
What is MAQ?
     |
     v
Who can create computers?
     |
     v
Where can they create them?
     |
     v
Which computer principals do they control?
     |
     v
What permissions do those computers inherit?
     |
     v
Which target computers can the user modify?
     |
     v
Can the conditions be chained?
     |
     v
What is the resulting privilege?
```

The most important principle is:

```text
MAQ > 0
   |
   X
Automatic Domain Compromise
```

Instead:

```text
Machine Account Quota
        +
Controlled Computer Principal
        +
Additional Weak Permission
        +
Reachable Target
        =
Potential Security Impact
```

---

# Related Notes

Active Directory methodology:

[Active Directory Penetration Testing Methodology](methodology.md)

Active Directory enumeration:

[Active Directory Enumeration](enumeration.md)

Groups:

[Active Directory Groups](groups.md)

Group Policy:

[Active Directory Group Policy](group-policy.md)

ACL and ACE:

[Active Directory ACL and ACE Abuse](acl-ace.md)

Kerberos:

[Kerberos](kerberos.md)

Kerberos Tickets:

[Kerberos Tickets](kerberos-tickets.md)

Resource-Based Constrained Delegation:

[Resource-Based Constrained Delegation](rbcd.md)

S4U:

[S4U](s4u.md)

Pass-the-Key:

[Pass-the-Key](pass-the-key.md)

Pass-the-Ticket:

[Pass-the-Ticket](pass-the-ticket.md)

BloodHound:

[BloodHound](bloodhound.md)

NetExec:

[NetExec](netexec.md)

Impacket:

[Impacket](impacket.md)

The following topics complement Machine Account Quota and can be linked once their dedicated notes are available:

```text
active-directory/credential-access.md
active-directory/gpp-passwords.md
active-directory/laps.md
active-directory/gmsa.md
active-directory/shadow-credentials.md
active-directory/ad-cs/index.md
active-directory/sccm.md
active-directory/privilege-escalation.md
```

---

# References

## Microsoft - Machine Account Quota

[Microsoft - ms-DS-MachineAccountQuota Attribute](https://learn.microsoft.com/en-us/windows/win32/adschema/a-ms-ds-machineaccountquota){ target="_blank" rel="noopener noreferrer" }

[Microsoft - MS-DS-Machine-Account-Quota](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-ada2/6ba13b0c-1620-478c-b2ae-eca041f2e1c4){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Computer Accounts

[Microsoft - Default Local Accounts and Active Directory](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts){ target="_blank" rel="noopener noreferrer" }

[Microsoft - New-ADComputer](https://learn.microsoft.com/en-us/powershell/module/activedirectory/new-adcomputer){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Get-ADComputer](https://learn.microsoft.com/en-us/powershell/module/activedirectory/get-adcomputer){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Domain Join

[Microsoft - Active Directory Domain Join Permissions](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers){ target="_blank" rel="noopener noreferrer" }

[Microsoft - NetJoin Legacy Account Reuse](https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/active-directory-domain-join-troubleshooting-guidance){ target="_blank" rel="noopener noreferrer" }

---

## Microsoft - Auditing

[Microsoft - Event 4741](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4741){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4742](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4742){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 4743](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4743){ target="_blank" rel="noopener noreferrer" }

[Microsoft - Event 5136](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-5136){ target="_blank" rel="noopener noreferrer" }

---

## Impacket

[Fortra Impacket](https://github.com/fortra/impacket){ target="_blank" rel="noopener noreferrer" }

[Impacket addcomputer.py](https://github.com/fortra/impacket/blob/master/examples/addcomputer.py){ target="_blank" rel="noopener noreferrer" }

[Impacket getTGT.py](https://github.com/fortra/impacket/blob/master/examples/getTGT.py){ target="_blank" rel="noopener noreferrer" }

---

## BloodHound

[BloodHound Documentation](https://bloodhound.specterops.io/){ target="_blank" rel="noopener noreferrer" }

---

## NetExec

[NetExec Documentation](https://www.netexec.wiki/){ target="_blank" rel="noopener noreferrer" }

---

## MITRE ATT&CK

[MITRE ATT&CK - Create Account](https://attack.mitre.org/techniques/T1136/){ target="_blank" rel="noopener noreferrer" }

[MITRE ATT&CK - Domain Account](https://attack.mitre.org/techniques/T1136/002/){ target="_blank" rel="noopener noreferrer" }

---

# Final Notes

Machine Account Quota should be understood as a security-principal creation capability.

The core relationship is:

```text
Domain User
    |
    v
Machine Account Quota
    |
    v
Create Computer
    |
    v
Controlled Security Principal
```

The important security question is not simply:

```text
Is MAQ 10?
```

It is:

```text
What can a controlled computer principal
be used to access or influence?
```

A complete assessment therefore expands:

```text
MAQ
 |
 v
Computer Creation
```

into:

```text
MAQ
 |
 v
Controlled Computer
 |
 +--> Kerberos
 |
 +--> Domain Computers Membership
 |
 +--> Directory ACLs
 |
 +--> Delegation
 |
 +--> AD CS
 |
 +--> Enterprise Infrastructure
```

The most important attack path is commonly:

```text
Compromised User
       |
       v
Create Computer
       |
       v
Controlled Computer Principal
       |
       +
Weak Target Computer ACL
       |
       v
RBCD
       |
       v
S4U
       |
       v
Target Access
```

But the correct interpretation remains:

```text
Machine Account Quota
        |
        X
Vulnerability by Itself
```

Instead:

```text
Machine Account Quota
        |
        v
Attack-Surface Primitive
        |
        +
Additional Misconfiguration
        |
        v
Exploitable Attack Path
```

For penetration testing:

```text
Enumerate MAQ
      |
      v
Enumerate Computer Creation Rights
      |
      v
Enumerate Computer ACLs
      |
      v
Map Delegation Paths
      |
      v
Map Domain Computers Access
      |
      v
Validate Minimum Necessary Condition
```

For defenders:

```text
Is MAQ Required?
      |
      +--> No
      |     |
      |     v
      |   Set to 0
      |
      +--> Yes
            |
            v
      Restrict and Monitor
```

The stronger enterprise model is:

```text
Ordinary Users
      |
      X
Broad Computer Creation

Approved Provisioning Identities
      |
      v
Explicit Delegation
      |
      v
Approved OU
      |
      v
Controlled Computer Lifecycle
```

A mature Active Directory assessment therefore treats Machine Account Quota as one component of the wider identity and authorization graph:

```text
User
 |
 v
Computer Creation
 |
 v
Computer Principal
 |
 v
Directory Relationships
 |
 v
Effective Privilege
```

The final question is always:

```text
Does the ability to create this principal
lead to control of something more privileged?
```

That distinction prevents a default Active Directory configuration from being overstated while still identifying the attack paths in which Machine Account Quota materially increases risk.
