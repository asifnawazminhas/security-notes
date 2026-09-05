---
title: Linux PrivEsc Explorer
description: Interactive Linux privilege escalation reference for authorised security assessments.
---

# Linux PrivEsc Explorer

<div class="privesc-hero">

<h2>Linux PrivEsc Explorer</h2>

<p>
Search Linux privilege escalation techniques based on sudo permissions,
SUID and SGID binaries, capabilities, services, scheduled jobs, filesystem
permissions, credentials, containers, groups, sockets, and system
configuration discovered during an authorised assessment.
</p>

<div class="privesc-card-badges">
<span class="privesc-badge privesc-severity-medium">Linux</span>
<span class="privesc-badge privesc-badge-category">PrivEsc</span>
<span class="privesc-badge privesc-badge-category">Interactive</span>
</div>

</div>


---

## Explorer

<div id="privesc-explorer" data-platform="linux">

<div class="privesc-toolbar">

<div class="privesc-search-wrapper">
<label for="privesc-search">Search techniques</label>
<input
    id="privesc-search"
    class="privesc-search"
    type="search"
    placeholder="Try: sudo, SUID, cap_setuid, systemd, cron, Docker..."
    autocomplete="off"
>
</div>

<div class="privesc-filter-wrapper">
<label for="privesc-category">Category</label>
<select id="privesc-category" class="privesc-filter">
<option value="all">All categories</option>
</select>
</div>

<div class="privesc-filter-wrapper">
<label for="privesc-severity">Severity</label>
<select id="privesc-severity" class="privesc-filter">
<option value="all">All severities</option>
<option value="critical">Critical</option>
<option value="high">High</option>
<option value="medium">Medium</option>
<option value="low">Low</option>
<option value="informational">Informational</option>
</select>
</div>

<button id="privesc-reset" class="privesc-reset" type="button">
Reset
</button>

</div>

<div id="privesc-active-filters" class="privesc-active-filters"></div>

<div class="privesc-results-header">

<span id="privesc-result-count">
Loading techniques...
</span>

<select id="privesc-sort" class="privesc-sort" aria-label="Sort techniques">
<option value="name">Sort: Name</option>
<option value="severity">Sort: Severity</option>
<option value="category">Sort: Category</option>
</select>

</div>

<div id="privesc-results" class="privesc-results">

<noscript>
PrivEsc Explorer requires JavaScript. The reference material below remains available without JavaScript.
</noscript>

</div>

<div id="privesc-empty" class="privesc-empty" hidden>
No techniques found. Try another search term or reset the filters.
</div>

</div>


---

## Search Examples

Try searching for:

```text
sudo
NOPASSWD
SETENV
SUID
SGID
cap_setuid
cap_dac_override
cap_sys_admin
systemd
cron
writable
PATH
Docker
docker.sock
LXD
NFS
no_root_squash
socket
credential
SSH
kernel
```

The explorer searches across technique names, categories, descriptions, prerequisites, commands, validation guidance, MITRE ATT&CK information, and tags.


---

## Linux Privilege Escalation Model

Linux privilege escalation commonly involves a lower-privileged user being able to influence a resource or execution path associated with a more privileged identity.

```text
Current User
    |
    v
Enumeration
    |
    +--> sudo
    +--> SUID / SGID
    +--> Capabilities
    +--> Services
    +--> systemd
    +--> Cron
    +--> Filesystem
    +--> PATH
    +--> Libraries
    +--> Credentials
    +--> Groups
    +--> Containers
    +--> Unix Sockets
    +--> NFS
    +--> Applications
    +--> Kernel
    |
    v
Candidate
    |
    v
Validate Privilege Relationship
    |
    v
Determine Impact
```

The presence of an interesting configuration does not automatically prove privilege escalation.


---

## Establish the Current Security Context

Start with:

```bash
id
```

```bash
whoami
```

```bash
groups
```

Additional context:

```bash
uname -a
```

```bash
cat /etc/os-release
```

```bash
hostname
```

Understanding the current identity and system context prevents incorrect assumptions later in the assessment.


---

## sudo

Inspect delegated sudo privileges:

```bash
sudo -l
```

Look for:

```text
NOPASSWD
SETENV
Wildcards
Interpreters
Editors
File utilities
Package managers
Service-management commands
Shell-capable applications
User-controlled arguments
User-controlled environment variables
```

A sudo entry is not automatically vulnerable.

The delegated command and its argument restrictions must be understood.


---

## sudo NOPASSWD

Example:

```text
(ALL) NOPASSWD: /usr/bin/example
```

Questions include:

```text
What can the executable do?
Can it execute commands?
Can it write files?
Can it load plugins?
Can it invoke an editor?
Can it invoke a pager?
Can it execute child processes?
Can arguments influence files or commands?
```

Use [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" } as a reference where applicable, but verify the exact local binary and sudo rule.


---

## sudo SETENV

`SETENV` can allow environment variables to be preserved or supplied to delegated commands.

Potentially security-sensitive variables depend on the command and execution context.

The presence of `SETENV` should be treated as a candidate requiring contextual analysis rather than automatic privilege escalation.


---

## sudo Wildcards

Wildcard rules may become dangerous when a privileged program interprets attacker-controlled filenames as command-line options or arguments.

The relevant relationship is:

```text
Privileged Command
      |
      v
Wildcard Expansion
      |
      v
User-Controlled Filename
      |
      v
Argument Interpretation
```

Validate the exact command behaviour before reporting the condition.


---

## SUID

Find SUID files:

```bash
find / -perm -4000 -type f 2>/dev/null
```

SUID causes an executable to run with the effective UID of its owner.

A SUID binary is not automatically vulnerable.

Review:

```text
Owner
Binary purpose
Arguments
Environment handling
File operations
External commands
Library loading
Configuration
Version
Custom code
```


---

## SGID

Find SGID files:

```bash
find / -perm -2000 -type f 2>/dev/null
```

SGID can provide access to security-sensitive groups or resources.

The impact depends on the owning group and the functionality exposed by the executable.


---

## Custom SUID Applications

Custom SUID applications deserve additional attention.

Useful review areas include:

```text
system()
popen()
exec*()
Relative executable paths
Temporary files
Environment variables
Writable configuration
Writable libraries
Unsafe file handling
User-controlled input
```

Prefer static analysis and permission inspection before executing invasive tests.


---

## Linux Capabilities

Enumerate file capabilities:

```bash
getcap -r / 2>/dev/null
```

Common security-sensitive capabilities include:

```text
CAP_SETUID
CAP_SETGID
CAP_DAC_OVERRIDE
CAP_DAC_READ_SEARCH
CAP_SYS_ADMIN
CAP_SYS_PTRACE
CAP_SYS_MODULE
CAP_NET_ADMIN
CAP_NET_RAW
```

Capabilities should always be interpreted in the context of the executable receiving them.


---

## CAP_SETUID

`CAP_SETUID` allows applicable processes to manipulate user IDs.

When assigned to a flexible interpreter or executable capable of arbitrary code execution, this can represent a strong privilege escalation candidate.

Verify:

```bash
getcap /path/to/binary
```

Do not assume every executable with `CAP_SETUID` provides arbitrary code execution.


---

## CAP_SETGID

`CAP_SETGID` can allow manipulation of group IDs.

Impact depends on which groups can be assumed and what those groups can access.


---

## CAP_DAC_OVERRIDE

This capability can bypass discretionary access-control checks for applicable file operations.

Potential impact includes access to otherwise protected files.

The exact executable functionality determines practical exploitability.


---

## CAP_DAC_READ_SEARCH

This capability can bypass certain file read and directory search restrictions.

It can be security sensitive where the executable exposes flexible file-reading functionality.


---

## CAP_SYS_ADMIN

`CAP_SYS_ADMIN` is extremely broad.

Depending on the context, it can expose security-sensitive operations involving:

```text
Mounts
Namespaces
Filesystem operations
Kernel interfaces
System administration
```

The presence of this capability warrants careful investigation.


---

## CAP_SYS_PTRACE

This capability can permit tracing or inspection of processes outside normal restrictions.

Impact depends on:

```text
Target process
Credential material
Process protections
Namespace boundaries
Kernel restrictions
```


---

## CAP_SYS_MODULE

This capability can permit kernel-module operations in applicable contexts.

Kernel module testing is potentially destabilising and should not be performed on production systems unless specifically authorised.


---

## Services

Enumerate services:

```bash
systemctl list-units --type=service --all
```

Installed service definitions:

```bash
systemctl list-unit-files --type=service
```

Inspect a service:

```bash
systemctl cat <service>
```

Useful fields include:

```text
User=
Group=
ExecStart=
ExecStartPre=
ExecStartPost=
Environment=
EnvironmentFile=
WorkingDirectory=
```


---

## systemd

A useful systemd assessment model is:

```text
systemd Unit
    |
    v
Privileged Identity
    |
    v
ExecStart
    |
    +--> Binary
    +--> Script
    +--> EnvironmentFile
    +--> Configuration
    |
    v
Can Current User Modify It?
```

Inspect ownership and permissions before changing anything.


---

## Writable systemd Executable

Example relationship:

```text
root service
    |
    v
ExecStart=/opt/example/service.sh
    |
    v
service.sh writable by normal user
```

Validate:

```bash
ls -l /opt/example/service.sh
```

```bash
namei -l /opt/example/service.sh
```

```bash
getfacl /opt/example/service.sh
```

The permission relationship itself may provide sufficient evidence without modifying the script.


---

## systemd Environment Files

A privileged service may consume an environment file:

```text
EnvironmentFile=/etc/example/example.env
```

Inspect:

```bash
ls -l /etc/example/example.env
```

```bash
getfacl /etc/example/example.env
```

Whether this creates privilege escalation depends on how the service uses those variables.


---

## Cron

Enumerate system cron configuration:

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d/
```

```bash
ls -la /etc/cron.daily/
```

```bash
ls -la /etc/cron.hourly/
```

User cron:

```bash
crontab -l
```

Look for privileged jobs executing writable resources.


---

## Writable Cron Script

A strong candidate relationship is:

```text
root cron job
    |
    v
Executes Script
    |
    v
Script Writable by Normal User
```

Inspect:

```bash
ls -l /path/to/script
```

```bash
getfacl /path/to/script
```

Prefer demonstrating permissions and execution identity without modifying the script.


---

## Cron PATH

Review PATH definitions inside:

```text
/etc/crontab
/etc/cron.d/*
```

A candidate may exist when:

```text
Privileged cron job
        +
Relative executable name
        +
Writable earlier PATH directory
```

All three conditions matter.


---

## Filesystem Permissions

Useful commands:

```bash
ls -la
```

```bash
stat /path/to/file
```

```bash
namei -l /path/to/file
```

```bash
getfacl /path/to/file
```

Interesting conditions include:

```text
Root-owned file writable by current user
Root-owned directory writable by current user
Privileged script writable by current user
Privileged configuration writable by current user
Writable parent directory
Unexpected ACL
```


---

## Writable Directories

Find writable directories carefully:

```bash
find / -type d -writable 2>/dev/null
```

The result set may be large.

Writable directories such as `/tmp` are expected and are not automatically vulnerabilities.

Determine whether a privileged process consumes attacker-controlled resources from the directory.


---

## PATH

Inspect:

```bash
echo "$PATH"
```

Readable format:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

A PATH candidate usually requires:

```text
Privileged Process
       +
Relative Command
       +
Writable PATH Directory
       +
Writable Directory Appears Earlier
```


---

## Credentials

Potential locations include:

```text
Shell history
Environment variables
Configuration files
Backup files
SSH keys
Application credentials
Database configuration
Deployment files
Cloud credentials
Service configuration
```

Search only within authorised scope.


---

## Shell History

Examples:

```bash
cat ~/.bash_history
```

```bash
cat ~/.zsh_history
```

History may contain:

```text
Passwords
Tokens
SSH commands
Database commands
Administrative commands
Internal hosts
API keys
```

Treat discovered credentials as sensitive assessment evidence.


---

## Environment Variables

Inspect:

```bash
env
```

or:

```bash
printenv
```

Look for secrets only where authorised.


---

## SSH Keys

Common location:

```text
~/.ssh/
```

Inspect permissions:

```bash
ls -la ~/.ssh/
```

Private keys should not be copied unnecessarily.

Establish relevance and scope before using discovered authentication material.


---

## Groups

Enumerate:

```bash
id
```

```bash
groups
```

Security-sensitive group memberships can include:

```text
sudo
wheel
docker
lxd
disk
shadow
libvirt
adm
```

The impact depends on system configuration.


---

## Docker

Check:

```bash
id
```

```bash
docker info
```

Docker access can be highly privileged when the client can communicate with a rootful Docker daemon.

Relevant factors include:

```text
docker group membership
Docker socket permissions
Rootful vs rootless daemon
Remote API exposure
Authorisation plugins
Host mounts
Container privileges
```


---

## Docker Socket

Inspect:

```bash
ls -l /var/run/docker.sock
```

The key question is:

```text
Can the current user control a rootful Docker daemon?
```

If yes, the access may effectively represent host-level administrative authority.


---

## LXD

Check:

```bash
id
```

```bash
lxc list
```

Membership in an LXD administrative group can be security sensitive depending on configuration and available host integration.

Do not assume all LXD environments are configured identically.


---

## NFS

Inspect mounted filesystems:

```bash
mount
```

```bash
findmnt
```

Client-visible NFS configuration can provide useful context.

Server-side export configuration should be reviewed where authorised.

A security-sensitive configuration can include:

```text
no_root_squash
```

but practical impact depends on export permissions, write access, mount access, and server configuration.


---

## Unix Sockets

Enumerate listening Unix sockets:

```bash
ss -lx
```

Inspect:

```bash
find / -type s 2>/dev/null
```

Privileged local APIs can be exposed through Unix sockets.

Review:

```text
Socket ownership
Socket permissions
Server identity
Protocol
Authentication
Authorisation
Available operations
```


---

## Libraries

Privilege escalation candidates can involve privileged applications loading resources from writable locations.

Investigate:

```text
Shared libraries
Plugin directories
Python modules
Application extensions
Configuration-controlled paths
Dynamic linker configuration
```

Do not report generic writable library directories without establishing a privileged consumer.


---

## Python Import Paths

For privileged Python applications, inspect:

```text
Imports
Working directory
sys.path
Custom modules
Writable module directories
Environment
```

The important question is whether a privileged Python process imports a module that a lower-privileged user can control.


---

## Custom Applications

Custom privileged applications should be reviewed for:

```text
Relative commands
Writable configuration
Writable plugins
Writable libraries
Temporary files
Environment variables
Unsafe file permissions
Local sockets
Credential storage
Service integration
Scheduled execution
```


---

## Kernel

Kernel privilege escalation should generally be considered after configuration-based paths have been investigated.

Collect:

```bash
uname -a
```

```bash
cat /etc/os-release
```

Relevant factors include:

```text
Exact kernel version
Distribution patches
Architecture
Exploit prerequisites
Namespaces
Capabilities
Security modules
Exploit mitigations
System stability
```

Do not infer vulnerability from a version string alone.


---

## Security Controls

Understand controls such as:

```text
SELinux
AppArmor
seccomp
Namespaces
Capabilities
sudo policy
Filesystem mount options
Container isolation
Kernel hardening
```

Examples:

```bash
getenforce 2>/dev/null
```

```bash
aa-status 2>/dev/null
```

```bash
findmnt
```

Security controls may materially affect exploitability.


---

## Candidate Validation

Use:

```text
Finding
   |
   v
Who Controls It?
   |
   v
Who Consumes It?
   |
   v
What UID/GID Is Used?
   |
   v
Can Current User Influence It?
   |
   v
Are Security Controls Present?
   |
   v
What Privilege Would Be Obtained?
```

Example:

```text
Writable backup.sh
       |
       v
Executed by cron?
       |
      Yes
       |
       v
Cron runs as root?
       |
      Yes
       |
       v
Current user can modify script?
       |
      Yes
       |
       v
Strong PrivEsc Candidate
```


---

## Evidence

Strong evidence should establish:

```text
Current identity
Controlled resource
Permission
Privileged consumer
Execution identity
Impact
```

Example:

```text
Current identity:
www-data

Resource:
/opt/example/backup.sh

Permissions:
-rwxrwxr-x root www-data

Privileged consumer:
root cron job

Execution identity:
root
```

This is stronger than simply stating that a file is writable.


---

## What Not to Report Automatically

Do not automatically report:

```text
SUID binary
SGID binary
Capability
Writable /tmp
Docker installed
Cron present
systemd service
Kernel version
sudo entry
Unix socket
Writable user file
NFS mount
```

Each observation requires security context.


---

## Detection Opportunities

Potential telemetry includes:

```text
sudo execution
Process creation
SUID execution
Capability changes
Filesystem permission changes
systemd changes
Cron changes
Sensitive file access
Container creation
Docker API activity
Kernel module operations
Authentication events
SSH activity
```

Useful data sources may include:

```text
auditd
journald
syslog
sudo logs
EDR
Container runtime logs
File-integrity monitoring
```


---

## Remediation Model

Common remediation themes include:

```text
Restrict sudo
     |
     v
Remove unnecessary SUID / SGID
     |
     v
Remove unnecessary capabilities
     |
     v
Correct filesystem permissions
     |
     v
Protect privileged scripts
     |
     v
Protect systemd resources
     |
     v
Protect cron resources
     |
     v
Use safe PATH handling
     |
     v
Restrict privileged groups
     |
     v
Protect container sockets
     |
     v
Remove exposed credentials
     |
     v
Patch vulnerable software
     |
     v
Harden kernel and mandatory access controls
```


---

## Quick Enumeration

```bash
id
```

```bash
uname -a
```

```bash
cat /etc/os-release
```

```bash
sudo -l
```

```bash
find / -perm -4000 -type f 2>/dev/null
```

```bash
find / -perm -2000 -type f 2>/dev/null
```

```bash
getcap -r / 2>/dev/null
```

```bash
systemctl list-units --type=service --all
```

```bash
cat /etc/crontab
```

```bash
ss -lntup
```

```bash
ss -lx
```

```bash
findmnt
```

```bash
env
```


---

## Checklist

### Identity

- [ ] Current user identified
- [ ] UID and GID recorded
- [ ] Group memberships reviewed
- [ ] Distribution identified
- [ ] Kernel identified

### sudo

- [ ] `sudo -l` reviewed
- [ ] NOPASSWD rules reviewed
- [ ] SETENV rules reviewed
- [ ] Wildcards reviewed
- [ ] Flexible delegated binaries reviewed

### SUID and SGID

- [ ] SUID files enumerated
- [ ] SGID files enumerated
- [ ] Custom binaries identified
- [ ] GTFOBins relevance checked
- [ ] Ownership and functionality understood

### Capabilities

- [ ] File capabilities enumerated
- [ ] CAP_SETUID reviewed
- [ ] CAP_SETGID reviewed
- [ ] CAP_DAC_OVERRIDE reviewed
- [ ] CAP_DAC_READ_SEARCH reviewed
- [ ] CAP_SYS_ADMIN reviewed
- [ ] CAP_SYS_PTRACE reviewed
- [ ] CAP_SYS_MODULE reviewed

### Services

- [ ] Services enumerated
- [ ] Privileged service identities reviewed
- [ ] ExecStart resources reviewed
- [ ] Writable scripts reviewed
- [ ] Writable binaries reviewed
- [ ] Environment files reviewed

### Cron

- [ ] System cron reviewed
- [ ] User cron reviewed
- [ ] Writable cron scripts investigated
- [ ] Cron PATH reviewed
- [ ] Wildcard behaviour considered

### Filesystem

- [ ] Root-owned writable files investigated
- [ ] Root-owned writable directories investigated
- [ ] ACLs reviewed where relevant
- [ ] Parent directories considered
- [ ] PATH directories reviewed

### Credentials

- [ ] Shell history considered
- [ ] Environment variables reviewed
- [ ] Configuration files reviewed
- [ ] SSH keys reviewed where authorised
- [ ] Backup files considered

### Groups and Containers

- [ ] docker membership reviewed
- [ ] Docker socket reviewed
- [ ] Rootless/rootful context understood
- [ ] LXD membership reviewed
- [ ] disk membership reviewed
- [ ] shadow membership reviewed
- [ ] libvirt membership reviewed

### Network and Local Interfaces

- [ ] Unix sockets reviewed
- [ ] NFS configuration considered
- [ ] Privileged local APIs investigated

### Applications

- [ ] Custom privileged applications reviewed
- [ ] Writable configuration reviewed
- [ ] Writable plugins reviewed
- [ ] Library loading considered
- [ ] Python import behaviour considered

### Kernel and Security Controls

- [ ] Kernel version identified
- [ ] Distribution patches considered
- [ ] SELinux/AppArmor considered
- [ ] Mount options considered
- [ ] Kernel LPE treated as contextual candidate

### Reporting

- [ ] Candidate distinguished from confirmed finding
- [ ] Privileged consumer identified
- [ ] Evidence collected
- [ ] Impact established
- [ ] Detection opportunities considered
- [ ] Remediation provided


---

## Related Notes

- [PrivEsc Explorer](./)
- [Windows PrivEsc Explorer](../windows/)
- [Linux Overview](../../linux/)
- [Linux Enumeration](../../linux/enumeration/)
- [Linux Privilege Escalation](../../linux/privilege-escalation/)
- [Linux Services](../../linux/services/)
- [Linux Credentials](../../linux/credentials/)


---

## References

- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK](https://attack.mitre.org/){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [systemd Documentation](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [Linux Capabilities Manual](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [Docker Security](https://docs.docker.com/engine/security/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }


---

!!! warning "Authorised testing only"
    Linux privilege escalation testing can affect services, scheduled jobs, filesystem permissions, containers, kernel state, authentication material, and security controls. Perform active validation only where explicitly authorised and prefer non-destructive evidence whenever possible.
