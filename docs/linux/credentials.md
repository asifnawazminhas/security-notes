# Linux Credentials

Credential discovery is an important part of an authorised Linux security assessment because credentials are frequently distributed across application configuration, shell history, environment variables, SSH configuration, databases, cloud tooling, containers, automation systems, and backup files.

The objective is not to collect every secret available on a host.

The objective is to determine:

```text
What Credentials Exist?
        |
        v
Why Are They Accessible?
        |
        v
Which Identity Do They Represent?
        |
        v
Where Can They Be Used?
        |
        v
Do They Cross a Security Boundary?
        |
        v
What Is the Real Impact?
```

Credential material should always be treated as sensitive evidence.

---

# 1. Credential Assessment Workflow

A structured workflow is:

```text
Establish Current Identity
        |
        v
Review Home Directory
        |
        v
Review Shell History
        |
        v
Review Environment
        |
        v
Review SSH
        |
        v
Review Application Configuration
        |
        v
Review Service Configuration
        |
        v
Review Databases
        |
        v
Review Source Repositories
        |
        v
Review Cloud Configuration
        |
        v
Review Containers
        |
        v
Review Backups
        |
        v
Identify Credential Candidate
        |
        v
Determine Access Cause
        |
        v
Determine Credential Scope
        |
        v
Validate Minimally
        |
        v
Assess Impact
```

---

# 2. Credential Sources

Common Linux credential sources include:

```text
Shell history
Environment variables
SSH keys
SSH configuration
Application configuration
.env files
Service environment files
Database configuration
Database client files
Git repositories
Git credentials
Cloud CLI configuration
Kubernetes configuration
Container configuration
Backup files
Automation scripts
Configuration-management systems
Logs
Process command lines
Process environments
Browser or desktop storage
Password databases
```

Not every discovered value is necessarily valid or security-sensitive.

---

# 3. Start With Current Context

Before searching for credentials:

```bash
whoami
```

```bash
id
```

```bash
echo "$HOME"
```

This establishes which user's files are naturally accessible.

---

# 4. Home Directory

List:

```bash
ls -la "$HOME"
```

Potentially interesting entries include:

```text
.bash_history
.zsh_history
.ssh/
.gitconfig
.git-credentials
.aws/
.azure/
.config/
.kube/
.local/
.mysql_history
.psql_history
.netrc
```

Only investigate resources relevant to the authorised scope.

---

# 5. Other Home Directories

List:

```bash
ls -la /home
```

Check directory permissions:

```bash
find /home -maxdepth 1 -mindepth 1 -type d -exec stat -c '%A %a %U %G %n' {} \; 2>/dev/null
```

Do not automatically search other users' files simply because their home directories are readable.

First determine whether the access is relevant to the assessment.

---

# 6. Shell History

Bash:

```bash
cat ~/.bash_history 2>/dev/null
```

Zsh:

```bash
cat ~/.zsh_history 2>/dev/null
```

Fish:

```bash
cat ~/.local/share/fish/fish_history 2>/dev/null
```

History can expose:

```text
Passwords supplied as arguments
API tokens
Database connection strings
SSH destinations
Cloud commands
Administrative commands
Internal hostnames
Deployment commands
```

---

# 7. Targeted History Search

Bash:

```bash
grep -Ei 'pass|passwd|password|pwd|secret|token|api[_-]?key|credential|auth|mysql|psql|ssh|sudo' ~/.bash_history 2>/dev/null
```

Zsh:

```bash
grep -Ei 'pass|passwd|password|pwd|secret|token|api[_-]?key|credential|auth|mysql|psql|ssh|sudo' ~/.zsh_history 2>/dev/null
```

Review matches manually.

Keyword matches frequently generate false positives.

---

# 8. History Files

Target the current user's home directory:

```bash
find "$HOME" -maxdepth 4 -type f \( \
    -name '*history*' -o \
    -name '.bash_history' -o \
    -name '.zsh_history' -o \
    -name '.mysql_history' -o \
    -name '.psql_history' -o \
    -name '.python_history' \
\) -ls 2>/dev/null
```

---

# 9. Shell History Security

A common exposure pattern is:

```text
User Executes Command
       |
       v
Secret Included on Command Line
       |
       v
Shell Stores Command
       |
       v
History File Remains Accessible
       |
       v
Credential Disclosure
```

Applications should avoid requiring secrets directly on command lines where safer mechanisms exist.

---

# 10. Environment Variables

Display:

```bash
printenv
```

Sorted:

```bash
printenv | sort
```

Target likely credential names:

```bash
printenv | grep -Ei 'pass|passwd|password|secret|token|api[_-]?key|credential|auth'
```

---

# 11. Environment Credential Examples

Possible variables include:

```text
DB_PASSWORD
DATABASE_URL
API_KEY
API_TOKEN
ACCESS_TOKEN
SECRET_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AZURE_CLIENT_SECRET
GOOGLE_APPLICATION_CREDENTIALS
GITHUB_TOKEN
CI_JOB_TOKEN
```

Variable names vary significantly between applications.

---

# 12. Environment Variables Are Not Automatically Vulnerabilities

The existence of:

```text
DB_PASSWORD
```

does not automatically mean:

```text
Credential Exposure Vulnerability
```

Determine:

```text
Which process receives it?
Who can inspect it?
Which identity does it represent?
What resource does it access?
Is the access expected?
```

---

# 13. Process Environment

For your own process:

```bash
tr '\0' '\n' < /proc/$$/environ
```

For another process where permissions permit:

```bash
tr '\0' '\n' < /proc/PID/environ
```

Replace `PID` with the process identifier.

---

# 14. Process Environment Access

Modern Linux security controls may restrict `/proc/PID/environ`.

Access can depend on:

```text
Process ownership
UID
ptrace restrictions
/proc mount options
Capabilities
Kernel security configuration
```

Do not attempt to bypass these controls during routine credential enumeration.

---

# 15. Process Command Lines

List:

```bash
ps -eo user,pid,ppid,comm,args
```

Target likely credential arguments:

```bash
ps -eo user,pid,ppid,args | grep -Ei -- '--password|--passwd|--token|--secret|--api-key|--apikey'
```

Avoid including the `grep` process itself when interpreting results.

---

# 16. Command-Line Credential Exposure

Potential pattern:

```text
application --username admin --password ExamplePassword
```

Command-line credentials can potentially appear in:

```text
Process listings
Monitoring tools
Audit logs
Shell history
Diagnostic output
```

Prefer mechanisms that do not expose secrets through process arguments.

---

# 17. `/proc/PID/cmdline`

Where permitted:

```bash
tr '\0' ' ' < /proc/PID/cmdline
```

This can provide the process's original argument vector.

Handle output carefully if credentials are present.

---

# 18. SSH Directory

Current user:

```bash
ls -la ~/.ssh 2>/dev/null
```

Common files include:

```text
authorized_keys
known_hosts
config
id_rsa
id_ed25519
id_ecdsa
certificate files
custom key files
```

---

# 19. SSH Private Keys

Candidate files:

```bash
find ~/.ssh -maxdepth 1 -type f -ls 2>/dev/null
```

Inspect file type:

```bash
file ~/.ssh/* 2>/dev/null
```

Do not assume every file is a private key.

---

# 20. SSH Key Permissions

```bash
stat -c '%A %a %U %G %n' ~/.ssh/* 2>/dev/null
```

A typical private key should have restrictive permissions.

Example:

```text
600
```

Actual security depends on ownership, ACLs, filesystem protections, and how the key is used.

---

# 21. SSH Private Key Identification

Private keys may begin with markers such as:

```text
-----BEGIN OPENSSH PRIVATE KEY-----
```

or format-specific PEM markers.

Avoid reproducing private-key contents in reports.

Use metadata and fingerprints where possible.

---

# 22. SSH Public Key Fingerprint

For a public key:

```bash
ssh-keygen -lf ~/.ssh/id_ed25519.pub 2>/dev/null
```

For a private key where authorised:

```bash
ssh-keygen -y -f ~/.ssh/id_ed25519 2>/dev/null | ssh-keygen -lf -
```

This can identify the key without publishing its private contents.

---

# 23. SSH Configuration

```bash
cat ~/.ssh/config 2>/dev/null
```

Potential information includes:

```text
Host aliases
Usernames
Internal hosts
Jump hosts
Identity files
Proxy commands
Ports
```

Example:

```text
Host production
    HostName 10.10.20.15
    User deploy
    IdentityFile ~/.ssh/deploy_key
```

---

# 24. SSH Known Hosts

```bash
cat ~/.ssh/known_hosts 2>/dev/null
```

Hashed hostnames may prevent straightforward hostname discovery.

Do not modify known-host entries during enumeration.

---

# 25. SSH Agent

Check:

```bash
echo "$SSH_AUTH_SOCK"
```

List keys available to the current agent:

```bash
ssh-add -l 2>/dev/null
```

The agent may provide access to keys without exposing private-key files.

---

# 26. SSH Agent Security

An SSH agent represents delegated signing authority.

The important question is:

```text
Who Can Access the Agent Socket?
        |
        v
Which Keys Are Loaded?
        |
        v
Where Are Those Keys Authorised?
```

Do not export or misuse agent-backed credentials outside the authorised scope.

---

# 27. SSH Agent Socket

Inspect:

```bash
ls -l "$SSH_AUTH_SOCK" 2>/dev/null
```

Where the variable is set.

The socket should normally be protected by filesystem permissions.

---

# 28. `authorized_keys`

Current user:

```bash
cat ~/.ssh/authorized_keys 2>/dev/null
```

This identifies keys authorised to authenticate as the current user.

It does not reveal the corresponding private keys.

---

# 29. SSH Key Options

`authorized_keys` entries can contain restrictions such as:

```text
from=
command=
no-agent-forwarding
no-port-forwarding
no-pty
restrict
```

These options can significantly constrain key capabilities.

Do not assess a key solely from its presence.

---

# 30. `.netrc`

Check:

```bash
ls -l ~/.netrc 2>/dev/null
```

Where authorised:

```bash
cat ~/.netrc 2>/dev/null
```

A `.netrc` file may contain:

```text
machine
login
password
```

It should be treated as sensitive credential material.

---

# 31. Git Configuration

```bash
git config --global --list 2>/dev/null
```

or:

```bash
cat ~/.gitconfig 2>/dev/null
```

Potential information:

```text
Username
Email
Credential helper
Proxy
Repository configuration
Signing configuration
```

---

# 32. Git Credential Storage

Check:

```bash
git config --global credential.helper 2>/dev/null
```

Potential helpers include:

```text
cache
store
Platform-specific credential managers
Custom helpers
```

---

# 33. `.git-credentials`

Check metadata:

```bash
ls -l ~/.git-credentials 2>/dev/null
```

If the `store` credential helper is used, this file may contain credentials in plaintext form.

Avoid reproducing full credential URLs in reports.

---

# 34. Repository Configuration

Inside an authorised repository:

```bash
git remote -v
```

Remote URLs may contain:

```text
Username
Internal hostname
Access token
Embedded credentials
```

Credential-bearing URLs should be remediated.

---

# 35. Git Repository Discovery

Target likely development locations:

```bash
find /opt /srv /var/www "$HOME" -type d -name .git -print 2>/dev/null
```

Review only repositories relevant to the assessment.

---

# 36. Git History

Inside an authorised repository:

```bash
git log --oneline --decorate -n 30
```

A secret removed from the current version may remain in repository history.

Do not automatically dump complete repository history.

---

# 37. Git Secret Exposure Model

```text
Secret Committed
      |
      v
Repository History
      |
      v
Secret Removed From Current File
      |
      v
Historical Commit Still Contains Secret
      |
      v
Credential Remains Recoverable
```

Removing a secret from the latest commit does not invalidate it.

Credential rotation may still be required.

---

# 38. Application Configuration

Common configuration locations include:

```text
/etc/
/opt/
/srv/
/var/www/
/usr/local/
/var/lib/
```

Prioritise configuration associated with running applications.

---

# 39. Configuration File Discovery

Targeted application search:

```bash
find /opt /srv /var/www /usr/local -type f \( \
    -name '*.conf' -o \
    -name '*.config' -o \
    -name '*.ini' -o \
    -name '*.yaml' -o \
    -name '*.yml' -o \
    -name '*.json' -o \
    -name '*.xml' -o \
    -name '*.properties' -o \
    -name '.env' \
\) -ls 2>/dev/null
```

---

# 40. Targeted Secret Search

For a known application:

```bash
grep -RniE 'password|passwd|secret|token|api[_-]?key|credential|client[_-]?secret' /opt/application 2>/dev/null
```

Do not recursively grep the entire filesystem by default.

---

# 41. Why Targeted Searching Matters

Broad searches can:

```text
Generate excessive I/O
Access unrelated user data
Trigger monitoring
Create large evidence sets
Expose unnecessary secrets
Reduce assessment focus
```

Prefer:

```text
Running Application
       |
       v
Known Configuration Directory
       |
       v
Targeted Search
```

---

# 42. `.env` Files

Search likely locations:

```bash
find /opt /srv /var/www "$HOME" -type f \( -name '.env' -o -name '.env.*' \) -ls 2>/dev/null
```

Common contents include:

```text
Database credentials
API keys
JWT secrets
Application encryption keys
Cloud credentials
SMTP credentials
OAuth secrets
```

---

# 43. `.env` Permissions

Inspect:

```bash
stat -c '%A %a %U %G %n' /opt/application/.env
```

ACL:

```bash
getfacl /opt/application/.env
```

Parent path:

```bash
namei -l /opt/application/.env
```

---

# 44. Service Environment Files

Find through systemd:

```bash
systemctl cat example.service
```

Look for:

```ini
EnvironmentFile=/etc/example/example.env
```

Metadata:

```bash
stat -c '%A %a %U %G %n' /etc/example/example.env
```

See [Linux Services](services.md) for detailed service analysis.

---

# 45. systemd Environment

Inspect:

```bash
systemctl show example.service -p Environment -p EnvironmentFiles
```

Do not copy secret values unnecessarily.

The important evidence may be:

```text
Secret exists
      +
File readable by unintended user
```

---

# 46. Web Application Configuration

Common application files can include:

```text
.env
config.php
settings.php
settings.py
application.properties
application.yml
appsettings.json
database.yml
wp-config.php
```

Only search technology-specific files after identifying the relevant application stack.

---

# 47. PHP Configuration

Example candidate search:

```bash
find /var/www /opt /srv -type f \( \
    -name 'config.php' -o \
    -name 'wp-config.php' -o \
    -name '*.php' \
\) 2>/dev/null
```

Do not indiscriminately grep every source file when targeted configuration files are already known.

---

# 48. Python Applications

Potential credential locations include:

```text
.env
settings.py
config.py
YAML configuration
systemd EnvironmentFile
Container environment
Secret-management integrations
```

Determine the framework before searching.

---

# 49. Django

Common configuration:

```text
settings.py
.env
```

Potential secrets include:

```text
SECRET_KEY
DATABASES
EMAIL credentials
Cloud credentials
Third-party API tokens
```

Exposure impact depends on the specific value.

---

# 50. Flask

Common patterns include:

```text
config.py
.env
Environment variables
Instance configuration
```

Look for:

```text
SECRET_KEY
Database URLs
API credentials
```

---

# 51. Node.js

Common locations include:

```text
.env
config/
package configuration
Process manager configuration
systemd EnvironmentFile
```

Potential secrets:

```text
DATABASE_URL
JWT_SECRET
SESSION_SECRET
API_KEY
OAuth client secrets
```

---

# 52. Java Applications

Potential configuration includes:

```text
application.properties
application.yml
application.yaml
XML configuration
Environment variables
JVM arguments
```

Search targeted application directories.

---

# 53. Spring Applications

Potential configuration:

```text
application.properties
application.yml
```

Common credential keys may include:

```text
spring.datasource.username
spring.datasource.password
management credentials
OAuth client secrets
```

Do not assume every property is active in the current profile.

---

# 54. Database Configuration

Potential database systems include:

```text
MySQL
MariaDB
PostgreSQL
Redis
MongoDB
SQLite
Oracle clients
```

Identify actual running software first:

```bash
ps -ef | grep -Ei '[m]ysql|[m]ariadb|[p]ostgres|[r]edis|[m]ongod'
```

---

# 55. MySQL Client Configuration

Potential user configuration:

```text
~/.my.cnf
```

Check:

```bash
ls -l ~/.my.cnf 2>/dev/null
```

Where relevant:

```bash
cat ~/.my.cnf 2>/dev/null
```

Possible contents:

```ini
[client]
user=application
password=ExamplePassword
host=database.internal
```

---

# 56. MySQL History

```bash
cat ~/.mysql_history 2>/dev/null
```

History can expose:

```text
Queries
Database names
Administrative commands
Potential credentials entered into SQL
```

Handle carefully.

---

# 57. PostgreSQL

Potential files include:

```text
~/.pgpass
~/.psql_history
```

Check:

```bash
ls -l ~/.pgpass ~/.psql_history 2>/dev/null
```

---

# 58. `.pgpass`

Format:

```text
hostname:port:database:username:password
```

Permissions should normally be restrictive.

Check:

```bash
stat -c '%A %a %U %G %n' ~/.pgpass 2>/dev/null
```

---

# 59. PostgreSQL History

```bash
cat ~/.psql_history 2>/dev/null
```

As with other shell-like histories, search only when relevant.

---

# 60. Redis

Configuration may include authentication settings.

Common paths vary, for example:

```text
/etc/redis/
```

Identify actual configuration through the running service:

```bash
systemctl cat redis.service 2>/dev/null
```

or distribution-specific service names.

---

# 61. Database Credential Validation

Do not immediately connect to a production database with every credential discovered.

First determine:

```text
Credential source
Identity
Database host
Database name
Expected access
Potential impact
Scope
```

Then use the minimum validation required.

---

# 62. Backup Files

Search targeted application directories:

```bash
find /etc /opt /srv /var/www -type f \( \
    -name '*.bak' -o \
    -name '*.backup' -o \
    -name '*.old' -o \
    -name '*.orig' -o \
    -name '*.save' \
\) -ls 2>/dev/null
```

Backup files can contain credentials removed from active configuration.

---

# 63. Compressed Backups

Candidate formats include:

```text
.tar
.tar.gz
.tgz
.zip
.gz
.7z
```

Search targeted directories:

```bash
find /opt /srv /var/backups /var/www -type f \( \
    -name '*.tar' -o \
    -name '*.tar.gz' -o \
    -name '*.tgz' -o \
    -name '*.zip' -o \
    -name '*.7z' \
\) -ls 2>/dev/null
```

Do not extract large or unrelated archives without need.

---

# 64. `/var/backups`

List:

```bash
ls -lah /var/backups 2>/dev/null
```

Potential contents depend on the distribution and installed applications.

Review permissions before accessing files.

---

# 65. Editor Backups

Target likely application directories:

```bash
find /opt /srv /var/www /etc -type f \( \
    -name '*~' -o \
    -name '*.swp' -o \
    -name '*.swo' \
\) -ls 2>/dev/null
```

Old editor files can expose previous configuration or credentials.

---

# 66. Configuration Management

Potential systems include:

```text
Ansible
Puppet
Chef
Salt
Custom deployment scripts
```

These systems often manage privileged configuration and therefore deserve careful credential handling.

---

# 67. Ansible

Potential files:

```text
ansible.cfg
inventory
group_vars/
host_vars/
roles/
vault files
```

Search targeted project locations:

```bash
find /opt /srv "$HOME" -type f -name 'ansible.cfg' -o -name 'hosts.ini' 2>/dev/null
```

Use parentheses when expanding more complex `find` expressions.

---

# 68. Ansible Vault

Encrypted vault content may contain secrets.

Recognise:

```text
$ANSIBLE_VAULT;
```

Do not attempt password cracking unless explicitly authorised.

The presence of an encrypted vault is not a credential exposure.

---

# 69. Puppet

Potential locations include:

```text
/etc/puppet/
/etc/puppetlabs/
```

Check only if Puppet is installed or running.

Configuration-management systems can contain:

```text
Certificates
API tokens
Deployment credentials
Repository credentials
```

---

# 70. Chef

Potential locations include:

```text
/etc/chef/
```

Possible sensitive material:

```text
Client keys
Validation keys
Server URLs
Configuration
```

Private keys should not be copied unnecessarily.

---

# 71. Salt

Potential configuration:

```text
/etc/salt/
```

Determine whether the host acts as:

```text
Master
Minion
Standalone system
```

before assessing credential impact.

---

# 72. CI/CD Credentials

Linux hosts involved in CI/CD may contain:

```text
GitHub tokens
GitLab tokens
Registry credentials
Cloud credentials
Deployment SSH keys
Artifact repository credentials
Package repository credentials
```

Potential locations include:

```text
Environment
Runner configuration
Service configuration
Build directories
Credential helpers
```

---

# 73. CI Runner Processes

Search:

```bash
ps -ef | grep -Ei '[g]itlab-runner|[g]ithub.*runner|[j]enkins'
```

Then identify:

```text
Service account
Working directory
Configuration
Environment
Credential storage
```

---

# 74. Jenkins

Potential Jenkins home directories include:

```text
/var/lib/jenkins
```

Actual configuration varies.

Do not recursively collect Jenkins credential stores unless explicitly required.

Jenkins may protect credentials using application-specific mechanisms.

---

# 75. Container Credentials

Containers can receive secrets through:

```text
Environment variables
Mounted files
Docker secrets
Kubernetes secrets
Configuration files
Cloud workload identities
```

Determine whether the host or container context is in scope.

---

# 76. Docker Configuration

Current user:

```bash
ls -la ~/.docker 2>/dev/null
```

Potential file:

```text
~/.docker/config.json
```

Check metadata:

```bash
stat -c '%A %a %U %G %n' ~/.docker/config.json 2>/dev/null
```

---

# 77. Docker Registry Credentials

Docker configuration can contain authentication material or references to credential helpers.

Do not reproduce registry credentials in reports.

Record:

```text
Registry
Credential storage mechanism
File permissions
Affected identity
```

---

# 78. Container Environment

For containers you are authorised to inspect, configuration may expose environment variables.

Avoid collecting secrets unless necessary.

A better assessment question is:

```text
Can an unintended identity retrieve container secrets?
```

---

# 79. Docker Socket

Inspect:

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

Access to the Docker daemon is highly privileged.

This is generally an administrative privilege issue rather than a credential disclosure.

See [Linux Services](services.md).

---

# 80. Kubernetes Configuration

Current user:

```bash
ls -la ~/.kube 2>/dev/null
```

Configuration:

```bash
ls -l ~/.kube/config 2>/dev/null
```

A kubeconfig may contain:

```text
Cluster endpoints
Client certificates
Client keys
Bearer tokens
Authentication plugins
Contexts
Namespaces
```

Treat it as credential material.

---

# 81. Kubeconfig Metadata

Inspect permissions:

```bash
stat -c '%A %a %U %G %n' ~/.kube/config 2>/dev/null
```

Avoid pasting complete kubeconfig files into reports.

---

# 82. Kubernetes Contexts

Where `kubectl` is installed and use is authorised:

```bash
kubectl config get-contexts
```

Current context:

```bash
kubectl config current-context
```

These commands can identify credential scope without performing workload actions.

---

# 83. Kubernetes Credential Scope

Determine:

```text
Cluster
Context
User
Namespace
Authentication method
RBAC permissions
```

Do not assume a kubeconfig provides administrative access.

RBAC determines effective authorisation.

---

# 84. Cloud Credentials

Linux systems may contain credentials for:

```text
AWS
Microsoft Azure
Google Cloud
Other cloud providers
```

Cloud environments should only be tested when explicitly included in scope.

---

# 85. AWS

Potential directory:

```bash
ls -la ~/.aws 2>/dev/null
```

Common files:

```text
~/.aws/config
~/.aws/credentials
```

Check metadata:

```bash
stat -c '%A %a %U %G %n' ~/.aws/credentials 2>/dev/null
```

---

# 86. AWS Credential Profiles

Where AWS CLI is installed:

```bash
aws configure list-profiles 2>/dev/null
```

This identifies profile names without printing secret values.

---

# 87. AWS Identity Validation

When cloud testing is explicitly authorised, identity can be determined using the provider's normal identity mechanisms.

The assessment should document:

```text
Account
Principal
Role
Permission scope
Credential source
```

Avoid unnecessary resource access.

---

# 88. Azure

Potential directory:

```bash
ls -la ~/.azure 2>/dev/null
```

The Azure CLI can maintain authentication state and configuration beneath this directory.

Treat files as sensitive.

---

# 89. Azure Identity

Where Azure CLI is installed and cloud testing is authorised:

```bash
az account show
```

This can reveal the currently selected account and subscription context.

Do not perform cloud enumeration outside scope.

---

# 90. Google Cloud

Potential directory:

```bash
ls -la ~/.config/gcloud 2>/dev/null
```

Possible content includes:

```text
CLI configuration
Authentication databases
Application-default credentials
Account information
```

Treat the entire directory as sensitive.

---

# 91. Google Cloud Accounts

Where authorised:

```bash
gcloud auth list
```

Configuration:

```bash
gcloud config list
```

Avoid exporting tokens unnecessarily.

---

# 92. Service Account Keys

Potential service account JSON may contain:

```text
client_email
private_key
project_id
token_uri
```

A private key is highly sensitive.

Do not include the full JSON or key in assessment reports.

---

# 93. Cloud Metadata Services

Cloud workloads may obtain temporary credentials through metadata or workload-identity services.

Do not query cloud metadata endpoints unless:

```text
Cloud environment is confirmed
Cloud testing is in scope
The request is operationally safe
```

Prefer platform-native identity commands when available.

---

# 94. Secret Managers

Applications may retrieve secrets dynamically from systems such as:

```text
Cloud secret managers
HashiCorp Vault
Kubernetes
Hardware-backed stores
Custom credential brokers
```

The absence of plaintext credentials can indicate better secret-management design.

Do not attempt to dump a secret store simply because the application can access it.

---

# 95. HashiCorp Vault

Potential environment variables may include:

```text
VAULT_ADDR
VAULT_TOKEN
VAULT_NAMESPACE
```

Check targeted environment variables:

```bash
printenv | grep '^VAULT_'
```

A Vault token should be treated as sensitive authentication material.

---

# 96. API Tokens

Search only relevant application directories:

```bash
grep -RniE 'api[_-]?key|api[_-]?token|access[_-]?token|bearer|client[_-]?secret' /opt/application 2>/dev/null
```

Potential tokens can belong to:

```text
Git platforms
Cloud APIs
Payment services
Monitoring platforms
Internal APIs
Messaging platforms
CI/CD systems
```

---

# 97. JWT Secrets

Applications may use secrets for signing or validating JWTs.

Potential variable names:

```text
JWT_SECRET
JWT_SIGNING_KEY
TOKEN_SECRET
```

Possession of a signing secret may have significant application impact.

Validate only within the authorised application scope.

---

# 98. Session Secrets

Potential variables:

```text
SESSION_SECRET
COOKIE_SECRET
SECRET_KEY
```

Impact depends on the application framework and how the secret is used.

Do not assume every `SECRET_KEY` has the same security significance.

---

# 99. OAuth Credentials

Potential values:

```text
CLIENT_ID
CLIENT_SECRET
TENANT_ID
REDIRECT_URI
```

A client ID is generally not secret.

A client secret is.

Correctly distinguish public identifiers from confidential credentials.

---

# 100. TLS Certificates

Search targeted service configuration rather than the whole filesystem.

Certificates themselves are generally public.

The corresponding private keys are sensitive.

---

# 101. Private Keys

Potential key formats include:

```text
OpenSSH
RSA PEM
EC PEM
PKCS#8
PKCS#12
```

Private-key material should not be reproduced in reports.

Record:

```text
Path
Owner
Permissions
Purpose
Fingerprint where appropriate
```

---

# 102. PEM Private Key Search

For a known application directory:

```bash
grep -RIl -- '-----BEGIN .*PRIVATE KEY-----' /opt/application 2>/dev/null
```

Use this only on targeted directories.

---

# 103. Certificate Fingerprints

For an X.509 certificate:

```bash
openssl x509 -in certificate.pem -noout -subject -issuer -serial -fingerprint -sha256
```

This provides useful evidence without exposing private-key material.

---

# 104. PKCS#12 Files

Candidate extensions:

```text
.p12
.pfx
```

Search targeted directories:

```bash
find /opt /srv /etc/application -type f \( -name '*.p12' -o -name '*.pfx' \) -ls 2>/dev/null
```

These files may contain certificates and private keys.

Do not attempt password guessing unless explicitly authorised.

---

# 105. Password Hashes

Linux password hashes are normally stored in:

```text
/etc/shadow
```

Check metadata:

```bash
ls -l /etc/shadow
```

Typical systems restrict access.

---

# 106. `/etc/shadow`

Do not read or copy `/etc/shadow` merely because elevated access is available.

Only collect password hashes when:

```text
Credential auditing is explicitly in scope
Password-strength testing is required
The assessment rules permit offline analysis
```

---

# 107. Shadow Exposure

A meaningful issue may exist when:

```text
Standard User
      |
      v
Can Read /etc/shadow
```

or an unauthorised copy of the shadow database is accessible elsewhere.

The issue is the access-control failure.

---

# 108. Shadow Backups

Potential historical files vary by distribution.

Rather than blindly searching the entire filesystem, inspect known system backup locations and permission anomalies when relevant.

Any readable password-hash database should be treated as sensitive evidence.

---

# 109. Password Hash Cracking

Offline password cracking can:

```text
Consume sensitive credential material
Reveal user passwords
Cause scope concerns
Create handling requirements
```

Only perform it when explicitly authorised.

A file-permission weakness can often be reported without cracking any password.

---

# 110. Application Password Hashes

Applications may maintain:

```text
Local users
Password hashes
API keys
Session tokens
Recovery tokens
```

Access to the database does not automatically authorise offline password attacks.

Follow the agreed testing scope.

---

# 111. Logs

Potential logs:

```text
/var/log/
Application logs
Web logs
Audit logs
CI/CD logs
Debug logs
```

Search a known application log directory:

```bash
grep -RniE 'password|passwd|secret|token|authorization|api[_-]?key' /var/log/application 2>/dev/null
```

---

# 112. Authorization Headers

Logs may accidentally contain:

```text
Authorization: Bearer ...
```

Such tokens should be redacted immediately in evidence.

Report the logging weakness without unnecessarily preserving active tokens.

---

# 113. Debug Logging

Debug modes can expose:

```text
Environment variables
Stack traces
Database URLs
API tokens
Request headers
Configuration
Filesystem paths
```

Determine whether debug logging is accessible to unintended users.

---

# 114. Core Dumps

Core dumps may contain process memory and therefore:

```text
Passwords
Tokens
Keys
Session data
Application secrets
```

Do not intentionally crash applications to obtain credentials.

---

# 115. Core Dump Locations

Configuration varies.

Where systemd-coredump is used:

```bash
coredumpctl list 2>/dev/null
```

Do not export dumps unless explicitly required.

---

# 116. Swap

Secrets may transiently appear in swap.

Direct swap analysis is intrusive and generally unnecessary for normal credential assessment.

Do not perform raw memory or swap extraction without explicit authorisation.

---

# 117. Memory

Process memory may contain:

```text
Passwords
Tokens
Encryption keys
Session data
```

Memory dumping is a high-sensitivity activity.

It should not be part of routine enumeration.

---

# 118. Browser Credentials

Desktop Linux systems may contain browser credential stores.

These can involve:

```text
Browser profiles
OS keyrings
Encrypted databases
Session cookies
Tokens
```

Do not collect browser credentials unless the assessment explicitly includes user credential stores.

---

# 119. Desktop Keyrings

Linux desktop environments may use systems such as:

```text
GNOME Keyring
KWallet
Secret Service
```

These exist specifically to protect credentials.

Do not attempt extraction merely because the service is present.

---

# 120. Password Managers

Password-manager databases are highly sensitive.

Their presence is not a vulnerability.

Assessment should focus on issues such as:

```text
Insecure permissions
Unprotected exports
Plaintext backups
Exposed master credentials
```

---

# 121. Credentials in Scripts

Search targeted script directories:

```bash
grep -RniE 'password|passwd|secret|token|api[_-]?key|credential' /opt/application/scripts 2>/dev/null
```

Automation scripts are a common source of hardcoded secrets.

---

# 122. Cron Credentials

Review scheduled scripts:

```bash
cat /etc/crontab
```

```bash
ls -la /etc/cron.d 2>/dev/null
```

Then inspect only referenced scripts.

Credentials may be stored in:

```text
Backup scripts
Database scripts
Deployment scripts
Synchronisation scripts
Monitoring scripts
```

---

# 123. Backup Scripts

Example:

```text
mysqldump
rsync
scp
sftp
curl
Cloud CLI
```

Scripts may rely on:

```text
Embedded passwords
SSH keys
Credential files
Environment variables
Service identities
```

Assess how authentication is implemented.

---

# 124. Service Scripts

Use:

```bash
systemctl cat example.service
```

Then inspect referenced scripts.

Service scripts often have access to higher-value credentials than interactive users.

See [Linux Services](services.md).

---

# 125. Database URLs

Applications frequently use connection strings such as:

```text
postgresql://user:password@host/database
mysql://user:password@host/database
```

Do not include full connection strings in reports.

Redact passwords.

---

# 126. URI Credential Redaction

Instead of:

```text
postgresql://admin:SuperSecretPassword@db.internal/prod
```

record:

```text
postgresql://admin:[REDACTED]@db.internal/prod
```

This preserves evidence while reducing credential exposure.

---

# 127. Token Redaction

Instead of:

```text
Authorization: Bearer eyJ...
```

record:

```text
Authorization: Bearer [REDACTED]
```

If identification is required, retain only a short non-sensitive prefix or hash where appropriate.

---

# 128. Secret Fingerprinting

A SHA-256 digest can sometimes identify a discovered secret without retaining the plaintext value.

Example:

```bash
printf '%s' 'secret-value' | sha256sum
```

Do not place real credentials directly in shared shell history solely to calculate a hash.

Use an appropriate secure evidence-handling process.

---

# 129. Evidence Redaction

Credential evidence should normally contain:

```text
Credential type
Username or principal
Source path
Permissions
Target service
Privilege level
Validation result
Redacted value
```

Avoid:

```text
Complete password
Complete API token
Private key
Session cookie
Cloud access token
```

---

# 130. Credential Reuse

A credential may potentially be reused across:

```text
SSH
Sudo
Databases
Web applications
Git
Cloud services
Internal APIs
Administrative interfaces
```

Do not attempt credential reuse broadly.

Validate only against authorised services and accounts.

---

# 131. Credential Reuse Risk

The risk model is:

```text
Credential Exposed on Host A
        |
        v
Same Credential Used on Host B
        |
        v
Higher Privilege or Wider Access
```

The root cause may be:

```text
Credential reuse
+
Credential exposure
```

These can be reported separately or together depending on context.

---

# 132. Password Reuse Validation

Avoid password spraying or broad authentication attempts.

If reuse testing is explicitly authorised:

```text
Use the minimum number of attempts
Avoid account lockout
Target known relevant identities
Record exact scope
Stop after sufficient proof
```

---

# 133. Credential Scope

For each discovered credential determine:

```text
Local host only?
Application?
Database?
Domain?
Cloud?
Git?
Container registry?
Kubernetes?
Administrative platform?
```

Scope often matters more than the credential format.

---

# 134. Credential Privilege

Classify approximately:

```text
Low privilege
Application user
Service account
Database user
Deployment account
Administrator
Root-equivalent
Cloud role
Cluster administrator
```

Do not infer privilege solely from usernames such as:

```text
admin
root
administrator
```

Validate actual permissions.

---

# 135. Credential Lifetime

Determine where possible:

```text
Static password?
Long-lived API key?
Short-lived token?
SSH certificate?
Temporary cloud credential?
Session token?
Rotating secret?
```

Short-lived credentials may significantly reduce exposure duration.

---

# 136. Credential Rotation

If a credential has been exposed:

```text
Remove Exposure
       +
Rotate Credential
       +
Review Usage
       +
Review Logs
```

Removing the file alone may not be sufficient.

---

# 137. Hardcoded Credentials

A common pattern:

```text
Source Code
    |
    v
Hardcoded Secret
    |
    v
Repository
    |
    v
Deployment
    |
    v
Multiple Copies
```

This creates difficult rotation and secret-management problems.

---

# 138. Hardcoded Credential Finding

Strong evidence includes:

```text
Path
File permissions
Credential type
Affected identity
Target service
Whether credential remains valid
Who can read it
```

Avoid reproducing the complete secret.

---

# 139. Plaintext Credential Finding

Example title:

```text
Application Credentials Stored in Plaintext Configuration Accessible to Standard Users
```

Description:

```text
The application stores authentication credentials in a configuration file
that is readable by users who do not require access to the credential.
```

---

# 140. Plaintext Credential Impact

Example:

```text
An unauthorised local user may obtain the application credential and use it
to authenticate to the associated service with the privileges assigned to
the affected account.
```

Do not claim administrative impact unless validated.

---

# 141. Plaintext Credential Recommendation

```text
Restrict access to the configuration file to the service identity and trusted
administrators.

Where supported, migrate the credential to an appropriate secret-management
mechanism and rotate the exposed credential.
```

---

# 142. SSH Private Key Finding

Example title:

```text
SSH Private Key Accessible to Unauthorised Local Users
```

Description:

```text
An SSH private key used by a privileged or service account is readable by
users who do not require access to the key.
```

Impact should describe the systems and identity for which the key is actually valid.

---

# 143. SSH Key Recommendation

```text
Restrict the private key to the intended account and trusted administrators.

Review authorised destinations, rotate the affected key pair where exposure
has occurred, and remove obsolete authorised-key entries.
```

---

# 144. Shell History Finding

Example title:

```text
Authentication Credentials Exposed Through Shell History
```

Description:

```text
A credential was supplied directly on a command line and persisted in the
user's shell history file.
```

Recommendation:

```text
Avoid supplying secrets directly as command-line arguments.

Use secure prompts, protected configuration files, environment mechanisms
appropriate to the application, or dedicated secret-management facilities.
Rotate credentials that have already been exposed.
```

---

# 145. Environment Variable Finding

Do not automatically report environment-based secrets.

A finding becomes stronger when:

```text
Sensitive Environment Variable
        |
        v
Visible to Unintended User
        |
        v
Valid Credential
        |
        v
Meaningful Resource Access
```

The exposure mechanism is the key issue.

---

# 146. Backup Credential Finding

Example title:

```text
Historical Application Backup Exposes Valid Credentials
```

Description:

```text
A backup copy of an application configuration file remains accessible and
contains authentication material that is no longer present in the active
configuration.
```

Recommendation:

```text
Remove unnecessary configuration backups, restrict access to retained
backups, and rotate credentials exposed through historical files.
```

---

# 147. Git Credential Finding

Example title:

```text
Valid Application Secret Retained in Git Repository History
```

Description:

```text
A secret removed from the current source tree remains recoverable from an
earlier repository commit.
```

Recommendation:

```text
Rotate the exposed secret.

Where necessary, remove sensitive historical content using an approved
repository-cleaning process and review downstream clones, forks, build
artifacts, and logs that may retain copies.
```

---

# 148. Cloud Credential Finding

Example title:

```text
Cloud Authentication Credential Accessible to Unauthorised Local User
```

Evidence should identify:

```text
Credential source
Cloud provider
Principal
File permissions
Effective cloud identity
Permission scope
```

Do not include the complete secret.

---

# 149. Kubernetes Credential Finding

Example title:

```text
Kubernetes Authentication Configuration Accessible to Unauthorised Local Users
```

Impact should be based on actual Kubernetes RBAC permissions.

Avoid assuming:

```text
Readable kubeconfig = cluster admin
```

---

# 150. Credential Evidence Model

```text
Source
  |
  v
Credential Type
  |
  v
File / Process Permissions
  |
  v
Current User Access
  |
  v
Affected Principal
  |
  v
Target Resource
  |
  v
Effective Privilege
  |
  v
Minimal Validation
  |
  v
Impact
```

---

# 151. Permission Evidence

For a credential file:

```bash
stat -c '%A %a %U %G %n' /path/to/credential
```

ACL:

```bash
getfacl /path/to/credential
```

Parent directories:

```bash
namei -l /path/to/credential
```

Current user:

```bash
id
```

This often provides stronger evidence than screenshots of plaintext credentials.

---

# 152. Readability Test

Without displaying the credential:

```bash
test -r /path/to/credential && echo "Readable" || echo "Not readable"
```

This can demonstrate access without exposing the file contents in terminal logs.

---

# 153. Writeability Test

```bash
test -w /path/to/credential && echo "Writable" || echo "Not writable"
```

Write access may be important if a privileged application trusts the credential or configuration file.

Do not modify the credential during routine testing.

---

# 154. Credential File Parent Directory

```bash
namei -l /path/to/credential
```

A protected credential file may still be replaceable if a parent directory is writable.

Read and write risks should be considered separately.

---

# 155. Low-Noise Credential Workflow

Start with:

```bash
ls -la "$HOME"
```

Then:

```bash
printenv | grep -Ei 'pass|secret|token|api[_-]?key|credential'
```

Then:

```bash
ls -la ~/.ssh 2>/dev/null
```

Then:

```bash
git config --global --list 2>/dev/null
```

Then identify running applications and search only their configuration directories.

---

# 156. High-Value Credential Locations

Prioritise:

```text
~/.ssh/
~/.aws/
~/.azure/
~/.config/gcloud/
~/.kube/
~/.docker/
Application .env files
Service EnvironmentFile files
Database client configuration
Deployment scripts
CI/CD runner configuration
Git repositories
Backup configuration
```

---

# 157. Avoid Full Filesystem Grep

Avoid beginning with:

```text
grep -R "password" /
```

This can be:

```text
Noisy
Slow
Privacy-invasive
Operationally expensive
Difficult to review
Likely to access irrelevant data
```

Use application-aware searches.

---

# 158. Search Strategy

Preferred:

```text
Identify Application
       |
       v
Identify Config Directory
       |
       v
Identify Expected File Types
       |
       v
Search Relevant Keywords
       |
       v
Review Small Result Set
```

---

# 159. Candidate Keywords

Useful targeted terms include:

```text
password
passwd
secret
token
api_key
api-key
apikey
client_secret
access_key
private_key
credential
authorization
bearer
database_url
connection_string
```

Context determines relevance.

---

# 160. False Positives

Keyword searches may return:

```text
Documentation
Examples
Variable names without values
Test fixtures
Public keys
Client IDs
Expired tokens
Placeholders
Hashes
Encrypted values
Comments
```

Never report based solely on keyword presence.

---

# 161. Placeholder Credentials

Examples:

```text
password=changeme
password=example
password=${DB_PASSWORD}
token=<TOKEN>
```

Determine whether the value is actually active.

A placeholder is not necessarily an exposed credential.

---

# 162. Encrypted Credentials

An encrypted value is not automatically secure or insecure.

Assess:

```text
Encryption method
Key location
Who can decrypt it
Application identity
File permissions
Secret-management design
```

Do not attempt decryption unless required.

---

# 163. Encoded Credentials

Base64 is encoding, not encryption.

Example detection:

```text
Authorization: Basic ...
```

However, do not decode authentication data unnecessarily.

The exposure may already be demonstrated by inappropriate access.

---

# 164. Public vs Secret Values

Examples generally not secret by themselves:

```text
Username
Email address
Client ID
Tenant ID
Project ID
Public certificate
Public SSH key
API endpoint
```

Examples normally sensitive:

```text
Password
Private key
Client secret
Access token
Refresh token
API secret
Session token
Cloud secret access key
```

Correct classification reduces false positives.

---

# 165. Credential Validation

The safest validation model is:

```text
Identify Candidate
      |
      v
Determine Format
      |
      v
Determine Intended Target
      |
      v
Determine Scope
      |
      v
Use Lowest-Risk Identity Check
      |
      v
Stop Once Validity Is Established
```

Do not continue enumerating resources merely because authentication succeeded.

---

# 166. Validation Without Authentication

Sometimes validity does not need to be tested directly.

Evidence may already establish:

```text
Credential is active application configuration
Service is currently running
Configuration references the credential
Credential file is exposed
```

This may be sufficient.

---

# 167. Authentication Risk

Credential testing can cause:

```text
Account lockout
MFA prompts
Alerts
Session invalidation
Rate limiting
Audit events
Production impact
```

Understand authentication controls before testing.

---

# 168. Minimal Authentication

If authentication validation is necessary:

```text
One credential
One known target
One controlled attempt
```

Avoid:

```text
One credential
      |
      v
Every service in the environment
```

---

# 169. Credential Chaining

Credential impact can expand through relationships:

```text
Application Credential
       |
       v
Database Access
       |
       v
Database Contains Another Secret
       |
       v
Administrative Service
```

Do not continue chaining automatically.

Each new system or credential must remain within scope.

---

# 170. Privilege Escalation Through Credentials

A common local relationship is:

```text
Standard User
      |
      v
Reads Root-Owned Application Config
      |
      v
Obtains Service Credential
      |
      v
Credential Authenticates as Privileged Identity
      |
      v
Privilege Escalation
```

Detailed privilege escalation analysis belongs in [Linux Privilege Escalation](privilege-escalation.md).

---

# 171. Lateral Movement Through Credentials

Another relationship:

```text
Compromised Host
      |
      v
Deployment SSH Key
      |
      v
Other Linux Host
```

Lateral movement should only be validated when the additional systems are explicitly in scope.

---

# 172. Credential Blast Radius

For each credential ask:

```text
How many systems?
How many applications?
Which environments?
Which privileges?
Production or development?
Interactive or service account?
MFA?
Network restrictions?
Expiration?
Rotation?
```

This determines practical severity.

---

# 173. Shared Credentials

Shared service or administrator credentials create:

```text
Poor attribution
Large blast radius
Difficult rotation
Cross-system compromise risk
```

Prefer unique identities and scoped credentials.

---

# 174. Default Credentials

Do not assume software uses default credentials merely because defaults exist in documentation.

Validate configuration safely.

Default-credential testing should account for lockout and service impact.

---

# 175. Passwordless Authentication

Passwordless mechanisms such as:

```text
SSH keys
Certificates
Workload identity
Kerberos
Cloud instance roles
Unix socket peer authentication
```

can be stronger than stored passwords when correctly implemented.

Do not treat absence of a password as an authentication weakness.

---

# 176. Secret Management

Preferred design:

```text
Application
    |
    v
Authenticated Workload Identity
    |
    v
Secret Manager
    |
    v
Short-Lived Secret
```

rather than:

```text
Application
    |
    v
World-Readable Config
    |
    v
Long-Lived Password
```

---

# 177. Credential Rotation Strategy

When exposure is confirmed:

```text
1. Identify all consumers.

2. Generate replacement credential.

3. Update legitimate consumers.

4. Revoke old credential.

5. Verify applications.

6. Review logs for misuse.

7. Remove exposed copies.

8. Correct the access-control weakness.
```

Order may vary depending on operational requirements.

---

# 178. SSH Key Rotation

For an exposed SSH key:

```text
Generate replacement key
      |
      v
Deploy new public key
      |
      v
Validate legitimate access
      |
      v
Remove old authorised key
      |
      v
Destroy exposed private key copies
```

Also review all destinations where the old key was authorised.

---

# 179. API Token Rotation

For exposed API tokens:

```text
Identify token owner
Identify permissions
Identify consumers
Create replacement
Update consumers
Revoke exposed token
Review audit logs
```

Prefer scoped and short-lived tokens where supported.

---

# 180. Cloud Credential Rotation

Cloud credential remediation should also review:

```text
IAM permissions
Access logs
Role assumptions
Created resources
Additional credentials
Persistence mechanisms
```

Cloud incident-response procedures may be appropriate when exposure is significant.

---

# 181. Evidence Handling

Credential evidence should be stored according to the engagement's secure evidence procedures.

Consider:

```text
Encryption at rest
Restricted access
Minimal retention
Redaction
Secure deletion
No unnecessary screenshots
No plaintext credentials in tickets
```

---

# 182. Terminal History

Be careful not to create a second credential exposure while testing.

Avoid commands such as:

```text
some-client --password REAL_PASSWORD
```

because the command may itself enter shell history.

Use safer authentication mechanisms supported by the client.

---

# 183. Screenshots

A screenshot containing:

```text
Password
Private key
API token
Session cookie
Cloud credential
```

creates another copy of the secret.

Prefer redacted evidence.

---

# 184. Reports

Never include complete active credentials in the final report.

Use:

```text
Username:
deploy

Credential:
[REDACTED]

Source:
/opt/application/.env
```

---

# 185. Evidence Hashing

For sensitive files, a cryptographic hash can demonstrate which file was assessed.

Example:

```bash
sha256sum /path/to/file
```

This hashes the complete file without displaying its contents.

The resulting digest can be included in working evidence where useful.

---

# 186. File Metadata

Collect:

```bash
stat /path/to/file
```

or concise:

```bash
stat -c 'Path=%n Owner=%U Group=%G Mode=%A Numeric=%a Size=%s Modified=%y' /path/to/file
```

This provides useful evidence without exposing secrets.

---

# 187. Strong Credential Finding

Weak:

```text
Password found.
```

Strong:

```text
The application configuration file contains a database credential.

The file is readable by the local "developers" group.

The current standard user is a member of that group.

The credential belongs to the production application database account.

The account has read and write access to the application's production
database.
```

---

# 188. Root Cause

Possible root causes include:

```text
Excessive file permissions
Incorrect ACL
Hardcoded credential
Insecure backup
Secret in source control
Credential in shell history
Credential in process arguments
Insecure service environment
Shared credential
Overprivileged credential
Insufficient secret rotation
```

Report the root cause rather than simply the location where the secret was discovered.

---

# 189. Credential Severity

Severity should consider:

```text
Credential validity
Credential privilege
Affected systems
Network reachability
MFA
Credential lifetime
Number of users with access
Environment sensitivity
Ability to rotate
Detection controls
```

A plaintext password is not automatically critical severity.

---

# 190. Credential Exposure vs Credential Privilege

Keep separate:

```text
Exposure:
Who can obtain the credential?
```

and:

```text
Privilege:
What can the credential do?
```

Severity depends on both.

---

# 191. Credential Exposure Matrix

```text
                    Credential Privilege
                Low       Medium       High

Exposure Low    Low        Medium       High

Exposure Med    Medium     High         High

Exposure High   Medium     High         Critical Candidate
```

This is only a conceptual prioritisation model.

Use the organisation's actual risk methodology for final severity.

---

# 192. Automated Enumeration

Tools such as LinPEAS can identify credential candidates.

[PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }

Potential output includes:

```text
Environment variables
History files
SSH material
Configuration
Cloud files
Database files
Interesting backups
```

Do not automatically collect every highlighted secret.

---

# 193. TruffleHog

[TruffleHog](https://github.com/trufflesecurity/trufflehog){ target="_blank" rel="noopener noreferrer" }

TruffleHog is designed to detect secrets across sources such as repositories and filesystems.

It can be useful for authorised secret-discovery exercises.

Use it only against explicitly scoped data sources.

---

# 194. Gitleaks

[Gitleaks](https://github.com/gitleaks/gitleaks){ target="_blank" rel="noopener noreferrer" }

Gitleaks can identify potential secrets in Git repositories and files.

It is particularly useful for:

```text
Repository scanning
Pre-commit controls
CI/CD secret detection
Historical secret discovery
```

Potential findings still require validation.

---

# 195. Secret Scanner Workflow

```text
Repository
    |
    v
Secret Scanner
    |
    v
Candidate
    |
    v
Manual Review
    |
    v
Real Secret?
    |
    +---- No -> False Positive
    |
    +---- Yes
           |
           v
       Still Valid?
           |
           v
       Determine Scope
           |
           v
         Rotate
```

---

# 196. Native Credential Enumeration

A low-noise native sequence:

```bash
whoami
id
ls -la "$HOME"
ls -la ~/.ssh 2>/dev/null
printenv | grep -Ei 'pass|secret|token|api[_-]?key|credential'
git config --global --list 2>/dev/null
ls -la ~/.aws ~/.azure ~/.config/gcloud ~/.kube ~/.docker 2>/dev/null
```

Then identify running applications and inspect only relevant configuration.

---

# 197. Credential Checklist

## Context

- [ ] Current user
- [ ] UID
- [ ] Groups
- [ ] Home directory
- [ ] Scope confirmed

## Shell

- [ ] Bash history
- [ ] Zsh history
- [ ] Database history
- [ ] Commands containing secrets
- [ ] Environment variables

## SSH

- [ ] `.ssh` directory
- [ ] Private keys
- [ ] Key permissions
- [ ] SSH config
- [ ] SSH agent
- [ ] `authorized_keys`
- [ ] Key restrictions

## Applications

- [ ] `.env`
- [ ] Configuration files
- [ ] Service environment files
- [ ] Scripts
- [ ] Backup configuration
- [ ] Logs
- [ ] Command-line arguments

## Databases

- [ ] `.my.cnf`
- [ ] `.mysql_history`
- [ ] `.pgpass`
- [ ] `.psql_history`
- [ ] Application database URLs
- [ ] Database service configuration

## Git

- [ ] `.gitconfig`
- [ ] Credential helper
- [ ] `.git-credentials`
- [ ] Remote URLs
- [ ] Repository history
- [ ] Hardcoded secrets

## Cloud

- [ ] AWS
- [ ] Azure
- [ ] Google Cloud
- [ ] Service account files
- [ ] Workload identities
- [ ] Credential permissions

## Containers

- [ ] Docker config
- [ ] Registry authentication
- [ ] Kubernetes config
- [ ] Container environment
- [ ] Mounted secret files

## Automation

- [ ] Ansible
- [ ] Puppet
- [ ] Chef
- [ ] Salt
- [ ] CI/CD runners
- [ ] Deployment scripts
- [ ] Backup scripts

## Evidence

- [ ] File path
- [ ] Owner
- [ ] Group
- [ ] Permissions
- [ ] ACL
- [ ] Parent directories
- [ ] Credential type
- [ ] Principal
- [ ] Target resource
- [ ] Privilege
- [ ] Validity
- [ ] Value redacted

---

# 198. Credential Validation Checklist

Before using a discovered credential:

- [ ] Is credential testing authorised?
- [ ] Is the target service in scope?
- [ ] Is the account known?
- [ ] Could authentication cause lockout?
- [ ] Could MFA be triggered?
- [ ] Is the credential temporary?
- [ ] Can validity be established without login?
- [ ] Is one attempt sufficient?
- [ ] Can testing affect production?
- [ ] Is the credential being handled securely?

---

# 199. Reporting Checklist

For a credential finding:

- [ ] Describe the exposure mechanism
- [ ] Identify affected credential type
- [ ] Identify affected principal
- [ ] Identify target system
- [ ] Describe actual privilege
- [ ] Explain who can access the credential
- [ ] Include permission evidence
- [ ] Redact secret values
- [ ] Avoid unnecessary screenshots
- [ ] Recommend credential rotation
- [ ] Recommend root-cause remediation
- [ ] Consider log review
- [ ] Consider credential reuse
- [ ] Consider historical copies

---

# 200. Quick Reference

Current context:

```bash
whoami
id
echo "$HOME"
```

Home:

```bash
ls -la "$HOME"
```

Environment:

```bash
printenv | grep -Ei 'pass|secret|token|api[_-]?key|credential'
```

SSH:

```bash
ls -la ~/.ssh 2>/dev/null
```

SSH agent:

```bash
ssh-add -l 2>/dev/null
```

Git:

```bash
git config --global --list 2>/dev/null
```

Cloud directories:

```bash
ls -la ~/.aws ~/.azure ~/.config/gcloud ~/.kube ~/.docker 2>/dev/null
```

Application configuration:

```bash
find /opt /srv /var/www /usr/local -type f \( -name '.env' -o -name '*.conf' -o -name '*.ini' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' \) -ls 2>/dev/null
```

Credential file metadata:

```bash
stat -c '%A %a %U %G %n' /path/to/file
```

ACL:

```bash
getfacl /path/to/file
```

Path permissions:

```bash
namei -l /path/to/file
```

---

# 201. Credential Decision Tree

```text
Credential Candidate
       |
       v
Is It Actually a Secret?
       |
       +---- No -> Ignore / Informational
       |
       +---- Yes
              |
              v
       Why Can I Access It?
              |
              v
       Intended Access?
              |
       +------+------+
       |             |
      Yes            No
       |             |
       v             v
Determine Scope   Exposure Candidate
       |             |
       +------+------+
              |
              v
       Which Principal?
              |
              v
       Which Resource?
              |
              v
       Still Valid?
              |
       +------+------+
       |             |
      No            Yes
       |             |
       v             v
Historical       Determine Privilege
Exposure             |
                     v
               Minimal Validation
                     |
                     v
                  Impact
                     |
                     v
                  Report
```

---

# 202. Credential Attack-Surface Model

```text
                Linux Host
                    |
       +------------+------------+
       |            |            |
       v            v            v
   User Data    Applications   Services
       |            |            |
       v            v            v
   History        Config      Environment
   SSH            .env       Command Line
   Git            DB         Credential File
       |            |            |
       +------------+------------+
                    |
                    v
                 Secrets
                    |
       +------------+------------+
       |            |            |
       v            v            v
      Local       Remote        Cloud
       |            |            |
       v            v            v
      Sudo         SSH          IAM
      Apps         DB           APIs
      Root         Git          Clusters
```

---

# 203. Credential Security Model

Good credential security aims for:

```text
Least Privilege
      +
Minimum Exposure
      +
Short Lifetime
      +
Unique Identity
      +
Secure Storage
      +
Controlled Distribution
      +
Rotation
      +
Monitoring
```

---

# 204. Final Testing Model

A reliable Linux credential assessment follows:

```text
1. Establish the current identity.

2. Review the current user's home directory.

3. Review relevant shell history.

4. Review environment variables.

5. Review SSH configuration and key material.

6. Identify running applications.

7. Identify application configuration.

8. Review service environment files.

9. Review database client configuration.

10. Review relevant scripts and automation.

11. Review source repositories.

12. Review cloud CLI configuration where in scope.

13. Review container and Kubernetes configuration where in scope.

14. Review targeted backup files.

15. Identify potential credentials.

16. Distinguish secrets from public identifiers and placeholders.

17. Determine why the credential is accessible.

18. Record file ownership, permissions, ACLs, and parent-directory permissions.

19. Determine the affected principal.

20. Determine the target resource.

21. Determine credential privilege.

22. Determine credential lifetime.

23. Determine potential blast radius.

24. Validate only when necessary.

25. Use the minimum authentication required.

26. Avoid account lockouts and production impact.

27. Redact credential values from evidence.

28. Identify credential reuse only within scope.

29. Report the root cause of the exposure.

30. Recommend both access-control remediation and credential rotation.
```

The objective is not:

```text
Find as Many Passwords as Possible
```

The preferred model is:

```text
Credential
    |
    v
Exposure
    |
    v
Identity
    |
    v
Scope
    |
    v
Privilege
    |
    v
Minimal Validation
    |
    v
Impact
    |
    v
Secure Remediation
```

---

# Related Notes

- [Linux](index.md)
- [Linux Enumeration](enumeration.md)
- [Linux Services](services.md)
- [Linux Privilege Escalation](privilege-escalation.md)
- [Linux Cheatsheet](../cheatsheets/linux.md)
- [Networking Cheatsheet](../cheatsheets/networking.md)
- [Active Directory Credential Access](../active-directory/credential-access.md)
- [SSH Lateral Movement](../active-directory/lateral-movement.md)

---

# References

- [OpenSSH](https://www.openssh.com/){ target="_blank" rel="noopener noreferrer" }
- [ssh(1) - Linux manual page](https://man7.org/linux/man-pages/man1/ssh.1.html){ target="_blank" rel="noopener noreferrer" }
- [ssh-agent(1) - Linux manual page](https://man7.org/linux/man-pages/man1/ssh-agent.1.html){ target="_blank" rel="noopener noreferrer" }
- [ssh-add(1) - Linux manual page](https://man7.org/linux/man-pages/man1/ssh-add.1.html){ target="_blank" rel="noopener noreferrer" }
- [Git - Git Credentials](https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage){ target="_blank" rel="noopener noreferrer" }
- [Git Documentation](https://git-scm.com/docs){ target="_blank" rel="noopener noreferrer" }
- [systemd.exec](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html){ target="_blank" rel="noopener noreferrer" }
- [Docker CLI Configuration](https://docs.docker.com/reference/cli/docker/){ target="_blank" rel="noopener noreferrer" }
- [Kubernetes - Organizing Cluster Access Using kubeconfig Files](https://kubernetes.io/docs/concepts/configuration/organize-cluster-access-kubeconfig/){ target="_blank" rel="noopener noreferrer" }
- [Kubernetes - Secrets](https://kubernetes.io/docs/concepts/configuration/secret/){ target="_blank" rel="noopener noreferrer" }
- [AWS CLI Configuration and Credential File Settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html){ target="_blank" rel="noopener noreferrer" }
- [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/){ target="_blank" rel="noopener noreferrer" }
- [Google Cloud CLI Authentication](https://cloud.google.com/sdk/docs/authorizing){ target="_blank" rel="noopener noreferrer" }
- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs){ target="_blank" rel="noopener noreferrer" }
- [Ansible Vault](https://docs.ansible.com/ansible/latest/vault_guide/index.html){ target="_blank" rel="noopener noreferrer" }
- [TruffleHog](https://github.com/trufflesecurity/trufflehog){ target="_blank" rel="noopener noreferrer" }
- [Gitleaks](https://github.com/gitleaks/gitleaks){ target="_blank" rel="noopener noreferrer" }
- [PEASS-ng](https://github.com/peass-ng/PEASS-ng){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Unsecured Credentials](https://attack.mitre.org/techniques/T1552/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credentials from Password Stores](https://attack.mitre.org/techniques/T1555/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Private Keys](https://attack.mitre.org/techniques/T1552/004/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Credentials In Files](https://attack.mitre.org/techniques/T1552/001/){ target="_blank" rel="noopener noreferrer" }
- [MITRE ATT&CK - Bash History](https://attack.mitre.org/techniques/T1552/003/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

---

> Use credential-discovery techniques only on Linux systems, applications, repositories, cloud environments, and accounts you own or have explicit permission to assess. Credentials, private keys, tokens, session material, and password hashes are sensitive evidence. Prefer targeted searches, metadata, permission analysis, redaction, and minimal validation over broad secret collection or unnecessary authentication attempts.
