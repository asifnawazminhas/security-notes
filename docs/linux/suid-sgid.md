---
title: Linux SUID and SGID Security
description: Practical Linux SUID and SGID security assessment covering enumeration, permission semantics, privileged binaries, custom executables, GTFOBins, writable resources, PATH and environment dependencies, shared libraries and privilege escalation analysis.
---

# Linux SUID and SGID Security

Linux supports special permission bits that can change the effective identity associated with execution or affect group behavior on directories.

Two important mechanisms are:

```text
SUID - Set User ID

SGID - Set Group ID
```

During an authorised security assessment, SUID and SGID executables deserve particular attention because they can intentionally provide functionality using privileges different from those of the invoking user.

The existence of an SUID or SGID binary is not automatically a vulnerability.

The important question is:

> Does the executable expose functionality, trust relationships or dependencies that allow a lower-privileged user to exceed the intended security boundary?

A useful assessment model is:

```text
Current User
     |
     v
SUID / SGID Executable
     |
     v
Effective Identity
     |
     +---- Program functionality
     +---- Arguments
     +---- Environment
     +---- PATH
     +---- Configuration
     +---- Helper programs
     +---- Libraries
     +---- Files
     |
     v
Can User Influence Privileged Behaviour?
```

!!! warning "Authorised Security Testing"

    Perform SUID and SGID testing only on systems you own or have explicit permission to assess. Prefer enumeration, metadata inspection and non-destructive validation. Do not replace privileged binaries, modify production dependencies or create persistence merely to prove impact.

---

# 1. Unix Identity During Execution

A Linux process can have several identity values.

Important concepts include:

```text
Real UID
Effective UID
Saved Set-User-ID

Real GID
Effective GID
Saved Set-Group-ID
```

At a high level:

```text
Real UID
    |
    +---- Identity of the user that started the process

Effective UID
    |
    +---- Identity commonly used for permission checks
```

SUID can cause the effective user ID associated with execution to be derived from the executable file's owner, subject to operating system rules.

SGID can similarly affect the effective group ID.

This is why a root-owned SUID executable requires careful review.

---

# 2. SUID

SUID means:

```text
Set User ID
```

The numeric special permission value is:

```text
4000
```

An SUID executable can appear as:

```text
-rwsr-xr-x
```

Notice:

```text
s
```

in the owner's execute position.

Example:

```bash
ls -l /usr/bin/passwd
```

A system may show something similar to:

```text
-rwsr-xr-x 1 root root ... /usr/bin/passwd
```

This is expected on many Linux systems because changing a password requires controlled access to privileged authentication resources.

The important point is:

```text
SUID root != Vulnerability
```

---

# 3. SGID

SGID means:

```text
Set Group ID
```

The numeric special permission value is:

```text
2000
```

An SGID executable can appear as:

```text
-rwxr-sr-x
```

The:

```text
s
```

appears in the group execute position.

When applied to an executable, SGID can cause the process to operate with an effective group identity associated with the executable's group, subject to system semantics.

This can provide access to resources that the invoking user could not otherwise access.

---

# 4. SGID on Directories

SGID has a different and very common use on directories.

Example:

```text
drwxrwsr-x root developers project/
```

For directories, SGID commonly causes newly created entries to inherit the directory's group rather than simply using the creator's primary group.

This is useful for shared working directories.

Therefore:

```text
SGID Directory
```

does not mean:

```text
Privilege Escalation
```

File and directory semantics must be distinguished.

---

# 5. SUID and SGID Numeric Modes

Special permission bits can be represented numerically.

```text
SUID = 4000
SGID = 2000
```

Example:

```text
4755
```

means:

```text
4000 - SUID
0755 - rwxr-xr-x
```

Example:

```text
2755
```

means:

```text
2000 - SGID
0755 - rwxr-xr-x
```

Example:

```text
6755
```

contains both:

```text
SUID + SGID
```

Do not assess security solely from the numeric mode.

---

# 6. Establish the Current Context

Before assessing privileged executables, record the current identity.

```bash
whoami
id
groups
```

Example:

```text
uid=1001(analyst) gid=1001(analyst) groups=1001(analyst),1002(developers)
```

Record:

```text
Username

UID

Primary GID

Supplementary groups

sudo permissions
```

This allows you to determine whether the SUID or SGID execution context provides access beyond what the user already possesses.

---

# 7. Enumerate SUID Executables

A common enumeration command is:

```bash
find / -xdev -type f -perm -4000 -print 2>/dev/null
```

This searches the current filesystem for regular files with the SUID bit set.

The:

```text
-xdev
```

option prevents `find` from descending into other mounted filesystems during that search.

If other filesystems are relevant, inspect them separately.

---

# 8. Enumerate SGID Executables

Use:

```bash
find / -xdev -type f -perm -2000 -print 2>/dev/null
```

This identifies regular files with SGID set.

Again, results require manual analysis.

A long list of SUID or SGID executables does not mean the system contains multiple privilege escalation vulnerabilities.

---

# 9. Enumerate Both SUID and SGID

A combined search can be performed with:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null
```

For each result, determine:

```text
Path

Owner

Group

Mode

File type

Package

Purpose

Whether it is expected

Whether it is custom

Whether it is writable

Dependencies

Security-sensitive functionality
```

---

# 10. Display Useful Metadata

Instead of collecting only filenames:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) \
    -exec stat -c '%A %a %U %G %n' {} \; 2>/dev/null
```

Representative output:

```text
-rwsr-xr-x 4755 root root /usr/bin/example
-rwxr-sr-x 2755 root shadow /usr/bin/example2
```

This immediately exposes:

```text
Permissions

Numeric mode

Owner

Group

Path
```

---

# 11. Inspect an Individual Binary

For an interesting result:

```bash
ls -l /path/to/binary
```

```bash
stat /path/to/binary
```

```bash
getfacl /path/to/binary
```

```bash
namei -l /path/to/binary
```

Determine:

```text
Who owns it?

Which group owns it?

Is SUID present?

Is SGID present?

Can the current user modify it?

Can the parent directory be modified?

Are ACLs present?
```

---

# 12. Identify the File Type

Use:

```bash
file /path/to/binary
```

Potential results include:

```text
ELF executable

Shell script

Python script

Perl script

Symbolic link

Other data
```

For ELF files, architecture and linkage information may also be useful.

Example:

```bash
file /usr/local/bin/custom-helper
```

Understanding the file type determines which additional analysis techniques are appropriate.

---

# 13. SUID Scripts

Modern Linux systems generally do not treat the SUID bit on interpreted scripts in the same way as SUID native executables.

Therefore, finding:

```text
-rwsr-xr-x root root script.sh
```

does not by itself mean the script executes with root privileges.

Do not infer behavior from the mode bits alone.

Validate the actual operating system behavior and execution mechanism.

---

# 14. Expected SUID Programs

Many legitimate Linux installations contain SUID programs.

Examples may include utilities related to:

```text
Password changes

User identity transitions

Mounting

Authentication

Privilege delegation
```

The exact list depends on:

```text
Distribution

Installed packages

System role

Configuration
```

Avoid creating a static rule such as:

```text
Any SUID root binary is suspicious.
```

Instead establish a baseline for the host.

---

# 15. Custom SUID Binaries

Custom SUID binaries deserve additional attention.

Examples may appear under:

```text
/usr/local/bin/

/opt/

/srv/

Application-specific directories
```

A useful targeted search is:

```bash
find /usr/local /opt /srv -type f \( -perm -4000 -o -perm -2000 \) \
    -print 2>/dev/null
```

A custom executable may have received less security review than a distribution-provided utility.

This does not automatically make it vulnerable, but it increases assessment priority.

---

# 16. Identify Package Ownership

For distribution-managed binaries, determine which package owns the file.

Debian-based systems:

```bash
dpkg -S /path/to/binary 2>/dev/null
```

RPM-based systems:

```bash
rpm -qf /path/to/binary 2>/dev/null
```

If no package owns a privileged binary, it may be:

```text
Locally compiled

Vendor supplied

Manually installed

Application specific
```

That is useful context for prioritisation.

---

# 17. Compare Against Package Metadata

Where appropriate, package verification can help identify unexpected modification.

On RPM-based systems:

```bash
rpm -V package-name
```

On Debian-based systems, available verification mechanisms depend on installed tooling and package metadata.

Do not assume a locally modified privileged binary is malicious.

Administrators may legitimately deploy custom builds.

Investigate the reason for the difference.

---

# 18. Check Binary Ownership

A privileged executable should normally be controlled by an appropriately trusted principal.

Example:

```bash
stat -c '%A %a %U %G %n' /usr/local/bin/custom-helper
```

Suppose:

```text
-rwsr-xr-x 4755 root root /usr/local/bin/custom-helper
```

The executable itself appears root-controlled.

Now inspect:

```bash
namei -l /usr/local/bin/custom-helper
```

because the parent directory also matters.

---

# 19. Writable SUID Binary

A root-owned SUID executable writable by a lower-privileged user is highly security sensitive.

Check effective write access:

```bash
if test -w /usr/local/bin/custom-helper; then
    echo "[+] Current context reports write access"
else
    echo "[-] Current context does not report write access"
fi
```

Also inspect:

```bash
getfacl /usr/local/bin/custom-helper
```

Do not modify the binary.

The evidence chain may already be sufficient:

```text
Current User
      |
      v
Write Access
      |
      v
Root-Owned SUID Executable
      |
      v
Privileged Execution Context
```

---

# 20. Parent Directory Control

A binary itself may not be writable:

```text
-rwsr-xr-x root root /opt/vendor/bin/helper
```

but inspect:

```bash
namei -l /opt/vendor/bin/helper
```

The complete path could reveal an unexpected writable directory.

Directory-entry manipulation and file-content modification are different permission relationships.

See [Linux Filesystem Permissions](filesystem-permissions.md).

---

# 21. POSIX ACLs

Do not rely only on:

```bash
ls -l
```

Inspect ACLs:

```bash
getfacl /path/to/binary
```

and relevant directories:

```bash
getfacl /path/to/directory
```

A named ACL can provide access not obvious from traditional mode bits.

---

# 22. Symbolic Links

Resolve the path:

```bash
readlink -f /path/to/binary
```

Then inspect:

```bash
namei -l /path/to/binary
```

Determine:

```text
Is the path a symlink?

Who controls the link?

What is the actual target?

Who controls the target?

Can the target change?
```

Always assess the actual object being executed.

---

# 23. SUID Program Functionality

After permissions, the next question is:

> What does the program actually do?

Potential security-sensitive functionality includes:

```text
Execute external programs

Read arbitrary files

Write arbitrary files

Change file ownership

Change permissions

Load plugins

Load configuration

Use environment variables

Invoke interpreters

Process attacker-controlled filenames

Perform privileged network operations
```

A SUID program becomes dangerous when exposed functionality exceeds the intended privileged operation.

---

# 24. Strings as an Initial Clue

For a custom binary, `strings` can provide initial clues.

```bash
strings /usr/local/bin/custom-helper | less
```

Search for interesting references:

```bash
strings /usr/local/bin/custom-helper | grep -E \
'(/bin/|/usr/bin/|/usr/local/|/etc/|/tmp/|system|exec|popen|PATH|HOME|LD_)'
```

Potential discoveries include:

```text
External command names

Configuration paths

Temporary paths

Error messages

Library names

Environment variables
```

`strings` output is not proof of execution behavior.

Use it to guide deeper analysis.

---

# 25. Dynamic Dependencies

For dynamically linked ELF binaries:

```bash
ldd /path/to/binary
```

This can show shared-library dependencies.

However, treat `ldd` carefully when analysing untrusted executables.

For an unknown or potentially hostile binary, prefer safer static inspection approaches rather than executing mechanisms that may cause code execution depending on the binary and platform behavior.

For normal trusted system binaries in an authorised environment, dependency inspection can still be useful.

---

# 26. readelf

`readelf` can inspect ELF metadata without executing the target.

Example:

```bash
readelf -h /path/to/binary
```

Dynamic section:

```bash
readelf -d /path/to/binary
```

Symbols:

```bash
readelf -s /path/to/binary
```

Potentially useful information includes:

```text
Architecture

ELF type

Shared-library dependencies

RPATH

RUNPATH

Symbols
```

---

# 27. RPATH and RUNPATH

Inspect:

```bash
readelf -d /path/to/binary | grep -E 'RPATH|RUNPATH'
```

If an SUID or SGID binary searches for shared libraries in an unsafe location, additional analysis may be required.

Assessment model:

```text
Privileged Binary
      |
      v
Library Search Path
      |
      v
Writable Directory?
      |
   +--+--+
   |     |
  No    Yes
   |     |
   v     v
Record   Determine Actual Loader Behaviour
```

Do not assume a writable directory automatically results in library hijacking.

Dynamic-loader behavior for privileged executables includes additional security restrictions.

---

# 28. Shared Libraries

For each relevant library dependency, determine:

```text
Library path

Owner

Group

Permissions

ACLs

Parent directory permissions
```

Example:

```bash
stat /usr/local/lib/libvendor.so
```

```bash
getfacl /usr/local/lib/libvendor.so
```

```bash
namei -l /usr/local/lib/libvendor.so
```

A privileged executable should not normally depend on libraries modifiable by untrusted users.

---

# 29. Environment Variables

Privileged execution can change how environment variables are handled.

Do not assume that environment variables affecting ordinary executables will have the same effect on SUID or SGID programs.

The runtime loader and application may apply secure-execution restrictions.

Potential variables still worth understanding include application-specific settings controlling:

```text
Configuration

Plugins

Data files

Temporary directories

External command behavior
```

Validate actual behavior rather than relying on a generic environment-hijacking assumption.

---

# 30. PATH Dependencies

A custom privileged executable may invoke another program.

For example, internal logic may conceptually perform:

```text
backup
```

instead of:

```text
/usr/local/sbin/backup
```

If command lookup uses PATH, determine:

```text
Effective PATH

Search order

Writable directories

Execution identity

Whether environment sanitisation occurs

Whether an absolute path is actually used
```

A meaningful relationship requires more than simply finding a command name in `strings`.

---

# 31. External Command Execution

Common C library functions associated with external command execution include:

```text
system()

popen()

execve()

execl()

execlp()

execvp()
```

Static analysis can help identify references.

Example:

```bash
readelf -Ws /path/to/binary | grep -E 'system|popen|exec'
```

The presence of one of these symbols is not itself a vulnerability.

You must determine:

```text
How it is called

Which command is executed

Whether arguments are user controlled

Whether PATH is involved

Whether privileges are retained
```

---

# 32. Absolute Versus Relative Commands

Compare:

```text
/usr/bin/logger
```

with:

```text
logger
```

An absolute path removes PATH-based lookup for that executable.

However, even an absolute path does not prove the complete operation is secure.

The privileged program may still trust:

```text
Arguments

Configuration

Files

Environment

Plugins

Libraries

Temporary resources
```

---

# 33. User-Controlled Arguments

A SUID program may accept command-line arguments.

Inspect usage:

```bash
/path/to/binary --help
```

only when it is safe and appropriate to execute the binary.

For unknown custom binaries, static inspection may be preferable first.

Questions include:

```text
Can the user choose a filename?

Can the user choose a destination?

Can the user choose a command?

Can options change configuration?

Can arguments cause another program to run?

Can path traversal affect file access?
```

---

# 34. File Read Functionality

A privileged executable that reads files may expose unintended data.

Assessment questions:

```text
Can the user choose the path?

Are paths restricted?

Are symbolic links followed?

Are ownership checks performed?

Can arbitrary privileged files be read?
```

This may create information disclosure without providing arbitrary code execution.

Do not reduce every SUID issue to "root shell".

---

# 35. File Write Functionality

Similarly, privileged file-writing functionality can be dangerous.

Determine:

```text
Can destination path be chosen?

Can existing files be overwritten?

Are symlinks followed?

Are permissions preserved?

Is content attacker controlled?

Are directories restricted?
```

A privileged arbitrary-file-write primitive can have serious impact even if the binary never executes another command.

Avoid overwriting privileged files during routine validation.

---

# 36. Temporary Files

Privileged binaries may use temporary files.

Potential locations include:

```text
/tmp

/var/tmp

Application-specific temporary directories
```

Assess:

```text
Filename predictability

Creation flags

Ownership

Permissions

Symlink handling

Existing-file behavior

Sticky-bit protections
```

Do not assume use of `/tmp` alone is vulnerable.

---

# 37. Configuration Files

A SUID program may load configuration.

Example:

```text
/etc/vendor/helper.conf
```

Inspect:

```bash
stat /etc/vendor/helper.conf
getfacl /etc/vendor/helper.conf
namei -l /etc/vendor/helper.conf
```

Determine what configuration controls.

A writable cosmetic configuration setting is different from a writable setting that controls:

```text
Executable path

Plugin path

File destination

Command

Privilege behavior
```

---

# 38. User Configuration

Privileged programs should be reviewed carefully when they load configuration from user-controlled locations.

Examples might include:

```text
Home directories

Current working directory

Environment-selected paths
```

Assessment questions:

```text
Does the program load user configuration before dropping privileges?

Which settings can be controlled?

Can those settings influence privileged behavior?
```

Do not assume user configuration is loaded simply because the non-SUID version of an application supports it.

---

# 39. Working Directory

A privileged binary may use relative paths.

Determine the current working directory:

```bash
pwd
```

Then inspect whether the binary references resources such as:

```text
./config

./helper

./plugins/

../data/
```

If a privileged executable trusts relative resources from a user-controlled working directory, further analysis may be required.

---

# 40. Privilege Dropping

Well-designed SUID applications may obtain required privilege and then drop it.

A simplified model is:

```text
Start
  |
  v
Elevated Effective Identity
  |
  v
Perform Narrow Privileged Operation
  |
  v
Drop Privilege
  |
  v
Continue Unprivileged
```

Do not assume the process remains privileged for its entire lifetime.

Understanding when privileges are dropped can materially change exploitability.

---

# 41. Real and Effective UID Validation

For a custom application under controlled laboratory conditions, developers can inspect:

```text
getuid()

geteuid()

getgid()

getegid()
```

These expose real and effective identities.

During a black-box assessment, system tracing or debugging may affect SUID behavior and should be used carefully.

Do not assume traced execution behaves identically to normal privileged execution.

---

# 42. Tracing Considerations

Tools such as:

```text
strace

ltrace

gdb
```

can be useful for program analysis.

However, privileged execution introduces additional security restrictions.

Tracing an SUID program may:

```text
Change privilege behavior

Be blocked

Cause privileges to be dropped

Produce behavior different from normal execution
```

Therefore, observations from a traced process must not automatically be treated as proof of normal SUID behavior.

---

# 43. Static Analysis First

For unfamiliar privileged binaries, a good workflow is:

```text
file
 |
 v
stat
 |
 v
readelf
 |
 v
strings
 |
 v
Package Identification
 |
 v
Configuration Review
 |
 v
Controlled Dynamic Analysis if Needed
```

This reduces unnecessary execution of unknown privileged code.

---

# 44. GTFOBins

GTFOBins documents Unix binaries whose legitimate functionality can become security relevant when combined with privilege mechanisms such as:

```text
sudo

SUID

capabilities
```

Use:

[GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }

The correct assessment model is:

```text
SUID Binary Found
       |
       v
Is Binary Known?
       |
       v
Review GTFOBins / Documentation
       |
       v
Does Technique Apply to This Mode?
       |
       v
Does Version / Configuration Matter?
       |
       v
Does It Cross Intended Boundary?
```

A GTFOBins match is a lead, not automatic proof.

---

# 45. SUID and Shell Behavior

Some programs can legitimately invoke a shell or other subprocess.

Whether privileges are retained depends on:

```text
Program

Shell

Invocation

UID handling

Operating system behavior

Privilege dropping
```

Do not assume:

```text
SUID + shell-capable binary = guaranteed root shell
```

Validate the exact context.

---

# 46. Unexpected SUID Copies

An important assessment pattern is an unexpected copy of a normally non-SUID utility with SUID enabled.

Search results should therefore be reviewed for:

```text
Unusual paths

Duplicate utilities

Files under /tmp

Files under home directories

Files under application directories

Recently modified privileged executables
```

Example metadata collection:

```bash
find / -xdev -type f -perm -4000 \
    -printf '%TY-%Tm-%Td %TH:%TM %u %g %m %p\n' 2>/dev/null
```

Timestamps are clues, not proof of malicious activity.

---

# 47. Compare Against Known Baseline

If you have:

```text
Golden image

Configuration-management baseline

Previous assessment output

Package inventory
```

compare the current SUID/SGID set.

This can reveal:

```text
New privileged executables

Removed privileged executables

Permission changes

Unexpected vendor binaries

Local customisations
```

Baseline comparison is generally more useful than declaring every SUID binary suspicious.

---

# 48. Find Recently Modified SUID Files

A targeted example:

```bash
find / -xdev -type f -perm -4000 -mtime -30 -print 2>/dev/null
```

This identifies SUID files whose modification time is within the specified range.

Interpret cautiously.

Legitimate causes include:

```text
Package updates

System upgrades

Application deployment

Administrative maintenance
```

Do not report recent modification as compromise evidence without corroboration.

---

# 49. SGID Group Access

SGID executables may provide access associated with a privileged group.

Example relationship:

```text
analyst
   |
   v
SGID Binary
   |
   v
Effective Group
   |
   v
Protected Resource
```

The target group may control:

```text
Logs

Authentication data

Device files

Application data

Database resources
```

Determine what the group actually grants.

---

# 50. SGID and Sensitive Groups

Do not assume every privileged-looking group means root-equivalent access.

Determine:

```text
Which files are group-owned?

Which devices are accessible?

Which sockets are accessible?

Which application resources are controlled?

Can group access be chained into another privilege boundary?
```

SGID findings may produce confidentiality or integrity impact without UID 0.

---

# 51. SUID and Linux Capabilities

Linux capabilities can provide selected privileged operations without full SUID root behavior.

Therefore, enumeration should consider both:

```text
SUID / SGID
```

and:

```text
File capabilities
```

A system may intentionally replace some SUID functionality with capabilities.

The next dedicated page covers this in depth:

```text
capabilities.md
```

---

# 52. Mount Options

SUID behavior can be affected by mount configuration.

Inspect the filesystem containing a binary:

```bash
findmnt -T /path/to/binary
```

Relevant mount options can include:

```text
nosuid
```

If a filesystem is mounted with `nosuid`, set-user-ID and set-group-ID behavior can be restricted according to the operating system and filesystem semantics.

Therefore:

```text
SUID Bit Present
```

does not always mean:

```text
SUID Behavior Effective
```

---

# 53. Check Mount Context

For an interesting binary:

```bash
findmnt -T /opt/vendor/bin/helper
```

Representative information can include:

```text
TARGET

SOURCE

FSTYPE

OPTIONS
```

Record whether:

```text
nosuid
```

is present.

Mount context is an important false-positive check.

---

# 54. Network Filesystems

SUID and SGID behavior on network filesystems can depend on:

```text
Mount options

Server configuration

Filesystem semantics

UID mapping

Security model
```

Do not assume a privileged bit observed on a remote filesystem behaves identically to one on a local filesystem.

---

# 55. Containers

Container environments can complicate SUID analysis.

A root-owned SUID binary inside a container may provide:

```text
Container root
```

without providing:

```text
Host root
```

Determine:

```text
Am I inside a container?

Which user namespace is used?

Is root mapped?

Which host resources are mounted?

Are privileged devices available?

What is the actual security boundary?
```

Do not report container UID 0 as host compromise without evidence.

---

# 56. User Namespaces

User namespaces can map container or namespace identities to different host identities.

Therefore:

```text
UID 0
```

inside a namespace does not necessarily equal unrestricted host root.

Assessment must identify the actual privilege boundary.

---

# 57. SELinux

SELinux can impose mandatory access controls beyond Unix UID/GID permissions.

Check:

```bash
getenforce 2>/dev/null
```

Possible results include:

```text
Enforcing
Permissive
Disabled
```

A SUID process may still be constrained by SELinux policy.

Do not ignore mandatory access controls when determining effective impact.

---

# 58. AppArmor

Check:

```bash
aa-status 2>/dev/null
```

An AppArmor profile can restrict a privileged program's:

```text
File access

Execution

Network access

Capabilities
```

The presence of SUID does not bypass every other security mechanism.

---

# 59. Core Security Question

For every SUID or SGID binary, ask:

```text
What privilege does it receive?

Why does it need that privilege?

What functionality does it expose?

Can the user control arguments?

Can the user control input files?

Can the user control output paths?

Can the user control configuration?

Can the user control dependencies?

Can the user influence PATH?

Can the user influence libraries?

Does it drop privilege?

Do mount options restrict it?

Do MAC controls restrict it?

Does the resulting capability exceed the intended design?
```

---

# 60. Practical Validation - Custom SUID Binary

## Scenario

Enumeration identifies:

```text
/usr/local/bin/report-helper
```

with:

```text
-rwsr-xr-x root root
```

## Step 1 - Establish Identity

```bash
id
```

## Step 2 - Inspect Metadata

```bash
stat /usr/local/bin/report-helper
```

```bash
getfacl /usr/local/bin/report-helper
```

## Step 3 - Inspect Complete Path

```bash
namei -l /usr/local/bin/report-helper
```

## Step 4 - Determine File Type

```bash
file /usr/local/bin/report-helper
```

## Step 5 - Determine Package Ownership

Debian-based:

```bash
dpkg -S /usr/local/bin/report-helper 2>/dev/null
```

RPM-based:

```bash
rpm -qf /usr/local/bin/report-helper 2>/dev/null
```

## Step 6 - Inspect Static Metadata

```bash
readelf -h /usr/local/bin/report-helper
```

```bash
readelf -d /usr/local/bin/report-helper
```

```bash
strings /usr/local/bin/report-helper | less
```

## Step 7 - Check Mount Context

```bash
findmnt -T /usr/local/bin/report-helper
```

This creates a strong initial evidence set without modifying or exploiting the binary.

---

# 61. Practical Validation - External Command Dependency

## Scenario

Static analysis suggests that a custom root-owned SUID binary invokes:

```text
report-archive
```

without an obvious absolute path.

Do not immediately create a replacement command.

First determine:

```text
Does the string correspond to actual execution?

Which API performs the execution?

What PATH is used?

Does the process retain privilege?

Can the current user write to any relevant PATH directory?
```

Inspect PATH directories where appropriate:

```bash
for d in /usr/local/sbin /usr/local/bin /usr/sbin /usr/bin; do
    stat -c '%A %a %U %G %n' "$d" 2>/dev/null
done
```

A defensible finding requires the complete relationship.

---

# 62. Practical Validation - Writable Configuration

## Scenario

A root-owned SUID application loads:

```text
/opt/vendor/helper.conf
```

Inspect:

```bash
stat /opt/vendor/helper.conf
```

```bash
getfacl /opt/vendor/helper.conf
```

```bash
namei -l /opt/vendor/helper.conf
```

Then determine which settings are consumed.

Do not modify the production configuration merely to prove write access.

A finding requires evidence that the writable setting can influence privileged behavior.

---

# 63. Practical Validation - SGID Resource Access

## Scenario

An SGID executable is owned by:

```text
root:reports
```

and executes with effective group:

```text
reports
```

Determine which resources are accessible to that group.

Example:

```bash
find /var/lib/reports -maxdepth 2 -group reports -ls 2>/dev/null
```

Assess whether the executable exposes access beyond its intended function.

The issue may involve:

```text
Unauthorised reading

Unauthorised modification

Credential exposure

Indirect privilege escalation
```

---

# 64. Representative Positive Result

Suppose:

```text
Current user:
analyst

Binary:
/usr/local/bin/report-helper

Permissions:
-rwsr-xr-x root root

Behavior:
Executes an external helper using PATH lookup

Effective execution:
Privileged

Relevant PATH directory:
/usr/local/vendor/bin

Directory permissions:
Writable by developers

Current user:
Member of developers
```

The relationship is:

```text
analyst
   |
   v
developers
   |
   v
Writable PATH Directory
   |
   v
External Command Resolution
   |
   v
SUID root Binary
   |
   v
Privileged Execution
```

If all components are validated, this can support a privilege escalation finding.

---

# 65. Representative Negative Result

Suppose:

```text
/usr/bin/example
```

is SUID root.

Further assessment shows:

```text
Distribution-managed binary

Expected SUID permission

Protected executable

Protected parent directories

No writable configuration

No unsafe command execution

No user-controlled privileged file operation

Privileges dropped appropriately

Relevant filesystem not unexpectedly writable
```

The correct conclusion may be:

```text
The SUID executable was reviewed and no unintended privilege escalation
condition was identified under the assessed configuration.
```

Do not report it simply because the SUID bit exists.

---

# 66. False Positives

Common false positives include:

```text
Expected distribution SUID binary

SGID shared directory

SUID script whose bit is not effective as assumed

SUID binary on a nosuid filesystem

GTFOBins entry that does not apply to the installed configuration

Binary that drops privilege before dangerous functionality

PATH reference where all search directories are protected

Library search assumption blocked by secure loader behavior

Container root mistaken for host root

SELinux or AppArmor restrictions ignored during analysis
```

Manual validation is essential.

---

# 67. Automated Enumeration

Common enumeration tools can identify SUID and SGID candidates.

Examples include:

```text
LinPEAS

LinEnum

linux-smart-enumeration
```

Use them as candidate generators.

```text
Automated Enumeration
        |
        v
SUID / SGID Candidate
        |
        v
Expected or Unusual?
        |
        v
Permission Review
        |
        v
Functionality Review
        |
        v
Dependency Review
        |
        v
Security Control Review
        |
        v
Manual Validation
```

---

# 68. Compare with GTFOBins

A simple workflow is:

```text
Enumerate SUID
     |
     v
Extract Basenames
     |
     v
Check GTFOBins
     |
     v
Review SUID-Specific Technique
     |
     v
Confirm Local Preconditions
```

Do not blindly execute every technique found online.

Some techniques:

```text
Change files

Spawn shells

Alter permissions

Create persistence

Access sensitive information
```

and may be inappropriate for production validation.

---

# 69. Evidence Collection

For an SUID or SGID finding, capture:

```text
Hostname

Distribution

Kernel

Current user

UID

GID

Groups

Binary path

File type

Owner

Group

Mode

ACL

Parent directory permissions

Mount point

Mount options

Package ownership

Binary purpose

Arguments

Relevant environment

External commands

Configuration dependencies

Library dependencies

Privilege behavior

Security-control context

Validation method
```

Evidence should explain why the executable crosses an intended security boundary.

---

# 70. Evidence Commands

Useful commands include:

```bash
id
```

```bash
stat /path/to/binary
```

```bash
getfacl /path/to/binary
```

```bash
namei -l /path/to/binary
```

```bash
file /path/to/binary
```

```bash
readelf -h /path/to/binary
```

```bash
readelf -d /path/to/binary
```

```bash
findmnt -T /path/to/binary
```

Use only the commands required to support the conclusion.

---

# 71. Reporting

Avoid:

> SUID binary found.

Avoid:

> `/usr/local/bin/helper` runs as root.

Prefer:

> The custom executable `/usr/local/bin/report-helper` is installed with the SUID bit and owned by root. The program performs a privileged operation while resolving an external helper through a search path containing a directory writable by the `developers` group. The assessed `analyst` account is a member of this group, allowing the user to influence code resolution within the privileged execution context.

This explains:

```text
Principal

Privileged mechanism

Executable

Controllable dependency

Execution context

Security impact
```

---

# 72. Example Finding

## Observation

A custom root-owned SUID executable trusts a lower-privileged writable dependency.

## Current User

```text
analyst
```

## Binary

```text
/usr/local/bin/report-helper
```

## Permissions

```text
-rwsr-xr-x root root
```

## Controllable Resource

```text
/usr/local/vendor/bin/
```

## Security Relationship

```text
analyst
   |
   v
developers
   |
   v
Writable Dependency Location
   |
   v
report-helper
   |
   v
SUID root Execution
```

## Impact

A lower-privileged user can influence a resource consumed during a privileged execution path.

## Recommendation

Use trusted absolute paths and ensure all privileged executable dependencies are writable only by trusted administrative principals.

---

# 73. Remediation

SUID and SGID remediation should address the underlying requirement.

Potential measures include:

```text
Remove unnecessary SUID bits

Remove unnecessary SGID bits

Use Linux capabilities where narrower privilege is sufficient

Protect privileged executables

Protect parent directories

Protect configuration

Protect helper programs

Use absolute executable paths

Avoid user-controlled privileged input

Drop privileges as early as possible

Use dedicated service interfaces

Apply SELinux or AppArmor where appropriate
```

Do not remove special bits blindly.

Some system functionality legitimately requires them.

---

# 74. Remove Unnecessary SUID

Administrators can remove SUID with:

```bash
chmod u-s /path/to/binary
```

or numerically by setting an appropriate mode without the `4000` bit.

This should only be done after confirming that the application does not require SUID functionality.

During an assessment, recommend the change rather than altering production permissions yourself unless remediation activity is explicitly in scope.

---

# 75. Remove Unnecessary SGID

For executables:

```bash
chmod g-s /path/to/binary
```

Again, determine whether SGID is required before changing it.

For directories, remember that SGID may intentionally support group inheritance.

Do not recommend removing it without understanding the operational design.

---

# 76. Prefer Narrow Privileges

If an application needs only one privileged operation, full SUID root may provide more authority than necessary.

Depending on the requirement, alternatives may include:

```text
Linux capabilities

Dedicated service

Privileged helper with narrow interface

sudo rule for a specific operation

File ACLs

Group-based access
```

Each alternative has its own security considerations.

The goal is:

```text
Minimum Privilege Required
```

rather than:

```text
No Privilege Mechanisms Anywhere
```

---

# 77. Protect Dependencies

A privileged binary should not trust resources modifiable by lower-privileged users.

Review:

```text
Binary

Parent directories

Shared libraries

Configuration files

Helper programs

Plugin directories

Temporary paths

Data files that control behavior
```

The security chain is only as strong as the least-protected trusted component.

---

# 78. Retesting

After remediation, repeat enumeration:

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null
```

For the affected resource:

```bash
stat /path/to/binary
getfacl /path/to/binary
namei -l /path/to/binary
findmnt -T /path/to/binary
```

Confirm:

```text
Unnecessary special bit removed

Required functionality still works

Writable dependency corrected

Unsafe path corrected

Configuration protected

Application still functions

Security boundary no longer exists
```

---

# SUID and SGID Assessment Checklist

## Identity

- [ ] Identify current user
- [ ] Record UID
- [ ] Record GID
- [ ] Review supplementary groups
- [ ] Review sudo context where relevant

## Enumeration

- [ ] Enumerate SUID executables
- [ ] Enumerate SGID executables
- [ ] Identify custom executables
- [ ] Identify unusual locations
- [ ] Compare against available baseline
- [ ] Identify recently modified candidates where relevant

## File Metadata

- [ ] Inspect owner
- [ ] Inspect group
- [ ] Inspect mode
- [ ] Inspect ACL
- [ ] Inspect parent directories
- [ ] Resolve symbolic links
- [ ] Identify file type
- [ ] Determine package ownership

## Program Analysis

- [ ] Understand intended purpose
- [ ] Review accepted arguments
- [ ] Review file operations
- [ ] Review external command execution
- [ ] Review configuration loading
- [ ] Review temporary-file handling
- [ ] Review privilege dropping
- [ ] Review user-controlled inputs

## PATH

- [ ] Identify external command execution
- [ ] Determine whether absolute paths are used
- [ ] Determine effective PATH
- [ ] Inspect PATH directory permissions
- [ ] Validate whether user can influence resolution

## Libraries

- [ ] Identify dynamic dependencies
- [ ] Inspect RPATH
- [ ] Inspect RUNPATH
- [ ] Inspect library permissions
- [ ] Inspect library parent directories
- [ ] Consider privileged-loader restrictions

## Environment

- [ ] Identify relevant environment variables
- [ ] Determine whether they survive privileged execution
- [ ] Review application-specific environment behavior
- [ ] Avoid generic environment-hijacking assumptions

## Filesystem Context

- [ ] Determine mount point
- [ ] Review mount options
- [ ] Check for `nosuid`
- [ ] Consider network filesystem semantics
- [ ] Consider container context
- [ ] Consider user namespaces

## Security Controls

- [ ] Review SELinux state
- [ ] Review AppArmor state
- [ ] Consider kernel protections
- [ ] Consider privilege-dropping behavior

## GTFOBins

- [ ] Check relevant binaries
- [ ] Use SUID-specific entry where applicable
- [ ] Confirm local prerequisites
- [ ] Confirm version/configuration
- [ ] Avoid unnecessary destructive validation

## Validation

- [ ] Confirm special permission is effective
- [ ] Confirm privileged identity
- [ ] Identify controllable resource
- [ ] Confirm resource affects privileged behavior
- [ ] Identify false positives
- [ ] Validate security boundary safely

## Evidence

- [ ] Capture `id`
- [ ] Capture binary metadata
- [ ] Capture ACL
- [ ] Capture complete path
- [ ] Capture file type
- [ ] Capture package context
- [ ] Capture mount context
- [ ] Capture dependency evidence
- [ ] Capture relevant security controls

## Reporting

- [ ] Identify affected principal
- [ ] Identify privileged binary
- [ ] Explain SUID or SGID context
- [ ] Explain controllable resource
- [ ] Explain execution relationship
- [ ] Explain impact
- [ ] Recommend root-cause remediation
- [ ] Define retest procedure

---

# Quick SUID and SGID Assessment Workflow

```text
Enumerate SUID / SGID
        |
        v
Identify Interesting Binary
        |
        v
Expected Package Binary?
     /             \
   Yes              No
    |                |
    v                v
Review Function   Higher Priority
    |                |
    +-------+--------+
            |
            v
       Inspect Metadata
            |
            v
       Inspect Full Path
            |
            v
       Inspect Mount
            |
            v
       Understand Program
            |
            v
       Inspect Arguments
            |
            v
       Inspect Dependencies
            |
            +---- PATH
            +---- Libraries
            +---- Configuration
            +---- Helpers
            +---- Temporary files
            |
            v
      Can User Influence It?
          /          \
        No            Yes
        |              |
        v              v
     Record      Does Influence Occur
                 While Privileged?
                    /       \
                  No         Yes
                  |           |
                  v           v
               Record      Validate
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

## SUID Enumeration

```bash
find / -xdev -type f -perm -4000 -print 2>/dev/null
```

## SGID Enumeration

```bash
find / -xdev -type f -perm -2000 -print 2>/dev/null
```

## Combined Enumeration

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) -print 2>/dev/null
```

## Detailed Enumeration

```bash
find / -xdev -type f \( -perm -4000 -o -perm -2000 \) \
    -exec stat -c '%A %a %U %G %n' {} \; 2>/dev/null
```

## Custom Locations

```bash
find /usr/local /opt /srv -type f \( -perm -4000 -o -perm -2000 \) \
    -print 2>/dev/null
```

## File Metadata

```bash
stat /path/to/binary
```

## ACL

```bash
getfacl /path/to/binary
```

## Complete Path

```bash
namei -l /path/to/binary
```

## File Type

```bash
file /path/to/binary
```

## Resolve Symlink

```bash
readlink -f /path/to/binary
```

## ELF Header

```bash
readelf -h /path/to/binary
```

## Dynamic Section

```bash
readelf -d /path/to/binary
```

## Interesting Symbols

```bash
readelf -Ws /path/to/binary | grep -E 'system|popen|exec'
```

## RPATH and RUNPATH

```bash
readelf -d /path/to/binary | grep -E 'RPATH|RUNPATH'
```

## Strings

```bash
strings /path/to/binary | less
```

## Debian Package Ownership

```bash
dpkg -S /path/to/binary 2>/dev/null
```

## RPM Package Ownership

```bash
rpm -qf /path/to/binary 2>/dev/null
```

## Mount Context

```bash
findmnt -T /path/to/binary
```

## SELinux

```bash
getenforce 2>/dev/null
```

## AppArmor

```bash
aa-status 2>/dev/null
```

---

# Practical Testing Model

For an interesting privileged executable, use:

```text
1. When does this apply?

   SUID or SGID is present and effective.

2. What should I inspect?

   Identity, permissions, executable, dependencies and security controls.

3. What result matters?

   A lower-privileged user can influence privileged behavior.

4. What does the result mean?

   Determine exactly which security boundary is crossed.

5. What else could explain it?

   Expected SUID behavior, privilege dropping, nosuid, MAC controls,
   containers or protected dependencies.

6. What should I capture?

   Identity, metadata, execution relationship and dependency evidence.

7. How should it be remediated?

   Remove unnecessary privilege or protect the complete trust chain.

8. How should it be retested?

   Repeat the original validation and confirm the trust relationship
   no longer exists.
```

---

# Related Notes

- [Linux Overview](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Filesystem Permissions](filesystem-permissions.md)
- [sudo Security](sudo.md)
- [Linux Scheduled Jobs](scheduled-jobs.md)
- [Linux Services](services.md)
- [Linux Credentials](credentials.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux PrivEsc Explorer](../privesc/linux.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)

The next dedicated Linux privilege mechanism is:

[Linux Capabilities Security](capabilities.md)

---

# SUID and SGID Testing Mindset

Do not think:

```text
SUID = Root

SGID = Root

SUID root = Vulnerable

GTFOBins Match = Exploitable

Custom Binary = Vulnerable

Relative Command = PATH Hijack

RPATH = Library Hijack

UID 0 in Container = Host Root
```

Instead think:

```text
What Special Permission Exists?
        |
        v
Is It Actually Effective?
        |
        v
Which Identity Does It Provide?
        |
        v
What Does the Program Do?
        |
        v
When Does It Hold Privilege?
        |
        v
What Inputs Can I Control?
        |
        v
What Dependencies Can I Control?
        |
        v
What Other Security Controls Apply?
        |
        v
Can My Control Influence Privileged Behaviour?
        |
        v
Does This Cross the Intended Security Boundary?
```

The SUID or SGID bit is the beginning of the investigation, not the finding.

---

# References

- [Linux man-pages - inode](https://man7.org/linux/man-pages/man7/inode.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - credentials](https://man7.org/linux/man-pages/man7/credentials.7.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - execve](https://man7.org/linux/man-pages/man2/execve.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - setuid](https://man7.org/linux/man-pages/man2/setuid.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - setgid](https://man7.org/linux/man-pages/man2/setgid.2.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - ld.so](https://man7.org/linux/man-pages/man8/ld.so.8.html){ target="_blank" rel="noopener noreferrer" }
- [Linux man-pages - capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html){ target="_blank" rel="noopener noreferrer" }
- [GNU Coreutils - File Permissions](https://www.gnu.org/software/coreutils/manual/html_node/File-permissions.html){ target="_blank" rel="noopener noreferrer" }
- [GTFOBins](https://gtfobins.github.io/){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [linux-smart-enumeration](https://github.com/diego-treitos/linux-smart-enumeration){ target="_blank" rel="noopener noreferrer" }

!!! tip "Prioritise unusual binaries"

    Distribution-provided SUID executables are common. Custom SUID binaries, unexpected copies of utilities and privileged executables in application-specific directories generally deserve higher assessment priority.

!!! tip "Follow dependencies"

    The privileged executable itself may be correctly protected while a configuration file, helper program, library or PATH directory is writable. Analyse the complete privileged execution chain.

!!! tip "Check nosuid"

    Before assuming that a special permission bit is effective, inspect the filesystem with `findmnt -T`. A `nosuid` mount can materially change the result.

!!! tip "Understand when privilege exists"

    Secure privileged programs often perform a narrow privileged operation and then drop privileges. Determine which functionality executes while elevated rather than assuming the complete program always runs with the file owner's authority.

!!! warning "SUID is a mechanism, not a vulnerability"

    SUID and SGID exist specifically to delegate selected privileges. A defensible finding requires evidence that the program or one of its trusted dependencies allows access beyond the intended privilege model.
