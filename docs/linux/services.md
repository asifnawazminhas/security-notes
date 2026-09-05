# Linux Services

Linux services are long-running or event-driven processes that provide operating system, network, application, monitoring, and management functionality.

From a security perspective, services are important because they frequently:

- Run with elevated privileges
- Start automatically
- Execute scripts or binaries
- Load configuration files
- Read environment files
- Access credentials
- Listen on network interfaces
- Interact with sensitive files
- Run scheduled operations
- Depend on other executables and libraries

The security question is not simply:

```text
Does a service run as root?
```

Many legitimate services require elevated privileges.

The more useful question is:

```text
Privileged Service
       |
       v
What Does It Execute?
       |
       v
What Does It Trust?
       |
       v
Can a Lower-Privileged User Influence It?
       |
       v
Can That Influence Cross a Security Boundary?
```

This page focuses on identifying, analysing, validating, and reporting insecure Linux service configurations.

---

# 1. Service Assessment Workflow

A practical workflow is:

```text
Enumerate Services
      |
      v
Identify Interesting Services
      |
      v
Determine Execution Identity
      |
      v
Inspect Unit Configuration
      |
      v
Identify Executables
      |
      v
Identify Scripts
      |
      v
Identify Configuration
      |
      v
Identify Environment Files
      |
      v
Inspect Permissions
      |
      v
Inspect Parent Directories
      |
      v
Identify Dependencies
      |
      v
Determine User Influence
      |
      v
Validate Safely
      |
      v
Assess Impact
```

---

# 2. Service Managers

Linux systems can use several service-management mechanisms.

Common examples include:

```text
systemd
SysV init
OpenRC
runit
Upstart
Application-specific supervisors
Container runtimes
```

Modern enterprise distributions commonly use systemd.

Do not assume every Linux host does.

---

# 3. Identify the Init System

PID 1:

```bash
ps -p 1 -o pid,comm,args
```

Example:

```text
PID COMMAND         COMMAND
1   systemd         /sbin/init
```

Check:

```bash
readlink -f /sbin/init
```

Where systemd is present:

```bash
systemctl --version
```

---

# 4. systemd

systemd manages:

```text
Services
Sockets
Timers
Mounts
Devices
Targets
Paths
Automounts
Slices
```

For host assessment, service units are particularly important.

Service units normally use:

```text
.service
```

Example:

```text
sshd.service
nginx.service
docker.service
application.service
```

---

# 5. Running Services

List running services:

```bash
systemctl list-units --type=service --state=running
```

All loaded service units:

```bash
systemctl list-units --type=service --all
```

Installed service unit files:

```bash
systemctl list-unit-files --type=service
```

---

# 6. Enabled Services

```bash
systemctl list-unit-files --type=service --state=enabled
```

An enabled service is configured to participate in startup according to its installation relationships.

Enabled does not necessarily mean currently running.

---

# 7. Failed Services

```bash
systemctl --failed
```

Failed services may reveal:

```text
Broken applications
Old deployments
Misconfiguration
Unused software
Incorrect permissions
Missing dependencies
```

Failure alone is not a security vulnerability.

---

# 8. Service Status

Inspect a specific service:

```bash
systemctl status example.service
```

Potential information includes:

```text
Loaded state
Active state
Main PID
Recent logs
Unit path
Process tree
Startup errors
```

---

# 9. Unit File Location

Display the fragment path:

```bash
systemctl show example.service -p FragmentPath
```

Example:

```text
FragmentPath=/etc/systemd/system/example.service
```

Inspect:

```bash
ls -l /etc/systemd/system/example.service
```

---

# 10. Common systemd Unit Locations

Common locations include:

```text
/etc/systemd/system/
/run/systemd/system/
/usr/lib/systemd/system/
/lib/systemd/system/
```

Distribution layout varies.

A useful hierarchy concept is:

```text
Vendor Units
     |
     v
System Configuration
     |
     v
Runtime Configuration
     |
     v
Drop-In Overrides
```

Use systemd tooling to determine the effective configuration rather than assuming one file contains the entire service definition.

---

# 11. Display Effective Unit Configuration

```bash
systemctl cat example.service
```

This is preferable to reading only the primary unit file because it can also show applicable drop-in configuration.

Example:

```ini
[Unit]
Description=Example Application

[Service]
User=appuser
ExecStart=/opt/example/bin/server

[Install]
WantedBy=multi-user.target
```

---

# 12. Service Properties

```bash
systemctl show example.service
```

Useful filtered view:

```bash
systemctl show example.service \
    -p User \
    -p Group \
    -p ExecStart \
    -p ExecStartPre \
    -p ExecStartPost \
    -p WorkingDirectory \
    -p Environment \
    -p EnvironmentFiles \
    -p FragmentPath
```

---

# 13. Execution Identity

Check:

```bash
systemctl show example.service -p User -p Group
```

Example:

```text
User=application
Group=application
```

For many system services, an empty `User=` means the service defaults to root.

Confirm against the running process.

---

# 14. Running Process Identity

Find the service PID:

```bash
systemctl show example.service -p MainPID
```

Then:

```bash
ps -o user,group,euser,egroup,pid,ppid,comm,args -p PID
```

Replace `PID` with the actual process identifier.

This helps establish the effective runtime identity.

---

# 15. Main Process

```bash
systemctl show example.service -p MainPID -p ExecMainPID
```

Process:

```bash
ps -fp PID
```

Executable:

```bash
readlink -f /proc/PID/exe
```

---

# 16. ExecStart

Display:

```bash
systemctl show example.service -p ExecStart
```

Or:

```bash
systemctl cat example.service
```

Example:

```ini
ExecStart=/opt/application/bin/server
```

The referenced executable becomes a primary security-analysis target.

---

# 17. Additional Execution Directives

Important directives include:

```text
ExecCondition
ExecStartPre
ExecStart
ExecStartPost
ExecReload
ExecStop
ExecStopPost
```

Inspect:

```bash
systemctl show example.service \
    -p ExecCondition \
    -p ExecStartPre \
    -p ExecStart \
    -p ExecStartPost \
    -p ExecReload \
    -p ExecStop \
    -p ExecStopPost
```

A service may execute several privileged programs, not just its primary executable.

---

# 18. Service Execution Chain

Model the complete chain:

```text
systemd
   |
   v
Service Unit
   |
   +---- ExecStartPre
   |
   +---- ExecStart
   |
   +---- ExecStartPost
   |
   +---- ExecReload
   |
   +---- ExecStop
   |
   v
Scripts / Binaries
```

Each referenced resource may require permission analysis.

---

# 19. Executable Permissions

If:

```ini
ExecStart=/opt/application/bin/server
```

inspect:

```bash
stat -c '%A %a %U %G %n' /opt/application/bin/server
```

ACL:

```bash
getfacl /opt/application/bin/server
```

Path:

```bash
namei -l /opt/application/bin/server
```

---

# 20. Why Parent Directories Matter

A binary can appear protected:

```text
-rwxr-xr-x root root server
```

while a parent directory is writable:

```text
drwxrwxr-x root application /opt/application/bin
```

The security relationship may therefore be:

```text
Protected Binary
      |
      v
Writable Parent Directory
      |
      v
File Replacement Possible?
```

Always inspect path components.

---

# 21. `namei`

Use:

```bash
namei -l /opt/application/bin/server
```

Example concept:

```text
f: /opt/application/bin/server
drwxr-xr-x root root /
drwxr-xr-x root root opt
drwxr-xr-x root root application
drwxrwxr-x root app  bin
-rwxr-xr-x root root server
```

This provides a compact path-permission view.

---

# 22. Service Scripts

Services frequently execute scripts:

```ini
ExecStart=/opt/application/start.sh
```

or:

```ini
ExecStart=/usr/bin/python3 /opt/application/server.py
```

or:

```ini
ExecStart=/bin/bash /opt/application/start.sh
```

Check:

```bash
stat -c '%A %a %U %G %n' /opt/application/start.sh
```

---

# 23. Script Security Model

```text
Privileged Service
      |
      v
Interpreter
      |
      v
Script
      |
      v
Can Standard User Modify Script?
      |
      +---- No -> Continue Analysis
      |
      +---- Yes
              |
              v
      Privileged Execution Relationship
```

A writable script executed by a higher-privileged service can create a serious privilege boundary weakness.

---

# 24. Script Dependencies

A protected script may call other resources.

Example:

```bash
#!/bin/bash

/opt/application/bin/backup
/opt/application/scripts/cleanup.sh
```

Inspect all relevant dependencies:

```text
Main Script
    |
    +---- Executable
    +---- Child Script
    +---- Config
    +---- Temporary File
    +---- Environment
```

---

# 25. Commands Without Absolute Paths

A script may contain:

```bash
backup-tool --run
```

rather than:

```bash
/usr/local/bin/backup-tool --run
```

Determine the execution environment and PATH.

Do not assume PATH hijacking is possible solely because an absolute path is absent.

---

# 26. Service PATH

Inspect service environment:

```bash
systemctl show example.service -p Environment
```

Also inspect the unit:

```bash
systemctl cat example.service
```

A unit can define:

```ini
Environment="PATH=/opt/application/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin"
```

Check each relevant PATH directory.

---

# 27. PATH Security Relationship

```text
Root Service
    |
    v
Script Runs "helper"
    |
    v
PATH Lookup
    |
    v
Writable Directory Before Real Helper
    |
    v
Potential Privileged Command Substitution
```

Every condition must be demonstrated before reporting.

---

# 28. Working Directory

Check:

```bash
systemctl show example.service -p WorkingDirectory
```

Example:

```text
WorkingDirectory=/opt/application
```

Inspect:

```bash
stat -c '%A %a %U %G %n' /opt/application
```

A writable working directory can matter when applications use relative paths or create security-sensitive files there.

---

# 29. Relative Paths

Applications may reference:

```text
./config.yml
./plugins/
./scripts/
./data/
```

Relative-path behaviour depends on the working directory.

A writable working directory does not automatically mean exploitation is possible.

Determine what the application actually loads.

---

# 30. Environment Variables

Inspect:

```bash
systemctl show example.service -p Environment
```

Example:

```text
Environment=APP_MODE=production
```

Environment variables may influence:

```text
Configuration
PATH
Library loading
Runtime behaviour
Application endpoints
Credentials
```

---

# 31. Environment Files

A unit may contain:

```ini
EnvironmentFile=/etc/example/example.env
```

Inspect through:

```bash
systemctl cat example.service
```

Then metadata:

```bash
stat -c '%A %a %U %G %n' /etc/example/example.env
```

---

# 32. Environment File Permissions

Environment files can contain:

```text
Database credentials
API keys
Application secrets
Paths
Runtime options
```

If the service runs with higher privilege, unauthorised modification may influence its behaviour.

If the file contains secrets, excessive read access may create a separate credential exposure.

---

# 33. Environment File Security Model

```text
Privileged Service
      |
      v
EnvironmentFile
      |
      +---- Read Exposure?
      |
      +---- Write Exposure?
              |
              v
       Can Behaviour Be Influenced?
```

Read and write exposure represent different security risks.

---

# 34. Drop-In Overrides

systemd supports service drop-ins.

View:

```bash
systemctl cat example.service
```

Potential locations include:

```text
/etc/systemd/system/example.service.d/
/run/systemd/system/example.service.d/
```

List:

```bash
ls -la /etc/systemd/system/example.service.d/ 2>/dev/null
```

---

# 35. Drop-In Permission Analysis

If a user can modify an effective service override, they may be able to alter service behaviour.

Inspect:

```bash
find /etc/systemd/system/example.service.d -maxdepth 1 -type f -ls 2>/dev/null
```

Parent:

```bash
namei -l /etc/systemd/system/example.service.d
```

---

# 36. Unit File Permissions

Inspect custom units:

```bash
find /etc/systemd/system -type f -name '*.service' -exec stat -c '%A %a %U %G %n' {} \; 2>/dev/null
```

Look for unexpected write access.

Do not assume every unit under `/etc/systemd/system` is custom; symlinks and locally installed package units may also appear there.

---

# 37. Writable Unit Files

Targeted candidate search:

```bash
find /etc/systemd/system -type f -name '*.service' -writable -ls 2>/dev/null
```

If a standard user can modify a privileged unit, investigate carefully.

Do not modify the unit merely to prove access.

---

# 38. Writable systemd Directories

```bash
find /etc/systemd/system -type d -writable -ls 2>/dev/null
```

A writable directory can sometimes be more important than individual file permissions because it may permit file creation or replacement.

Validate actual effective permissions.

---

# 39. Service Configuration Files

Applications frequently read configuration from:

```text
/etc/application/
/opt/application/
/srv/application/
/var/lib/application/
```

Identify actual configuration from:

```text
Service arguments
Environment variables
Application documentation
Process command line
Open files
```

---

# 40. Process Command Line

Find PID:

```bash
systemctl show example.service -p MainPID
```

Then:

```bash
ps -o user,pid,ppid,comm,args -p PID
```

Command-line arguments can reveal:

```text
Config paths
Ports
Log paths
Working directories
Runtime modes
```

They can also contain secrets, so handle output carefully.

---

# 41. Open Files

Where `lsof` is installed and permissions allow:

```bash
lsof -p PID
```

This can identify:

```text
Configuration
Logs
Libraries
Sockets
Database files
Temporary files
```

Use targeted output rather than collecting unnecessary data.

---

# 42. Process File Descriptors

Without `lsof`, inspect where permitted:

```bash
ls -l /proc/PID/fd
```

Do not assume another user's file descriptors are accessible.

---

# 43. Process Environment

Where permitted:

```bash
tr '\0' '\n' < /proc/PID/environ
```

This can expose sensitive values.

Use only when necessary and authorised.

---

# 44. Service User

A strong design normally uses a dedicated account where root privileges are unnecessary.

Check:

```bash
systemctl show example.service -p User -p Group
```

Then:

```bash
id serviceuser
```

Assess:

```text
Groups
Home directory
Shell
File access
Supplementary privileges
```

---

# 45. Service Accounts

Find an account:

```bash
getent passwd serviceuser
```

Example:

```text
serviceuser:x:998:998:Application Service:/var/lib/application:/usr/sbin/nologin
```

A non-login shell is common for service accounts.

---

# 46. Supplementary Groups

systemd can specify:

```ini
SupplementaryGroups=
```

Inspect:

```bash
systemctl show example.service -p SupplementaryGroups
```

Additional groups can substantially increase service access.

---

# 47. Dynamic Users

systemd can use:

```ini
DynamicUser=yes
```

Check:

```bash
systemctl show example.service -p DynamicUser
```

Dynamic users can reduce the need for persistent service accounts.

They are one component of service hardening.

---

# 48. Root Services

Find root-owned running processes:

```bash
ps -eo user,pid,ppid,comm,args | awk '$1 == "root"'
```

Then correlate custom processes with service units.

Do not report:

```text
Service runs as root
```

without explaining why root is unnecessary or how the service can be influenced.

---

# 49. Privileged Service Candidate

A stronger candidate is:

```text
Service Runs as Root
        +
User Can Modify Service Dependency
        =
Potential Privilege Boundary Weakness
```

Examples of dependencies include:

```text
Executable
Script
Config
Environment file
Plugin
Writable working directory
Helper program
```

---

# 50. Service Restart Permissions

A user may have permission to restart a service through:

```text
sudo
PolicyKit
Application management tooling
Custom scripts
```

Check sudo:

```bash
sudo -l
```

Example:

```text
(root) /usr/bin/systemctl restart application.service
```

Restart permission alone does not necessarily permit modification of the service.

---

# 51. Restart Relationship

A dangerous combination can be:

```text
User Can Modify Service Resource
          +
User Can Restart Privileged Service
          =
Immediate Trigger Available
```

Without restart rights, the issue may still be exploitable during:

```text
Boot
Administrative restart
Application update
Crash recovery
Scheduled restart
```

The timing affects practical impact.

---

# 52. Service Enablement

Check:

```bash
systemctl is-enabled example.service
```

Runtime:

```bash
systemctl is-active example.service
```

Possible results include:

```text
enabled
disabled
static
masked
active
inactive
failed
```

Interpret each in context.

---

# 53. Service Dependencies

Show dependencies:

```bash
systemctl list-dependencies example.service
```

Reverse dependencies:

```bash
systemctl list-dependencies --reverse example.service
```

Dependencies can help determine operational importance and impact.

---

# 54. Ordering

Inspect:

```bash
systemctl show example.service -p Before -p After
```

This can reveal relationships with:

```text
Network
Databases
Storage
Other applications
Targets
```

---

# 55. Requires and Wants

```bash
systemctl show example.service -p Requires -p Wants
```

These properties can help understand service dependencies.

They are usually architectural information rather than direct vulnerabilities.

---

# 56. Socket Activation

Some services are started through `.socket` units.

List:

```bash
systemctl list-units --type=socket --all
```

Installed socket units:

```bash
systemctl list-unit-files --type=socket
```

---

# 57. Socket-Activated Services

Inspect:

```bash
systemctl cat example.socket
```

Associated service:

```bash
systemctl status example.socket
```

Potentially important directives include:

```text
ListenStream
ListenDatagram
SocketUser
SocketGroup
SocketMode
Accept
```

---

# 58. Unix Socket Permissions

If a service exposes:

```text
/run/application.sock
```

inspect:

```bash
stat -c '%A %a %U %G %n' /run/application.sock
```

Socket permissions can define which local users can interact with a privileged daemon.

---

# 59. High-Privilege Sockets

Examples of security-sensitive sockets may include:

```text
Container runtime sockets
Virtualisation management sockets
Database administration sockets
Custom root daemon sockets
```

The important question is what operations the socket permits.

---

# 60. Listening Network Services

Identify:

```bash
ss -lntup
```

Then correlate the process with its service.

Example workflow:

```text
Port 8443
   |
   v
PID
   |
   v
Process
   |
   v
systemd Service
   |
   v
Service Configuration
```

---

# 61. Bind Address

Differentiate:

```text
127.0.0.1:8080
```

from:

```text
0.0.0.0:8080
```

and:

```text
[::]:8080
```

A listening service's exposure depends on:

```text
Bind address
Firewall
Routing
Network controls
Container networking
```

---

# 62. Local-Only Services

A local-only listener can still be security-relevant if:

```text
Local users can access privileged functionality
Another service proxies requests
SSRF can reach it
A container can access it
Authentication is weak
```

Do not dismiss localhost services automatically.

---

# 63. Service Version

Version information may be obtained from:

```text
Package database
Binary version command
Service logs
Application API
Banner
```

Prefer package-manager information when assessing vendor patch status.

---

# 64. Binary Package Ownership

Debian-based:

```bash
dpkg -S /usr/sbin/example 2>/dev/null
```

RPM-based:

```bash
rpm -qf /usr/sbin/example 2>/dev/null
```

This helps distinguish packaged software from custom binaries.

---

# 65. Package Version

Debian:

```bash
dpkg-query -W -f='${Package} ${Version}\n' package-name
```

RPM:

```bash
rpm -q package-name
```

Do not determine vulnerability status from upstream version numbers alone.

---

# 66. Custom Service Detection

Custom services commonly use:

```text
/opt
/srv
/usr/local
/home
Custom application directories
```

Find custom unit references:

```bash
grep -RniE 'Exec(Start|Stop|Reload)=/(opt|srv|usr/local|home)/' /etc/systemd/system 2>/dev/null
```

Review results manually.

---

# 67. Custom Executables

```bash
find /opt /srv /usr/local -type f -executable -ls 2>/dev/null
```

Correlate with actual service configuration.

Do not assume every executable in these directories is service-related.

---

# 68. Custom Scripts

```bash
find /opt /srv /usr/local -type f \( \
    -name '*.sh' -o \
    -name '*.py' -o \
    -name '*.pl' -o \
    -name '*.rb' \
\) -ls 2>/dev/null
```

Prioritise scripts referenced by privileged services.

---

# 69. Interpreter-Based Services

Examples:

```ini
ExecStart=/usr/bin/python3 /opt/application/server.py
```

```ini
ExecStart=/usr/bin/node /opt/application/server.js
```

```ini
ExecStart=/bin/bash /opt/application/start.sh
```

The interpreter may be protected while the script is writable.

Always inspect both.

---

# 70. Python Services

For:

```ini
ExecStart=/usr/bin/python3 /opt/application/server.py
```

review:

```text
server.py
Imported local modules
Working directory
Virtual environment
Configuration
Plugin directories
PYTHONPATH
```

Do not assume Python import manipulation is possible without validating actual module resolution.

---

# 71. Python Virtual Environments

A service may use:

```text
/opt/application/venv/bin/python
```

Inspect:

```bash
namei -l /opt/application/venv/bin/python
```

Environment directory:

```bash
stat -c '%A %a %U %G %n' /opt/application/venv
```

Weak permissions in a privileged application's virtual environment can be significant.

---

# 72. Node.js Services

A Node service may execute:

```ini
ExecStart=/usr/bin/node /opt/application/server.js
```

Review:

```text
server.js
package.json
node_modules
Environment files
Working directory
Application configuration
```

Permission analysis remains the primary focus.

---

# 73. Java Services

Example:

```ini
ExecStart=/usr/bin/java -jar /opt/application/application.jar
```

Inspect:

```bash
stat -c '%A %a %U %G %n' /opt/application/application.jar
```

Also inspect:

```text
Configuration
Classpath
Working directory
External libraries
Startup scripts
```

---

# 74. Shell-Based Services

Example:

```ini
ExecStart=/bin/bash /opt/application/start.sh
```

Review the complete script:

```bash
sed -n '1,240p' /opt/application/start.sh
```

Do not modify it during enumeration.

---

# 75. Configuration Includes

Applications may recursively load configuration.

Example:

```text
/etc/application/application.conf
      |
      v
include /etc/application/conf.d/*.conf
```

Check included directories as well as the primary file.

---

# 76. Plugin Directories

Some services dynamically load:

```text
Plugins
Modules
Extensions
Providers
Hooks
```

Identify these from application configuration or documentation.

Then inspect:

```bash
stat -c '%A %a %U %G %n' /path/to/plugins
```

A writable plugin directory used by a privileged service deserves investigation.

---

# 77. Plugin Security Model

```text
Privileged Application
      |
      v
Loads Plugins
      |
      v
Plugin Directory
      |
      v
Writable by Lower-Privileged User?
```

If yes, determine whether arbitrary plugin loading actually occurs.

---

# 78. Library Dependencies

For a dynamically linked binary:

```bash
ldd /opt/application/bin/server
```

This shows normal runtime library dependencies.

Do not use `ldd` on an untrusted executable when safer inspection methods are available, because some historical or unusual binaries may cause unsafe behaviour during inspection.

For trusted assessment targets, package and ELF inspection tools may be preferable.

---

# 79. ELF Interpreter and Dependencies

Where available:

```bash
readelf -l /opt/application/bin/server | grep 'Requesting program interpreter'
```

Dynamic section:

```bash
readelf -d /opt/application/bin/server
```

Look for:

```text
NEEDED
RPATH
RUNPATH
```

---

# 80. RPATH and RUNPATH

Inspect:

```bash
readelf -d /opt/application/bin/server | grep -E 'RPATH|RUNPATH'
```

If a privileged executable searches a user-writable library directory, investigate further.

Do not assume every RPATH or RUNPATH is insecure.

---

# 81. Dynamic Linker Environment

Service environment may influence library loading through variables such as:

```text
LD_LIBRARY_PATH
```

Check:

```bash
systemctl show example.service -p Environment
```

Privileged execution contexts may ignore or sanitise certain linker variables.

Validate actual behaviour before reporting.

---

# 82. `/etc/ld.so.preload`

Inspect metadata:

```bash
ls -l /etc/ld.so.preload 2>/dev/null
```

If present and authorised to read:

```bash
cat /etc/ld.so.preload
```

Unexpected unprivileged write access to this file would be highly security-sensitive.

---

# 83. Temporary Files

Services may use:

```text
/tmp
/var/tmp
/run
Application-specific temporary directories
```

Look for insecure patterns such as:

```text
Predictable filenames
Unsafe permissions
Following attacker-controlled links
Shared writable directories
```

Do not assume temporary-file use itself is vulnerable.

---

# 84. PrivateTmp

Check:

```bash
systemctl show example.service -p PrivateTmp
```

When enabled, systemd can provide a service with isolated temporary directories.

This can reduce exposure to some shared temporary-file attacks.

---

# 85. RuntimeDirectory

Check:

```bash
systemctl show example.service -p RuntimeDirectory -p RuntimeDirectoryMode
```

systemd can create controlled runtime directories for services.

This is generally preferable to ad hoc creation of sensitive directories under shared locations.

---

# 86. StateDirectory

```bash
systemctl show example.service -p StateDirectory
```

Related directives can include:

```text
RuntimeDirectory
StateDirectory
CacheDirectory
LogsDirectory
ConfigurationDirectory
```

These can help systemd manage directory ownership and lifecycle securely.

---

# 87. PID Files

Some services use PID files:

```text
/run/application.pid
/var/run/application.pid
```

Identify from application configuration.

Check permissions:

```bash
stat -c '%A %a %U %G %n' /run/application.pid 2>/dev/null
```

PID-file weaknesses require application-specific validation.

---

# 88. Log Files

Identify service logs:

```bash
journalctl -u example.service
```

or application-specific files.

Permissions:

```bash
stat -c '%A %a %U %G %n' /var/log/application/application.log
```

Log write access does not normally translate into service execution, but unsafe log processing can create application-specific risks.

---

# 89. Journal Logs

Recent:

```bash
journalctl -u example.service -n 100
```

Current boot:

```bash
journalctl -u example.service -b
```

Follow:

```bash
journalctl -u example.service -f
```

Use follow mode only when useful and stop it when finished.

---

# 90. Service Errors

Errors can reveal:

```text
Configuration paths
Missing files
Permissions
Dependency failures
Runtime identities
Network endpoints
```

Example:

```bash
journalctl -u example.service -p warning
```

Do not expose sensitive log content unnecessarily in reports.

---

# 91. Credentials in Service Configuration

Potential locations include:

```text
Environment=
EnvironmentFile=
Command-line arguments
Application config
Credential files
Cloud configuration
Database configuration
```

Do not automatically collect secret values.

Often the security issue can be demonstrated through permissions and metadata.

---

# 92. Credentials in Command Lines

Check:

```bash
ps -eo user,pid,ppid,comm,args
```

Poorly designed services may include:

```text
--password
--token
--api-key
```

Command-line arguments may be visible to other users depending on the environment.

Prefer secure credential mechanisms.

---

# 93. systemd Credentials

Modern systemd provides credential-related mechanisms for services.

Inspect properties:

```bash
systemctl show example.service | grep -i credential
```

Where used, these mechanisms can reduce reliance on plaintext secrets in command lines or general environment variables.

Implementation and availability depend on systemd version and configuration.

---

# 94. Service Configuration Ownership

For a configuration file:

```bash
stat -c '%A %a %U %G %n' /etc/application/application.conf
```

ACL:

```bash
getfacl /etc/application/application.conf
```

Path:

```bash
namei -l /etc/application/application.conf
```

---

# 95. Writable Configuration

A writable configuration file becomes important when the application supports directives that influence privileged behaviour.

Examples can include:

```text
Executable paths
Plugin paths
Hooks
Scripts
Log destinations
Include files
Command templates
Module loading
```

The exact impact depends on the application.

---

# 96. Configuration Validation Model

```text
Writable Config
      |
      v
Privileged Service Reads It
      |
      v
Which Settings Can User Change?
      |
      v
Can Setting Influence Execution?
      |
      v
Privilege Boundary?
```

Do not stop at:

```text
Config is writable
```

---

# 97. Recursive Includes

If configuration contains:

```text
include=/etc/application/conf.d/*
```

inspect:

```bash
ls -la /etc/application/conf.d
```

and:

```bash
find /etc/application/conf.d -maxdepth 1 -type f -exec stat -c '%A %a %U %G %n' {} \;
```

An included file can be just as security-sensitive as the primary configuration.

---

# 98. Writable Include Directory

Check:

```bash
stat -c '%A %a %U %G %n' /etc/application/conf.d
```

A writable include directory can sometimes allow creation of new configuration files even when existing files are protected.

Validate whether the application automatically loads newly created entries.

---

# 99. Service Symlinks

Inspect:

```bash
readlink -f /etc/systemd/system/example.service
```

systemd commonly uses symlinks for enablement.

A symlink is not inherently insecure.

Analyse the final target and directory permissions.

---

# 100. Service Enablement Symlinks

Example:

```text
/etc/systemd/system/multi-user.target.wants/example.service
```

Inspect:

```bash
ls -l /etc/systemd/system/multi-user.target.wants/
```

These usually reference actual service units.

Do not modify enablement links during routine enumeration.

---

# 101. Masked Services

Check:

```bash
systemctl is-enabled example.service
```

A masked service commonly resolves to:

```text
/dev/null
```

Inspect:

```bash
ls -l /etc/systemd/system/example.service 2>/dev/null
```

Masking prevents normal service activation.

---

# 102. Service Restart Behaviour

Check:

```bash
systemctl show example.service -p Restart -p RestartSec
```

Possible policies include:

```text
no
on-success
on-failure
on-abnormal
on-watchdog
on-abort
always
```

Automatic restart can affect exploit timing and operational impact, but should primarily be understood for service reliability.

---

# 103. Start Limits

Inspect:

```bash
systemctl show example.service -p StartLimitIntervalUSec -p StartLimitBurst
```

Avoid repeatedly crashing or restarting production services during testing.

---

# 104. Permissions to Manage Services

Check sudo:

```bash
sudo -l
```

Also consider PolicyKit on systems where service management is delegated through it.

Do not assume `systemctl` execution itself grants administrative control.

Authorization is evaluated separately.

---

# 105. PolicyKit

PolicyKit can control privileged operations for desktop and system services.

Processes:

```bash
ps -ef | grep '[p]olkit'
```

Installed command where available:

```bash
command -v pkcheck
```

PolicyKit assessment should focus on actual policies and granted actions rather than its mere presence.

---

# 106. D-Bus Services

Linux services frequently expose functionality through D-Bus.

List user-visible bus names where tooling is available:

```bash
busctl list
```

System services can expose privileged methods.

Authorization may be enforced through:

```text
D-Bus policy
PolicyKit
Application logic
Unix identity
```

---

# 107. D-Bus Service Files

Potential locations include:

```text
/usr/share/dbus-1/system-services/
/usr/share/dbus-1/services/
```

Inspect:

```bash
ls -la /usr/share/dbus-1/system-services/ 2>/dev/null
```

Do not assume service activation through D-Bus is insecure.

---

# 108. Service Hardening Properties

systemd provides numerous sandboxing and restriction features.

Useful properties include:

```text
NoNewPrivileges
PrivateTmp
PrivateDevices
ProtectSystem
ProtectHome
ProtectKernelTunables
ProtectKernelModules
ProtectControlGroups
ProtectClock
RestrictSUIDSGID
LockPersonality
MemoryDenyWriteExecute
CapabilityBoundingSet
AmbientCapabilities
SystemCallFilter
RestrictAddressFamilies
```

Not every option is appropriate for every service.

---

# 109. `NoNewPrivileges`

Check:

```bash
systemctl show example.service -p NoNewPrivileges
```

`NoNewPrivileges=yes` prevents the service and its descendants from gaining privileges through certain execution mechanisms.

It is a useful hardening control but not a complete sandbox.

---

# 110. `ProtectSystem`

```bash
systemctl show example.service -p ProtectSystem
```

Potential settings include:

```text
no
yes
full
strict
```

This can make portions of the filesystem read-only to the service.

Compatibility must be considered.

---

# 111. `ProtectHome`

```bash
systemctl show example.service -p ProtectHome
```

This can restrict service access to:

```text
/home
/root
/run/user
```

depending on configuration.

---

# 112. `PrivateDevices`

```bash
systemctl show example.service -p PrivateDevices
```

This can limit service access to physical devices.

It is particularly useful for services that do not require direct device access.

---

# 113. `ProtectKernelTunables`

```bash
systemctl show example.service -p ProtectKernelTunables
```

This can reduce access to kernel runtime configuration.

---

# 114. `ProtectKernelModules`

```bash
systemctl show example.service -p ProtectKernelModules
```

Services that do not require module management generally should not need unrestricted kernel module access.

---

# 115. `ProtectControlGroups`

```bash
systemctl show example.service -p ProtectControlGroups
```

This can restrict service modification of control-group state.

---

# 116. `RestrictSUIDSGID`

```bash
systemctl show example.service -p RestrictSUIDSGID
```

This can restrict creation of SUID and SGID files by the service.

---

# 117. Capabilities

Check:

```bash
systemctl show example.service \
    -p CapabilityBoundingSet \
    -p AmbientCapabilities
```

Services may retain selected Linux capabilities rather than full root authority.

---

# 118. Capability Bounding Set

A service can restrict capabilities using:

```ini
CapabilityBoundingSet=
```

Inspect:

```bash
systemctl show example.service -p CapabilityBoundingSet
```

Least privilege should be applied where practical.

---

# 119. Ambient Capabilities

Check:

```bash
systemctl show example.service -p AmbientCapabilities
```

Ambient capabilities allow selected privileges to be inherited across executable transitions under defined conditions.

Review whether each capability is operationally required.

---

# 120. High-Impact Capabilities

Examples requiring careful justification include:

```text
CAP_SYS_ADMIN
CAP_SYS_PTRACE
CAP_DAC_OVERRIDE
CAP_DAC_READ_SEARCH
CAP_SETUID
CAP_SETGID
CAP_NET_ADMIN
```

Risk depends on application functionality and containment.

---

# 121. systemd Security Analysis

Where supported:

```bash
systemd-analyze security example.service
```

This produces a hardening assessment.

Use it as:

```text
Hardening Review
```

not:

```text
Vulnerability Proof
```

---

# 122. Overall systemd Security Review

```bash
systemd-analyze security
```

This may evaluate multiple units.

Results can be extensive.

Focus on relevant custom or high-risk services.

---

# 123. Hardening Score Interpretation

A poor `systemd-analyze security` score does not automatically mean:

```text
Service Vulnerable
```

It generally means:

```text
Service Has Broad Access
```

Determine whether:

```text
The access is necessary
The service is exposed
The service processes untrusted input
The service can be compromised
Additional controls exist
```

---

# 124. Privilege Separation

Prefer architecture such as:

```text
Small Privileged Component
        |
        v
Restricted Interface
        |
        v
Unprivileged Worker
```

rather than:

```text
Entire Application
        |
        v
Runs as root
```

where application requirements allow separation.

---

# 125. Service User Hardening

A dedicated service user should normally have only the resources required for the application.

Review:

```bash
id serviceuser
```

and:

```bash
getent passwd serviceuser
```

Consider:

```text
Groups
Home directory
Shell
File ownership
Sudo rights
SSH access
```

---

# 126. Service Account Sudo

Check whether a service account has sudo rights where appropriate:

```bash
sudo -l -U serviceuser
```

This generally requires sufficient privilege to query another user's sudo policy.

Do not assume service accounts are unprivileged merely because they are not root.

---

# 127. Service Account Shell

```bash
getent passwd serviceuser
```

Common restricted shells include:

```text
/usr/sbin/nologin
/bin/false
```

A login shell may be operationally required in some environments.

Treat it as a configuration consideration rather than an automatic vulnerability.

---

# 128. Writable Service Binary Candidate

Find writable executables in custom application paths:

```bash
find /opt /srv /usr/local -type f -executable -writable -ls 2>/dev/null
```

Then correlate each candidate with:

```bash
systemctl cat service-name
```

Do not report unrelated writable executables as service weaknesses.

---

# 129. Writable Service Script Candidate

```bash
find /opt /srv /usr/local -type f \( \
    -name '*.sh' -o \
    -name '*.py' -o \
    -name '*.pl' -o \
    -name '*.rb' \
\) -writable -ls 2>/dev/null
```

Next determine whether a privileged service actually executes the file.

---

# 130. Writable Configuration Candidate

```bash
find /etc /opt /srv /usr/local -type f \( \
    -name '*.conf' -o \
    -name '*.ini' -o \
    -name '*.yaml' -o \
    -name '*.yml' -o \
    -name '*.json' \
\) -writable -ls 2>/dev/null
```

This can produce false positives.

Use targeted application paths whenever possible.

---

# 131. Root-Owned Writable Service Resources

Target likely custom application locations:

```bash
find /opt /srv /usr/local -user root -writable -ls 2>/dev/null
```

A root-owned object writable by the current user deserves investigation, but ownership alone does not establish its security significance.

---

# 132. ACL Review

For a candidate:

```bash
getfacl /opt/application/start.sh
```

Example concept:

```text
user::rwx
user:analyst:rw-
group::r-x
mask::rwx
other::r-x
```

An ACL can explain write access not obvious from basic mode bits.

---

# 133. Effective User Access

Where available:

```bash
test -r /path/to/file && echo "Readable"
test -w /path/to/file && echo "Writable"
test -x /path/to/file && echo "Executable"
```

These tests evaluate access from the current shell's context.

They are useful supporting evidence.

---

# 134. Non-Destructive Directory Write Test

Where required and authorised:

```bash
dir="/opt/application"
testfile="$dir/.write-test-$$"

if touch "$testfile" 2>/dev/null; then
    echo "[+] Write access confirmed: $dir"
    rm -f "$testfile"
else
    echo "[-] Write access denied: $dir"
fi
```

Do not replace service executables merely to prove directory write access.

---

# 135. Non-Destructive File Permission Evidence

Prefer:

```bash
stat -c '%A %a %U %G %n' /opt/application/start.sh
getfacl /opt/application/start.sh
namei -l /opt/application/start.sh
```

This may be sufficient to demonstrate the permission weakness without altering the service.

---

# 136. Service Restart Testing

Restarting a production service can cause:

```text
Downtime
Connection loss
Data loss
Transaction interruption
Monitoring alerts
Automatic failover
```

Do not restart services unless explicitly authorised and operationally safe.

---

# 137. Safer Validation

Prefer:

```text
Permission Evidence
       +
Service Configuration
       +
Runtime Identity
       +
Execution Relationship
```

over:

```text
Modify Production Script
       +
Restart Service
```

Full exploitation is often unnecessary.

---

# 138. Privileged Script Finding

Example chain:

```text
Current user:
analyst
      |
      v
Member of:
application
      |
      v
application group can write:
 /opt/application/start.sh
      |
      v
start.sh executed by:
 application.service
      |
      v
application.service runs as:
 root
```

This establishes a meaningful privilege relationship.

---

# 139. Writable Unit Finding

Example:

```text
Current User
      |
      v
Can Modify Unit File
      |
      v
Unit Starts as root
      |
      v
Unit Controls Executed Command
      |
      v
Privilege Boundary Weakness
```

A restart or boot event may be required for the modified configuration to execute.

---

# 140. Writable Environment File Finding

Example:

```text
Root Service
     |
     v
Reads EnvironmentFile
     |
     v
File Writable by Standard User
     |
     v
Environment Influences Executed Program
```

The impact depends on which variables the service actually uses.

---

# 141. Writable Config Finding

Example:

```text
Root Application
      |
      v
Reads Writable Config
      |
      v
Config Supports Plugin Path
      |
      v
User Controls Loaded Component
```

The application's configuration semantics must be verified.

---

# 142. Writable Plugin Directory Finding

```text
Privileged Service
      |
      v
Loads Plugins Automatically
      |
      v
Plugin Directory Writable
      |
      v
Lower-Privileged User Controls Loaded Code
```

This can be significant when plugin execution occurs with the service identity.

---

# 143. Excessive Service Privileges

A service may run as root even when its functionality requires only limited access.

Assessment should consider:

```text
Network ports
Files
Devices
Capabilities
Directories
Kernel interfaces
Other services
```

Possible remediation may involve:

```text
Dedicated service account
Capabilities
Filesystem permissions
systemd sandboxing
Privilege separation
```

---

# 144. Root Is Not Automatically a Finding

Avoid:

```text
Finding:
Nginx master process runs as root
```

Many services intentionally start a privileged master process and then drop privileges for workers.

Understand the service architecture first.

---

# 145. Worker Processes

Example process analysis:

```bash
ps -eo user,pid,ppid,comm,args | grep '[n]ginx'
```

You may observe:

```text
root       master process
www-data   worker process
www-data   worker process
```

Assess the privileges of the component that handles untrusted input.

---

# 146. Privilege Dropping

Some applications:

```text
Start as root
      |
      v
Bind privileged resource
      |
      v
Drop privileges
      |
      v
Process requests as service user
```

This can significantly reduce impact.

Verify actual process identities.

---

# 147. Chroot and RootDirectory

Check:

```bash
systemctl show example.service -p RootDirectory -p RootImage
```

These can provide filesystem isolation.

They are not complete security boundaries by themselves.

---

# 148. User Namespace

Check service settings:

```bash
systemctl show example.service -p PrivateUsers
```

User namespaces can help isolate identity mappings in some configurations.

Compatibility and kernel policy matter.

---

# 149. Network Isolation

Check:

```bash
systemctl show example.service -p PrivateNetwork
```

A service with:

```text
PrivateNetwork=yes
```

receives a separate network namespace.

This may significantly reduce network exposure.

---

# 150. Address Family Restrictions

```bash
systemctl show example.service -p RestrictAddressFamilies
```

A service may be restricted to only required socket families.

This is a defence-in-depth control.

---

# 151. System Call Filtering

```bash
systemctl show example.service -p SystemCallFilter
```

System call filtering can reduce available kernel attack surface.

It requires application-specific compatibility testing.

---

# 152. Memory Protections

Check:

```bash
systemctl show example.service -p MemoryDenyWriteExecute
```

This can prevent mappings that are simultaneously writable and executable in supported scenarios.

Not every runtime is compatible with this restriction.

---

# 153. Device Access

```bash
systemctl show example.service -p DevicePolicy -p DeviceAllow
```

Services generally should not receive broad device access unless required.

---

# 154. Read-Write Paths

Check:

```bash
systemctl show example.service \
    -p ReadWritePaths \
    -p ReadOnlyPaths \
    -p InaccessiblePaths
```

These can restrict filesystem access beyond normal Unix permissions.

---

# 155. Service Hardening Model

```text
Dedicated User
      +
Minimal Groups
      +
Restricted Capabilities
      +
Protected Filesystem
      +
Private Temporary Space
      +
Restricted Devices
      +
Restricted Network
      +
System Call Filtering
      +
NoNewPrivileges
      =
Reduced Service Attack Surface
```

Not every control applies to every application.

---

# 156. SysV Init

Legacy services may use:

```text
/etc/init.d/
```

List:

```bash
ls -la /etc/init.d/
```

Running service information may still be exposed through:

```bash
service --status-all 2>/dev/null
```

Behaviour varies between distributions.

---

# 157. SysV Script Permissions

Inspect:

```bash
stat -c '%A %a %U %G %n' /etc/init.d/example
```

Path:

```bash
namei -l /etc/init.d/example
```

A writable root-executed init script is security-sensitive.

---

# 158. SysV Script Analysis

Review:

```bash
sed -n '1,260p' /etc/init.d/example
```

Look for:

```text
Executables
Configuration
Environment files
PATH
Temporary files
Relative commands
Helper scripts
```

---

# 159. `/etc/default`

Debian-family services may read environment or configuration from:

```text
/etc/default/
```

Example:

```bash
ls -la /etc/default
```

Correlate files with actual service scripts or units.

---

# 160. `/etc/sysconfig`

RHEL-family services may use:

```text
/etc/sysconfig/
```

Example:

```bash
ls -la /etc/sysconfig 2>/dev/null
```

Again, determine whether the service actually reads the file.

---

# 161. OpenRC

Check:

```bash
command -v rc-service
```

Services:

```bash
rc-status 2>/dev/null
```

Service scripts commonly exist beneath:

```text
/etc/init.d/
```

Use OpenRC-native tools where applicable.

---

# 162. Supervisor Processes

Applications may use:

```text
supervisord
s6
runit
PM2
custom process managers
```

Process enumeration:

```bash
ps -ef
```

Determine the actual supervisor before analysing startup configuration.

---

# 163. Supervisor Configuration

For supervisord, configuration may commonly appear beneath:

```text
/etc/supervisor/
/etc/supervisord.conf
```

Exact locations vary.

Inspect only when the process manager is actually present.

---

# 164. PM2

Node.js deployments may use PM2.

Check:

```bash
command -v pm2
```

Processes:

```bash
ps -ef | grep '[P]M2'
```

PM2 configuration and process ownership should be reviewed according to the deployment model.

---

# 165. Container Services

Services may actually be containers managed through:

```text
Docker
Podman
containerd
Kubernetes
systemd wrappers
```

A systemd unit might contain:

```text
ExecStart=/usr/bin/docker ...
```

or:

```text
ExecStart=/usr/bin/podman ...
```

Review both the systemd configuration and container configuration.

---

# 166. Docker Service

Check:

```bash
systemctl status docker 2>/dev/null
```

Socket:

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

Users with unrestricted Docker daemon access may effectively possess extensive host authority.

---

# 167. Container Socket Permissions

```bash
stat -c '%A %a %U %G %n' /var/run/docker.sock 2>/dev/null
```

Current groups:

```bash
id
```

Do not treat Docker group membership as a software vulnerability.

It represents highly privileged administrative delegation.

---

# 168. Podman

Check:

```bash
podman info 2>/dev/null
```

Podman can operate rootless or rootful.

The security model differs significantly depending on deployment.

---

# 169. Service Network Exposure

For each network service document:

```text
Protocol
Port
Bind address
Process
Service
Execution user
Authentication
Encryption
Firewall exposure
Application version
```

Example:

```text
TCP/8443
0.0.0.0
application.service
User=application
TLS enabled
Host firewall restricted
```

---

# 170. Service Authentication

A service can be correctly permissioned locally but insecure remotely.

Assess where relevant:

```text
Authentication required?
Default credentials?
Anonymous access?
Mutual authentication?
TLS?
Administrative interface exposed?
```

Network application testing should remain within the applicable service and web assessment sections.

---

# 171. Service Configuration Backups

Search a specific service configuration directory:

```bash
find /etc/application -type f \( \
    -name '*.bak' -o \
    -name '*.old' -o \
    -name '*.orig' -o \
    -name '*~' \
\) -ls 2>/dev/null
```

Backups can expose older secrets or weaker configuration.

---

# 172. Service Secrets

Potential locations:

```text
Environment files
Configuration
Command line
Credential files
Key files
Cloud configuration
Database configuration
```

Detailed credential analysis belongs in [Linux Credentials](credentials.md).

---

# 173. TLS Private Keys

A network service may reference a private key.

Example configuration:

```text
ssl_certificate_key /etc/application/tls/server.key
```

Inspect metadata:

```bash
stat -c '%A %a %U %G %n' /etc/application/tls/server.key
```

Avoid copying private keys unless explicitly required and authorised.

---

# 174. Private-Key Permissions

Private keys should generally be accessible only to identities requiring them.

Potentially excessive permissions:

```text
World-readable
Broad group-readable
User-writable when privileged service trusts the key
```

Actual requirements depend on the service architecture.

---

# 175. Service Database Credentials

Applications may use database credentials from:

```text
Config files
Environment files
Secret stores
Unix sockets
Peer authentication
Managed identities
```

Do not assume plaintext passwords must exist.

Prefer credential-less or managed authentication mechanisms where practical.

---

# 176. Logs and Secrets

Review whether services log:

```text
Passwords
Tokens
Session IDs
Authorization headers
Private keys
Database connection strings
Personal data
```

Logging sensitive values can create a secondary exposure.

---

# 177. Service Core Dumps

A crashed service may generate a core dump containing:

```text
Credentials
Tokens
Keys
Request data
Application memory
```

Check relevant system policy before collecting any core files.

Do not intentionally crash services to obtain dumps.

---

# 178. Service Resource Limits

Inspect:

```bash
systemctl show example.service | grep '^Limit'
```

Resource limits may influence availability and hardening.

They are normally operational controls rather than direct privilege escalation mechanisms.

---

# 179. Restart and Availability Risk

Before interacting with a service determine:

```text
Is it production?
Is it clustered?
Is failover available?
Are users connected?
Can transactions be interrupted?
Will restart lose state?
```

Service security testing must account for availability.

---

# 180. Low-Noise Service Enumeration

Start with:

```bash
systemctl list-units --type=service --state=running
```

Then:

```bash
systemctl list-unit-files --type=service
```

For an interesting service:

```bash
systemctl status example.service
systemctl cat example.service
systemctl show example.service -p User -p Group -p ExecStart -p WorkingDirectory -p EnvironmentFiles -p FragmentPath
```

Then inspect only referenced resources.

---

# 181. High-Value Service Targets

Prioritise:

```text
Custom services
Root services using /opt or /srv
Services using scripts
Services with writable configuration
Services with writable environment files
Services loading plugins
Services with custom helper binaries
Services with privileged sockets
Services exposing administrative interfaces
```

This is usually more effective than analysing every standard distribution service equally.

---

# 182. Service Enumeration Decision Tree

```text
Service Found
    |
    v
Standard or Custom?
    |
    v
Which User?
    |
    v
Which Executable?
    |
    v
Script or Binary?
    |
    v
Which Config?
    |
    v
Environment File?
    |
    v
Working Directory?
    |
    v
Plugins / Helpers?
    |
    v
Any User-Writable Resource?
    |
    +---- No
    |      |
    |      v
    |   Review Hardening
    |
    +---- Yes
           |
           v
    Does Privileged Service Consume It?
           |
           +---- No -> Lower Priority
           |
           +---- Yes
                  |
                  v
            Validate Relationship
                  |
                  v
               Finding
```

---

# 183. Automated Enumeration

Tools such as LinPEAS can identify service-related candidates.

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Potential findings include:

```text
Writable service files
Interesting processes
Sudo rules
Capabilities
Cron
Credentials
Service configuration
```

Always reproduce important findings manually.

---

# 184. pspy

[pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }

pspy can be useful when short-lived privileged processes are difficult to observe.

Examples include:

```text
Periodic service scripts
Administrative maintenance
Cron
Service health checks
```

Use only where authorised.

---

# 185. Native Validation

If automation reports:

```text
Writable service script
```

validate with:

```bash
id
stat -c '%A %a %U %G %n' /path/to/script
getfacl /path/to/script
namei -l /path/to/script
systemctl cat example.service
systemctl show example.service -p User -p Group -p ExecStart
```

This creates reproducible evidence independent of the tool.

---

# 186. False Positive Example

Tool output:

```text
/opt/application/logs is writable
```

Further analysis:

```text
Service runs as application user
Directory stores only application logs
No executable or configuration is loaded from it
No privileged process consumes attacker-controlled content
```

Result:

```text
Not a privilege escalation finding
```

---

# 187. Strong Finding Example

Enumeration:

```text
Current user:
analyst

Groups:
analyst application

Service:
backup.service

Service user:
root

ExecStart:
/opt/backup/scripts/backup.sh

Permissions:
-rwxrwxr-x root application backup.sh
```

Relationship:

```text
analyst
   |
   v
application group
   |
   v
Can modify backup.sh
   |
   v
backup.service
   |
   v
Executes as root
```

This represents a meaningful privilege boundary weakness.

---

# 188. Reporting - Writable Root Service Script

## Title

```text
Standard User Can Modify Script Executed by Root Service
```

## Description

```text
A system service running with root privileges executes a script that is
writable by a group containing standard users.

A lower-privileged user can therefore modify a resource trusted by a
privileged service.
```

## Evidence

```text
Service:
backup.service

Execution identity:
root

ExecStart:
/opt/backup/scripts/backup.sh

Script owner:
root

Script group:
backup

Current user:
analyst

Current user groups:
analyst backup
```

## Impact

```text
A user with write access to the affected script may be able to influence
commands executed by the service with root privileges when the service next
executes the script.
```

## Recommendation

```text
Remove write access to the service script from unprivileged users and groups.

Restrict modification rights to trusted administrative or deployment
identities and review parent-directory permissions to prevent file
replacement.
```

---

# 189. Reporting - Writable Unit File

## Title

```text
Unprivileged User Can Modify Privileged systemd Service Configuration
```

## Description

```text
A systemd unit that executes with elevated privileges can be modified by a
lower-privileged user.

The unit configuration controls the executable and runtime properties of the
service.
```

## Impact

```text
Unauthorised modification of the unit could allow the lower-privileged user
to influence privileged execution when the service is subsequently started
or restarted.
```

## Recommendation

```text
Restrict write permissions on systemd unit files and their parent
directories to trusted administrative identities.

Review ACLs and deployment processes that may be granting unnecessary
modification rights.
```

---

# 190. Reporting - Writable Environment File

## Title

```text
Privileged Service Uses User-Writable Environment Configuration
```

## Description

```text
A privileged service loads runtime environment configuration from a file
that can be modified by a lower-privileged user.
```

## Impact

```text
Depending on the variables consumed by the application, an attacker may be
able to alter service behaviour or influence resources loaded by the
privileged process.
```

## Recommendation

```text
Restrict modification of the environment file to trusted administrative or
service-management identities.

Review the service to ensure sensitive runtime behaviour cannot be
controlled through unnecessarily broad environment configuration.
```

---

# 191. Reporting - Excessive Service Privileges

## Title

```text
Application Service Runs With Excessive Operating System Privileges
```

## Description

```text
The application service executes with privileges broader than those required
for its documented functionality.

Compromise of the service could therefore provide unnecessary access to
host resources.
```

## Recommendation

```text
Run the service using a dedicated least-privileged account where possible.

Grant only required Linux capabilities and filesystem permissions, and apply
appropriate systemd sandboxing controls after compatibility testing.
```

---

# 192. Remediation - File Permissions

For privileged service resources:

```text
Unit files
Executables
Scripts
Configuration
Environment files
Plugins
Libraries
Credentials
```

ensure:

```text
Trusted ownership
Minimum required group access
No unnecessary world write
No unnecessary user write
Secure parent directories
Appropriate ACLs
```

---

# 193. Remediation - Dedicated Users

Prefer:

```ini
[Service]
User=application
Group=application
```

when the application does not require root.

Then grant only the specific filesystem or capability access required.

Do not change production service identities without application testing.

---

# 194. Remediation - Capabilities

Instead of full root, some services can use narrowly scoped capabilities.

Conceptually:

```text
Root
  |
  v
Determine Required Privileged Operation
  |
  v
Specific Capability
  |
  v
Dedicated Service User
```

Capabilities themselves must still be carefully constrained.

---

# 195. Remediation - `NoNewPrivileges`

Where compatible:

```ini
[Service]
NoNewPrivileges=yes
```

This can prevent the service and descendants from acquiring additional privileges through certain mechanisms.

Test application functionality before deployment.

---

# 196. Remediation - Filesystem Protection

Potential systemd options include:

```ini
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
```

Actual configuration must account for directories the application legitimately needs to write.

Use:

```text
ReadWritePaths=
```

where carefully scoped exceptions are necessary.

---

# 197. Remediation - Capabilities

Example conceptual configuration:

```ini
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE
```

This may allow a non-root service to bind to privileged ports without receiving broad root privileges.

Only grant capabilities actually required.

---

# 198. Remediation - Runtime Directories

Prefer systemd-managed directories where appropriate:

```ini
RuntimeDirectory=application
StateDirectory=application
LogsDirectory=application
```

This can simplify ownership and lifecycle management.

---

# 199. Remediation - Environment Secrets

Avoid unnecessarily storing secrets in:

```text
Command-line arguments
World-readable environment files
Shell scripts
General-purpose environment variables
```

Prefer appropriate secret-management or service credential mechanisms.

---

# 200. Remediation - Plugins

For privileged applications:

```text
Plugin directories should not be writable by untrusted users.
```

Where possible:

```text
Restrict plugin installation
Validate plugin provenance
Use signed packages
Disable unused extension mechanisms
```

---

# 201. Remediation - Monitoring

Monitor changes to security-sensitive service resources:

```text
/etc/systemd/system/
/etc/init.d/
/opt/application/bin/
/opt/application/scripts/
/etc/application/
```

Relevant events can include:

```text
Unit changes
Service restarts
Executable replacement
Permission changes
Configuration modification
Unexpected enablement
```

---

# 202. Service Evidence Checklist

For every important service collect:

- [ ] Service name
- [ ] Unit path
- [ ] Service state
- [ ] Enablement state
- [ ] Execution user
- [ ] Execution group
- [ ] Main PID
- [ ] ExecStart
- [ ] ExecStartPre
- [ ] ExecStartPost
- [ ] Working directory
- [ ] Environment
- [ ] Environment files
- [ ] Executable permissions
- [ ] Script permissions
- [ ] Configuration permissions
- [ ] Parent-directory permissions
- [ ] ACLs
- [ ] Plugin directories
- [ ] Helper programs
- [ ] Network listeners
- [ ] Unix sockets
- [ ] Capabilities
- [ ] systemd hardening
- [ ] Restart permissions
- [ ] Relevant logs

---

# 203. Service Security Checklist

## Discovery

- [ ] Identify init system
- [ ] Enumerate running services
- [ ] Enumerate enabled services
- [ ] Identify failed services
- [ ] Identify custom services
- [ ] Identify network-facing services

## Identity

- [ ] Determine service user
- [ ] Determine service group
- [ ] Verify runtime process identity
- [ ] Review supplementary groups
- [ ] Identify root services

## Execution

- [ ] Review `ExecStart`
- [ ] Review `ExecStartPre`
- [ ] Review `ExecStartPost`
- [ ] Review `ExecReload`
- [ ] Review `ExecStop`
- [ ] Identify scripts
- [ ] Identify interpreters
- [ ] Identify helper programs

## Filesystem

- [ ] Unit permissions
- [ ] Executable permissions
- [ ] Script permissions
- [ ] Parent directories
- [ ] ACLs
- [ ] Working directory
- [ ] Configuration
- [ ] Environment files
- [ ] Plugin directories
- [ ] Library directories
- [ ] Temporary files

## Privilege

- [ ] Root or dedicated user
- [ ] Capabilities
- [ ] Sudo relationship
- [ ] Restart permissions
- [ ] PolicyKit
- [ ] Privileged sockets
- [ ] Device access

## Hardening

- [ ] `NoNewPrivileges`
- [ ] `PrivateTmp`
- [ ] `PrivateDevices`
- [ ] `ProtectSystem`
- [ ] `ProtectHome`
- [ ] `ProtectKernelTunables`
- [ ] `ProtectKernelModules`
- [ ] `ProtectControlGroups`
- [ ] `RestrictSUIDSGID`
- [ ] `CapabilityBoundingSet`
- [ ] `AmbientCapabilities`
- [ ] `SystemCallFilter`
- [ ] `RestrictAddressFamilies`

## Network

- [ ] Listening ports
- [ ] Bind addresses
- [ ] Authentication
- [ ] Encryption
- [ ] Firewall exposure
- [ ] Administrative interfaces
- [ ] Unix socket permissions

## Validation

- [ ] Confirm current identity
- [ ] Confirm effective write access
- [ ] Confirm privileged consumer
- [ ] Confirm execution relationship
- [ ] Avoid unnecessary restart
- [ ] Avoid production modification
- [ ] Preserve evidence

---

# 204. Quick Service Enumeration

Running services:

```bash
systemctl list-units --type=service --state=running
```

Installed:

```bash
systemctl list-unit-files --type=service
```

Failed:

```bash
systemctl --failed
```

Specific service:

```bash
systemctl status example.service
```

Configuration:

```bash
systemctl cat example.service
```

Important properties:

```bash
systemctl show example.service -p User -p Group -p ExecStart -p ExecStartPre -p ExecStartPost -p WorkingDirectory -p EnvironmentFiles -p FragmentPath
```

Security:

```bash
systemd-analyze security example.service
```

Listeners:

```bash
ss -lntup
```

---

# 205. Manual Validation Sequence

For a suspicious service:

```bash
id
```

```bash
systemctl cat example.service
```

```bash
systemctl show example.service -p User -p Group -p ExecStart -p WorkingDirectory -p EnvironmentFiles
```

Then:

```bash
stat -c '%A %a %U %G %n' /path/to/executable
```

```bash
getfacl /path/to/executable
```

```bash
namei -l /path/to/executable
```

Repeat for referenced scripts and configuration.

---

# 206. High-Value Relationship Model

The strongest service privilege escalation candidates usually look like:

```text
Lower-Privileged User
        |
        v
Has Write Access
        |
        v
Trusted Resource
        |
        v
Consumed by Service
        |
        v
Service Runs With Higher Privilege
```

Trusted resources can include:

```text
Binary
Script
Configuration
Environment
Plugin
Helper
Library
Unit file
```

---

# 207. What Not to Report Automatically

Do not automatically report:

```text
systemd is installed
A service runs as root
A service listens on a port
A service starts automatically
A service uses a shell script
A service has a configuration file
A service uses /tmp
A service has no systemd hardening score
A service has broad capabilities
A service uses an environment file
```

Each observation needs context and impact.

---

# 208. Strong Finding Model

Prefer:

```text
Current User
      |
      v
Effective Permission
      |
      v
User-Controlled Resource
      |
      v
Privileged Service
      |
      v
Execution Relationship
      |
      v
Security Boundary Crossed
```

rather than:

```text
Tool highlighted service
      |
      v
Finding
```

---

# 209. Final Testing Model

A reliable Linux service assessment follows:

```text
1. Identify the service manager.

2. Enumerate running and installed services.

3. Prioritise custom and privileged services.

4. Determine each service's runtime identity.

5. Review effective service configuration.

6. Identify every executed binary and script.

7. Identify configuration and environment files.

8. Identify working directories and runtime directories.

9. Identify helper programs and plugins.

10. Inspect executable permissions.

11. Inspect script permissions.

12. Inspect configuration permissions.

13. Inspect environment-file permissions.

14. Inspect parent-directory permissions.

15. Review ACLs.

16. Review PATH and relative command usage where relevant.

17. Review library-loading behaviour where relevant.

18. Identify sockets and network listeners.

19. Review delegated restart or management permissions.

20. Review capabilities and service privileges.

21. Review systemd sandboxing controls.

22. Correlate lower-privileged write access with privileged consumption.

23. Validate the relationship with minimal modification.

24. Avoid unnecessary service restarts.

25. Preserve reproducible evidence.

26. Determine realistic security impact.

27. Recommend remediation of the underlying trust relationship.
```

The goal is not:

```text
Find Root Service
      |
      v
Call It Vulnerable
```

The preferred model is:

```text
Service
   |
   v
Identity
   |
   v
Execution
   |
   v
Dependencies
   |
   v
Permissions
   |
   v
User Influence
   |
   v
Privilege Boundary
   |
   v
Validated Impact
```

---

# Related Notes

- [Linux](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)

---

# References

- [systemd](https://systemd.io/){ target="_blank" rel="noopener noreferrer" }
- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.unit](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.socket](https://www.freedesktop.org/software/systemd/man/latest/systemd.socket.html){ target="_blank" rel="noopener noreferrer" }
- [systemd-analyze](https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html){ target="_blank" rel="noopener noreferrer" }
- [systemd Security and Sandboxing](https://systemd.io/SECURITY/){ target="_blank" rel="noopener noreferrer" }
- [Linux Kernel Documentation](https://docs.kernel.org/){ target="_blank" rel="noopener noreferrer" }
- [capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [OpenRC](https://github.com/OpenRC/openrc){ target="_blank" rel="noopener noreferrer" }
- [D-Bus](https://www.freedesktop.org/wiki/Software/dbus/){ target="_blank" rel="noopener noreferrer" }
- [polkit](https://www.freedesktop.org/software/polkit/docs/latest/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [pspy](https://github.com/DominicBreuker/pspy){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - System Services: Service Execution](https://attack.mitre.org/techniques/T1569/002/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Create or Modify System Process: Systemd Service](https://attack.mitre.org/techniques/T1543/002/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Event Triggered Execution](https://attack.mitre.org/techniques/T1546/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Scheduled Task/Job](https://attack.mitre.org/techniques/T1053/){ target="_blank" rel="noopener noreferrer" }

---

> Use these techniques only on Linux systems you own or have explicit permission to assess. Prefer configuration, permission, and execution-chain evidence over modifying service resources. Restarting, stopping, crashing, or changing production services can affect availability and should only be performed when explicitly authorised and operationally safe.
