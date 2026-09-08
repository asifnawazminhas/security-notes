---
title: Linux Filesystem Permissions
description: Practical Linux filesystem permission assessment covering Unix permissions, ownership, ACLs, writable resources, directory permissions, privileged consumers, symlinks, mount options and privilege escalation analysis.
---

# Linux Filesystem Permissions

Linux filesystem permissions are a fundamental part of the operating system security model.

During an authorised security assessment, permission analysis helps determine whether a lower-privileged user can read sensitive information, modify security-sensitive resources or influence files consumed by a higher-privileged process.

The objective is not simply to identify writable files and directories.

The important relationship is:

```text
Lower-Privileged User
        |
        v
Filesystem Permission
        |
        v
Controllable Resource
        |
        v
Privileged Consumer
        |
        v
Security-Sensitive Operation
        |
        v
Potential Security Boundary
```

A writable file or directory is not automatically a vulnerability.

The assessment must determine what the user can control, who consumes that resource and whether the relationship can create meaningful security impact.

!!! warning "Authorised Security Testing"

    Perform filesystem permission testing only on systems you own or have explicit permission to assess. Prefer read-only enumeration and controlled test files. Do not modify production executables, scripts, configuration files or other operational resources merely to prove that they are writable.

---

# 1. Linux Permission Model

Traditional Linux filesystem permissions are primarily based on:

```text
User / Owner

Group

Other
```

Each can receive combinations of:

```text
Read
Write
Execute
```

Represented as:

```text
r = read
w = write
x = execute
```

Example:

```bash
ls -l /etc/passwd
```

Representative output:

```text
-rw-r--r-- 1 root root 2847 Aug 20 10:14 /etc/passwd
```

Breakdown:

```text
- rw- r-- r--
|  |   |   |
|  |   |   +---- Other
|  |   +-------- Group
|  +------------ Owner
+--------------- File type
```

The first character identifies the object type.

Common values include:

| Character | Meaning |
|---|---|
| `-` | Regular file |
| `d` | Directory |
| `l` | Symbolic link |
| `c` | Character device |
| `b` | Block device |
| `p` | Named pipe |
| `s` | Socket |

The remaining characters describe permission bits.

---

# 2. Numeric Permission Representation

Linux permissions are also commonly represented numerically.

```text
Read    = 4
Write   = 2
Execute = 1
```

The values are combined.

Examples:

| Permission | Numeric |
|---|---:|
| `r--` | 4 |
| `rw-` | 6 |
| `r-x` | 5 |
| `rwx` | 7 |

A mode such as:

```text
755
```

means:

```text
Owner: rwx = 7
Group: r-x = 5
Other: r-x = 5
```

A mode such as:

```text
640
```

means:

```text
Owner: rw- = 6
Group: r-- = 4
Other: --- = 0
```

Do not judge security solely from the numeric mode.

Ownership, ACLs, directory permissions and the consuming process must also be considered.

---

# 3. Establish the Current Identity

Permission analysis begins with the current identity.

```bash
whoami
id
```

Example:

```text
uid=1001"analyst" gid=1001"analyst" groups=1001"analyst",1002"developers"
```

Additional commands:

```bash
id -u
id -un
id -g
id -gn
groups
```

Record:

```text
Username

UID

Primary GID

Supplementary groups

sudo rights

Session context
```

Group membership is particularly important because access may be granted through a supplementary group rather than directly to the user.

---

# 4. Basic Permission Inspection

Use:

```bash
ls -l /path/to/file
```

For directories:

```bash
ls -ld /path/to/directory
```

The `-d` option is important when inspecting the directory object itself.

Example:

```bash
ls -ld /opt/application
```

Representative output:

```text
drwxrwxr-x 4 root developers 4096 Aug 20 12:00 /opt/application
```

This indicates:

```text
Owner: root
Group: developers

Owner permissions:
rwx

Group permissions:
rwx

Other permissions:
r-x
```

If the current user belongs to:

```text
developers
```

the user may be able to create, rename or remove entries within that directory, depending on the complete permission context.

That does not automatically constitute a vulnerability.

---

# 5. Use stat for Detailed Metadata

The `stat` command provides additional filesystem metadata.

```bash
stat /path/to/file
```

Example:

```bash
stat /opt/application/config.ini
```

Representative output:

```text
  File: /opt/application/config.ini
  Size: 2048
Access: (0640/-rw-r-----)
Uid: (    0/    root)
Gid: ( 1002/developers)
```

Useful information includes:

```text
File type

Numeric permissions

Owner UID

Owner name

Group GID

Group name

Size

Timestamps

Filesystem information
```

Focused output can be produced with:

```bash
stat -c '%A %a %U %G %n' /path/to/file
```

Representative output:

```text
-rw-r----- 640 root developers /opt/application/config.ini
```

---

# 6. Files and Directories Behave Differently

One of the most important concepts in Linux permission analysis is that directory permissions have different effects from file permissions.

For a regular file:

```text
Read
    |
    +---- Read file contents

Write
    |
    +---- Modify file contents

Execute
    |
    +---- Attempt to execute the file
```

For a directory:

```text
Read
    |
    +---- List directory entries

Write
    |
    +---- Create or remove directory entries
    +---- Rename entries when other conditions permit

Execute
    |
    +---- Traverse / search the directory
    +---- Access entries by name
```

This distinction is critical.

A file can be:

```text
root-owned

not writable by the current user
```

while its parent directory may still permit the user to remove or replace the directory entry.

Therefore, inspect both:

```text
File permissions
        +
Parent directory permissions
```

---

# 7. Directory Write Permission

Suppose:

```bash
ls -l /opt/application/run.sh
```

returns:

```text
-rwxr-xr-x 1 root root 1200 Aug 20 12:00 /opt/application/run.sh
```

At first glance, the current user cannot modify the file.

Now inspect the parent:

```bash
ls -ld /opt/application
```

Suppose it returns:

```text
drwxrwxr-x 2 root developers 4096 Aug 20 12:00 /opt/application
```

If the current user belongs to:

```text
developers
```

the directory itself requires further analysis.

The important distinction is:

```text
Modify File Contents
```

versus:

```text
Modify Directory Entry
```

These are not equivalent operations.

A directory's permissions can affect whether an entry can be created, renamed or removed even when the file itself is not directly writable.

Do not alter the production file during testing.

Validate the directory separately using a controlled test file.

---

# 8. Safely Test Directory Write Access

Do not test write access by modifying an existing production file.

Use a separate test file.

Example:

```bash
test_dir="/opt/application"
test_file="$test_dir/.permission-test-$$"

if touch "$test_file" 2>/dev/null; then
    echo "[+] Directory allows controlled file creation"
    rm -f "$test_file"
else
    echo "[-] Controlled file creation was not permitted"
fi
```

This tests whether the current context can create an entry without modifying an application resource.

Record:

```text
Directory

Current user

Permission metadata

Test filename

Creation result

Cleanup result
```

!!! note "Creation does not prove exploitation"

    Successfully creating a file demonstrates a filesystem capability. It does not demonstrate privilege escalation unless a higher-privileged component trusts or consumes attacker-controlled content from that location.

---

# 9. Safely Test Existing File Write Access

Where a file is security sensitive, prefer permission inspection rather than modifying it.

Shell test operators can help:

```bash
test -r /path/to/file && echo "Readable"
test -w /path/to/file && echo "Writable"
test -x /path/to/file && echo "Executable"
```

Example:

```bash
if test -w /opt/application/config.ini; then
    echo "[+] Current context reports write access"
else
    echo "[-] Current context does not report write access"
fi
```

This avoids modifying the target.

However, the result should still be interpreted alongside:

```text
ACLs

Ownership

Groups

Parent directory

Mount state

Application behaviour
```

---

# 10. Inspect Every Component of a Path

A useful Linux utility for permission analysis is:

```bash
namei -l /path/to/file
```

Example:

```bash
namei -l /opt/vendor/scripts/backup.sh
```

Representative output may resemble:

```text
f: /opt/vendor/scripts/backup.sh
drwxr-xr-x root root /
drwxr-xr-x root root opt
drwxrwxr-x root developers vendor
drwxrwxr-x root developers scripts
-rwxr-xr-x root root backup.sh
```

This is useful because it exposes permissions across the complete path.

A security-sensitive file should not be assessed independently from the directories used to reach it.

---

# 11. Access Control Lists

Traditional Unix permission bits are not always the complete permission model.

Linux filesystems can support POSIX ACLs.

Inspect ACLs with:

```bash
getfacl /path/to/file
```

Example:

```bash
getfacl /opt/application/config.ini
```

Representative output:

```text
# file: opt/application/config.ini
# owner: root
# group: root
user::rw-
user:analyst:rw-
group::r--
mask::rw-
other::---
```

Although:

```bash
ls -l
```

might suggest restrictive traditional permissions, the named ACL:

```text
user:analyst:rw-
```

grants the user additional access.

Therefore:

```text
ls -l
```

should not always be treated as the complete access-control picture.

---

# 12. ACL Mask

POSIX ACLs can include a mask.

Example:

```text
user::rw-
user:analyst:rwx
group::r--
mask::r-x
other::---
```

The effective permissions of named users and relevant group entries are constrained by the ACL mask.

In this example:

```text
user:analyst:rwx
```

does not necessarily mean all three permissions are effective.

The mask:

```text
mask::r-x
```

limits the effective rights.

`getfacl` may display effective permissions where relevant.

Always inspect the complete ACL.

---

# 13. Default ACLs

Directories can contain default ACLs that affect newly created children.

Example:

```bash
getfacl /opt/application
```

Potential output:

```text
default:user::rwx
default:group::r-x
default:other::---
```

Default ACLs are important when determining what permissions new files or directories may inherit.

They can affect:

```text
Application-created files

Log files

Deployment artifacts

Generated scripts

Configuration

Shared working directories
```

---

# 14. Ownership

Inspect ownership using:

```bash
ls -l /path/to/file
```

or:

```bash
stat /path/to/file
```

Ownership is security relevant because the owner can generally modify the object's permission bits, subject to filesystem and kernel rules.

Important questions include:

```text
Who owns the file?

Who owns the directory?

Can ownership be changed?

Can permissions be changed?

Does a privileged process trust the resource?
```

A root-owned file is not automatically protected if its containing directory can be manipulated by a lower-privileged user.

---

# 15. chown and chmod

Permission modification is commonly performed using:

```bash
chmod
```

Ownership modification uses:

```bash
chown
```

Examples for understanding syntax:

```bash
chmod 640 example.conf
chmod u+rw example.conf
chmod g+r example.conf
```

Ownership:

```bash
chown user:group example.conf
```

These operations normally require appropriate ownership or privilege.

During an assessment, do not change production permissions merely to demonstrate that permission modification is possible.

Instead determine whether the current user has the necessary authority.

---

# 16. umask

The process `umask` influences permissions assigned when new files and directories are created.

Display it:

```bash
umask
```

Symbolic representation:

```bash
umask -S
```

Example:

```text
0022
```

A `umask` should not be evaluated in isolation.

Its security significance depends on:

```text
Application

Created resource

Parent directory

Ownership

Default ACLs

Data sensitivity
```

---

# 17. Special Permission Bits

Linux supports additional permission bits:

```text
SUID

SGID

Sticky bit
```

They are represented numerically as:

```text
SUID   = 4000
SGID   = 2000
Sticky = 1000
```

These bits have different behavior depending on whether they are applied to files or directories.

---

# 18. Sticky Bit

The sticky bit is commonly used on shared writable directories.

Example:

```bash
ls -ld /tmp
```

Typical output:

```text
drwxrwxrwt
```

The final:

```text
t
```

indicates the sticky bit.

Without additional protections, a writable directory could permit users to remove or rename entries owned by other users.

The sticky bit restricts such operations according to Linux filesystem rules.

Therefore:

```text
World-Writable Directory
```

and:

```text
World-Writable Directory + Sticky Bit
```

should not be treated as equivalent configurations.

---

# 19. SUID and SGID Context

SUID and SGID executable analysis is covered in detail in [SUID and SGID](suid-sgid.md).

During filesystem analysis, identify the bits using:

```bash
ls -l /path/to/file
```

SUID example:

```text
-rwsr-xr-x
```

SGID example:

```text
-rwxr-sr-x
```

The existence of these bits does not automatically represent a vulnerability.

They become security relevant when the executable exposes functionality that allows an unintended security boundary to be crossed.

---

# 20. Find World-Writable Files

A targeted search can identify world-writable files.

```bash
find / -xdev -type f -perm -0002 -print 2>/dev/null
```

The `-xdev` option prevents crossing into other mounted filesystems during that particular search.

Potential results require manual validation.

Do not report:

```text
World-writable file found
```

without determining:

```text
What is the file?

Who owns it?

Why is it writable?

Who uses it?

Does a privileged process consume it?

Can security-sensitive behaviour be influenced?
```

---

# 21. Find World-Writable Directories

```bash
find / -xdev -type d -perm -0002 -print 2>/dev/null
```

Expected results may include:

```text
/tmp

/var/tmp
```

depending on the system.

These are normally designed to support shared temporary storage.

The presence of a world-writable directory is not itself sufficient evidence of a weakness.

Focus on unexpected writable directories used by:

```text
Privileged services

Scheduled jobs

Deployment tooling

Backup software

Administrative scripts

Security tooling

Custom applications
```

---

# 22. Find Files Writable by the Current User

For targeted locations, `find` can help identify writable files.

Example:

```bash
find /opt /usr/local /srv -type f -writable -print 2>/dev/null
```

Writable directories:

```bash
find /opt /usr/local /srv -type d -writable -print 2>/dev/null
```

Targeted searches are generally preferable to scanning:

```text
/
```

without a reason.

Large filesystem scans can:

```text
Generate significant output

Cause unnecessary I/O

Traverse sensitive areas

Interact with unusual filesystems

Create operational noise
```

---

# 23. High-Value Filesystem Locations

Locations worth understanding commonly include:

```text
/etc
/opt
/usr/local
/srv
/var
/var/www
/home
/root
/tmp
/var/tmp
```

Their importance depends on the host role.

For example:

```text
/opt
```

often contains third-party or custom applications.

```text
/usr/local
```

often contains locally installed software.

```text
/srv
```

may contain service-specific data.

```text
/var/www
```

commonly contains web application resources.

Do not assume that a location is security sensitive solely because of its path.

---

# 24. Privileged Service Resources

Service-related files are particularly important.

For systemd services, identify the service:

```bash
systemctl status example.service
```

Inspect the unit:

```bash
systemctl cat example.service
```

Look for directives such as:

```text
ExecStart=
ExecStartPre=
ExecStartPost=
ExecReload=
Environment=
EnvironmentFile=
WorkingDirectory=
```

Suppose:

```text
ExecStart=/opt/vendor/bin/service
```

Inspect:

```bash
namei -l /opt/vendor/bin/service
```

and:

```bash
getfacl /opt/vendor/bin/service
```

Also inspect:

```text
Configuration files

Environment files

Scripts

Parent directories

Plugins

Modules

Libraries
```

A root service is not a finding.

A lower-privileged user being able to modify a resource executed or loaded by that root service can be security relevant.

See [Linux Services](services.md).

---

# 25. Scheduled Job Resources

Filesystem permissions should also be correlated with scheduled jobs.

Review:

```bash
cat /etc/crontab
```

System cron directories may include:

```text
/etc/cron.d/
/etc/cron.hourly/
/etc/cron.daily/
/etc/cron.weekly/
/etc/cron.monthly/
```

systemd timers:

```bash
systemctl list-timers --all
```

If a scheduled job references:

```text
/opt/application/backup.sh
```

inspect:

```bash
namei -l /opt/application/backup.sh
```

and:

```bash
getfacl /opt/application/backup.sh
```

Assessment relationship:

```text
Scheduled Job
       |
       v
Execution UID
       |
       v
Script / Executable
       |
       v
Filesystem Permissions
       |
       v
Can Current User Influence It?
```

See [Scheduled Jobs](scheduled-jobs.md).

---

# 26. Configuration Files

Privileged applications frequently consume configuration files.

Examples:

```text
/etc/application.conf

/opt/vendor/config.ini

/etc/default/application

/etc/sysconfig/application

Application-specific YAML / JSON files
```

Inspect:

```bash
stat /path/to/config
```

```bash
getfacl /path/to/config
```

A writable configuration file can be security relevant when:

```text
Lower-Privileged User
        |
        v
Modifies Configuration
        |
        v
Privileged Application Reads Configuration
        |
        v
Security-Sensitive Behaviour Changes
```

Do not modify the production configuration merely to prove writability.

---

# 27. Executable Scripts

Scripts used by privileged processes deserve particular attention.

Common interpreters include:

```text
sh
bash
python
python3
perl
ruby
php
```

Suppose a privileged job executes:

```text
/usr/local/bin/maintenance.sh
```

Inspect:

```bash
stat /usr/local/bin/maintenance.sh
```

```bash
namei -l /usr/local/bin/maintenance.sh
```

```bash
getfacl /usr/local/bin/maintenance.sh
```

Also determine whether the script references additional files.

For example:

```text
Configuration

Helper scripts

Executable commands

Environment files

Plugins

Libraries
```

A protected top-level script can still depend on a lower-privileged resource.

---

# 28. PATH and Executable Search

Filesystem permissions interact with PATH-based execution.

Display:

```bash
printf '%s\n' "$PATH" | tr ':' '\n'
```

Inspect a relevant directory:

```bash
ls -ld /usr/local/bin
```

A meaningful PATH-related condition generally requires:

```text
Privileged Process
        |
        v
Executes Command Without Absolute Path
        |
        v
Searches PATH
        |
        v
Writable Directory Appears Before Legitimate Binary
        |
        v
Lower-Privileged User Can Influence Resolution
```

A writable PATH entry alone is not sufficient evidence.

You must establish the privileged consumer.

---

# 29. Shell Scripts and Relative Commands

Consider a privileged script containing:

```bash
backup-tool --run
```

instead of:

```bash
/usr/local/sbin/backup-tool --run
```

This may require additional investigation into the execution environment.

Determine:

```text
Which PATH is used?

Which user executes the script?

Where is the legitimate executable?

Are earlier PATH directories writable?

Does the shell resolve aliases or functions?

Is the environment sanitised?
```

Do not place replacement executables into production paths merely to test this relationship.

Use permission and configuration evidence first.

---

# 30. Library and Module Search Paths

Applications can load code from additional locations.

Examples can include:

```text
Shared libraries

Python modules

Perl modules

Plugins

Application modules
```

The security question is not simply whether a module directory is writable.

Determine:

```text
Does a privileged application load from it?

Which file is expected?

What is the search order?

Can the current user create or modify the expected resource?

Does another security control restrict loading?
```

Avoid creating malicious libraries or modules during routine validation.

---

# 31. Symbolic Links

Symbolic links can affect how paths are resolved.

Identify them with:

```bash
ls -l /path
```

Resolve a path:

```bash
readlink -f /path/to/link
```

Example:

```bash
readlink -f /opt/application/current/config.ini
```

When analysing a privileged resource, determine whether any component is a symbolic link.

```text
Privileged Process
        |
        v
References Path
        |
        v
Symbolic Link
        |
        v
Actual Target
```

Inspect permissions on the actual target and its parent directories.

---

# 32. Symlink Security Context

A symbolic link is not inherently vulnerable.

Security relevance depends on:

```text
Who creates the link?

Who follows the link?

Which resource is targeted?

What protections are present?

Can the path be changed between validation and use?

Which filesystem and kernel protections apply?
```

Symlink and race-condition issues can become complex.

Avoid destructive attempts to redirect privileged writes during routine testing unless explicitly authorised and operationally safe.

---

# 33. Hard Links

Hard links are directory entries referring to the same inode.

Inspect inode information:

```bash
ls -li /path/to/file
```

Hard-link behavior is affected by:

```text
Filesystem

Ownership

Kernel protections

Directory permissions
```

Modern Linux systems can implement hard-link protections through kernel settings.

For example:

```bash
sysctl fs.protected_hardlinks
```

Do not infer vulnerability merely from the ability to create normal hard links within user-controlled resources.

---

# 34. Symlink Protections

Relevant kernel protections may include:

```bash
sysctl fs.protected_symlinks
```

and:

```bash
sysctl fs.protected_hardlinks
```

Their significance depends on the filesystem operation being assessed.

These controls are defense-in-depth and should be interpreted together with:

```text
Directory permissions

Sticky bit

Application behaviour

Privilege context
```

---

# 35. Temporary Directories

Common temporary directories include:

```text
/tmp
/var/tmp
```

User-specific temporary locations may also exist.

Inspect:

```bash
ls -ld /tmp /var/tmp
```

Typical `/tmp` permissions may resemble:

```text
drwxrwxrwt
```

The sticky bit is important.

Security concerns arise when privileged software handles temporary resources unsafely, for example by relying on predictable or untrusted paths.

Do not treat the existence of shared temporary storage as a vulnerability.

---

# 36. Mount Options

Filesystem behavior can be influenced by mount options.

Inspect:

```bash
findmnt
```

Focused output:

```bash
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

Potentially relevant options include:

```text
ro
rw
nosuid
nodev
noexec
```

Interpretation:

| Option | General Purpose |
|---|---|
| `ro` | Read-only mount |
| `rw` | Read/write mount |
| `nosuid` | Restrict SUID/SGID effects on that mount |
| `nodev` | Do not interpret device special files |
| `noexec` | Restrict direct execution from the filesystem |

These options are defense-in-depth.

For example:

```text
noexec
```

does not mean arbitrary content on that filesystem can never influence execution through every possible interpreter or application behavior.

Likewise, absence of `noexec` is not automatically a vulnerability.

---

# 37. Network Filesystems

Remote filesystems can introduce additional trust relationships.

Examples include:

```text
NFS

CIFS / SMB

Distributed filesystems

Cloud-backed mounts
```

Inspect:

```bash
findmnt
```

Review:

```text
Remote source

Mount point

Filesystem type

Mount options

Ownership mapping

Permissions

Credential handling

Privileged consumers
```

Filesystem permissions should not be interpreted without considering the remote filesystem's access-control model.

---

# 38. NFS Context

NFS introduces security considerations beyond local Unix permissions.

During assessment, determine:

```text
Which NFS shares are mounted?

Which server provides them?

Which mount options apply?

How are UIDs and GIDs mapped?

What resources are stored there?

Which privileged processes use them?
```

Do not assume that local ownership values alone describe the complete security model.

---

# 39. Sensitive Files

Linux systems contain many files that may be security sensitive.

Examples include:

```text
/etc/passwd
/etc/shadow
/etc/sudoers
/etc/ssh/sshd_config
/root/.ssh/
/etc/systemd/system/
/etc/cron.d/
```

Application-specific sensitive resources can include:

```text
.env files

Database configuration

Private keys

API credentials

Deployment configuration

Backup configuration

Cloud credentials
```

The security issue may involve:

```text
Unauthorised read access

Unauthorised modification

Insecure ownership

Overly broad ACLs

Privileged consumer relationships
```

See [Linux Credentials](credentials.md).

---

# 40. `/etc/passwd` and `/etc/shadow`

Inspect metadata:

```bash
ls -l /etc/passwd /etc/shadow
```

Typical configurations restrict `/etc/shadow` significantly more than `/etc/passwd`.

The assessment should focus on whether the current user has unexpected:

```text
Read access

Write access

Ownership

ACL permissions
```

Do not modify authentication databases during routine validation.

Use metadata and non-destructive access checks.

---

# 41. SSH Private Keys

Search only appropriate user or application locations.

For the current user:

```bash
find "$HOME" -type f \( -name 'id_rsa' -o -name 'id_ed25519' -o -name 'id_ecdsa' \) -print 2>/dev/null
```

Inspect permissions:

```bash
ls -l ~/.ssh
```

Potential issues include:

```text
Private key readable by unintended users

Shared key material

Backup copies

Keys stored in application directories
```

Do not copy private keys unless necessary and explicitly permitted by the engagement evidence-handling requirements.

---

# 42. Application Secrets

Targeted searches can identify potentially sensitive application configuration.

Example:

```bash
find /var/www /opt /srv -type f \( \
    -name '.env' -o \
    -name '*.conf' -o \
    -name '*.ini' -o \
    -name '*.yml' -o \
    -name '*.yaml' \
\) -print 2>/dev/null
```

Do not immediately dump every matching file.

First determine:

```text
Is the file relevant?

Does the current user legitimately require access?

Could it contain sensitive data?

Is reading it within scope?
```

This reduces unnecessary exposure of sensitive information.

---

# 43. Backup Files

Potential backup patterns include:

```text
*.bak
*.backup
*.old
*~
```

Target a relevant application directory:

```bash
find /opt/application -type f \( \
    -name '*.bak' -o \
    -name '*.backup' -o \
    -name '*.old' \
\) -print 2>/dev/null
```

A backup file becomes security relevant when it exposes:

```text
Credentials

Private keys

Configuration secrets

Old application code

Sensitive operational data
```

---

# 44. Privileged Group Relationships

Filesystem access may derive from group membership.

Examples of groups that can be security sensitive depending on the system include:

```text
docker
lxd
disk
adm
systemd-journal
libvirt
```

Do not report membership alone.

Determine:

```text
Which resources does the group control?

Can the group read sensitive information?

Can it modify privileged resources?

Can it influence a privileged service?

Does the access cross the intended security boundary?
```

---

# 45. File Capabilities

Capabilities are covered separately in [Linux Capabilities](capabilities.md), but filesystem analysis should identify whether an executable carries capabilities.

Example:

```bash
getcap /path/to/binary
```

Recursive enumeration:

```bash
getcap -r / 2>/dev/null
```

File capability analysis should include:

```text
Binary

Owner

Permissions

Capability

Who can execute it?

Who can modify it?

Why does it require the capability?
```

---

# 46. Immutable and Extended Attributes

Linux files can have filesystem-specific extended attributes.

Where supported, inspect attributes with:

```bash
lsattr /path/to/file
```

An immutable attribute may appear as:

```text
i
```

Do not assume Unix mode bits alone determine whether an operation can succeed.

Extended attributes, filesystem type, mount state and security modules can affect behavior.

---

# 47. SELinux Context

SELinux can impose additional access-control restrictions beyond traditional Unix permissions.

Where available:

```bash
ls -Z /path/to/file
```

Example:

```bash
ls -Z /var/www/html
```

SELinux state:

```bash
getenforce
```

Possible states commonly include:

```text
Enforcing
Permissive
Disabled
```

A file appearing writable through Unix permissions does not necessarily mean every process can use it in every way when mandatory access controls apply.

See [Linux Security Controls](security-controls.md).

---

# 48. AppArmor Context

AppArmor can also restrict application access beyond traditional Unix permissions.

Where available:

```bash
aa-status
```

When evaluating a filesystem-related attack path, determine whether the privileged consumer is subject to an AppArmor profile.

Filesystem permissions answer:

```text
Can the Unix identity access this resource?
```

Mandatory access controls can add another question:

```text
Is this process allowed to access the resource under its security policy?
```

---

# 49. Effective Access

The effective result of a filesystem operation can depend on multiple layers.

```text
Current UID / GID
        |
        v
Traditional Mode Bits
        |
        v
POSIX ACL
        |
        v
Directory Traversal
        |
        v
Mount State / Options
        |
        v
Mandatory Access Control
        |
        v
Filesystem-Specific Behaviour
        |
        v
Effective Access
```

This is why a simple:

```bash
ls -l
```

should not always be treated as the final answer.

---

# 50. Permission Analysis Workflow

Use the following workflow when a potentially interesting filesystem resource is identified.

```text
Identify Resource
        |
        v
Determine Current Identity
        |
        v
Inspect File Type
        |
        v
Inspect Owner / Group
        |
        v
Inspect Mode Bits
        |
        v
Inspect ACL
        |
        v
Inspect Parent Directories
        |
        v
Resolve Symlinks
        |
        v
Check Mount Context
        |
        v
Identify Consumer
        |
        v
Determine Consumer UID / GID
        |
        v
Determine Whether Resource Is Trusted
        |
        v
Perform Safe Validation
        |
        v
Collect Evidence
```

---

# 51. Practical Validation - Writable Directory

## Scenario

Enumeration identifies:

```text
/opt/vendor/scripts
```

as potentially writable.

## Establish Context

```bash
id
```

## Inspect the Directory

```bash
ls -ld /opt/vendor/scripts
```

```bash
stat /opt/vendor/scripts
```

```bash
getfacl /opt/vendor/scripts
```

## Inspect the Path

```bash
namei -l /opt/vendor/scripts
```

## Controlled Write Test

```bash
test_dir="/opt/vendor/scripts"
test_file="$test_dir/.permission-test-$$"

if touch "$test_file" 2>/dev/null; then
    echo "[+] Controlled file creation succeeded"
    ls -l "$test_file"
    rm -f "$test_file"
else
    echo "[-] Controlled file creation failed"
fi
```

## Interpretation

A successful test proves:

```text
Current security context can create a file in the directory.
```

It does not prove:

```text
Current user can become root.
```

Further validation is required.

---

# 52. Identify the Privileged Consumer

Suppose the directory contains:

```text
backup.sh
```

Search for references in relevant service and scheduler configuration.

For systemd:

```bash
grep -R "/opt/vendor/scripts/backup.sh" /etc/systemd/system /usr/lib/systemd/system /lib/systemd/system 2>/dev/null
```

For cron:

```bash
grep -R "/opt/vendor/scripts/backup.sh" /etc/crontab /etc/cron.d 2>/dev/null
```

If a root-controlled scheduler references the script, the relationship becomes more significant.

Confirm the execution identity independently.

Do not assume that the existence of a reference means it is currently active.

---

# 53. Representative Positive Result

A validated condition might look like:

```text
Current user:
analyst
UID:
1001

Resource:
/opt/vendor/scripts

Permission:
Group developers has rwx

Current user groups:
developers

Privileged consumer:
backup.service

Execution identity:
root

Referenced script:
/opt/vendor/scripts/backup.sh
```

Relationship:

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
/opt/vendor/scripts
   |
   v
backup.sh
   |
   v
backup.service
   |
   v
root
```

This supports a meaningful privilege-boundary finding if the user can actually influence the resource consumed by the privileged service.

---

# 54. Representative Negative Result

Suppose:

```text
/opt/vendor/cache
```

is writable.

Further investigation shows:

```text
No privileged service references it.

No scheduled job uses it.

Files are only consumed by the current user's application.

No security-sensitive data is present.
```

The appropriate conclusion may be:

```text
Write access confirmed, but no privileged or security-sensitive consumer
was identified. The observation does not currently demonstrate a privilege
escalation condition.
```

This is an important outcome.

Not every interesting permission should become a finding.

---

# 55. False Positives and Alternative Explanations

Common false positives include:

```text
Expected /tmp permissions

Application cache directories

User-owned working directories

Writable log directories with no executable consumer

Container filesystems interpreted as host resources

Development directories intentionally writable by developers

ACL mask reducing apparently broad ACL permissions

Protected privileged file inside an apparently interesting path

Read-only filesystem

Inactive service configuration

Disabled scheduled job
```

Also consider:

```text
SELinux

AppArmor

Mount namespaces

Containers

Filesystem namespaces

Network filesystem semantics
```

before reaching a conclusion.

---

# 56. Automated Enumeration

Automated tools can help identify candidate permission issues.

Examples include:

```text
LinPEAS

LinEnum

linux-smart-enumeration
```

These tools can identify:

```text
Writable files

Writable directories

SUID binaries

Capabilities

Scheduled jobs

Interesting configuration

Credential material
```

However:

```text
Automated Finding
       |
       v
Candidate
       |
       v
Manual Validation
       |
       v
Context
       |
       v
Security Conclusion
```

Never copy automated tool output directly into a report without validation.

---

# 57. Avoid Noisy Full-Filesystem Searches

Commands such as:

```bash
find / ...
```

can be useful but may create substantial filesystem activity.

Prefer targeted locations such as:

```text
/opt
/usr/local
/srv
/etc
/var/www
```

when the system role suggests they are relevant.

This provides:

```text
Less noise

Less I/O

More relevant output

Lower operational impact

Faster analysis
```

---

# 58. Evidence Collection

For a filesystem permission finding, record:

```text
Hostname

Distribution

Current user

UID

GID

Groups

Affected path

File type

Owner

Group

Mode

ACL

Parent directory permissions

Resolved path

Mount information

Privileged consumer

Consumer UID

Command used

Observed result

Validation method
```

Example evidence commands:

```bash
id
```

```bash
stat /opt/vendor/scripts/backup.sh
```

```bash
getfacl /opt/vendor/scripts/backup.sh
```

```bash
namei -l /opt/vendor/scripts/backup.sh
```

Then capture evidence of the privileged consumer separately.

---

# 59. Reporting

Avoid reporting:

> `/opt/vendor` is writable.

Prefer:

> The `developers` group has write access to `/opt/vendor/scripts`, and the assessed user is a member of that group. The directory contains `backup.sh`, which is referenced by a systemd service executing as root. This allows a lower-privileged user to influence a resource consumed within a root execution context.

This explains:

```text
Who

What

Permission

Privileged consumer

Security boundary

Impact
```

---

# 60. Example Finding Structure

## Observation

The assessed user has write access to a directory containing a script used by a privileged service.

## Affected Resource

```text
/opt/vendor/scripts/backup.sh
```

## Current Security Context

```text
User: analyst
UID: 1001
Group: developers
```

## Privileged Consumer

```text
backup.service
```

running as:

```text
root
```

## Security Impact

The permission relationship allows a lower-privileged principal to influence a resource consumed by a higher-privileged process.

## Evidence

Capture:

```text
id

stat output

ACL

Parent directory permissions

Service configuration

Service execution identity
```

## Recommendation

Restrict modification of privileged service resources to trusted administrative principals.

---

# 61. Remediation

Filesystem permission remediation should address the underlying trust relationship.

Possible measures include:

```text
Remove unnecessary write permissions

Correct file ownership

Correct directory ownership

Restrict group membership

Remove unnecessary ACL entries

Protect privileged executables

Protect privileged scripts

Protect configuration files

Protect parent directories

Use dedicated service accounts

Separate writable data from executable resources
```

Avoid simply applying:

```text
chmod 700
```

to everything.

Permissions must continue to support legitimate application functionality.

---

# 62. Separate Code and Writable Data

A useful hardening principle is to separate:

```text
Executable / Trusted Code
```

from:

```text
Application-Writable Data
```

For example:

```text
/opt/vendor/bin/
    |
    +---- Administrator controlled
    +---- Application executables

/var/lib/vendor/
    |
    +---- Application writable
    +---- Runtime data
```

This reduces the chance that a service account or application user can modify code that later executes with higher privilege.

---

# 63. Retesting

After remediation, repeat the original validation.

Inspect:

```bash
stat /path/to/resource
```

```bash
getfacl /path/to/resource
```

```bash
namei -l /path/to/resource
```

Then verify controlled access.

For a directory:

```bash
test_dir="/path/to/directory"
test_file="$test_dir/.permission-retest-$$"

if touch "$test_file" 2>/dev/null; then
    echo "[!] Write access still exists"
    rm -f "$test_file"
else
    echo "[+] Controlled file creation is no longer permitted"
fi
```

Also confirm:

```text
Application still functions

Service still starts

Scheduled job still executes

Required users retain legitimate access

Security-sensitive resource is protected
```

---

# Linux Filesystem Permission Checklist

## Identity

- [ ] Identify current user
- [ ] Record UID
- [ ] Record GID
- [ ] Review supplementary groups
- [ ] Review sudo context where relevant

## Basic Permissions

- [ ] Inspect file type
- [ ] Inspect owner
- [ ] Inspect group
- [ ] Inspect mode
- [ ] Inspect numeric permissions
- [ ] Distinguish file and directory rights

## ACLs

- [ ] Inspect POSIX ACLs
- [ ] Review named users
- [ ] Review named groups
- [ ] Review ACL mask
- [ ] Review default ACLs on directories

## Path

- [ ] Inspect parent directory
- [ ] Inspect every relevant path component
- [ ] Resolve symbolic links
- [ ] Inspect actual target
- [ ] Consider hard links where relevant

## Writable Resources

- [ ] Identify writable files
- [ ] Identify writable directories
- [ ] Identify unexpected world-writable resources
- [ ] Distinguish expected temporary locations
- [ ] Use controlled test files where necessary
- [ ] Avoid modifying production resources

## Privileged Consumers

- [ ] Correlate resources with services
- [ ] Correlate resources with scheduled jobs
- [ ] Correlate resources with administrative scripts
- [ ] Correlate resources with privileged applications
- [ ] Determine execution UID
- [ ] Determine execution GID
- [ ] Confirm the resource is actually consumed

## Sensitive Files

- [ ] Review privileged configuration
- [ ] Review SSH material
- [ ] Review application secrets
- [ ] Review backup files
- [ ] Review authentication files
- [ ] Avoid unnecessary secret exposure

## Special Permissions

- [ ] Review SUID
- [ ] Review SGID
- [ ] Review sticky bit
- [ ] Review file capabilities where relevant
- [ ] Review extended attributes where relevant

## Filesystems

- [ ] Review mount points
- [ ] Review mount options
- [ ] Identify network filesystems
- [ ] Consider container or namespace context
- [ ] Consider read-only filesystems

## Security Controls

- [ ] Consider SELinux
- [ ] Consider AppArmor
- [ ] Consider kernel symlink protections
- [ ] Consider hard-link protections
- [ ] Consider filesystem-specific behavior

## Validation

- [ ] Confirm effective access
- [ ] Identify privileged consumer
- [ ] Confirm consumer identity
- [ ] Identify false positives
- [ ] Perform safe validation
- [ ] Clean up test artifacts

## Reporting

- [ ] Record current identity
- [ ] Record affected resource
- [ ] Record owner and group
- [ ] Record permissions
- [ ] Record ACL
- [ ] Record parent permissions
- [ ] Record privileged consumer
- [ ] Explain security boundary
- [ ] Provide root-cause remediation
- [ ] Define retest procedure

---

# Quick Permission Assessment Workflow

```text
Interesting File / Directory
          |
          v
       id
          |
          v
       stat
          |
          v
      getfacl
          |
          v
      namei -l
          |
          v
Resolve Symlinks
          |
          v
Check Mount Context
          |
          v
Can Current User Influence It?
          |
       +--+--+
       |     |
      No    Yes
       |     |
       v     v
   Record   Identify Consumer
                 |
                 v
         Consumer Privileged?
                 |
              +--+--+
              |     |
             No    Yes
              |     |
              v     v
          Low Risk  Confirm Use
                         |
                         v
                  Safe Validation
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

## File Permissions

```bash
ls -l /path/to/file
stat /path/to/file
stat -c '%A %a %U %G %n' /path/to/file
```

## Directory Permissions

```bash
ls -ld /path/to/directory
stat /path/to/directory
```

## Complete Path

```bash
namei -l /path/to/file
```

## ACLs

```bash
getfacl /path/to/file
```

## Access Checks

```bash
test -r /path/to/file && echo "Readable"
test -w /path/to/file && echo "Writable"
test -x /path/to/file && echo "Executable"
```

## World-Writable Files

```bash
find / -xdev -type f -perm -0002 -print 2>/dev/null
```

## World-Writable Directories

```bash
find / -xdev -type d -perm -0002 -print 2>/dev/null
```

## Targeted Writable Files

```bash
find /opt /usr/local /srv -type f -writable -print 2>/dev/null
```

## Targeted Writable Directories

```bash
find /opt /usr/local /srv -type d -writable -print 2>/dev/null
```

## SUID

```bash
find / -xdev -type f -perm -4000 -print 2>/dev/null
```

## SGID

```bash
find / -xdev -type f -perm -2000 -print 2>/dev/null
```

## Capabilities

```bash
getcap -r / 2>/dev/null
```

## Symbolic Links

```bash
readlink -f /path/to/link
```

## Extended Attributes

```bash
lsattr /path/to/file
```

## Mounts

```bash
findmnt
findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS
```

## SELinux Context

```bash
ls -Z /path/to/file
getenforce
```

---

# Related Notes

- [Linux Overview](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

The following Linux pages build further on the permission relationships described here:

```text
sudo.md
scheduled-jobs.md
suid-sgid.md
capabilities.md
security-controls.md
```

---

# Filesystem Permission Testing Mindset

Do not think:

```text
Writable = Vulnerable

World-Writable = Privilege Escalation

Root-Owned = Protected

755 = Secure

777 = Exploitable

ACL Entry = Effective Permission

SUID = Vulnerable

noexec = Execution Impossible
```

Instead think:

```text
Who Am I?
      |
      v
What Can I Access?
      |
      v
What Can I Modify?
      |
      v
Can I Modify the File or Its Directory Entry?
      |
      v
What Additional ACLs Apply?
      |
      v
What Security Controls Apply?
      |
      v
Who Consumes the Resource?
      |
      v
Under Which UID / GID?
      |
      v
Can My Access Influence Privileged Behaviour?
      |
      v
Can the Relationship Be Safely Validated?
```

That relationship is what turns a filesystem observation into a defensible security finding.

---

# References

- [Linux man-pages - inode](https://man7.org/linux/man-pages/man7/inode.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - path_resolution](https://man7.org/linux/man-pages/man7/path_resolution.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [GNU Coreutils - File Permissions](https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html){ target="_blank" rel="noopener noreferrer" }
- [GNU Coreutils - chmod](https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html){ target="_blank" rel="noopener noreferrer" }
- [GNU Coreutils - chown](https://www.gnu.org/software/coreutils/manual/html_node/chown-invocation.html){ target="_blank" rel="noopener noreferrer" }
- [GNU findutils](https://www.gnu.org/software/findutils/manual/html_mono/find.html){ target="_blank" rel="noopener noreferrer" }
- [Red Hat - Managing File System Permissions](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_basic_system_settings/managing-file-system-permissions_configuring-basic-system-settings){ target="_blank" rel="noopener noreferrer" }
- [Linux Kernel Documentation](https://docs.kernel.org/){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

!!! tip "Inspect the parent directory"

    A file's mode bits are only part of the security relationship. Parent-directory permissions can determine whether directory entries can be created, removed or replaced, so inspect the complete path when assessing privileged resources.

!!! tip "Use controlled probes"

    When practical validation is required, create a separate uniquely named test file and remove it immediately afterward. Do not modify a production executable, script or configuration file simply to demonstrate write access.

!!! tip "Find the consumer"

    The most important step after identifying a writable resource is determining who consumes it. A writable resource becomes significantly more important when a service, scheduled job or other higher-privileged process trusts it.

!!! warning "Writable does not mean vulnerable"

    A standard user being able to write to a file or directory is not by itself evidence of privilege escalation. A defensible finding should demonstrate the relevant trust relationship, privileged consumer and realistic security impact.
