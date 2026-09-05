---
title: Red Teaming
description: Red teaming methodology, infrastructure, initial access, command and control, credential access, lateral movement, persistence, and defence evasion for authorised security assessments.
---

# Red Teaming

Red teaming is a goal-driven security assessment discipline that evaluates how well an organisation can prevent, detect, investigate, and respond to realistic adversary activity.

Unlike a vulnerability assessment that primarily identifies individual weaknesses, a red team assessment evaluates how multiple weaknesses, trust relationships, identities, systems, and security controls interact across an attack path.

```text
Reconnaissance
      |
      v
Attack Surface
      |
      v
Initial Access
      |
      v
Execution
      |
      v
Command and Control
      |
      v
Credential Access
      |
      v
Privilege Escalation
      |
      v
Lateral Movement
      |
      v
Objective
      |
      v
Detection and Response Evaluation
```

Red teaming should always be performed under explicit authorisation, an agreed scope, defined rules of engagement, and appropriate operational controls.


---

## Red Teaming Notes

<div class="grid cards" markdown>

-   :material-server-network:{ .lg .middle } **Infrastructure**

    ---

    Design and operate redirectors, domains, servers, payload delivery infrastructure, logging, segmentation, and supporting services.

    [:octicons-arrow-right-24: Infrastructure](infrastructure.md)

-   :material-door-open:{ .lg .middle } **Initial Access**

    ---

    Understand externally reachable attack surfaces and the paths through which an authorised assessment may establish an initial foothold.

    [:octicons-arrow-right-24: Initial Access](initial-access.md)

-   :material-access-point-network:{ .lg .middle } **Command and Control**

    ---

    Understand C2 architecture, communication channels, redirectors, operational security, traffic considerations, and defensive visibility.

    [:octicons-arrow-right-24: Command and Control](command-and-control.md)

-   :material-key-chain:{ .lg .middle } **Credential Access**

    ---

    Assess how credentials, authentication material, tokens, secrets, and privileged identities can affect an attack path.

    [:octicons-arrow-right-24: Credential Access](credential-access.md)

-   :material-transit-connection-variant:{ .lg .middle } **Lateral Movement**

    ---

    Evaluate how access can propagate between systems through credentials, remote administration protocols, trust relationships, and management infrastructure.

    [:octicons-arrow-right-24: Lateral Movement](lateral-movement.md)

-   :material-link-variant:{ .lg .middle } **Persistence**

    ---

    Understand persistence mechanisms and evaluate whether security controls can identify unauthorised mechanisms designed to retain access.

    [:octicons-arrow-right-24: Persistence](persistence.md)

-   :material-shield-off-outline:{ .lg .middle } **Defence Evasion**

    ---

    Study the security controls, telemetry gaps, execution restrictions, and defensive assumptions that affect detection and prevention.

    [:octicons-arrow-right-24: Defence Evasion](defence-evasion.md)

</div>


---

## Red Teaming vs Penetration Testing

Penetration testing and red teaming overlap technically, but their objectives are different.

| Area | Penetration Testing | Red Teaming |
|---|---|---|
| Primary goal | Identify and validate vulnerabilities | Evaluate security against realistic attack paths |
| Scope | Often broad technical coverage | Usually objective-driven |
| Visibility | Usually known to security stakeholders | Often limited to selected stakeholders |
| Testing style | Vulnerability-oriented | Adversary-oriented |
| Detection testing | Useful but not always central | Usually a major objective |
| Attack chaining | Common | Fundamental |
| Operational security | Moderate | High |
| Social engineering | Scope dependent | Scope dependent |
| Physical security | Less common | Scope dependent |
| Success measurement | Vulnerabilities and impact | Objectives, detection, response, and resilience |

A red team assessment should not simply attempt to generate the largest possible number of findings.

The objective is to understand whether realistic attack paths can reach agreed objectives and how effectively the organisation responds.


---

## Red Teaming vs Purple Teaming

Red teaming focuses on adversary simulation and objective achievement.

Purple teaming introduces deliberate collaboration between offensive and defensive teams to improve detection, prevention, response, and knowledge transfer.

```text
Red Teaming

Red
 |
 v
Adversary Activity
 |
 v
Blue Team Detection and Response


Purple Teaming

Red <------> Blue
 |             |
 +---- Share --+
       |
       v
Detection Improvement
       |
       v
Validation
       |
       v
Repeat
```

The two approaches are complementary.

A red team assessment can identify defensive gaps, while a later purple team exercise can reproduce selected behaviours collaboratively and improve the corresponding controls.


---

# Engagement Lifecycle

A structured red team engagement should have clearly defined phases.

```text
Planning
   |
   v
Scoping
   |
   v
Rules of Engagement
   |
   v
Threat Modelling
   |
   v
Infrastructure Preparation
   |
   v
Reconnaissance
   |
   v
Initial Access
   |
   v
Post-Compromise Operations
   |
   v
Objective
   |
   v
Cleanup
   |
   v
Reporting
   |
   v
Detection Review
```


---

## 1. Planning

Planning establishes why the assessment is being performed.

Questions include:

```text
What security capability is being evaluated?
What business risk is being tested?
What systems are relevant?
What attacker profile is appropriate?
What constitutes success?
What activities are prohibited?
Who must know about the assessment?
```

The engagement should have measurable objectives rather than an unrestricted instruction to "hack the organisation."


---

## 2. Scope

The scope defines where testing is permitted.

Examples include:

```text
Domains
IP ranges
Cloud tenants
Applications
Endpoints
Active Directory
Identity providers
Email infrastructure
VPN infrastructure
Wireless networks
Physical locations
Third-party systems
```

Scope should also identify exclusions.

```text
Production-critical systems
Safety systems
Medical systems
Payment systems
Specific accounts
Specific subsidiaries
Third-party infrastructure
Destructive actions
```

Never infer authorisation from technical reachability.


---

## 3. Rules of Engagement

The Rules of Engagement define how the assessment may operate.

Typical subjects include:

```text
Authorised dates and times
Permitted targets
Prohibited targets
Testing source addresses
Social engineering permissions
Credential handling
Persistence restrictions
Payload restrictions
Data access restrictions
Data exfiltration restrictions
Cloud restrictions
Availability restrictions
Escalation contacts
Emergency stop procedure
Cleanup requirements
Evidence handling
Reporting requirements
```

The Rules of Engagement should be available to the assessment team throughout the engagement.


---

## 4. Objectives

Red team objectives should represent meaningful security outcomes.

Examples:

```text
Obtain access to a defined application
Reach a designated server
Demonstrate access to a protected dataset
Obtain a specified privilege level
Access a representative administrative interface
Reach a simulated crown-jewel system
Evaluate detection of a defined attack chain
```

Where possible, use synthetic objectives rather than accessing real sensitive data.


---

## 5. Threat Modelling

Threat modelling helps determine which behaviours are relevant to the organisation.

Potential inputs include:

```text
Industry
Geography
Technology stack
Threat intelligence
Known threat actors
Previous incidents
Existing security controls
Business processes
Critical assets
Identity architecture
Cloud architecture
```

MITRE ATT&CK can provide a useful common language for describing adversary behaviours.

[MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }


---

# Operational Model

A practical red team workflow can be represented as:

```text
External
   |
   v
Reconnaissance
   |
   v
Initial Access
   |
   v
Foothold
   |
   +-------------------+
   |                   |
   v                   v
Local Enumeration    Credential Access
   |                   |
   +---------+---------+
             |
             v
      Privilege Escalation
             |
             v
      Internal Discovery
             |
             v
       Lateral Movement
             |
             v
        Target System
             |
             v
          Objective
```


---

# Reconnaissance

Reconnaissance attempts to understand the externally visible attack surface before interacting deeply with individual systems.

Useful information can include:

```text
Domains
Subdomains
IP addresses
Autonomous systems
Cloud infrastructure
VPN gateways
Remote-access services
Email infrastructure
Technology stacks
Public applications
Public repositories
Metadata
Leaked credentials
Public documents
Employee information
Third-party relationships
```

Reconnaissance should remain within the authorised scope and applicable engagement rules.


---

## Passive Reconnaissance

Passive reconnaissance attempts to collect information without directly interacting with the target infrastructure where practical.

Sources can include:

```text
DNS records
Certificate transparency
Search engines
Public code repositories
Public documentation
Internet scanning datasets
WHOIS / RDAP
Public cloud references
Job advertisements
Technology documentation
```


---

## Active Reconnaissance

Active reconnaissance interacts directly with target systems.

Examples include:

```text
DNS resolution
Port scanning
Service identification
HTTP probing
Content discovery
Technology fingerprinting
Authentication-surface discovery
```

The amount and rate of active reconnaissance should reflect the Rules of Engagement.


---

# Attack Surface Mapping

Raw reconnaissance should be converted into an understandable attack surface.

```text
Organisation
     |
     +--> Domains
     |
     +--> Applications
     |
     +--> Remote Access
     |
     +--> Identity
     |
     +--> Cloud
     |
     +--> Email
     |
     +--> Third Parties
```

Each exposed service should be considered in terms of:

```text
Ownership
Technology
Authentication
Internet exposure
Privilege relationship
Business importance
Potential attack path
```


---

# Initial Access

Initial access is the point at which the assessment establishes an authorised foothold.

Potential categories can include:

```text
External application weakness
Exposed remote service
Credential-based access
Cloud identity weakness
Misconfiguration
Approved social engineering
Approved physical access
Supply-chain scenario
```

The exact techniques permitted depend on the Rules of Engagement.

See:

[Initial Access](initial-access.md)


---

# Foothold

A foothold is not necessarily the final objective.

After obtaining access, first establish context.

```text
Who am I?
Where am I?
What system is this?
What privileges do I have?
What network can I reach?
What security controls are present?
What data is accessible?
What should I avoid touching?
```

On Windows:

```cmd
whoami /all
```

On Linux:

```bash
id
```

Avoid immediately performing broad automated activity before understanding the host and its role.


---

# Situational Awareness

After obtaining a foothold, gather enough information to understand the environment.

Potential areas include:

```text
Operating system
Hostname
Network configuration
Domain membership
Current identity
Privileges
Processes
Services
Security software
Local users
Logged-on users
Network connections
Mounted resources
Installed applications
Environment variables
```


---

# Privilege Escalation

Privilege escalation attempts to move from the current security context to a more privileged one where required by the engagement objective.

Windows areas include:

```text
Services
Scheduled tasks
Privileges
Filesystem permissions
Registry permissions
DLL loading
PATH configuration
Credentials
Drivers
Custom applications
```

Linux areas include:

```text
sudo
SUID
SGID
Capabilities
systemd
cron
Filesystem permissions
PATH
Credentials
Containers
Sockets
Kernel
```

Use the interactive privilege escalation references:

- [Windows PrivEsc Explorer](../privesc/windows/)
- [Linux PrivEsc Explorer](../privesc/linux/)


---

# Credential Access

Credentials and authentication material frequently connect otherwise separate systems.

Relevant material can include:

```text
Passwords
Password hashes
Kerberos tickets
Access tokens
API keys
SSH keys
Cloud credentials
Application secrets
Service-account credentials
Browser credentials
Configuration secrets
```

Credential handling requires particular care because real credentials can provide access beyond the intended assessment scope.

See:

[Credential Access](credential-access.md)


---

# Internal Discovery

Internal discovery establishes what the compromised identity or system can access.

Potential questions include:

```text
What networks are reachable?
What hosts exist?
What services are exposed?
What domain is the host joined to?
What trusts exist?
What shares are accessible?
What management infrastructure exists?
What cloud services are reachable?
Which identities are privileged?
```

Discovery should be deliberate rather than unnecessarily noisy.


---

# Active Directory

Where Active Directory is in scope, relevant areas can include:

```text
Domain structure
Users
Groups
Computers
ACLs
Kerberos
NTLM
Delegation
Certificate Services
Trusts
Group Policy
Management infrastructure
Credential exposure
```

Use the dedicated documentation:

[Active Directory](../active-directory/)


---

# Lateral Movement

Lateral movement attempts to move from one authorised system or identity to another as part of an attack path.

Potential mechanisms include:

```text
Remote administration
Shared credentials
Administrative protocols
SSH
SMB
WinRM
WMI
RDP
Cloud management interfaces
Application administration
Management infrastructure
```

The existence of valid credentials does not automatically authorise access to every system where those credentials work.

Scope remains authoritative.

See:

[Lateral Movement](lateral-movement.md)


---

# Command and Control

Command and control provides communication between assessment infrastructure and authorised test systems.

A simplified architecture may look like:

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
Internet
   |
   v
Authorised Test Host
```

Operational considerations include:

```text
Infrastructure isolation
Domain management
TLS
Logging
Redirectors
Access control
Firewall rules
Payload control
Traffic profiles
Cleanup
Defensive visibility
```

See:

[Command and Control](command-and-control.md)


---

# Infrastructure

Red team infrastructure should be treated as production security infrastructure for the duration of an engagement.

Important controls include:

```text
Strong authentication
Restricted administration
SSH key authentication
Firewall restrictions
Logging
Patch management
Encrypted communications
Separate engagement infrastructure
Minimal exposed services
Backups of required configuration
Credential protection
```

See:

[Infrastructure](infrastructure.md)


---

# Persistence

Persistence mechanisms attempt to maintain access across changes such as:

```text
Process termination
User logoff
System restart
Credential rotation
Service restart
```

Persistence can create substantial operational risk.

For many engagements, demonstrating that persistence is possible is preferable to deploying a persistent mechanism.

See:

[Persistence](persistence.md)


---

# Defence Evasion

Defence evasion testing evaluates how security controls respond to authorised adversary behaviours.

Relevant defensive layers can include:

```text
Antivirus
EDR
Application control
PowerShell controls
AMSI
Attack Surface Reduction
Firewalling
Proxy controls
Email security
Identity protection
SIEM
Network detection
Cloud security controls
```

The goal should be to evaluate security controls, not disable protections unnecessarily.

See:

[Defence Evasion](defence-evasion.md)


---

# Objective Execution

The engagement should define what constitutes successful objective completion.

A useful model is:

```text
Objective
   |
   v
Can It Be Reached?
   |
   +--> No --> Document Blocking Control
   |
   +--> Yes
          |
          v
   Minimum Evidence Required
          |
          v
   Stop
```

Do not collect additional sensitive information simply because access is technically possible.


---

# Proof of Access

Where an objective involves sensitive systems or data, use the minimum evidence necessary.

Prefer:

```text
Synthetic marker
Filename
Directory listing
Metadata
Hash of approved test file
Screenshot of authorised test object
Controlled test account
```

Avoid unnecessary copying of:

```text
Personal information
Production databases
Customer records
Medical information
Financial information
Authentication databases
Large datasets
```


---

# Data Exfiltration Simulation

Where exfiltration testing is required, synthetic data is preferable.

```text
Synthetic Dataset
      |
      v
Approved Channel
      |
      v
Controlled Destination
      |
      v
Detection Measurement
```

The purpose is usually to evaluate whether exfiltration behaviour is detected, not to remove real organisational data.


---

# Operational Security

Red team operational security helps prevent the assessment itself from creating unnecessary risk.

Consider:

```text
Infrastructure attribution
Credential storage
Payload storage
Logging
Operator access
Source addresses
DNS records
Certificates
Cloud metadata
Repository exposure
Screenshots
Reports
Temporary files
Engagement data
```


---

## Engagement Data

Treat engagement data as sensitive.

Potentially sensitive material includes:

```text
Credentials
Hashes
Tokens
Hostnames
Internal IP addresses
Architecture information
Vulnerability evidence
Screenshots
Customer data
Source code
Configuration files
```

Store only what is required.


---

# Detection Engineering Perspective

Red team activity should produce useful defensive learning.

For each meaningful action, consider:

```text
What happened?
What telemetry should exist?
Was it logged?
Was it detected?
Was an alert generated?
Was the alert investigated?
Was the activity prevented?
How quickly did the organisation respond?
```

This converts technical execution into measurable defensive outcomes.


---

# Telemetry

Useful telemetry can include:

```text
Endpoint process creation
Authentication events
PowerShell logs
Service changes
Scheduled-task changes
Network connections
DNS queries
Proxy logs
Firewall logs
EDR telemetry
Cloud audit logs
Identity-provider logs
Email security logs
Application logs
```

Telemetry requirements should ideally be considered during engagement planning rather than only after testing.


---

# MITRE ATT&CK Mapping

MITRE ATT&CK provides a useful framework for mapping observed behaviours.

A red team attack path may span several tactics:

```text
Reconnaissance
      |
Resource Development
      |
Initial Access
      |
Execution
      |
Persistence
      |
Privilege Escalation
      |
Defence Evasion
      |
Credential Access
      |
Discovery
      |
Lateral Movement
      |
Collection
      |
Command and Control
      |
Exfiltration
      |
Impact
```

Not every engagement needs to exercise every tactic.


---

# Evidence Collection

Evidence should be collected throughout the assessment.

Useful evidence includes:

```text
Timestamp
Source host
Target host
Current identity
Technique
Command or action
Result
Privilege level
Relevant screenshot
Relevant log
Objective relationship
Detection result
```

A simple evidence model:

```text
Action
  |
  v
Technical Result
  |
  v
Security Impact
  |
  v
Detection Result
  |
  v
Evidence
```


---

# Timeline

Maintain a reliable operational timeline.

Example:

| Time | Source | Target | Action | Result |
|---|---|---|---|---|
| 09:12 | Operator | Web application | Authentication test | Access obtained |
| 09:37 | Foothold | Endpoint | Host enumeration | User context identified |
| 10:04 | Endpoint | Internal service | Connection test | Service reachable |
| 10:31 | Endpoint | Target system | Objective validation | Objective reached |

Use UTC or an explicitly documented timezone consistently.


---

# Cleanup

Cleanup is part of the engagement, not an optional final step.

Track changes such as:

```text
Created files
Created accounts
Modified files
Modified permissions
Created services
Created scheduled tasks
Registry changes
SSH keys
Persistence mechanisms
Cloud resources
Firewall rules
DNS records
Temporary infrastructure
```

A useful workflow is:

```text
Change Made
    |
    v
Record Change
    |
    v
Assessment Ends
    |
    v
Reverse Change
    |
    v
Verify
```


---

# Reporting

A red team report should explain the attack path rather than presenting only isolated findings.

```text
Initial Condition
      |
      v
Weakness 1
      |
      v
Access
      |
      v
Weakness 2
      |
      v
Privilege
      |
      v
Weakness 3
      |
      v
Lateral Movement
      |
      v
Objective
```

This helps stakeholders understand how individual weaknesses combine into business risk.


---

## Finding Structure

A useful finding structure is:

```text
Title
Severity
Affected Systems
Description
Attack Path
Evidence
Impact
Detection Observations
Remediation
References
```


---

## Attack Path Narrative

The report should explain:

```text
Where the attack started
What weakness enabled access
What privileges were obtained
What credentials or trust relationships were used
How lateral movement occurred
Which objective was reached
Which controls detected the activity
Which controls failed to detect the activity
```


---

# Severity

Severity should reflect the actual demonstrated impact.

Consider:

```text
Starting access
Required privileges
Exploit complexity
User interaction
Attack reliability
Affected systems
Privilege obtained
Data exposure
Business impact
Detection capability
Attack chaining
```

Avoid assigning critical severity simply because a technique sounds powerful.


---

# Red Team Success Metrics

Useful metrics can include:

```text
Objective reached
Time to initial access
Time to detection
Time to investigation
Time to containment
Number of attack stages detected
Number of attack stages prevented
Number of meaningful attack paths
Telemetry coverage
Alert quality
Response effectiveness
```

The number of vulnerabilities discovered is usually not the best measure of red team effectiveness.


---

# Stop Conditions

Operators should know when testing must stop.

Potential stop conditions include:

```text
Unexpected production impact
System instability
Access to excluded systems
Unexpected sensitive data
Third-party infrastructure reached
Safety concern
Incident-response escalation
Customer instruction
Loss of infrastructure control
Uncertain scope
```

When scope becomes uncertain, do not assume permission.


---

# Emergency Communication

The engagement should have an escalation path.

```text
Operator
   |
   v
Red Team Lead
   |
   v
Authorised Customer Contact
   |
   v
Security / Incident Response
```

Emergency contact details should be available before testing begins.


---

# Red Team Checklist

## Before the Engagement

- [ ] Written authorisation confirmed
- [ ] Scope confirmed
- [ ] Rules of Engagement approved
- [ ] Objectives defined
- [ ] Exclusions documented
- [ ] Testing window confirmed
- [ ] Emergency contacts confirmed
- [ ] Stop conditions understood
- [ ] Infrastructure prepared
- [ ] Operator access restricted
- [ ] Logging enabled
- [ ] Evidence handling agreed
- [ ] Cleanup process defined

## Reconnaissance

- [ ] Domains identified
- [ ] Subdomains investigated
- [ ] IP ranges understood
- [ ] External services identified
- [ ] Applications mapped
- [ ] Identity surfaces identified
- [ ] Remote-access services reviewed
- [ ] Cloud exposure considered
- [ ] Third-party boundaries respected

## Initial Access

- [ ] Permitted techniques confirmed
- [ ] Initial access documented
- [ ] Source and target recorded
- [ ] Security context established
- [ ] Scope revalidated after access

## Post-Compromise

- [ ] Current identity established
- [ ] Host role understood
- [ ] Security controls identified
- [ ] Privilege escalation assessed
- [ ] Credentials handled securely
- [ ] Internal discovery controlled
- [ ] Lateral movement remained in scope

## Objective

- [ ] Objective reached or blocking control identified
- [ ] Minimum required evidence collected
- [ ] Sensitive data collection minimised
- [ ] Detection status recorded

## Cleanup

- [ ] Files removed
- [ ] Accounts removed
- [ ] Persistence removed
- [ ] Configuration restored
- [ ] Cloud resources removed
- [ ] Infrastructure decommissioned
- [ ] Cleanup verified

## Reporting

- [ ] Timeline complete
- [ ] Attack path documented
- [ ] Findings evidenced
- [ ] Detection observations included
- [ ] Remediation included
- [ ] MITRE ATT&CK mappings reviewed
- [ ] Executive impact explained


---

# Red Team Decision Model

```text
                 START
                   |
                   v
          Written Authorisation?
             /           \
           No             Yes
           |               |
          STOP             v
                         Scope
                           |
                           v
                   Attack Surface
                           |
                           v
                    Initial Access
                      /        \
                    No          Yes
                    |            |
             Document Path       v
                           Establish Context
                                |
                                v
                         Need More Privilege?
                           /           \
                         No             Yes
                         |               |
                         |        Privilege Escalation
                         |               |
                         +-------+-------+
                                 |
                                 v
                          Internal Discovery
                                 |
                                 v
                         Lateral Movement?
                           /           \
                         No             Yes
                         |               |
                         +-------+-------+
                                 |
                                 v
                              Objective
                                 |
                                 v
                        Minimum Evidence
                                 |
                                 v
                              Cleanup
                                 |
                                 v
                              Report
```


---

# Final Testing Model

A mature red team workflow can be summarised as:

```text
Authorisation
      |
      v
Scope
      |
      v
Threat Model
      |
      v
Infrastructure
      |
      v
Reconnaissance
      |
      v
Initial Access
      |
      v
Situational Awareness
      |
      v
Privilege Escalation
      |
      v
Credential Access
      |
      v
Discovery
      |
      v
Lateral Movement
      |
      v
Objective
      |
      v
Detection Evaluation
      |
      v
Cleanup
      |
      v
Reporting
      |
      v
Security Improvement
```


---

# Related Notes

- [Windows](../windows/)
- [Linux](../linux/)
- [PrivEsc Explorer](../privesc/)
- [Active Directory](../active-directory/)
- [Web Application Security](../web/)
- [Purple Teaming](../purple-teaming/)
- [Cheatsheets](../cheatsheets/)


---

# References

- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-115 - Technical Guide to Information Security Testing and Assessment](https://csrc.nist.gov/pubs/sp/800/115/final){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team){ target="_blank" rel="noopener noreferrer" }
- [MITRE Caldera](https://caldera.mitre.org/){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Red teaming can involve actions that affect production systems, identities, credentials, applications, cloud environments, security controls, and sensitive information. Perform testing only with explicit written authorisation and within the approved scope and Rules of Engagement. Stop when scope, safety, or authorisation becomes uncertain.
