---
title: sudo Security
description: Practical Linux sudo security assessment covering sudo permissions, sudoers configuration, command restrictions, target users, NOPASSWD rules, wildcards, environment handling, scripts, interpreters, editors, file dependencies and privilege escalation analysis.
---

# sudo Security

`sudo` allows authorised users to execute commands as another user according to configured policy.

It is commonly used to delegate administrative capabilities without giving users unrestricted access to the root account.

During an authorised Linux security assessment, `sudo` configuration is one of the most important privilege-related areas to review.

The objective is not simply to identify commands that can be executed with `sudo`.

The objective is to determine whether delegated functionality allows a lower-privileged user to cross an unintended security boundary.

```text
Current User
     |
     v
sudo Policy
     |
     v
Permitted Command
     |
     v
Target User
     |
     v
Command Functionality
     |
     +---- Arguments
     +---- Environment
     +---- Referenced files
     +---- Child processes
     +---- Plugins / modules
     +---- External commands
     |
     v
Can Delegated Access Exceed Intended Boundary?
```

A `sudo` rule is not automatically a vulnerability.

The security question is:

> Can the permitted command or something it trusts be influenced in a way that provides capabilities beyond those intentionally delegated?

!!! warning "Authorised Security Testing"

    Use these techniques only on systems you own or have explicit permission to assess. Prefer configuration inspection and non-destructive validation. Do not alter production `sudoers` files, privileged scripts, system binaries or application configuration merely to demonstrate impact.

---

# 1. What sudo Does

The basic syntax is:

```bash
sudo command
```

A command can also be executed as another user:

```bash
sudo -u username command
```

`sudo` policy determines whether the requesting user is permitted to perform the requested operation.

Important components include:

```text
Requesting User

Host

Run-As User

Run-As Group

Command

Arguments

Authentication Requirement

Environment

sudo Options
```

These relationships are normally configured through:

```text
/etc/sudoers
```

and commonly:

```text
/etc/sudoers.d/
```

Configuration should normally be edited with `visudo`, not by directly modifying the files.

During an assessment, prefer read-only inspection.

---

# 2. Establish the Current Context

Start with:

```bash
whoami
id
```

Record:

```text
Username

UID

Primary GID

Supplementary groups
```

Then determine whether the user belongs to an administrative group.

```bash
groups
```

Common administrative groups may include:

```text
sudo
wheel
```

depending on the distribution.

Group membership alone does not prove what the user can execute.

The effective `sudo` policy is more important.

---

# 3. Enumerate sudo Permissions

The primary assessment command is:

```bash
sudo -l
```

This lists commands the current user is permitted to execute according to the applicable `sudo` policy.

Representative output may resemble:

```text
User analyst may run the following commands on server01:
    (root) /usr/bin/systemctl status example.service
```

Interpretation:

```text
Requesting user:
analyst

Run-as user:
root

Permitted command:
/usr/bin/systemctl status example.service
```

Do not stop at the command name.

Determine what the command can actually do.

---

# 4. sudo -l Without Prompting for a Password

In some assessment situations, you may want to avoid an unexpected interactive password prompt.

Use:

```bash
sudo -n -l
```

The `-n` option requests non-interactive behavior.

If authentication is required and no cached credentials are available, `sudo` should fail instead of prompting.

This can be useful during controlled enumeration or automated collection.

Do not interpret failure as proof that no sudo rights exist.

Authentication state and policy can affect the result.

---

# 5. Understanding sudo -l Output

A rule may resemble:

```text
(root) /usr/bin/systemctl restart example.service
```

Another might resemble:

```text
(backup) /usr/local/bin/backup-status
```

The section in parentheses represents the permitted run-as context.

For example:

```text
(root)
```

means the command can be executed as root according to that rule.

```text
(backup)
```

means it can be executed as the `backup` user.

Do not assume that only root delegation is security relevant.

Access to another service or application account can expose:

```text
Credentials

Configuration

Data

SSH keys

Application secrets

Additional sudo permissions

Group memberships

Files inaccessible to the original user
```

Privilege escalation can therefore be multi-stage.

---

# 6. Run-As Users

A useful model is:

```text
analyst
   |
   | sudo
   v
backup
   |
   +---- Sensitive files
   +---- SSH keys
   +---- Application configuration
   +---- Additional privileges
   |
   v
Potential Additional Security Boundary
```

Always determine:

```text
Which user can the command run as?

Which group can it run as?

What access does that identity have?

Does the target identity have additional sudo permissions?
```

If authorised and appropriate, the target user's effective privileges can be assessed separately after access has been legitimately established.

---

# 7. NOPASSWD

A rule may contain:

```text
NOPASSWD:
```

Example:

```text
(root) NOPASSWD: /usr/bin/systemctl restart example.service
```

This means the applicable command can be executed without `sudo` requiring the user's password under that rule.

`NOPASSWD` is not automatically a vulnerability.

The relevant question remains:

```text
What functionality has been delegated?
```

A narrowly restricted non-interactive operational command may be intentional.

A broadly capable command may represent significantly greater risk.

---

# 8. PASSWD Versus NOPASSWD

The difference affects authentication requirements:

```text
PASSWD
   |
   +---- sudo may require authentication

NOPASSWD
   |
   +---- command can be authorised without that password prompt
```

However:

```text
Password Required != Secure Rule

NOPASSWD != Vulnerable Rule
```

The capability exposed by the command remains the primary security consideration.

---

# 9. sudo Authentication Cache

`sudo` can cache successful authentication for a period determined by policy.

This means subsequent commands may not immediately prompt again.

The assessment should therefore distinguish:

```text
Rule permits command
```

from:

```text
Authentication currently cached
```

The two are not equivalent.

Do not infer `NOPASSWD` simply because no password prompt appeared.

---

# 10. List sudo Version

Version information can be obtained with:

```bash
sudo --version
```

The output can include:

```text
sudo version

sudoers policy plugin version

sudoers file grammar version

I/O plugin information

Build options
```

Version information can help understand supported features.

Do not report a vulnerability based solely on a version string.

Confirm:

```text
Distribution package

Vendor patches

Security backports

Configuration

Exploit prerequisites

Actual affected condition
```

before reaching a vulnerability conclusion.

---

# 11. sudoers Configuration

The primary policy file is commonly:

```text
/etc/sudoers
```

Additional configuration may exist under:

```text
/etc/sudoers.d/
```

Whether the current user can read these files depends on system configuration.

Where access is permitted:

```bash
ls -l /etc/sudoers
ls -ld /etc/sudoers.d
ls -l /etc/sudoers.d 2>/dev/null
```

If the files are readable within scope:

```bash
sudo cat /etc/sudoers
```

should not be used merely to circumvent normal read permissions unless the applicable sudo policy explicitly permits and the assessment requires it.

In most cases:

```bash
sudo -l
```

is the safer starting point for determining the current user's effective delegated commands.

---

# 12. Never Edit sudoers Directly During Testing

Administrators normally use:

```bash
visudo
```

because it validates syntax before committing changes.

A malformed sudoers configuration can affect administrative access.

During a penetration test:

```text
Do not add yourself to sudoers.

Do not change NOPASSWD rules.

Do not weaken command restrictions.

Do not alter /etc/sudoers merely to prove write access.
```

If unexpected write access is identified, validate the filesystem permission safely and report the security relationship.

---

# 13. Check sudoers Permissions

Inspect:

```bash
stat /etc/sudoers
```

and where relevant:

```bash
getfacl /etc/sudoers
```

Inspect the directory:

```bash
stat /etc/sudoers.d
```

```bash
getfacl /etc/sudoers.d
```

The important questions are:

```text
Can an unprivileged user modify sudo policy?

Can an unprivileged user create trusted policy files?

Are unexpected ACLs present?

Are parent directory permissions appropriate?
```

Unexpected write access to effective sudo policy is highly security sensitive.

Do not modify the policy to demonstrate the issue.

---

# 14. Command Paths

sudo rules should be analysed using the exact command specification.

For example:

```text
(root) /usr/bin/systemctl restart application.service
```

is very different from a broadly scoped rule.

Record the exact:

```text
Executable path

Arguments

Wildcards

Run-as identity

Tags

Options
```

Do not simplify a rule during reporting in a way that changes its security meaning.

---

# 15. Verify the Binary

If a rule permits:

```text
/usr/local/bin/backup-status
```

inspect the actual object:

```bash
ls -l /usr/local/bin/backup-status
```

```bash
stat /usr/local/bin/backup-status
```

```bash
getfacl /usr/local/bin/backup-status
```

Inspect the complete path:

```bash
namei -l /usr/local/bin/backup-status
```

Questions include:

```text
Who owns the binary?

Who can modify it?

Can its parent directory be modified?

Is it a script?

Is it a symbolic link?

Does it load additional configuration?
```

A carefully restricted sudo rule can become unsafe if the permitted executable itself is modifiable by the requesting user.

---

# 16. Writable sudo Executable

Consider:

```text
analyst ALL=(root) /usr/local/bin/backup-status
```

If:

```bash
stat /usr/local/bin/backup-status
```

shows that `analyst` can modify the file, the relationship is significant.

```text
analyst
   |
   v
Write Access
   |
   v
/usr/local/bin/backup-status
   |
   v
sudo
   |
   v
root
```

Do not modify the executable during routine validation.

The combination of:

```text
sudo rule
+
confirmed write permission
+
root run-as context
```

can provide sufficient evidence of the trust-boundary problem.

---

# 17. Parent Directory Permissions

The executable itself may appear protected:

```text
-rwxr-xr-x root root /usr/local/bin/custom-backup
```

but its parent directory must also be inspected.

```bash
namei -l /usr/local/bin/custom-backup
```

A lower-privileged user may be unable to modify the existing file contents while still having meaningful control over the directory entry under certain permission configurations.

Therefore always review:

```text
Executable

Parent directory

Complete path

ACLs
```

See [Linux Filesystem Permissions](filesystem-permissions.md).

---

# 18. Scripts Permitted Through sudo

A sudo rule may permit a script:

```text
(root) /opt/application/maintenance.sh
```

Inspect:

```bash
stat /opt/application/maintenance.sh
getfacl /opt/application/maintenance.sh
namei -l /opt/application/maintenance.sh
```

Then inspect what the script depends on.

Possible dependencies include:

```text
Configuration files

Helper scripts

Environment files

External commands

Libraries

Temporary files

Input files

Plugins
```

The top-level script can be root-owned and protected while still trusting another writable resource.

---

# 19. Script Dependency Model

A useful model is:

```text
sudo Rule
    |
    v
Root-Owned Script
    |
    +---- Helper script
    |
    +---- Configuration
    |
    +---- External command
    |
    +---- Input file
    |
    +---- Temporary resource
    |
    v
Can User Influence Any Dependency?
```

Do not evaluate only the first file in the execution chain.

---

# 20. External Commands

Suppose an authorised script invokes external programs.

Determine whether it uses:

```text
Absolute paths
```

such as:

```bash
/usr/bin/logger
```

or relies on command lookup such as:

```bash
logger
```

Relative command resolution may require further assessment of the execution environment and sudo policy.

Do not assume that a command without an absolute path is exploitable.

You must determine the effective PATH and whether an attacker-controlled location can actually influence resolution.

---

# 21. PATH Handling

Display the current PATH:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

However, the current user's shell PATH may not be the PATH used by sudo.

sudo policy can define a controlled path using settings such as:

```text
secure_path
```

Where visible through `sudo -l`, policy options may provide relevant context.

The assessment question is:

```text
What PATH is effective for the privileged command?
```

not:

```text
What PATH does my current shell have?
```

---

# 22. secure_path

A sudoers configuration can define a trusted executable search path.

Conceptually:

```text
Defaults secure_path="..."
```

This can reduce risk from user-controlled PATH entries.

However, the presence of `secure_path` does not automatically make every sudo rule safe.

You must still assess:

```text
Permitted binary

Arguments

Dependencies

Writable resources

Environment

Command functionality
```

---

# 23. Environment Variables

sudo normally applies environment-handling rules when executing commands.

Relevant policy concepts include:

```text
env_reset

env_keep

env_check

env_delete

setenv
```

The effective configuration depends on sudoers policy and build configuration.

During assessment, determine whether environment variables relevant to the permitted program can be influenced.

Examples might include application-specific variables controlling:

```text
Configuration paths

Plugin paths

Runtime behaviour

Temporary directories

Language runtimes
```

Do not assume arbitrary environment variables survive sudo execution.

Validate the actual policy.

---

# 24. SETENV

Some sudo rules can allow users greater control over environment variables.

If `SETENV` appears in applicable policy output, determine:

```text
Which command does it apply to?

Which environment variables matter to that command?

Does the application trust those variables?

Can they influence privileged behaviour?
```

`SETENV` alone is not automatically a finding.

The privileged program's behavior determines impact.

---

# 25. Command Arguments

Argument restrictions are critical.

Compare:

```text
/usr/bin/systemctl status example.service
```

with a rule that allows substantially broader argument selection.

When reviewing a sudo rule, capture the complete command specification exactly as shown.

Ask:

```text
Are arguments fixed?

Are arguments optional?

Can additional arguments be supplied?

Are wildcards present?

Can arguments reference files?

Can arguments change configuration?

Can arguments launch another program?
```

Do not assume that a restricted-looking command remains restricted without understanding how sudo matches that rule.

---

# 26. Wildcards

sudoers command specifications can contain wildcard patterns.

Wildcards require careful analysis because command-line arguments are matched according to sudoers policy rules rather than according to an administrator's intuitive idea of a filesystem pattern.

A rule that appears to constrain access to:

```text
/var/log/application/*
```

should therefore be reviewed carefully.

Questions include:

```text
What portion of the command is wildcarded?

Can multiple arguments be supplied?

Can path traversal or alternate path forms affect the application?

How does the permitted program interpret the resulting arguments?
```

Do not assume that every wildcard creates an escape.

The exact rule and program behavior must be validated.

---

# 27. Broad Command Delegation

Some commands expose substantially more functionality than their names suggest.

Examples of command categories requiring careful review include:

```text
Text editors

Pagers

Interpreters

Shells

Debuggers

Package managers

Service managers

Archive utilities

File-management tools

Build tools

Version-control tools

Network clients
```

The question is not whether a command appears administrative.

The question is:

> Does the permitted functionality allow execution, file modification, subprocess creation or another action outside the intended delegated task?

---

# 28. Interpreters

Interpreters can expose broad program execution capabilities.

Examples include:

```text
python
python3
perl
ruby
php
bash
sh
```

If an interpreter is delegated through sudo, determine whether:

```text
The script is fixed

Arguments are fixed

Interactive execution is possible

Arbitrary code can be supplied

Additional modules can be loaded

Environment variables affect module resolution
```

Do not conclude from the interpreter name alone.

The exact sudo command specification matters.

---

# 29. Editors

Text editors may provide functionality beyond simply editing one file.

Potential capabilities can include:

```text
Opening additional files

Writing additional files

Launching subprocesses

Using plugins

Using configuration files
```

If an editor is permitted through sudo, determine whether the policy genuinely restricts it to the intended operation.

Do not use editor subprocess functionality during production testing unless such impact validation is explicitly authorised and necessary.

---

# 30. Pagers

Programs used to display text can sometimes expose additional interactive features.

The security relevance depends on:

```text
Program

Version

Invocation

Environment

sudo restrictions

Interactive context
```

Do not assume that every pager invocation permits arbitrary execution.

Assess the exact delegated command.

---

# 31. Service Management

sudo rules frequently delegate service operations.

Example:

```text
(root) /usr/bin/systemctl restart application.service
```

This may be entirely legitimate.

The assessment should correlate the rule with the service configuration.

Inspect:

```bash
systemctl cat application.service
```

Determine:

```text
Who owns the unit?

Who owns the executable?

Can the current user modify configuration?

Can the current user modify EnvironmentFile resources?

Can the current user modify the service executable?

Can the current user modify scripts called by the service?
```

The rule becomes more significant when the user can control a resource the privileged service consumes.

See [Linux Services](services.md).

---

# 32. Example Service Relationship

Suppose:

```text
analyst ALL=(root) NOPASSWD: /usr/bin/systemctl restart reports.service
```

The restart permission itself may be expected.

But:

```bash
systemctl cat reports.service
```

shows:

```text
ExecStart=/opt/reports/start.sh
```

and:

```bash
stat /opt/reports/start.sh
```

shows the user can modify the script.

The relevant relationship is:

```text
analyst
   |
   +---- Can modify start.sh
   |
   +---- Can restart reports.service through sudo
   |
   v
root executes start.sh
```

The vulnerability is not simply:

```text
User can restart a service.
```

It is the combined trust relationship.

---

# 33. Scheduled Job Management

A delegated command may also interact with scheduled tasks or timers.

If a sudo rule permits management of a timer or scheduled service, determine whether the user can modify resources consumed by the resulting privileged execution.

Correlate with [Scheduled Jobs](scheduled-jobs.md).

---

# 34. File Operations

Commands that read, copy, move or otherwise manipulate files should be analysed based on their permitted scope.

Ask:

```text
Can the user choose the source?

Can the user choose the destination?

Can protected files be read?

Can protected files be replaced?

Can ownership or mode be preserved or changed?

Can symbolic links affect behavior?
```

Do not perform destructive file replacement during routine validation.

---

# 35. Archive Utilities

Archive tools can interact with many files and directories.

When delegated through sudo, determine:

```text
Can archive contents be chosen?

Can extraction paths be chosen?

Can options invoke external functionality?

Can protected files be read?

Can privileged paths be written?
```

The exact utility, arguments and sudo rule determine whether a meaningful security boundary exists.

---

# 36. Package Management

Package-management tools are highly privileged because software installation inherently changes system state.

Examples include distribution-specific tools such as:

```text
apt
apt-get
dnf
yum
rpm
dpkg
```

If package management is delegated, determine whether the scope is intentionally equivalent to administrative software installation.

Do not install or remove packages merely to prove impact.

The delegated capability itself may already establish the level of access.

---

# 37. Shell Delegation

If policy explicitly allows a root shell, the security meaning is usually clear.

For example, a policy equivalent to unrestricted root command execution should not be reported as a privilege escalation vulnerability if the user is intentionally authorised as an administrator.

Always distinguish:

```text
Intended Administrative Access
```

from:

```text
Unintended Privilege Escalation
```

Context matters.

---

# 38. ALL Rules

An applicable sudo rule may grant broad command execution.

Conceptually:

```text
ALL
```

can represent very broad permissions depending on where it appears in the sudoers rule.

Do not interpret `ALL` without understanding its position.

sudoers specifications can involve:

```text
User

Host

Run-as user

Run-as group

Command
```

Record the complete rule rather than reporting only the word `ALL`.

---

# 39. Group-Based sudo Rules

sudo permissions can be assigned to groups.

A typical policy concept may resemble:

```text
%administrators
```

where `%` denotes a Unix group in sudoers syntax.

Determine:

```bash
id
```

and:

```bash
groups
```

Then correlate group membership with effective output from:

```bash
sudo -l
```

The effective policy matters more than simply finding a group definition.

---

# 40. Included sudoers Files

sudo policy can be split across multiple files.

Commonly:

```text
/etc/sudoers.d/
```

is used for modular policy.

Assess:

```bash
ls -ld /etc/sudoers.d
```

and, where permitted:

```bash
ls -l /etc/sudoers.d
```

Check:

```text
Directory owner

Directory permissions

File owners

File permissions

ACLs
```

Unexpected unprivileged write access to a trusted policy location requires careful investigation.

---

# 41. Symbolic Links and sudo Resources

If a sudo-permitted script or configuration is a symbolic link, resolve it:

```bash
readlink -f /path/to/resource
```

Then inspect:

```bash
namei -l /path/to/resource
```

The security assessment should consider the actual target rather than only the visible link.

---

# 42. Configuration Dependencies

Suppose:

```text
(root) /usr/local/bin/report-generator
```

is permitted.

The executable itself is protected.

However, it loads:

```text
/etc/report-generator/config.yml
```

or:

```text
/opt/reports/config.yml
```

Inspect:

```bash
stat /opt/reports/config.yml
getfacl /opt/reports/config.yml
namei -l /opt/reports/config.yml
```

If the current user can modify security-sensitive configuration consumed by the privileged command, the sudo rule requires deeper analysis.

---

# 43. Plugin and Extension Directories

Applications can support:

```text
Plugins

Modules

Extensions

Hooks

Templates
```

If a sudo-permitted application loads code or behavior from such locations, determine:

```text
Which directories are searched?

Who owns them?

Who can write to them?

Does the application load them during privileged execution?

Can configuration change the search location?
```

Do not create malicious plugins merely to validate the relationship unless explicitly authorised.

---

# 44. Temporary Files

Privileged commands may create or consume temporary files.

Review whether they use:

```text
/tmp

/var/tmp

Application-specific temporary directories
```

The existence of temporary files is not itself a weakness.

The security question is whether privileged software trusts attacker-controlled temporary resources unsafely.

Kernel protections, sticky-bit semantics and application behavior all affect the result.

---

# 45. sudoedit

`sudoedit` provides a controlled mechanism for editing authorised files.

It should be distinguished from simply running an editor as root.

Where `sudoedit` permissions are present, determine:

```text
Which files can be edited?

Are paths fixed?

Are wildcards involved?

Which sudo version and vendor package are present?

What policy restrictions apply?
```

Do not infer a vulnerability solely because `sudoedit` is available.

---

# 46. Command Digests

sudoers can support command digests that tie an allowed command to cryptographic content.

Where such configuration is used, it can help ensure that the authorised command has not changed.

During assessment, document digest restrictions if they materially affect the command's trust model.

Do not assume every sudo deployment uses command digests.

---

# 47. NOEXEC

sudo can support a `NOEXEC` policy tag in applicable environments.

Its purpose is to restrict certain delegated programs from executing additional commands through supported mechanisms.

However, `NOEXEC` should be treated as defense-in-depth rather than a universal guarantee.

Its effectiveness depends on:

```text
Operating system

Program behavior

How subprocesses are created

sudo build and configuration
```

Do not assume that `NOEXEC` makes an otherwise excessively powerful command safe.

---

# 48. INTERCEPT and Other Policy Features

Modern sudo versions can support additional policy and execution-control features depending on build and configuration.

Do not assume that every system supports or enables the same sudo features.

During assessment, use:

```bash
sudo --version
```

and effective policy output to understand the local environment.

Avoid designing findings around a feature that is not actually deployed.

---

# 49. GTFOBins

GTFOBins documents legitimate Unix binaries that can expose security-sensitive functionality when placed in particular privilege contexts.

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

It can be useful when reviewing an unfamiliar sudo-permitted binary.

However:

```text
Binary Listed on GTFOBins
```

does not mean:

```text
System Vulnerable
```

The correct workflow is:

```text
sudo -l
   |
   v
Identify Permitted Binary
   |
   v
Understand Exact Rule
   |
   v
Understand Binary Functionality
   |
   v
Check Version / Environment
   |
   v
Check Restrictions
   |
   v
Determine Actual Security Impact
```

---

# 50. Practical Validation Workflow

Use this workflow for each interesting sudo rule.

```text
sudo -l
   |
   v
Identify Rule
   |
   v
Record Run-As User
   |
   v
Record Exact Command
   |
   v
Record Arguments
   |
   v
Record Tags / Options
   |
   v
Inspect Binary
   |
   v
Inspect Parent Directories
   |
   v
Inspect Dependencies
   |
   v
Inspect Environment
   |
   v
Understand Program Functionality
   |
   v
Determine Security Boundary
   |
   v
Safe Validation
   |
   v
Evidence
   |
   v
Conclusion
```

---

# 51. Practical Validation - Writable sudo Script

## Scenario

`sudo -l` returns:

```text
(root) NOPASSWD: /opt/vendor/backup.sh
```

## Step 1 - Establish Identity

```bash
id
```

## Step 2 - Record sudo Rule

```bash
sudo -l
```

## Step 3 - Inspect Script

```bash
stat /opt/vendor/backup.sh
```

```bash
getfacl /opt/vendor/backup.sh
```

## Step 4 - Inspect Complete Path

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

# 52. Representative Positive Result

Suppose the evidence shows:

```text
User:
analyst

sudo rule:
(root) NOPASSWD: /opt/vendor/backup.sh

Script owner:
root

Script group:
developers

Permissions:
-rwxrwxr-x

Current user's groups:
developers
```

Relationship:

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
sudo as root
```

This provides strong evidence that the sudo trust boundary is incorrectly configured.

The production script does not need to be modified to demonstrate the underlying condition.

---

# 53. Representative Negative Result

Suppose:

```text
(root) /usr/bin/systemctl status application.service
```

is permitted.

Further assessment determines:

```text
Arguments are restricted.

Service resources are root-owned.

Application configuration is protected.

No writable dependencies are identified.

No additional privileged functionality is available through the permitted invocation.
```

The appropriate conclusion may be:

```text
The delegated command was reviewed and no unintended privilege escalation
path was identified under the assessed configuration.
```

This is a valid assessment outcome.

---

# 54. Multi-Step Privilege Relationships

sudo does not always lead directly to root.

Example:

```text
webuser
   |
   | sudo
   v
deploy
   |
   +---- Deployment credentials
   |
   +---- Application configuration
   |
   +---- Additional group membership
   |
   | sudo
   v
root
```

Assessment should consider the complete privilege graph.

A transition to another account can materially change the security context even when it does not immediately provide UID 0.

---

# 55. False Positives and Alternative Explanations

Common false positives include:

```text
NOPASSWD rule for narrowly restricted operational command

sudo permission intentionally equivalent to administrator access

Read-only status command with no additional functionality

Service restart permission where all service resources are protected

GTFOBins-listed binary invoked with effective restrictions

Writable file unrelated to the sudo-permitted command

Current shell PATH mistaken for sudo's effective PATH

sudo authentication cache mistaken for NOPASSWD

Inactive or obsolete sudo configuration

Rule that does not actually apply to current host or user
```

Always validate the effective policy.

---

# 56. Automated Enumeration

Tools such as:

```text
LinPEAS

LinEnum

linux-smart-enumeration
```

can highlight sudo permissions.

However:

```text
Automated Tool
      |
      v
Interesting sudo Rule
      |
      v
Manual Review
      |
      v
Program Analysis
      |
      v
Dependency Analysis
      |
      v
Security Conclusion
```

Do not treat automated classification as proof of exploitability.

---

# 57. Evidence Collection

For each significant sudo observation, capture:

```text
Hostname

Current user

UID

GID

Groups

sudo version

sudo -l output

Run-as user

Run-as group

Authentication requirement

Exact permitted command

Arguments

Tags

Binary path

Binary owner

Binary group

Binary permissions

ACLs

Parent directory permissions

Relevant dependencies

Relevant environment behavior

Validation result
```

Useful commands include:

```bash
id
sudo --version
sudo -l
stat /path/to/command
getfacl /path/to/command
namei -l /path/to/command
```

---

# 58. Reporting

Avoid:

> User has sudo access.

This provides insufficient context.

Prefer:

> The `analyst` account is permitted to execute `/opt/vendor/backup.sh` as root through sudo without additional authentication. The script is writable by the `developers` group, of which `analyst` is a member. As a result, a lower-privileged user can modify code that sudo subsequently executes with UID 0.

This identifies:

```text
Principal

sudo rule

Target identity

Controllable resource

Trust relationship

Security impact
```

---

# 59. Example Finding

## Observation

The assessed user can execute a group-writable maintenance script as root through sudo.

## Current User

```text
analyst
```

## sudo Rule

```text
(root) NOPASSWD: /opt/vendor/maintenance.sh
```

## Affected Resource

```text
/opt/vendor/maintenance.sh
```

## Permission Relationship

```text
Owner: root
Group: developers
Group permission: write
Current user: member of developers
```

## Impact

A lower-privileged user can influence code that is explicitly authorised to execute as root.

## Recommendation

Remove write access to the script and its trusted dependencies from non-administrative principals.

---

# 60. Reporting Intentional Administrative Access

Not every broad sudo rule is a vulnerability.

Suppose:

```text
User:
sysadmin

Role:
Linux administrator

sudo:
Full root administration
```

If this access is intentionally required and consistent with the approved privilege model, reporting:

```text
User can become root through sudo
```

as a vulnerability would be misleading.

Instead review:

```text
Is the user expected to be an administrator?

Is the account appropriately protected?

Is access centrally managed?

Is privileged activity logged?

Is the access still required?
```

---

# 61. Remediation

sudo remediation should follow least privilege.

Prefer:

```text
Specific commands

Specific target users

Specific arguments where practical

Protected executables

Protected configuration

Protected dependencies

Minimal environment exposure
```

Avoid unnecessarily broad delegation.

For example, administrators should consider whether users need:

```text
Full shell

Full interpreter

Generic editor

Package manager

Broad service manager

Wildcard command
```

when a narrower administrative operation would satisfy the business requirement.

---

# 62. Protect sudo-Executed Resources

All resources trusted by privileged sudo commands should have appropriate ownership and permissions.

Review:

```text
Executable

Script

Configuration

Environment file

Helper script

Plugin directory

Library path

Parent directories
```

The security model should resemble:

```text
Privileged sudo Command
       |
       v
Trusted Resource
       |
       v
Writable Only by Trusted Administrators
```

---

# 63. Prefer Purpose-Built Administrative Interfaces

Instead of delegating a broadly capable command, consider purpose-built wrappers or service-management interfaces that expose only the required operation.

However, wrapper scripts must themselves be designed securely.

A wrapper should avoid:

```text
User-controlled command execution

Unsafe wildcards

Untrusted PATH resolution

Writable dependencies

Unvalidated file paths

Unnecessary environment inheritance
```

A poorly designed wrapper can be more dangerous than the original command.

---

# 64. Logging

sudo can generate security-relevant logs depending on system configuration.

Common sources may include:

```text
systemd journal

Authentication logs

sudo-specific logs

Central logging
```

On systemd systems:

```bash
journalctl _COMM=sudo --no-pager 2>/dev/null
```

Availability and permissions vary.

Possible traditional log locations include distribution-specific authentication logs.

Do not assume the same file exists on every Linux distribution.

---

# 65. I/O Logging

sudo can support command input/output logging depending on policy and configuration.

Where deployed, this can provide additional visibility into privileged administrative activity.

During a security review, determine whether privileged activity is:

```text
Logged

Protected

Centralised

Monitored

Retained appropriately
```

Logging does not replace least privilege, but it improves accountability and detection.

---

# 66. Retesting

After remediation, repeat:

```bash
sudo -l
```

Confirm that:

```text
Unnecessary rule removed

Command narrowed

Run-as context corrected

NOPASSWD removed where policy requires authentication

Wildcards restricted where practical

Unsafe environment handling removed

Writable dependencies protected
```

Then inspect affected resources:

```bash
stat /path/to/resource
getfacl /path/to/resource
namei -l /path/to/resource
```

If the original issue involved group write access, confirm the user no longer has effective modification rights.

---

# sudo Assessment Checklist

## Identity

- [ ] Identify current user
- [ ] Record UID
- [ ] Record GID
- [ ] Review groups
- [ ] Determine administrative role

## Enumeration

- [ ] Run `sudo -l`
- [ ] Consider `sudo -n -l` where appropriate
- [ ] Record sudo version
- [ ] Identify run-as users
- [ ] Identify run-as groups
- [ ] Identify NOPASSWD rules
- [ ] Identify command tags
- [ ] Identify policy options

## Commands

- [ ] Record exact executable path
- [ ] Record arguments
- [ ] Identify wildcards
- [ ] Identify interpreters
- [ ] Identify editors
- [ ] Identify pagers
- [ ] Identify service-management commands
- [ ] Identify package-management commands
- [ ] Identify file-management commands
- [ ] Identify custom scripts

## Filesystem

- [ ] Inspect command owner
- [ ] Inspect command group
- [ ] Inspect command permissions
- [ ] Inspect ACLs
- [ ] Inspect parent directories
- [ ] Resolve symbolic links
- [ ] Identify writable dependencies

## Scripts

- [ ] Review helper scripts
- [ ] Review external commands
- [ ] Review configuration files
- [ ] Review environment files
- [ ] Review temporary resources
- [ ] Review plugin directories
- [ ] Review relative command usage

## Environment

- [ ] Determine effective PATH
- [ ] Review `secure_path`
- [ ] Review relevant environment policy
- [ ] Identify SETENV where applicable
- [ ] Identify application-specific environment dependencies

## sudoers

- [ ] Review `/etc/sudoers` permissions
- [ ] Review `/etc/sudoers.d` permissions
- [ ] Review ACLs where relevant
- [ ] Identify unexpected writable policy resources
- [ ] Do not modify policy during routine validation

## Validation

- [ ] Determine intended delegated capability
- [ ] Determine actual delegated capability
- [ ] Identify privileged dependencies
- [ ] Identify alternative explanations
- [ ] Avoid destructive proof
- [ ] Validate the trust relationship
- [ ] Distinguish intended administration from escalation

## Evidence

- [ ] Capture `id`
- [ ] Capture `sudo -l`
- [ ] Capture sudo version where relevant
- [ ] Capture command metadata
- [ ] Capture ACLs
- [ ] Capture path permissions
- [ ] Capture dependency evidence
- [ ] Record target identity

## Reporting

- [ ] Identify principal
- [ ] Identify exact sudo rule
- [ ] Identify target identity
- [ ] Identify controllable resource
- [ ] Explain privilege boundary
- [ ] Explain preconditions
- [ ] Provide root-cause remediation
- [ ] Define retest procedure

---

# Quick sudo Assessment Workflow

```text
            sudo -l
               |
               v
        Interesting Rule?
          /          \
        No            Yes
        |              |
        v              v
     Record       Run-As Context
                       |
                       v
                  Exact Command
                       |
                       v
                 Arguments / Tags
                       |
                       v
                  Inspect Binary
                       |
                       v
               Inspect Dependencies
                       |
                       v
                Inspect Filesystem
                       |
                       v
                Inspect Environment
                       |
                       v
            Understand Functionality
                       |
                       v
             Intended Capability?
                 /          \
               Yes          No
               |             |
               v             v
         Verify Scope    Validate Impact
               |             |
               +------+------+
                      |
                      v
                   Evidence
                      |
                      v
                   Report
```

---

# Command Reference

## Current Identity

```bash
whoami
id
groups
```

## sudo Permissions

```bash
sudo -l
```

## Non-Interactive Enumeration

```bash
sudo -n -l
```

## sudo Version

```bash
sudo --version
```

## sudoers Metadata

```bash
stat /etc/sudoers
stat /etc/sudoers.d
```

## ACLs

```bash
getfacl /etc/sudoers
getfacl /etc/sudoers.d
```

## Permitted Binary

```bash
stat /path/to/binary
getfacl /path/to/binary
namei -l /path/to/binary
```

## Symbolic Link Resolution

```bash
readlink -f /path/to/resource
```

## Current PATH

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

## systemd Service

```bash
systemctl cat application.service
```

## sudo Logs on systemd Systems

```bash
journalctl _COMM=sudo --no-pager 2>/dev/null
```

---

# Practical Questions

For every sudo rule, answer:

```text
1. Which user receives the delegated capability?

2. Which target user or group can the command run as?

3. What exact command is permitted?

4. Which arguments are permitted?

5. Is authentication required?

6. Which environment is used?

7. Can the executable be modified?

8. Can its parent directory be modified?

9. Is it a script?

10. What dependencies does it trust?

11. Are configuration files writable?

12. Are helper scripts writable?

13. Are external commands resolved safely?

14. Are wildcards present?

15. Does the command expose additional functionality?

16. Is this capability intentionally delegated?

17. Does the observed behavior cross an intended security boundary?

18. Can the issue be demonstrated without modifying production resources?
```

If these questions cannot be answered, the sudo assessment is incomplete.

---

# Related Notes

- [Linux Overview](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Filesystem Permissions](filesystem-permissions.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

The following Linux pages build further on sudo-related privilege relationships:

[Linux Scheduled Jobs](scheduled-jobs.md)

[Linux SUID and SGID Security](suid-sgid.md)

[Linux Capabilities Security](capabilities.md)

[Linux Security Controls](security-controls.md)

---

# sudo Security Mindset

Do not think:

```text
sudo = Vulnerable

NOPASSWD = Vulnerable

GTFOBins Match = Root

Service Restart = Root

Wildcard = Exploitable

Editor = Automatically Vulnerable

Old sudo Version = Vulnerable
```

Instead think:

```text
What Is Delegated?
        |
        v
To Which Principal?
        |
        v
As Which User / Group?
        |
        v
With Which Arguments?
        |
        v
Under Which Environment?
        |
        v
What Does the Program Actually Allow?
        |
        v
What Resources Does It Trust?
        |
        v
Can I Influence Those Resources?
        |
        v
Does This Exceed the Intended Delegation?
        |
        v
Can the Security Boundary Be Safely Validated?
```

This approach produces defensible sudo findings rather than simply reporting the existence of privileged commands.

---

# References

- [sudo Project](https://www.sudo.ws/){ target="_blank" rel="noopener noreferrer" }
- [sudo Documentation](https://www.sudo.ws/docs/){ target="_blank" rel="noopener noreferrer" }
- [sudo Manual](https://www.sudo.ws/docs/man/sudo.man/){ target="_blank" rel="noopener noreferrer" }
- [sudoers Manual](https://www.sudo.ws/docs/man/sudoers.man/){ target="_blank" rel="noopener noreferrer" }
- [visudo Manual](https://www.sudo.ws/docs/man/visudo.man/){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages](https://www.kernel.org/doc/man-pages/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

!!! tip "Start with sudo -l"

    `sudo -l` is normally the most useful starting point because it shows the policy relevant to the current user. Record the complete command specification rather than extracting only the executable name.

!!! tip "Follow the dependencies"

    A protected sudo-permitted executable can still trust writable configuration files, helper scripts, environment files or other resources. Analyse the complete execution chain.

!!! tip "Distinguish delegation from escalation"

    sudo exists specifically to delegate privilege. A user having sudo rights is therefore not automatically a vulnerability. The important question is whether the effective capability exceeds the organisation's intended privilege model.

!!! warning "Do not modify privileged resources unnecessarily"

    When a sudo-permitted script or executable is writable, permission metadata and the applicable sudo rule can often establish the security problem without replacing or modifying the production resource.
