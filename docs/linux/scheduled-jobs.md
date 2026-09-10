---
title: Linux Scheduled Jobs
description: Practical Linux scheduled job security assessment covering cron, crontab, systemd timers, anacron, writable scripts, PATH handling, environment files, dependencies, permissions, execution context and privilege escalation analysis.
---

# Linux Scheduled Jobs

Linux systems use several mechanisms to execute commands automatically at specific times, intervals or system events.

Common mechanisms include:

```text
cron
crontab
system cron directories
anacron
systemd timers
at
application-specific schedulers
```

During an authorised security assessment, scheduled jobs are important because they can create a trust relationship between a lower-privileged user and a higher-privileged execution context.

The key question is not:

> Does a root cron job exist?

The key question is:

> Can a lower-privileged user influence something that a privileged scheduled job executes, loads, reads or trusts?

A useful model is:

```text
Scheduled Job
      |
      v
Execution Identity
      |
      v
Command / Script
      |
      +---- Executable
      +---- Arguments
      +---- Configuration
      +---- Environment
      +---- Helper scripts
      +---- PATH
      +---- Working directory
      +---- Input files
      |
      v
Can Lower-Privileged User Influence It?
      |
   +--+--+
   |     |
  No    Yes
   |     |
   v     v
Record   Validate Security Boundary
```

A privileged scheduled job is not automatically a vulnerability.

The security issue arises when an untrusted principal can influence resources consumed by that privileged execution.

!!! warning "Authorised Security Testing"

    Perform scheduled-job testing only on systems you own or have explicit permission to assess. Prefer read-only inspection and controlled test files. Do not modify production scripts, cron files, systemd units, binaries or configuration merely to demonstrate that they are writable.

---

# 1. Scheduled Execution Mechanisms

Linux systems can schedule execution through several mechanisms.

Common examples include:

| Mechanism | Typical Purpose |
|---|---|
| cron | Repeated scheduled execution |
| user crontab | Per-user scheduled commands |
| `/etc/crontab` | System-wide cron configuration |
| `/etc/cron.d/` | Additional system cron definitions |
| `/etc/cron.hourly/` | Periodic hourly jobs |
| `/etc/cron.daily/` | Periodic daily jobs |
| `/etc/cron.weekly/` | Periodic weekly jobs |
| `/etc/cron.monthly/` | Periodic monthly jobs |
| anacron | Periodic jobs that can run after missed schedules |
| systemd timers | systemd-based scheduled activation |
| at | One-time scheduled execution |

Applications can also implement their own schedulers.

Examples include:

```text
Backup software

Monitoring agents

Deployment systems

Database maintenance

Web applications

Container platforms

Enterprise management agents
```

A complete assessment should therefore not assume that all scheduled execution appears in `crontab`.

---

# 2. Establish the Current Context

Start by identifying the current user.

```bash
whoami
id
groups
```

Record:

```text
Username

UID

Primary GID

Supplementary groups

sudo permissions
```

This is necessary because filesystem access to scheduled-job resources may derive from:

```text
Owner permissions

Group permissions

Supplementary groups

POSIX ACLs

sudo delegation
```

---

# 3. Identify the Distribution and Init System

Basic operating system information:

```bash
cat /etc/os-release
```

Determine the process running as PID 1:

```bash
ps -p 1 -o pid,comm,args
```

On many modern Linux systems this will be:

```text
systemd
```

This matters because systemd timers may be as important as traditional cron jobs.

Do not assume every Linux distribution uses the same scheduling mechanisms or directory layout.

---

# 4. Check the cron Service

Depending on the distribution, the service may be called:

```text
cron
```

or:

```text
crond
```

Check both where appropriate:

```bash
systemctl status cron --no-pager 2>/dev/null
systemctl status crond --no-pager 2>/dev/null
```

Process enumeration can provide additional context:

```bash
ps aux | grep -E '[c]ron|[c]rond'
```

Do not conclude that scheduled execution is absent simply because one expected service name does not exist.

---

# 5. Current User Crontab

List the current user's crontab:

```bash
crontab -l
```

Representative output:

```text
*/15 * * * * /home/analyst/bin/sync.sh
```

Record:

```text
Schedule

Command

Arguments

Referenced files

Environment

Execution identity
```

A user's own cron job normally executes under that same user's security context.

It therefore does not automatically create privilege escalation.

It may still expose:

```text
Credentials

Interesting scripts

Network destinations

Application configuration

Operational information
```

---

# 6. System-Wide Crontab

Inspect:

```bash
cat /etc/crontab
```

A system-wide crontab can include an explicit user field.

Representative example:

```text
17 * * * * root cd / && run-parts --report /etc/cron.hourly
```

The structure commonly resembles:

```text
minute
hour
day of month
month
day of week
user
command
```

Example:

```text
*/5 * * * * root /opt/application/backup.sh
```

The important information is:

```text
Schedule:
Every five minutes

Execution user:
root

Command:
/opt/application/backup.sh
```

The next step is not to modify the script.

The next step is to inspect its trust chain.

---

# 7. Cron Time Fields

Traditional cron schedules commonly use five time fields:

```text
* * * * *
| | | | |
| | | | +---- Day of week
| | | +------ Month
| | +-------- Day of month
| +---------- Hour
+------------ Minute
```

Examples:

```text
0 2 * * *       Daily at 02:00
*/10 * * * *    Every 10 minutes
0 0 * * 0       Weekly on Sunday at midnight
```

Exact behavior can vary with the cron implementation and environment.

During a security assessment, the schedule is important because it helps establish whether a potentially vulnerable job is active and how frequently the privileged consumer runs.

---

# 8. `/etc/cron.d`

Additional system cron jobs may exist in:

```text
/etc/cron.d/
```

Enumerate:

```bash
ls -la /etc/cron.d
```

Inspect metadata:

```bash
stat /etc/cron.d
```

Where files are readable:

```bash
grep -R -n -v '^[[:space:]]*#' /etc/cron.d 2>/dev/null
```

This can reveal:

```text
Application maintenance

Backup jobs

Package maintenance

Monitoring jobs

Custom enterprise scripts
```

Review each interesting command and its execution identity.

---

# 9. Periodic Cron Directories

Common periodic directories include:

```text
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/
```

Enumerate:

```bash
ls -la /etc/cron.hourly 2>/dev/null
ls -la /etc/cron.daily 2>/dev/null
ls -la /etc/cron.weekly 2>/dev/null
ls -la /etc/cron.monthly 2>/dev/null
```

Inspect directory permissions:

```bash
stat /etc/cron.hourly 2>/dev/null
stat /etc/cron.daily 2>/dev/null
stat /etc/cron.weekly 2>/dev/null
stat /etc/cron.monthly 2>/dev/null
```

Unexpected write access to a privileged scheduler directory is security sensitive.

Do not create a script in such a directory merely to prove execution.

---

# 10. run-parts

Some cron configurations use:

```text
run-parts
```

to execute files from a directory.

Example:

```text
run-parts /etc/cron.daily
```

If `run-parts` is involved, determine:

```text
Which directory is processed?

Which naming rules apply?

Who owns the directory?

Who can create files there?

Who can modify existing files?

Which execution identity is used?
```

Do not assume that every file in the directory will necessarily execute.

`run-parts` behavior and filename rules can vary by implementation and options.

---

# 11. Inspect Cron Resource Permissions

For an interesting cron script:

```text
/opt/application/backup.sh
```

inspect:

```bash
stat /opt/application/backup.sh
```

```bash
getfacl /opt/application/backup.sh
```

```bash
namei -l /opt/application/backup.sh
```

Check effective write access:

```bash
if test -w /opt/application/backup.sh; then
    echo "[+] Current context reports write access"
else
    echo "[-] Current context does not report write access"
fi
```

Do not modify the production script.

See [Linux Filesystem Permissions](filesystem-permissions.md).

---

# 12. Parent Directory Permissions

A script can be protected while its parent directory is writable.

Example:

```text
-rwxr-xr-x root root /opt/application/backup.sh
```

This does not complete the assessment.

Inspect:

```bash
namei -l /opt/application/backup.sh
```

Example path:

```text
/
└── opt/
    └── application/
        └── backup.sh
```

The complete security relationship depends on every relevant path component.

---

# 13. POSIX ACLs

Traditional mode bits may not represent all effective access.

Inspect:

```bash
getfacl /opt/application/backup.sh
```

and:

```bash
getfacl /opt/application
```

Look for:

```text
Named user entries

Named group entries

ACL mask

Default ACLs
```

An apparently protected root-owned script can still be writable through an ACL.

---

# 14. Cron Script Dependencies

Do not analyse only the top-level script.

Suppose:

```text
/etc/crontab
      |
      v
/opt/application/backup.sh
      |
      +---- /opt/application/config.ini
      |
      +---- /opt/application/helpers/archive.sh
      |
      +---- backup-tool
      |
      +---- /tmp/application-state
```

Each dependency may affect the trust relationship.

Review:

```text
Helper scripts

Configuration files

Environment files

External commands

Input files

Temporary resources

Plugins

Modules

Output paths
```

A protected cron script can still depend on an untrusted resource.

---

# 15. Inspect Scripts Safely

Where authorised and readable:

```bash
sed -n '1,200p' /opt/application/backup.sh
```

or:

```bash
less /opt/application/backup.sh
```

Review for:

```text
Relative command execution

User-controlled paths

Writable configuration

Temporary files

Wildcards

External scripts

Environment variables

Network resources

Credential material
```

Do not unnecessarily copy sensitive values into notes or reports.

---

# 16. PATH in Cron Jobs

Cron jobs can execute with a different environment from an interactive shell.

A system crontab may explicitly define:

```text
PATH=...
```

Do not assume that:

```bash
echo "$PATH"
```

shows the PATH used by the scheduled job.

The important question is:

> Which PATH is effective when the scheduler executes the command?

Inspect the scheduler configuration and the script itself.

---

# 17. Relative Command Execution

Suppose a privileged scheduled script contains:

```bash
backup-tool --run
```

instead of:

```bash
/usr/local/sbin/backup-tool --run
```

This requires further analysis.

Determine:

```text
Effective PATH

Location of legitimate backup-tool

Permissions on PATH directories

Command lookup order

Execution identity
```

A relative command is not automatically exploitable.

A meaningful condition generally requires:

```text
Privileged Scheduled Job
        |
        v
Relative Command
        |
        v
Effective PATH
        |
        v
Writable Earlier Directory
        |
        v
Attacker Can Influence Resolution
```

Do not place a replacement executable in a production PATH merely to prove the condition.

---

# 18. Inspect PATH Directories

If a scheduled job defines:

```text
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin
```

inspect relevant directories:

```bash
for d in /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin; do
    stat -c '%A %a %U %G %n' "$d" 2>/dev/null
done
```

Where ACLs are relevant:

```bash
getfacl /usr/local/bin
```

The assessment should establish whether the current user has effective write access to a directory that participates in privileged command resolution.

---

# 19. Environment Variables

Cron jobs can define environment variables in configuration.

Examples may include:

```text
PATH
SHELL
HOME
MAILTO
```

Application-specific variables can also affect execution.

When reviewing a privileged job, determine whether user-controlled environment data influences:

```text
Executable lookup

Configuration location

Plugin loading

Module loading

Temporary paths

Application behavior
```

Do not assume that the interactive shell environment is inherited by cron.

---

# 20. SHELL

Cron configurations can specify a shell:

```text
SHELL=/bin/sh
```

or another shell depending on configuration.

The shell can affect:

```text
Syntax

Expansion

Command interpretation

Environment handling
```

When analysing a complex cron command, identify which interpreter actually processes it.

---

# 21. Working Directory Assumptions

Scripts may assume a particular current working directory.

For example:

```bash
./helper.sh
```

or:

```bash
cat config.ini
```

Such relative references require investigation.

Determine:

```text
What is the working directory?

Who controls it?

Can the referenced file be influenced?

Does the script change directories first?

Is the path predictable?
```

A relative path alone does not prove a vulnerability.

---

# 22. Wildcards in Scheduled Jobs

Wildcards can appear in scripts executed by schedulers.

Examples:

```bash
some-command *
```

The security impact depends entirely on how the target command interprets filenames and options.

Assessment questions include:

```text
Which directory is being processed?

Who can create files there?

Can filenames be interpreted as command options?

Does the program support security-sensitive options?

Which user executes the job?
```

Do not conclude:

```text
Wildcard = Privilege Escalation
```

without validating the exact utility and context.

---

# 23. Writable Configuration Files

Suppose a root cron job executes:

```text
/opt/reports/generate
```

The binary is protected, but it reads:

```text
/opt/reports/config.yml
```

Inspect:

```bash
stat /opt/reports/config.yml
getfacl /opt/reports/config.yml
namei -l /opt/reports/config.yml
```

The relevant relationship may be:

```text
Low-Privileged User
        |
        v
Writable Configuration
        |
        v
Root Scheduled Process
        |
        v
Configuration Controls Security-Sensitive Behaviour
```

Do not modify the configuration until the impact and authorisation requirements are understood.

---

# 24. Writable Helper Scripts

A protected top-level script can call another script.

Example:

```bash
#!/bin/sh
/opt/application/helpers/archive.sh
```

Inspect:

```bash
stat /opt/application/helpers/archive.sh
getfacl /opt/application/helpers/archive.sh
namei -l /opt/application/helpers/archive.sh
```

Follow the execution chain until the relevant trusted resources are understood.

---

# 25. Symbolic Links

Resolve symbolic links:

```bash
readlink -f /opt/application/backup.sh
```

Then inspect:

```bash
namei -l /opt/application/backup.sh
```

Questions include:

```text
Is the scheduled resource a symlink?

Who controls the link?

Who controls the target?

Can the target path change?

Which process follows it?

Which protections apply?
```

A symbolic link is not inherently vulnerable.

---

# 26. Temporary Files

Scheduled scripts may create temporary resources.

Examples:

```text
/tmp/report.tmp

/var/tmp/backup.list
```

Security significance depends on:

```text
Creation method

Filename predictability

Permissions

Directory sticky bit

Symlink handling

Existing-file handling

Execution identity

Kernel protections
```

Do not treat every privileged use of `/tmp` as vulnerable.

---

# 27. Sensitive Output Files

Scheduled jobs may create:

```text
Backups

Reports

Database exports

Logs

Archives

Credential snapshots

Configuration exports
```

Inspect resulting permissions where relevant.

Example:

```bash
stat /var/backups/application.tar
```

Potential issues include:

```text
Sensitive backup readable by untrusted users

Output file writable by untrusted users

Credentials included in logs

Private data stored in shared locations
```

Scheduled-job assessment is therefore not limited to privilege escalation.

---

# 28. Credentials in Scheduled Jobs

Scheduled jobs may contain or reference credentials.

Potential locations include:

```text
Cron command lines

Environment files

Configuration files

Backup scripts

Database scripts

Cloud CLI configuration

Application-specific secrets
```

Do not unnecessarily expose or copy secrets.

Record only the evidence required to demonstrate the issue.

See [Linux Credentials](credentials.md).

---

# 29. User Crontabs

User crontabs are commonly stored internally by the cron implementation rather than being intended for direct manual editing.

Enumerate the current user's configured jobs with:

```bash
crontab -l
```

Administrators can typically inspect another user's crontab using appropriate privileges:

```bash
crontab -u username -l
```

During a non-root assessment, do not attempt to bypass access controls to inspect another user's scheduled jobs.

Use accessible system configuration and authorised privilege paths.

---

# 30. Cron Spool Directories

Cron spool locations vary by distribution and implementation.

Potential locations can include paths under:

```text
/var/spool/
```

Do not assume a specific spool path is universal.

Where accessible, inspect metadata rather than modifying files.

The important question is whether an untrusted principal can influence a scheduler-controlled job definition.

---

# 31. anacron

`anacron` is designed for periodic jobs that do not require a machine to remain continuously running.

Potential configuration includes:

```text
/etc/anacrontab
```

Where present:

```bash
cat /etc/anacrontab
```

Inspect referenced commands and directories using the same trust-chain methodology used for cron.

Questions include:

```text
Which user ultimately executes the job?

Which command runs?

Which files are trusted?

Can the current user influence them?
```

---

# 32. systemd Timers

Modern Linux systems commonly use systemd timers.

Enumerate:

```bash
systemctl list-timers --all
```

Representative columns may include:

```text
NEXT

LEFT

LAST

PASSED

UNIT

ACTIVATES
```

Example relationship:

```text
backup.timer
      |
      v
backup.service
      |
      v
ExecStart=/opt/application/backup.sh
      |
      v
Execution Identity
      |
      v
Filesystem Trust Chain
```

Timers should be correlated with the service units they activate.

---

# 33. Inspect a systemd Timer

For a timer:

```text
backup.timer
```

inspect:

```bash
systemctl status backup.timer --no-pager
```

and:

```bash
systemctl cat backup.timer
```

Look for timer directives such as:

```text
OnCalendar=

OnBootSec=

OnUnitActiveSec=

OnUnitInactiveSec=

Unit=
```

The timer determines when activation occurs.

The associated service normally determines what executes.

---

# 34. Identify the Activated Service

A timer can activate a corresponding service.

Inspect:

```bash
systemctl cat backup.service
```

Relevant directives include:

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

These directives help establish the execution and trust context.

---

# 35. systemd Execution Identity

If no explicit:

```text
User=
```

is configured for a system service, do not blindly assume the identity without confirming the unit context and systemd semantics.

Where a `User=` directive exists, record it.

Example:

```text
User=backup
Group=backup
```

Then assess that account's privileges and access.

A service account may still provide a meaningful security boundary even when it is not root.

---

# 36. systemd Environment Files

A service can load:

```text
EnvironmentFile=
```

Example:

```text
EnvironmentFile=/etc/application/backup.env
```

Inspect:

```bash
stat /etc/application/backup.env
getfacl /etc/application/backup.env
namei -l /etc/application/backup.env
```

If the file affects privileged execution and is writable by a lower-privileged user, further validation is required.

---

# 37. systemd Working Directory

A service can specify:

```text
WorkingDirectory=
```

This matters when the executable or scripts use relative paths.

Example:

```text
WorkingDirectory=/opt/application
```

If a script then references:

```text
./helper.sh
```

inspect:

```text
/opt/application/helper.sh
```

and the directory itself.

---

# 38. systemd Unit File Permissions

Determine the source unit file:

```bash
systemctl show -p FragmentPath backup.service
```

Example:

```text
FragmentPath=/etc/systemd/system/backup.service
```

Inspect:

```bash
stat /etc/systemd/system/backup.service
getfacl /etc/systemd/system/backup.service
namei -l /etc/systemd/system/backup.service
```

Unexpected lower-privileged write access to a privileged unit file is security sensitive.

Do not modify the unit during routine validation.

---

# 39. systemd Drop-Ins

systemd units can be extended or overridden through drop-in configuration.

Display the complete effective unit:

```bash
systemctl cat backup.service
```

This is preferable to inspecting only one file because it can show applicable drop-ins.

Potential drop-in directories may resemble:

```text
backup.service.d/
```

Inspect any discovered files and directories for ownership and permissions.

---

# 40. User systemd Timers

Users can have their own systemd units and timers.

Where applicable:

```bash
systemctl --user list-timers --all
```

User-level timers normally execute within the user's own context.

They can still reveal:

```text
Credentials

Application configuration

Scripts

Network destinations

Operational workflows
```

Do not confuse user timers with system-level privileged timers.

---

# 41. at Jobs

The `at` facility can schedule one-time execution.

Check whether the command exists:

```bash
command -v at
```

List the current user's queued jobs:

```bash
atq
```

Depending on permissions and implementation, users generally see jobs they are authorised to inspect.

Do not assume that an empty `atq` means no scheduled execution exists elsewhere on the system.

---

# 42. Scheduler Access Controls

Some scheduler implementations can use files controlling which users may schedule jobs.

Examples can include:

```text
/etc/cron.allow

/etc/cron.deny

/etc/at.allow

/etc/at.deny
```

Where present:

```bash
ls -l /etc/cron.allow /etc/cron.deny /etc/at.allow /etc/at.deny 2>/dev/null
```

Their semantics depend on the relevant scheduler implementation.

Do not interpret these files without understanding the local implementation.

---

# 43. Application-Specific Schedulers

Not all scheduled execution is controlled by operating-system cron or systemd.

Applications may maintain schedules internally.

Examples include:

```text
Backup platforms

CI/CD agents

Database maintenance systems

Web applications

Monitoring software

Configuration-management platforms
```

Clues can appear in:

```text
Running processes

Application configuration

Logs

Service definitions

Web interfaces

Database tables
```

During assessment, consider whether the host role suggests another scheduling mechanism.

---

# 44. Containers and Scheduled Jobs

Containerised environments can complicate scheduler analysis.

A cron process observed inside a container may execute only within that container's namespace.

Determine:

```text
Am I on the host or inside a container?

Which filesystem is visible?

Which UID namespace applies?

Which scheduler owns the job?

Are host directories mounted?

Does the job interact with the host?
```

Do not report a container-local root job as host privilege escalation without demonstrating the actual boundary.

---

# 45. Mount Context

If a scheduled resource resides on another filesystem, inspect:

```bash
findmnt -T /opt/application/backup.sh
```

This can reveal:

```text
Filesystem

Mount point

Source

Mount options
```

Relevant options may include:

```text
ro

rw

noexec

nosuid
```

Mount options can affect execution but should not be interpreted as universal security guarantees.

---

# 46. Mandatory Access Controls

SELinux or AppArmor can affect scheduled execution.

SELinux state:

```bash
getenforce 2>/dev/null
```

AppArmor status:

```bash
aa-status 2>/dev/null
```

A filesystem permission relationship may still be constrained by mandatory access control.

Assessment should therefore distinguish:

```text
Unix permission allows operation
```

from:

```text
Effective security policy allows operation
```

See [Linux Security Controls](security-controls.md).

---

# 47. Logging Cron Activity

Logging varies by distribution and configuration.

On systemd-based systems, useful searches can include:

```bash
journalctl --no-pager | grep -i cron
```

Where a specific service exists:

```bash
journalctl -u cron --no-pager 2>/dev/null
```

or:

```bash
journalctl -u crond --no-pager 2>/dev/null
```

Traditional log locations vary.

Do not assume:

```text
/var/log/cron
```

or another particular file exists on every system.

---

# 48. Logging systemd Timers

Inspect a timer:

```bash
journalctl -u backup.timer --no-pager
```

Inspect the activated service:

```bash
journalctl -u backup.service --no-pager
```

This can help establish:

```text
Whether the job is active

When it last ran

Whether execution succeeded

Whether failures occurred
```

Logging evidence can strengthen the conclusion that a potentially vulnerable scheduled job is actually in use.

---

# 49. Identify Recently Executed Jobs

Useful evidence may come from:

```text
Journal entries

Application logs

Output files

File modification times

Service state

Timer state
```

Do not rely on timestamps alone to prove that a particular process created a file.

Correlate multiple sources where possible.

---

# 50. Practical Validation - Writable Root Cron Script

## Scenario

The system-wide crontab contains:

```text
*/5 * * * * root /opt/vendor/backup.sh
```

## Step 1 - Establish Identity

```bash
id
```

## Step 2 - Record the Job

```bash
grep -n '/opt/vendor/backup.sh' /etc/crontab /etc/cron.d/* 2>/dev/null
```

## Step 3 - Inspect the Script

```bash
stat /opt/vendor/backup.sh
```

```bash
getfacl /opt/vendor/backup.sh
```

## Step 4 - Inspect the Complete Path

```bash
namei -l /opt/vendor/backup.sh
```

## Step 5 - Check Effective Write Access

```bash
if test -w /opt/vendor/backup.sh; then
    echo "[+] Current context reports write access"
else
    echo "[-] Current context does not report write access"
fi
```

Do not modify the script.

---

# 51. Representative Positive Result

Suppose the evidence shows:

```text
Current user:
analyst

Groups:
analyst developers

Scheduled job:
*/5 * * * * root /opt/vendor/backup.sh

Script:
-rwxrwxr-x root developers /opt/vendor/backup.sh
```

The relationship is:

```text
analyst
   |
   v
developers
   |
   v
Write Permission
   |
   v
/opt/vendor/backup.sh
   |
   v
cron
   |
   v
root
```

This provides strong evidence of an unintended privilege boundary.

The script does not need to be modified to establish the core issue.

---

# 52. Practical Validation - Writable Dependency

## Scenario

The scheduled script itself is protected:

```text
-rwxr-xr-x root root /opt/vendor/backup.sh
```

The script reads:

```text
/opt/vendor/backup.conf
```

Inspect:

```bash
stat /opt/vendor/backup.conf
getfacl /opt/vendor/backup.conf
namei -l /opt/vendor/backup.conf
```

Suppose:

```text
-rw-rw-r-- root developers /opt/vendor/backup.conf
```

and the current user belongs to:

```text
developers
```

The assessment must now determine what the configuration controls.

The relevant chain is:

```text
analyst
   |
   v
Writable Configuration
   |
   v
Protected backup.sh
   |
   v
Root Cron Execution
```

Whether this becomes exploitable depends on the configuration semantics.

---

# 53. Practical Validation - systemd Timer

## Scenario

Enumeration identifies:

```text
reports.timer
```

## Step 1 - Inspect Timer

```bash
systemctl cat reports.timer
```

## Step 2 - Inspect Service

```bash
systemctl cat reports.service
```

## Step 3 - Determine Unit Path

```bash
systemctl show -p FragmentPath reports.service
```

## Step 4 - Inspect Execution Resources

Suppose:

```text
ExecStart=/opt/reports/generate.sh
```

Inspect:

```bash
stat /opt/reports/generate.sh
getfacl /opt/reports/generate.sh
namei -l /opt/reports/generate.sh
```

## Step 5 - Determine Execution Context

Review:

```text
User=
Group=
```

and the effective system service context.

## Step 6 - Correlate Logs

```bash
journalctl -u reports.timer --no-pager
journalctl -u reports.service --no-pager
```

This creates a defensible evidence chain without modifying the scheduled resource.

---

# 54. Representative Negative Result

Suppose:

```text
root /usr/local/sbin/security-maintenance
```

runs daily.

Further analysis shows:

```text
Executable is root-owned.

Executable is not writable by unprivileged users.

Parent directories are protected.

Configuration is protected.

Helper scripts are protected.

PATH contains only protected directories.

No user-controlled inputs were identified.

Job is operating as intended.
```

A reasonable conclusion is:

```text
A privileged scheduled job was identified and reviewed. No lower-privileged
control over the job or its trusted dependencies was identified under the
assessed configuration.
```

The existence of the root job should not be reported as a vulnerability.

---

# 55. False Positives

Common false positives include:

```text
Root cron job with fully protected resources

User-owned cron job running as the same user

Writable output directory with no influence over execution

World-writable /tmp use with safe temporary-file handling

Inactive cron configuration

Disabled systemd timer

Relative path where effective PATH is fully protected

Wildcard with no security-sensitive interpretation

Writable configuration that cannot alter privileged behavior

Container-local scheduler mistaken for host scheduler
```

Always validate the complete trust relationship.

---

# 56. Automated Enumeration

Automated Linux enumeration tools can identify scheduled-job candidates.

Examples include:

```text
LinPEAS

LinEnum

linux-smart-enumeration
```

These can highlight:

```text
Cron entries

Writable scripts

Writable directories

systemd timers

Interesting service files

Permissions

Capabilities
```

Use automated output as a candidate generator.

```text
Automated Detection
       |
       v
Candidate Scheduled Job
       |
       v
Manual Inspection
       |
       v
Execution Identity
       |
       v
Dependency Analysis
       |
       v
Permission Validation
       |
       v
Security Conclusion
```

---

# 57. Targeted Scheduled-Job Collection

A concise read-only collection can include:

```bash
echo '=== IDENTITY ==='
id

echo
echo '=== USER CRONTAB ==='
crontab -l 2>/dev/null || true

echo
echo '=== SYSTEM CRONTAB ==='
cat /etc/crontab 2>/dev/null || true

echo
echo '=== CRON.D ==='
grep -R -n -v '^[[:space:]]*#' /etc/cron.d 2>/dev/null || true

echo
echo '=== SYSTEMD TIMERS ==='
systemctl list-timers --all --no-pager 2>/dev/null || true

echo
echo '=== AT QUEUE ==='
atq 2>/dev/null || true
```

This provides a useful starting point without modifying system state.

---

# 58. Evidence Collection

For each potentially significant scheduled-job finding, record:

```text
Hostname

Distribution

Current user

UID

GID

Groups

Scheduler type

Job name

Schedule

Execution identity

Command

Arguments

Executable path

Script path

Configuration files

Environment files

Helper scripts

Owner

Group

Permissions

ACLs

Parent directory permissions

Mount context

Relevant security controls

Last observed execution

Validation method
```

Evidence should demonstrate the relationship rather than simply listing files.

---

# 59. Evidence Chain

A strong scheduled-job finding normally demonstrates:

```text
1. The scheduled job exists.

2. The scheduled job is active or relevant.

3. The execution identity is privileged relative to the tester.

4. A resource used by the job is controllable by the tester.

5. The resource can influence the privileged operation.

6. The condition crosses an intended security boundary.
```

If one of these components is missing, additional validation may be required.

---

# 60. Reporting

Avoid:

> A root cron job exists.

Avoid:

> `/opt/vendor/backup.sh` is writable.

Prefer:

> A system-wide cron job executes `/opt/vendor/backup.sh` as root every five minutes. The script is writable by the `developers` group, and the assessed user is a member of that group. This allows a lower-privileged user to influence code that is subsequently executed with root privileges.

This explains:

```text
Scheduler

Frequency

Execution identity

Controllable resource

Current user's access

Security impact
```

---

# 61. Example Finding

## Observation

A root cron job executes a script writable by a non-administrative group.

## Scheduled Job

```text
*/5 * * * * root /opt/vendor/backup.sh
```

## Current User

```text
analyst
```

## Relevant Group

```text
developers
```

## Resource

```text
/opt/vendor/backup.sh
```

## Permission

```text
-rwxrwxr-x root developers
```

## Security Relationship

```text
analyst
   |
   v
developers
   |
   v
Write Access
   |
   v
backup.sh
   |
   v
cron
   |
   v
root
```

## Impact

The current user can influence code consumed by a scheduled process executing with a higher security context.

## Recommendation

Restrict modification of the script and all trusted dependencies to appropriate administrative principals.

---

# 62. Remediation

Scheduled-job remediation should address the root trust relationship.

Potential measures include:

```text
Protect scheduled scripts

Protect executables

Protect configuration files

Protect environment files

Protect helper scripts

Protect parent directories

Remove unnecessary group write permissions

Remove unnecessary ACL entries

Use absolute executable paths

Use controlled PATH values

Avoid unsafe temporary-file handling

Avoid unnecessary wildcard processing

Use dedicated service accounts

Apply least privilege
```

Do not simply change one file's mode if another writable dependency remains.

---

# 63. Protect the Entire Execution Chain

A secure design should resemble:

```text
Privileged Scheduler
        |
        v
Protected Job Definition
        |
        v
Protected Script / Binary
        |
        v
Protected Configuration
        |
        v
Protected Dependencies
        |
        v
Controlled Inputs
```

Protecting only the top-level executable is insufficient when it loads writable dependencies.

---

# 64. Use Least Privilege

A scheduled task should run with the minimum identity required.

Instead of:

```text
root
```

consider whether a dedicated service account can perform the required operation.

Example:

```text
backup-agent
```

with access only to:

```text
Required source data

Required backup destination

Required configuration
```

Reducing execution privilege can reduce the impact of a compromised scheduled job.

---

# 65. Separate Writable Data from Executable Code

Avoid designs where a privileged scheduler executes code from directories intended to be writable by application users.

Prefer separation such as:

```text
/opt/vendor/bin/
    |
    +---- Administrator controlled
    +---- Executable code

/var/lib/vendor/
    |
    +---- Application runtime data
    +---- Writable by service account
```

This reduces dangerous trust relationships.

---

# 66. Retesting

After remediation, repeat the original assessment.

For cron:

```bash
cat /etc/crontab
```

```bash
grep -R -n -v '^[[:space:]]*#' /etc/cron.d 2>/dev/null
```

For systemd:

```bash
systemctl list-timers --all
systemctl cat affected.timer
systemctl cat affected.service
```

Then inspect the resource:

```bash
stat /path/to/resource
getfacl /path/to/resource
namei -l /path/to/resource
```

Confirm that the original lower-privileged user can no longer influence the trusted resource.

Where appropriate, confirm the legitimate scheduled operation still functions.

---

# Scheduled Job Assessment Checklist

## Context

- [ ] Identify current user
- [ ] Record UID and GID
- [ ] Review supplementary groups
- [ ] Review sudo permissions
- [ ] Identify distribution
- [ ] Identify init system

## cron

- [ ] Review current user crontab
- [ ] Review `/etc/crontab`
- [ ] Review `/etc/cron.d/`
- [ ] Review periodic cron directories
- [ ] Identify execution users
- [ ] Identify custom scripts
- [ ] Identify application-specific jobs

## anacron

- [ ] Determine whether anacron is used
- [ ] Review `/etc/anacrontab` where present
- [ ] Follow referenced commands
- [ ] Determine execution context

## systemd Timers

- [ ] Enumerate all timers
- [ ] Identify activated services
- [ ] Review timer configuration
- [ ] Review service configuration
- [ ] Review `User=`
- [ ] Review `Group=`
- [ ] Review `ExecStart=`
- [ ] Review `EnvironmentFile=`
- [ ] Review `WorkingDirectory=`
- [ ] Review drop-ins

## at

- [ ] Determine whether `at` is available
- [ ] Review current user's queue
- [ ] Review scheduler access controls where relevant

## Filesystem

- [ ] Inspect scheduled executable
- [ ] Inspect scripts
- [ ] Inspect owner and group
- [ ] Inspect permissions
- [ ] Inspect ACLs
- [ ] Inspect parent directories
- [ ] Resolve symbolic links
- [ ] Review mount context

## Dependencies

- [ ] Review helper scripts
- [ ] Review configuration files
- [ ] Review environment files
- [ ] Review external commands
- [ ] Review plugins or modules
- [ ] Review temporary files
- [ ] Review input files
- [ ] Review output files

## PATH

- [ ] Identify effective scheduled-job PATH
- [ ] Identify relative commands
- [ ] Review command lookup order
- [ ] Inspect relevant PATH directories
- [ ] Confirm whether current user can influence resolution

## Security Controls

- [ ] Consider SELinux
- [ ] Consider AppArmor
- [ ] Consider mount options
- [ ] Consider containers and namespaces
- [ ] Review relevant logging

## Validation

- [ ] Confirm the job exists
- [ ] Confirm the job is relevant or active
- [ ] Confirm execution identity
- [ ] Confirm user control over a trusted resource
- [ ] Confirm the resource affects privileged behavior
- [ ] Identify false positives
- [ ] Avoid destructive proof
- [ ] Clean up controlled test artifacts

## Evidence

- [ ] Capture scheduler configuration
- [ ] Capture execution identity
- [ ] Capture resource metadata
- [ ] Capture ACLs
- [ ] Capture complete path permissions
- [ ] Capture relevant service configuration
- [ ] Capture logs where useful
- [ ] Record validation procedure

## Reporting

- [ ] Explain scheduler
- [ ] Explain execution identity
- [ ] Explain controllable resource
- [ ] Explain current user's access
- [ ] Explain trust relationship
- [ ] Explain security impact
- [ ] Recommend root-cause remediation
- [ ] Define retest procedure

---

# Quick Scheduled Job Assessment Workflow

```text
Enumerate Schedulers
        |
        +---- cron
        |
        +---- anacron
        |
        +---- systemd timers
        |
        +---- at
        |
        +---- application schedulers
        |
        v
Identify Interesting Job
        |
        v
Determine Execution Identity
        |
        v
Identify Command / Script
        |
        v
Inspect Permissions
        |
        v
Inspect Parent Directories
        |
        v
Inspect Dependencies
        |
        v
Inspect PATH / Environment
        |
        v
Can Current User Influence Anything?
        |
     +--+--+
     |     |
    No    Yes
     |     |
     v     v
  Record   Does Privileged Job Consume It?
              |
           +--+--+
           |     |
          No    Yes
           |     |
           v     v
        Record  Validate
                   |
                   v
                Evidence
                   |
                   v
                 Report
```

---

# Command Reference

## Identity

```bash
whoami
id
groups
```

## Current User Crontab

```bash
crontab -l
```

## System Crontab

```bash
cat /etc/crontab
```

## `/etc/cron.d`

```bash
ls -la /etc/cron.d
grep -R -n -v '^[[:space:]]*#' /etc/cron.d 2>/dev/null
```

## Periodic Cron Directories

```bash
ls -la /etc/cron.hourly 2>/dev/null
ls -la /etc/cron.daily 2>/dev/null
ls -la /etc/cron.weekly 2>/dev/null
ls -la /etc/cron.monthly 2>/dev/null
```

## anacron

```bash
cat /etc/anacrontab 2>/dev/null
```

## systemd Timers

```bash
systemctl list-timers --all
```

## Timer Details

```bash
systemctl status example.timer --no-pager
systemctl cat example.timer
```

## Activated Service

```bash
systemctl cat example.service
systemctl show -p FragmentPath example.service
```

## User Timers

```bash
systemctl --user list-timers --all
```

## at Jobs

```bash
atq
```

## File Metadata

```bash
stat /path/to/resource
```

## ACL

```bash
getfacl /path/to/resource
```

## Complete Path

```bash
namei -l /path/to/resource
```

## Symbolic Link

```bash
readlink -f /path/to/resource
```

## Mount Context

```bash
findmnt -T /path/to/resource
```

## Effective Write Test

```bash
test -w /path/to/resource && echo "Writable"
```

## Cron Logs

```bash
journalctl -u cron --no-pager 2>/dev/null
journalctl -u crond --no-pager 2>/dev/null
```

## Timer Logs

```bash
journalctl -u example.timer --no-pager
journalctl -u example.service --no-pager
```

---

# Scheduled Job Testing Mindset

Do not think:

```text
Root Cron Job = Vulnerability

Writable Directory = Root

Relative Command = PATH Hijack

Wildcard = Exploitable

/tmp = Vulnerable

systemd Timer = Privilege Escalation

Root-Owned Script = Secure
```

Instead think:

```text
What Is Scheduled?
        |
        v
Who Executes It?
        |
        v
Which Command Runs?
        |
        v
Which Files Does It Trust?
        |
        v
Which Environment Does It Use?
        |
        v
Which Dependencies Are Loaded?
        |
        v
Can My User Influence Any of Them?
        |
        v
Does the Privileged Job Consume That Resource?
        |
        v
Does This Cross an Intended Security Boundary?
        |
        v
Can I Validate It Safely?
```

This approach separates ordinary scheduled administration from a defensible privilege escalation finding.

---

# Related Notes

- [Linux Overview](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Filesystem Permissions](filesystem-permissions.md)
- [sudo Security](sudo.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

The following Linux pages build further on scheduled-job privilege relationships:

[Linux SUID and SGID Security](suid-sgid.md)

[Linux Capabilities Security](capabilities.md)

[Linux Security Controls](security-controls.md)

---

# References

- [crontab(5) - Linux man-pages](https://man7.org/linux/man-pages/man5/crontab.5.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.timer](https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html){ target="_blank" rel="noopener noreferrer" }
- [systemd.unit](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html){ target="_blank" rel="noopener noreferrer" }
- [GNU Coreutils](https://www.gnu.org/software/coreutils/manual/coreutils.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages](https://www.kernel.org/doc/man-pages/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

!!! tip "Follow the complete execution chain"

    A root-owned cron script can still depend on a writable helper script, configuration file, PATH directory, environment file or temporary resource. Protecting the top-level script alone does not necessarily protect the scheduled operation.

!!! tip "Correlate timers with services"

    A systemd timer generally tells you when activation occurs. The associated service is where you will usually find the execution identity, executable, environment and other resources that determine the security impact.

!!! tip "Use evidence instead of destructive proof"

    When a privileged scheduled script is demonstrably writable by the assessed user, the scheduler configuration, identity information and permission evidence can often establish the trust-boundary problem without modifying the script.

!!! warning "Privileged scheduling is normal"

    Root and other privileged accounts routinely execute scheduled maintenance. The existence of a privileged job is not a vulnerability unless an unintended principal can influence the operation or gain access beyond the intended security model.
