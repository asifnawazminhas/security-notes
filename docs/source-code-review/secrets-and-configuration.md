# Secrets and Configuration Source Code Review

Secrets and configuration are critical parts of source code security review.

Security vulnerabilities are not always caused by unsafe application logic.

A secure-looking application can still be compromised through:

```text
Hard-coded credentials
Exposed API keys
Weak JWT secrets
Cloud credentials
Database connection strings
Private keys
Debug configuration
Insecure CORS settings
Unsafe proxy trust
Weak session configuration
Disabled TLS verification
Development configuration in production
Exposed administrative functionality
Insecure framework settings
```

Configuration therefore forms part of the application's attack surface.

A useful model is:

```text
Source Code
    +
Configuration
    +
Environment
    +
Secrets
    +
Infrastructure
        |
        v
Effective Security Posture
```

The objective of this review is to answer:

```text
What secrets exist?

Where do they come from?

Where are they stored?

Where are they used?

Can they be exposed?

Are security-sensitive settings safe?

Do environment-specific configurations weaken security?

Does the deployed behaviour match the intended configuration?
```

---

# Authorised Testing

Use these techniques only against repositories, applications, environments, and infrastructure that you are authorised to assess.

Configuration files may contain highly sensitive information including:

```text
Passwords
API keys
Access tokens
Database credentials
Cloud credentials
Private keys
Signing keys
OAuth client secrets
SAML credentials
SMTP credentials
Service-account credentials
Internal hostnames
Internal network information
```

Do not unnecessarily copy, expose, or use discovered credentials.

The presence of a credential should normally be sufficient to investigate:

```text
What is it?

Where is it used?

Is it active?

What privilege does it represent?

Should it exist in this location?
```

Do not authenticate to unrelated systems merely because a credential has been discovered.

---

# Core Review Model

A useful workflow is:

```text
Repository
    |
    v
Configuration Discovery
    |
    v
Secrets Discovery
    |
    v
Security Configuration
    |
    v
Environment Differences
    |
    v
Runtime Behaviour
    |
    v
Exposure Analysis
    |
    v
Impact
```

---

# Configuration Is Code

Modern applications frequently define important security behaviour through configuration rather than application logic.

Examples:

```text
Authentication
Authorisation
Session handling
JWT validation
CORS
CSRF
Security headers
TLS
Database access
Proxy trust
Logging
Error handling
Debug mode
File storage
Cloud access
OAuth
OIDC
SAML
Rate limiting
```

Therefore:

```text
Code Review
    !=
Only Source Files
```

A complete review includes configuration.

---

# Start With Repository Discovery

Before searching for vulnerabilities, understand the repository.

Open the repository:

```bash
code .
```

Review:

```text
Root directory
Application directories
Configuration directories
Infrastructure directories
CI/CD configuration
Container configuration
Environment files
Build files
Deployment manifests
```

---

# Common Configuration Locations

Look for:

```text
config/
configuration/
settings/
deploy/
deployment/
infra/
infrastructure/
docker/
kubernetes/
k8s/
helm/
terraform/
.github/
.gitlab/
```

Also inspect the repository root.

---

# Find Configuration Files

Useful command:

```bash
find . -type f \( \
-name "*.env" -o \
-name ".env*" -o \
-name "*.yml" -o \
-name "*.yaml" -o \
-name "*.json" -o \
-name "*.toml" -o \
-name "*.ini" -o \
-name "*.conf" -o \
-name "*.config" -o \
-name "*.properties" \
\)
```

This will produce many files.

Manual triage is required.

---

# Important Files

Prioritise files such as:

```text
.env
.env.local
.env.development
.env.production

appsettings.json
appsettings.Development.json
appsettings.Production.json

application.properties
application.yml
application-dev.yml
application-prod.yml

settings.py
local_settings.py

config.py
configuration.py

config.js
config.ts

web.config
machine.config

docker-compose.yml
Dockerfile

values.yaml
Chart.yaml

terraform.tfvars
*.tf

serverless.yml
```

---

# Configuration Inventory

Build a simple inventory.

| File | Environment | Security Relevance |
|---|---|---|
| `.env` | Local | Secrets |
| `appsettings.json` | Default | Application configuration |
| `appsettings.Production.json` | Production | Production overrides |
| `application.yml` | Default | Spring configuration |
| `settings.py` | Django | Framework security |
| `docker-compose.yml` | Deployment | Services and credentials |
| `values.yaml` | Kubernetes | Deployment configuration |

---

# Environment Hierarchy

Applications often merge configuration.

For example:

```text
Default Configuration
        |
        v
Environment Configuration
        |
        v
Environment Variables
        |
        v
Runtime Overrides
```

Therefore, reviewing one file may not reveal the effective setting.

---

# Effective Configuration

Always ask:

```text
What value actually wins?
```

For example:

```text
appsettings.json

"RequireHttps": true
```

but:

```text
appsettings.Production.json

"RequireHttps": false
```

The production override may determine the effective behaviour.

---

# Environment Comparison

Compare:

```text
Development
Testing
Staging
Production
```

Look for differences in:

```text
Debug mode
Logging
Authentication
CORS
TLS
Database configuration
Secrets
Error handling
Security headers
Rate limiting
```

---

# Search Environment Names

```bash
rg -n -i \
'development|production|staging|testing|environment|profile' \
.
```

---

# Secrets Discovery

Start with broad searches.

```bash
rg -n -i \
'password|passwd|secret|api.?key|access.?key|private.?key|client.?secret|token|credential' \
.
```

This produces candidates.

It does not prove that every result is a secret.

---

# Candidate vs Confirmed Secret

A match such as:

```text
password
```

may represent:

```text
Variable name
Documentation
Placeholder
Test value
Configuration key
Actual credential
```

Therefore:

```text
Secret-Looking String
        !=
Confirmed Credential
```

---

# High-Value Secret Types

Prioritise:

```text
Cloud credentials
Database credentials
Private keys
JWT signing secrets
OAuth client secrets
SAML signing keys
API keys
Service-account credentials
SMTP credentials
Webhook secrets
Session secrets
Encryption keys
Third-party integration credentials
```

---

# Search for Private Keys

```bash
rg -n \
'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY' \
.
```

Also search:

```bash
find . -type f \( \
-name "*.pem" -o \
-name "*.key" -o \
-name "*.pfx" -o \
-name "*.p12" -o \
-name "*.jks" -o \
-name "*.keystore" \
\)
```

The presence of a key file requires further analysis.

---

# Search for Certificates

```bash
find . -type f \( \
-name "*.crt" -o \
-name "*.cer" -o \
-name "*.pem" -o \
-name "*.pfx" -o \
-name "*.p12" \
\)
```

Certificates themselves are often public.

Private keys are sensitive.

---

# Database Credentials

Search:

```bash
rg -n -i \
'connection.?string|database.?url|db.?password|db.?user|jdbc:|mongodb://|postgres://|postgresql://|mysql://' \
.
```

Review:

```text
Hostname
Username
Password
Database
TLS configuration
Privilege level
```

---

# Connection Strings

Example:

```text
Server=db.internal;
Database=production;
User Id=app;
Password=example;
```

Questions:

```text
Is the password real?

Is it committed?

Which environment uses it?

What privileges does the account have?

Is TLS required?

Can the credential be rotated?
```

---

# Cloud Credentials

Search for references to:

```text
AWS
Azure
Google Cloud
Service accounts
Access keys
Storage keys
SAS tokens
```

Example:

```bash
rg -n -i \
'aws_access_key|aws_secret|azure.*key|storage.*key|service.?account|client.?secret|tenant.?id|subscription.?id' \
.
```

Not every identifier is secret.

For example:

```text
Tenant IDs
Subscription IDs
Client IDs
```

are not necessarily credentials.

---

# AWS Credentials

Potentially sensitive values include:

```text
AWS access key ID
AWS secret access key
Session token
Assume-role credentials
```

Search configuration and Git history.

Do not attempt to use discovered cloud credentials outside the authorised scope.

---

# Azure Credentials

Potentially sensitive values include:

```text
Client secrets
Storage account keys
SAS tokens
Service principal credentials
Certificates
```

Search:

```bash
rg -n -i \
'client.?secret|storage.?key|shared.?access|sas.?token|connection.?string' \
.
```

---

# Google Cloud Credentials

Look for:

```text
Service account JSON
Private keys
API keys
Credentials files
```

Search:

```bash
rg -n \
'"private_key"|"private_key_id"|"client_email"|"project_id"' \
-g '*.json' \
.
```

Again, not every match is sensitive by itself.

---

# API Keys

Search:

```bash
rg -n -i \
'api.?key|apikey|x-api-key' \
.
```

Trace:

```text
Secret
  |
  v
Configuration
  |
  v
Application
  |
  v
External Service
```

Determine:

```text
Which service?

What privilege?

Server-side or client-side?

Can it be rotated?

Is it intentionally public?
```

---

# Public vs Private API Keys

Some API identifiers are designed to be public.

Examples may include:

```text
Public analytics identifiers
Publishable payment keys
Client IDs
Public project identifiers
```

Do not report every API-looking value as a secret.

Determine the provider's security model.

---

# JWT Secrets

Search:

```bash
rg -n -i \
'jwt.*secret|jwt.*key|signing.?key|token.?secret' \
.
```

Trace where the value is used.

```text
Configuration
     |
     v
JWT Signing / Verification
```

---

# Weak JWT Secrets

Look for patterns such as:

```text
secret
changeme
development
password
test
default
```

But determine whether the value is actually used in the relevant environment.

---

# JWT Algorithms

Search:

```bash
rg -n -i \
'HS256|HS384|HS512|RS256|RS384|RS512|ES256|algorithm' \
.
```

Algorithm presence alone does not indicate a vulnerability.

Review the complete JWT verification configuration.

---

# Session Secrets

Search:

```bash
rg -n -i \
'session.?secret|cookie.?secret|secret.?key' \
.
```

These may be used for:

```text
Session signing
Cookie signing
CSRF protection
Framework cryptography
```

---

# Django SECRET_KEY

Search:

```bash
rg -n \
'SECRET_KEY' \
-g '*.py' \
.
```

Example:

```python
SECRET_KEY = "..."
```

Determine:

```text
Is it a placeholder?

Is it development-only?

Is it committed?

Is production overriding it?
```

---

# Flask SECRET_KEY

Search:

```bash
rg -n \
'SECRET_KEY|secret_key' \
-g '*.py' \
.
```

The key may protect signed session cookies.

A hard-coded production key deserves careful review.

---

# Express Session Secrets

Search:

```bash
rg -n \
'secret\s*:' \
-g '*.js' \
-g '*.ts' \
.
```

Then identify whether the value belongs to:

```text
express-session
cookie-session
JWT
Other middleware
```

---

# ASP.NET Secrets

Search:

```bash
rg -n -i \
'connectionstrings|clientsecret|apikey|password|jwt.*key|signingkey' \
-g '*.json' \
-g '*.cs' \
.
```

Review:

```text
appsettings.json
appsettings.*.json
User Secrets usage
Environment variables
Azure Key Vault integration
```

---

# Spring Secrets

Search:

```bash
rg -n -i \
'password|secret|token|api-key|apikey|jwt|spring.datasource' \
-g '*.properties' \
-g '*.yml' \
-g '*.yaml' \
.
```

Review:

```text
application.properties
application.yml
application-*.properties
application-*.yml
```

---

# Laravel Secrets

Prioritise:

```text
.env
config/
```

Search:

```bash
rg -n -i \
'APP_KEY|DB_PASSWORD|MAIL_PASSWORD|AWS_SECRET|CLIENT_SECRET|API_KEY' \
.
```

---

# OAuth and OIDC Secrets

Search:

```bash
rg -n -i \
'client.?id|client.?secret|oauth|openid|oidc' \
.
```

Remember:

```text
Client ID
```

is generally not itself secret.

```text
Client Secret
```

normally is.

---

# OAuth Redirect Configuration

Search:

```bash
rg -n -i \
'redirect.?uri|callback.?url|oauth.*callback' \
.
```

Review:

```text
Exact redirect configuration
Environment-specific callbacks
Wildcard behaviour
Host construction
```

---

# SAML Configuration

Search:

```bash
rg -n -i \
'saml|metadata|entity.?id|certificate|private.?key|assertion.?consumer|acs' \
.
```

Review:

```text
Identity provider metadata
Service provider configuration
Signing certificates
Private keys
Audience
Entity IDs
Callback endpoints
```

---

# SMTP Credentials

Search:

```bash
rg -n -i \
'smtp|mail.*password|mail.*user|mail.*secret' \
.
```

SMTP accounts can sometimes provide access to:

```text
Password reset messages
Application notifications
Internal email
```

Assess impact based on actual privilege.

---

# Webhook Secrets

Search:

```bash
rg -n -i \
'webhook.*secret|signature.*secret|hmac.*secret' \
.
```

Trace:

```text
Webhook Request
       |
       v
Signature Verification
       |
       v
Secret
```

---

# Encryption Keys

Search:

```bash
rg -n -i \
'encryption.?key|encrypt.?key|master.?key|crypto.?key' \
.
```

Determine:

```text
Purpose
Algorithm
Storage
Rotation
Environment
```

---

# Hard-Coded Credentials

Common anti-pattern:

```python
username = "admin"
password = "..."
```

Search:

```bash
rg -n -i \
'(password|passwd|secret|token|api.?key)\s*[:=]' \
.
```

Manual triage is essential.

---

# Default Credentials

Search:

```bash
rg -n -i \
'admin.*admin|admin.*password|default.*password|changeme|change.?me' \
.
```

These may exist in:

```text
Tests
Documentation
Development setup
Seed data
Production bootstrap
```

Context determines severity.

---

# Seed Data

Search:

```bash
rg -n -i \
'seed|fixture|bootstrap|default.?user|create.?admin' \
.
```

Look for automatically created:

```text
Administrator accounts
Default passwords
API keys
Service users
```

---

# Test Credentials

Test directories often contain credentials.

Search:

```text
tests/
test/
fixtures/
samples/
examples/
```

Do not assume test credentials are harmless.

Sometimes they are reused in production or staging.

Verify before reporting.

---

# Example Configuration Files

Files such as:

```text
.env.example
config.example
settings.example.py
```

should normally contain placeholders rather than live secrets.

Compare:

```text
Example Configuration
        |
        v
Actual Configuration
```

---

# Git Ignore

Inspect:

```bash
cat .gitignore
```

Look for:

```text
.env
*.key
*.pem
credentials
secrets
appsettings.*.json
```

A missing ignore rule is not itself a vulnerability.

It can, however, increase the chance of accidental secret commits.

---

# Git History

Deleting a secret from the current branch does not necessarily remove it from Git history.

Search commits.

```bash
git log --all --oneline
```

Search changes containing a term:

```bash
git log -S 'password' --all
```

or:

```bash
git log -S 'client_secret' --all
```

---

# Git Grep

Search tracked content:

```bash
git grep -n -i \
'password\|secret\|token\|api.key'
```

---

# Inspect a Commit

```bash
git show <commit>
```

Review whether:

```text
Credentials were introduced
Credentials were removed
Security settings changed
Debugging was enabled
Authentication was weakened
```

---

# Git Blame

For suspicious configuration:

```bash
git blame path/to/config
```

This can identify the commit introducing the value.

---

# Secret Removed From Source

If history shows:

```diff
- API_KEY="real-value"
+ API_KEY=os.getenv("API_KEY")
```

do not assume the issue is resolved.

Ask:

```text
Was the credential rotated?

Does it remain active?

Does Git history still expose it?
```

Credential rotation is often required.

---

# Secret Scanning Tools

Manual searching should be complemented by dedicated scanners.

Useful tools include:

```text
Gitleaks
TruffleHog
GitHub Secret Scanning
Semgrep
OpenGrep
```

---

# Gitleaks

Gitleaks can detect potential secrets in repositories and Git history.

Project:

```text
https://github.com/gitleaks/gitleaks
```

Typical repository scan:

```bash
gitleaks git .
```

Review the current documentation for version-specific options.

---

# Gitleaks Results

Treat results as candidates.

For each result determine:

```text
Secret type
Location
Commit
Environment
Validity
Privilege
Exposure
```

---

# TruffleHog

Project:

```text
https://github.com/trufflesecurity/trufflehog
```

TruffleHog can search repositories and other supported sources for potential secrets.

For source-review engagements, use it only against authorised repositories and resources.

---

# Secret Verification

Some secret scanners can attempt credential verification.

This changes the nature of the activity from:

```text
Static discovery
```

to:

```text
Interaction with an external service
```

Only perform verification when it is explicitly within scope.

---

# GitHub Secret Scanning

Repositories hosted on GitHub may use GitHub secret scanning and push protection.

These can help identify supported secret formats before or after commits.

They complement local review.

---

# Visual Studio Code Search

Use:

```text
Ctrl + Shift + F
```

Search:

```text
password
secret
token
api_key
apikey
private_key
client_secret
connectionstring
```

Use include patterns to narrow searches.

Example:

```text
*.json
*.yml
*.yaml
*.env
*.properties
```

---

# Search Exclusions

Large repositories may contain:

```text
node_modules
vendor
dist
build
generated files
```

Use exclusions where appropriate.

For ripgrep:

```bash
rg -n -i \
'password|secret|token' \
-g '!node_modules/**' \
-g '!vendor/**' \
-g '!dist/**' \
-g '!build/**' \
.
```

Do not exclude directories blindly if they are security-relevant.

---

# Debug Mode

Search:

```bash
rg -n -i \
'debug\s*[:=]|DEBUG|development.?mode|dev.?mode' \
.
```

Potential impacts include:

```text
Stack traces
Environment disclosure
Source disclosure
Debug endpoints
Interactive debugging
Verbose errors
Sensitive logging
```

---

# Django DEBUG

Search:

```bash
rg -n \
'DEBUG\s*=' \
-g '*.py' \
.
```

Determine effective production configuration.

```python
DEBUG = True
```

in a development settings file is not automatically a production vulnerability.

---

# Flask Debug

Search:

```bash
rg -n \
'debug\s*=\s*True|DEBUG\s*=\s*True|FLASK_DEBUG' \
-g '*.py' \
.
```

Review how the application is launched in production.

---

# ASP.NET Environment

Search:

```bash
rg -n \
'UseDeveloperExceptionPage|IsDevelopment|ASPNETCORE_ENVIRONMENT' \
.
```

Developer exception functionality should not be assumed active simply because the code exists behind an environment check.

---

# Spring Debug and Actuator

Search:

```bash
rg -n -i \
'management\.endpoints|management\.endpoint|actuator|show-details|show-values' \
-g '*.properties' \
-g '*.yml' \
-g '*.yaml' \
.
```

Review exposure and authentication.

---

# Spring Actuator Exposure

Configuration may include:

```text
management.endpoints.web.exposure.include
```

Determine:

```text
Which endpoints are enabled?

Which endpoints are exposed?

Are they authenticated?

Are sensitive values masked?

Is the management interface separately bound?
```

Do not infer Internet exposure from the property alone.

---

# Error Handling

Search:

```bash
rg -n -i \
'stack.?trace|show.?errors|detailed.?errors|exception.?details' \
.
```

Review whether production responses expose:

```text
Stack traces
Filesystem paths
Database errors
Framework versions
Internal hostnames
Secrets
```

---

# Logging Configuration

Search:

```bash
rg -n -i \
'loglevel|log.level|logging.level|verbose|trace|debug' \
.
```

Excessive production logging can expose sensitive information.

---

# Sensitive Logging

Search code for:

```bash
rg -n -i \
'log.*password|logger.*password|log.*token|logger.*token|log.*secret|logger.*secret|console\.log.*token' \
.
```

Manual inspection is required.

---

# CORS Configuration

Search:

```bash
rg -n -i \
'cors|allow.?origin|allowed.?origin|Access-Control-Allow-Origin' \
.
```

Review:

```text
Allowed origins
Credential handling
Dynamic origin reflection
Wildcard configuration
Environment differences
```

---

# CORS Is Not Authentication

Remember:

```text
CORS
 !=
Authentication
```

and:

```text
CORS
 !=
Authorisation
```

CORS controls browser cross-origin access.

---

# CSRF Configuration

Search:

```bash
rg -n -i \
'csrf|xsrf|antiforgery|anti-forgery' \
.
```

Determine:

```text
Where CSRF protection is enabled
Which routes are excluded
Whether authentication uses cookies
Whether APIs use bearer tokens
```

---

# CSRF Exceptions

Search for:

```text
csrf_exempt
IgnoreAntiforgeryToken
disable csrf
csrf().disable()
```

Framework-specific examples:

```bash
rg -n \
'csrf_exempt|IgnoreAntiforgeryToken|csrf.*disable' \
.
```

An exception may be legitimate.

Review the authentication model.

---

# Cookie Security

Search:

```bash
rg -n -i \
'httponly|secure.?cookie|samesite|cookie.?secure|cookie.?domain|cookie.?path' \
.
```

Review:

```text
Secure
HttpOnly
SameSite
Domain
Path
Expiration
```

---

# Session Configuration

Search:

```bash
rg -n -i \
'session|session.?timeout|session.?cookie|idle.?timeout' \
.
```

Review:

```text
Expiration
Idle timeout
Absolute timeout
Rotation
Cookie settings
Server-side invalidation
```

---

# ASP.NET Cookie Configuration

Search:

```bash
rg -n \
'CookieSecurePolicy|HttpOnly|SameSite|Cookie\.SecurePolicy|ConfigureApplicationCookie' \
-g '*.cs' \
.
```

---

# Django Cookie Configuration

Search:

```bash
rg -n \
'SESSION_COOKIE_|CSRF_COOKIE_' \
-g '*.py' \
.
```

Common settings include:

```text
SESSION_COOKIE_SECURE
SESSION_COOKIE_HTTPONLY
SESSION_COOKIE_SAMESITE
CSRF_COOKIE_SECURE
CSRF_COOKIE_SAMESITE
```

Review effective production values.

---

# Flask Cookie Configuration

Search:

```bash
rg -n \
'SESSION_COOKIE_|REMEMBER_COOKIE_' \
-g '*.py' \
.
```

---

# Express Cookie Configuration

Search:

```bash
rg -n \
'httpOnly|sameSite|secure|cookie\s*:' \
-g '*.js' \
-g '*.ts' \
.
```

Trace which cookie the configuration applies to.

---

# Security Headers

Search:

```bash
rg -n -i \
'content-security-policy|strict-transport-security|x-content-type-options|referrer-policy|permissions-policy|frame-ancestors|x-frame-options' \
.
```

Determine whether headers are configured:

```text
Application middleware
Reverse proxy
Web server
CDN
API gateway
```

---

# Missing Header in Source

Do not conclude:

```text
Header not configured in application
        =
Header absent in production
```

It may be injected by infrastructure.

Runtime validation is necessary.

---

# Content Security Policy

Search:

```bash
rg -n -i \
'content-security-policy|script-src|default-src|unsafe-inline|unsafe-eval' \
.
```

Review the complete policy.

The presence of:

```text
unsafe-inline
unsafe-eval
```

weakens particular CSP protections but does not by itself prove an exploitable XSS vulnerability.

---

# HSTS

Search:

```bash
rg -n -i \
'strict-transport-security|hsts' \
.
```

Determine whether HTTPS termination occurs:

```text
Application
Reverse proxy
Load balancer
CDN
```

---

# TLS Verification

One of the most important configuration reviews is outbound TLS verification.

Search:

```bash
rg -n -i \
'verify\s*=\s*false|verify_ssl|ssl_verify|rejectUnauthorized|ServerCertificateCustomValidationCallback|TrustAll|HostnameVerifier' \
.
```

---

# Python TLS Verification

Search:

```bash
rg -n \
'verify\s*=\s*False' \
-g '*.py' \
.
```

Example:

```python
requests.get(
    url,
    verify=False
)
```

Determine whether the call handles sensitive traffic.

---

# Node.js TLS Verification

Search:

```bash
rg -n \
'rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED' \
-g '*.js' \
-g '*.ts' \
.
```

---

# Java TLS Verification

Search:

```bash
rg -n -i \
'TrustManager|X509TrustManager|HostnameVerifier|setDefaultHostnameVerifier|trustAll' \
-g '*.java' \
.
```

Custom trust managers deserve careful review.

---

# .NET TLS Verification

Search:

```bash
rg -n \
'ServerCertificateCustomValidationCallback|CertificateValidation|RemoteCertificateValidationCallback' \
-g '*.cs' \
.
```

Inspect whether certificate validation is bypassed.

---

# Proxy Trust

Applications behind reverse proxies may trust forwarded headers.

Search:

```bash
rg -n -i \
'trust proxy|forwardedheaders|x-forwarded|forwarded.?headers|proxyfix' \
.
```

Potentially security-sensitive headers include:

```text
X-Forwarded-For
X-Forwarded-Host
X-Forwarded-Proto
Forwarded
```

---

# Express trust proxy

Search:

```bash
rg -n \
'trust proxy' \
-g '*.js' \
-g '*.ts' \
.
```

Review the trust model.

An overly broad trust configuration can affect:

```text
Client IP
Protocol detection
Host handling
Rate limiting
Secure cookies
```

---

# ASP.NET Forwarded Headers

Search:

```bash
rg -n \
'UseForwardedHeaders|ForwardedHeadersOptions|KnownProxies|KnownNetworks' \
-g '*.cs' \
.
```

---

# Django Proxy Settings

Search:

```bash
rg -n \
'SECURE_PROXY_SSL_HEADER|USE_X_FORWARDED_HOST' \
-g '*.py' \
.
```

Review whether only trusted proxies can influence the relevant headers.

---

# Host Configuration

Search:

```bash
rg -n -i \
'allowed.?hosts|trusted.?hosts|host.?validation' \
.
```

---

# Django ALLOWED_HOSTS

Search:

```bash
rg -n \
'ALLOWED_HOSTS' \
-g '*.py' \
.
```

Understand environment overrides before concluding exposure.

---

# Flask Host Handling

Review:

```text
ProxyFix
SERVER_NAME
Host validation
Reverse proxy configuration
```

---

# File Upload Configuration

Search:

```bash
rg -n -i \
'upload|multipart|max.?file|max.?upload|allowed.?extension|content.?type' \
.
```

Review:

```text
Upload limits
Storage path
Allowed types
Filename handling
Public accessibility
Execution risk
```

---

# Upload Directories

Search for:

```text
uploads/
media/
attachments/
documents/
tmp/
temp/
```

Determine whether:

```text
Uploaded content is executable
Uploaded content is directly served
Content-Disposition is safe
Content types are controlled
```

---

# Filesystem Paths

Search:

```bash
rg -n -i \
'temp.?dir|upload.?dir|storage.?path|file.?path|base.?path' \
.
```

Configuration can determine whether a path traversal or upload issue becomes exploitable.

---

# XML Security Configuration

Search:

```bash
rg -n -i \
'doctype|external.?entities|resolve.?entities|xmlresolver|dtd' \
.
```

Review parser-specific configuration.

Do not assume XML parsing is vulnerable merely because XML is used.

---

# Deserialization Configuration

Search:

```bash
rg -n -i \
'type.?name.?handling|deseriali[sz]|polymorphic|default.?typing' \
.
```

Configuration can substantially affect deserialization risk.

---

# Jackson

Search:

```bash
rg -n \
'enableDefaultTyping|activateDefaultTyping|JsonTypeInfo|ObjectMapper' \
-g '*.java' \
.
```

Review actual type configuration and reachable data.

---

# Newtonsoft.Json

Search:

```bash
rg -n \
'TypeNameHandling|JsonSerializerSettings' \
-g '*.cs' \
.
```

The presence of `TypeNameHandling` requires contextual analysis.

---

# Rate Limiting Configuration

Search:

```bash
rg -n -i \
'rate.?limit|ratelimit|throttle|requests.?per|burst|quota' \
.
```

Determine whether sensitive endpoints are covered.

Prioritise:

```text
Login
MFA
Password reset
Registration
Search
Expensive APIs
Exports
```

---

# Authentication Configuration

Search:

```bash
rg -n -i \
'authentication|authorize|authorise|login|jwt|oauth|oidc|saml|mfa|2fa' \
.
```

Configuration may define:

```text
Anonymous routes
Role mappings
Authentication providers
Token lifetimes
OAuth providers
SAML metadata
```

---

# Anonymous Routes

Search framework-specific configuration for:

```text
permitAll
AllowAnonymous
AllowAny
anonymous
public
```

Do not report anonymous access without understanding what the route is intended to do.

---

# JWT Validation Configuration

Review:

```text
Issuer
Audience
Signing key
Algorithms
Expiration
Clock skew
Key source
```

Search:

```bash
rg -n -i \
'issuer|audience|signing.?key|validate.?issuer|validate.?audience|clock.?skew' \
.
```

---

# OAuth Configuration

Review:

```text
Client ID
Client secret
Redirect URIs
Issuer
Scopes
PKCE
State
Nonce
```

Configuration alone may not show whether runtime validation is correctly implemented.

Trace the authentication flow.

---

# SAML Configuration

Review:

```text
Entity ID
Metadata URL
Signing requirements
Encryption requirements
Certificates
Assertion lifetime
Audience
Destination
```

---

# Caching

Search:

```bash
rg -n -i \
'cache|redis|memcached' \
.
```

Review:

```text
Authentication state caching
Permission caching
Sensitive response caching
Cache key construction
Tenant separation
```

---

# Redis Credentials

Search:

```bash
rg -n -i \
'redis.*password|redis://|rediss://' \
.
```

Review whether:

```text
Authentication is configured
TLS is used where required
Sensitive credentials are committed
```

---

# Message Queues

Search:

```bash
rg -n -i \
'rabbitmq|kafka|amqp|queue|broker|service.?bus' \
.
```

Review:

```text
Credentials
TLS
Authentication
Authorisation
Queue names
Sensitive messages
```

---

# Storage Configuration

Search:

```bash
rg -n -i \
's3|bucket|blob|storage|container|object.?storage' \
.
```

Review:

```text
Credentials
Bucket/container names
Public access
Signed URL configuration
Upload behaviour
Encryption
```

---

# Signed URLs

Search:

```bash
rg -n -i \
'signed.?url|presigned|pre.?signed|sas.?token' \
.
```

Review:

```text
Expiration
Permissions
Object scope
Content type
HTTP method
```

---

# Internal URLs

Configuration may expose:

```text
Internal hostnames
Private IP addresses
Internal domains
Administrative endpoints
Service names
```

Search:

```bash
rg -n \
'https?://[^ "'\'']+' \
.
```

Not every internal URL constitutes a vulnerability.

Assess exposure and impact.

---

# Localhost and Internal Services

Search:

```bash
rg -n -i \
'localhost|127\.0\.0\.1|0\.0\.0\.0|internal|\.local' \
.
```

This can help map internal architecture.

---

# Binding Addresses

Review services bound to:

```text
127.0.0.1
0.0.0.0
Specific interface
```

Binding to:

```text
0.0.0.0
```

means listening on available interfaces, but does not by itself prove Internet exposure.

Firewall and infrastructure configuration matter.

---

# Administrative Interfaces

Search:

```bash
rg -n -i \
'admin|management|manage|actuator|debug|metrics|health|swagger|openapi' \
.
```

Review:

```text
Authentication
Network exposure
Sensitive information
Environment restrictions
```

---

# Swagger / OpenAPI

Search:

```bash
rg -n -i \
'swagger|openapi|api.?docs' \
.
```

API documentation is not inherently a vulnerability.

Determine whether it exposes sensitive or unintended functionality.

---

# Health Endpoints

Search:

```bash
rg -n -i \
'health|healthcheck|readiness|liveness' \
.
```

Review whether responses expose:

```text
Database status
Internal dependencies
Hostnames
Versions
Secrets
```

---

# Metrics

Search:

```bash
rg -n -i \
'metrics|prometheus|micrometer' \
.
```

Metrics may expose operational information.

Review authentication and network exposure.

---

# Docker Configuration

Review:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

---

# Dockerfile Review

Look for:

```text
Secrets copied into image
Root execution
Development servers
Debug configuration
Sensitive files
Unnecessary packages
Exposed management ports
```

---

# Docker COPY

Search:

```bash
rg -n \
'^COPY|^ADD' \
-g 'Dockerfile*' \
.
```

Determine whether:

```text
.env
.git
credentials
private keys
```

could be included.

---

# .dockerignore

Inspect:

```bash
find . -name '.dockerignore' -print
```

Review whether sensitive local files are excluded from build context where appropriate.

---

# Docker Environment Variables

Search:

```bash
rg -n \
'ENV|environment:|env_file:' \
-g 'Dockerfile*' \
-g '*.yml' \
-g '*.yaml' \
.
```

Avoid assuming environment variables are automatically secure.

They can still leak through:

```text
Logs
Process inspection
Container configuration
Debug endpoints
CI/CD
```

depending on environment.

---

# Kubernetes

Review:

```text
Deployment
StatefulSet
DaemonSet
Ingress
Service
ConfigMap
Secret
ServiceAccount
Role
RoleBinding
ClusterRole
ClusterRoleBinding
```

---

# Kubernetes Secrets

Search:

```bash
rg -n \
'kind:\s*Secret|secretKeyRef|envFrom|imagePullSecrets' \
-g '*.yml' \
-g '*.yaml' \
.
```

Kubernetes Secret objects are not equivalent to encryption merely because they are named `Secret`.

Review storage and deployment controls.

---

# ConfigMaps

Search:

```bash
rg -n \
'kind:\s*ConfigMap|configMapKeyRef' \
-g '*.yml' \
-g '*.yaml' \
.
```

Sensitive credentials should generally not be placed in ordinary ConfigMaps.

---

# Kubernetes Security Context

Search:

```bash
rg -n \
'securityContext|runAsUser|runAsNonRoot|privileged|allowPrivilegeEscalation|readOnlyRootFilesystem' \
-g '*.yml' \
-g '*.yaml' \
.
```

Container hardening is broader than application source review, but these settings can materially affect exploit impact.

---

# Privileged Containers

Search:

```bash
rg -n \
'privileged:\s*true' \
-g '*.yml' \
-g '*.yaml' \
.
```

Confirm actual deployment use before reporting.

---

# Host Mounts

Search:

```bash
rg -n \
'hostPath|docker\.sock' \
-g '*.yml' \
-g '*.yaml' \
.
```

These may significantly increase the impact of container compromise.

---

# Kubernetes Service Accounts

Review:

```text
Service account
RBAC
Token mounting
Cloud workload identity
```

Search:

```bash
rg -n \
'serviceAccountName|automountServiceAccountToken' \
-g '*.yml' \
-g '*.yaml' \
.
```

---

# Helm

Review:

```text
values.yaml
values-*.yaml
templates/
```

Environment-specific values may override secure defaults.

---

# Terraform

Search:

```bash
find . -type f \( \
-name "*.tf" -o \
-name "*.tfvars" \
\)
```

Review:

```text
Credentials
Public exposure
Security groups
Storage permissions
IAM
Network rules
Secrets
```

---

# Terraform Variables

Search:

```bash
rg -n -i \
'password|secret|token|key|credential' \
-g '*.tf' \
-g '*.tfvars' \
.
```

---

# CI/CD Configuration

Review:

```text
.github/workflows/
.gitlab-ci.yml
Jenkinsfile
azure-pipelines.yml
bitbucket-pipelines.yml
```

CI/CD often has access to highly privileged secrets.

---

# GitHub Actions

Search:

```bash
rg -n \
'secrets\.|permissions:|pull_request_target|workflow_run|workflow_dispatch' \
-g '*.yml' \
-g '*.yaml' \
.github \
2>/dev/null
```

Review:

```text
Secret usage
Workflow permissions
Untrusted code execution
Third-party actions
Artifact handling
Deployment credentials
```

---

# CI/CD Secrets in Commands

Look for:

```text
echo $SECRET
printenv
env
set
debug output
```

A secret may be securely stored but accidentally exposed through logs.

---

# Third-Party Actions

Review:

```text
uses:
```

in GitHub Actions.

Prefer understanding:

```text
Publisher
Pinning strategy
Permissions
Secrets available to action
```

Supply-chain review may be relevant.

---

# Dependency Configuration

Review:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml

requirements.txt
poetry.lock
Pipfile.lock

pom.xml
build.gradle

*.csproj
packages.lock.json

composer.json
composer.lock
```

Dependency security is covered more deeply in the dedicated dependency notes, but manifests can expose:

```text
Private registries
Credentials
Internal package names
Scripts
```

---

# Package Registry Credentials

Search:

```bash
rg -n -i \
'npm.*token|registry.*token|nuget.*key|pypi.*token|package.*token' \
.
```

Also inspect:

```text
.npmrc
.pypirc
NuGet.Config
pip.conf
```

---

# `.npmrc`

Search:

```bash
find . -name '.npmrc' -print
```

Look for:

```text
_authToken
_auth
username
password
registry
```

---

# `.pypirc`

Search:

```bash
find . -name '.pypirc' -print
```

Review for repository credentials.

---

# NuGet Configuration

Search:

```bash
find . -iname 'NuGet.Config' -print
```

Review package source credentials.

---

# Source Maps

Search:

```bash
find . -type f -name '*.map'
```

Source maps may expose:

```text
Original source
Internal paths
Comments
API endpoints
Development information
```

Assess whether they are deployed publicly.

---

# Frontend Secrets

One critical principle is:

```text
Anything delivered to the browser
cannot be treated as a secret.
```

This includes:

```text
JavaScript bundles
HTML
Source maps
Frontend environment variables
Client configuration
```

---

# Frontend Environment Variables

Frameworks may intentionally expose variables with prefixes such as:

```text
NEXT_PUBLIC_
VITE_
REACT_APP_
```

depending on the framework.

Values embedded into browser bundles are visible to users.

---

# Next.js

Search:

```bash
rg -n \
'NEXT_PUBLIC_|process\.env' \
-g '*.js' \
-g '*.jsx' \
-g '*.ts' \
-g '*.tsx' \
.
```

Determine whether sensitive server-side variables are accidentally exposed to client code.

---

# Vite

Search:

```bash
rg -n \
'VITE_|import\.meta\.env' \
-g '*.js' \
-g '*.jsx' \
-g '*.ts' \
-g '*.tsx' \
.
```

---

# React

Search:

```bash
rg -n \
'REACT_APP_|process\.env' \
-g '*.js' \
-g '*.jsx' \
-g '*.ts' \
-g '*.tsx' \
.
```

---

# Client-Side Configuration

Search browser code for:

```text
API keys
Internal API URLs
Feature flags
Environment names
Debug flags
Authentication configuration
```

Not all of these are vulnerabilities.

They help map the application.

---

# Feature Flags

Search:

```bash
rg -n -i \
'feature.?flag|feature.?toggle|enable.*feature|disable.*feature' \
.
```

Security controls should not rely solely on client-side feature flags.

---

# Security Feature Flags

Prioritise flags controlling:

```text
Authentication
MFA
Authorisation
Debugging
Administrative features
TLS
CSRF
Security headers
```

Determine who controls the flag and where enforcement occurs.

---

# Disabled Security

Search:

```bash
rg -n -i \
'disable.*auth|auth.*disabled|disable.*csrf|disable.*tls|verify.*false|allow.*all|permit.*all' \
.
```

These are review candidates, not automatic vulnerabilities.

---

# Commented-Out Security

Search:

```bash
rg -n -i \
'TODO.*security|TODO.*auth|FIXME.*security|FIXME.*auth|temporary.*auth|disable.*temporar' \
.
```

Comments can reveal intentionally weakened controls.

---

# TODO and FIXME

General search:

```bash
rg -n -i \
'TODO|FIXME|HACK|XXX|temporary|workaround' \
.
```

Prioritise comments near:

```text
Authentication
Authorisation
Cryptography
TLS
Input validation
Secrets
```

---

# Development Backdoors

Search for concepts such as:

```text
dev login
test login
bypass auth
mock auth
debug user
impersonate
```

```bash
rg -n -i \
'dev.?login|test.?login|bypass.?auth|mock.?auth|debug.?user|impersonat|login.?as' \
.
```

Confirm reachability and environment conditions.

---

# Test Routes

Search:

```bash
rg -n -i \
'/test|/debug|/dev|test.?route|debug.?route' \
.
```

A route name alone does not prove production exposure.

---

# Cryptographic Configuration

Search:

```bash
rg -n -i \
'md5|sha1|des|3des|rc4|aes|cipher|algorithm|encryption|hash' \
.
```

Do not report an algorithm merely because it appears.

Determine:

```text
Purpose
Mode
Key management
Security context
Protocol
Compatibility requirements
```

---

# Randomness

Search:

```bash
rg -n -i \
'Math\.random|java\.util\.Random|System\.Random|random\.random|rand\(' \
.
```

Determine whether the output is security-sensitive.

Examples:

```text
Password reset tokens
Session IDs
API keys
CSRF tokens
MFA secrets
```

Non-security use may be harmless.

---

# Default Configuration

Search for defaults:

```bash
rg -n -i \
'default|fallback|changeme|localhost|example\.com|test' \
.
```

Determine whether insecure fallback values can become active.

---

# Dangerous Fallback Pattern

Example:

```python
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "development-secret"
)
```

Questions:

```text
Can production start without SECRET_KEY?

Would the fallback then become active?

Does deployment guarantee the variable exists?
```

---

# Fail-Open Configuration

Security-sensitive configuration should be reviewed for fail-open behaviour.

Conceptually:

```text
Security Configuration Missing
          |
          v
Allow Operation
```

versus:

```text
Security Configuration Missing
          |
          v
Fail Startup / Deny Operation
```

---

# Missing Environment Variable

Search code handling configuration errors.

Example:

```text
if secret missing:
    disable authentication
```

would deserve investigation.

Safer designs often fail closed for security-critical configuration.

---

# Environment Variable Inventory

Search:

```bash
rg -n \
'process\.env|os\.environ|os\.getenv|Environment\.GetEnvironmentVariable|System\.getenv' \
.
```

This helps identify runtime configuration dependencies.

---

# Python Environment Variables

```bash
rg -n \
'os\.environ|os\.getenv' \
-g '*.py' \
.
```

---

# Node.js Environment Variables

```bash
rg -n \
'process\.env' \
-g '*.js' \
-g '*.ts' \
.
```

---

# .NET Environment Variables

```bash
rg -n \
'Environment\.GetEnvironmentVariable|IConfiguration|GetConnectionString' \
-g '*.cs' \
.
```

---

# Java Environment Variables

```bash
rg -n \
'System\.getenv|@Value|Environment\.getProperty' \
-g '*.java' \
.
```

---

# Configuration Source-to-Sink Analysis

Configuration values should also be traced.

Example:

```text
Environment Variable
        |
        v
Configuration Object
        |
        v
Security-Sensitive API
```

For example:

```text
TLS_VERIFY
    |
    v
Configuration
    |
    v
HTTP Client
```

---

# Secret Source-to-Sink Analysis

A secret can leak through a sink.

```text
Secret
  |
  v
Application
  |
  +--> Logger
  |
  +--> HTTP Response
  |
  +--> Error Message
  |
  +--> Frontend Bundle
  |
  +--> Metrics
```

Search both secret sources and exposure sinks.

---

# Secret Logging

Example model:

```text
OAuth Client Secret
        |
        v
Configuration
        |
        v
Debug Logger
```

This may expose a securely stored secret despite correct secret storage.

---

# Secrets in Exceptions

Review whether configuration objects are included in:

```text
Exception messages
Debug pages
Diagnostic endpoints
Health endpoints
```

---

# Secrets in API Responses

Search for configuration serialization.

Examples:

```text
config
settings
environment
diagnostics
debug
```

Trace whether secrets are filtered.

---

# Secrets in Frontend Bundles

Model:

```text
Server Environment
       |
       v
Build Process
       |
       v
JavaScript Bundle
       |
       v
Browser
```

Anything embedded into the final bundle should be considered exposed to users.

---

# Secret Management

Identify whether the application uses:

```text
Environment variables
Secret managers
Vault
Cloud key management
Kubernetes Secrets
Encrypted configuration
CI/CD secrets
```

---

# Secret Managers

Potential systems include:

```text
HashiCorp Vault
AWS Secrets Manager
Azure Key Vault
Google Secret Manager
Kubernetes Secrets
```

The use of a secret manager is not automatically secure.

Review:

```text
Authentication
Permissions
Retrieval
Caching
Logging
Rotation
```

---

# Secret Rotation

Ask:

```text
Can the secret be rotated?

How is rotation performed?

Does the application support multiple active keys?

Are old credentials invalidated?
```

---

# Key Rotation

For signing keys:

```text
Old Key
   |
   v
Transition
   |
   v
New Key
```

Review how previously issued tokens or sessions are handled.

---

# Least Privilege

A credential's risk depends heavily on its privilege.

Example:

```text
Database credential
```

may be:

```text
Read-only
Application schema owner
Database administrator
```

Do not assess impact from credential type alone.

---

# Configuration and Authorisation

Some applications define permissions through configuration.

Search:

```bash
rg -n -i \
'role|permission|policy|scope|group|admin' \
-g '*.json' \
-g '*.yml' \
-g '*.yaml' \
-g '*.properties' \
.
```

Review role mappings carefully.

---

# Wildcard Permissions

Search for:

```text
*
admin
all
FullControl
```

within security configuration.

Determine framework semantics.

A wildcard in unrelated configuration may have no security significance.

---

# Default Roles

Search:

```bash
rg -n -i \
'default.?role|default.?permission|new.?user.?role' \
.
```

Review privileges assigned to newly created users.

---

# Tenant Configuration

Search:

```bash
rg -n -i \
'tenant|organisation|organization|customer|workspace' \
.
```

Configuration may define:

```text
Tenant IDs
Default tenant
Tenant routing
Cross-tenant administrative behaviour
```

---

# Static Analysis

Static analysis can automate parts of secrets and configuration review.

Useful approaches:

```text
ripgrep
Semgrep
OpenGrep
CodeQL
Gitleaks
TruffleHog
```

Each solves a different problem.

---

# ripgrep

Best for:

```text
Fast manual discovery
Configuration search
Known variable names
Framework settings
Dangerous flags
```

---

# Semgrep / OpenGrep

Useful for detecting code structures such as:

```text
Hard-coded secret assigned to security configuration

TLS verification disabled

Debug mode enabled

Dangerous cryptographic configuration

Environment variable with insecure fallback
```

---

# Example Structural Rule Concept

Suppose Python code contains:

```python
requests.get(
    url,
    verify=False
)
```

A structural rule can identify similar calls.

The result should be treated as:

```text
TLS Verification Review Candidate
```

rather than automatically assigning vulnerability severity.

---

# CodeQL

CodeQL becomes useful where configuration values flow through application code.

Example:

```text
Environment Variable
      |
      v
Configuration Helper
      |
      v
HTTP Client
      |
      v
TLS Behaviour
```

or:

```text
Secret
  |
  v
Configuration
  |
  v
Logger
```

---

# Variant Analysis

Every confirmed configuration weakness should trigger variant analysis.

Example:

```text
One HTTP client disables TLS verification
        |
        v
Search all HTTP clients
        |
        v
Find other disabled verification
```

---

# Secret Variant Analysis

If one hard-coded credential is found:

```text
Confirmed Secret
      |
      v
Identify Secret Type
      |
      v
Search Current Tree
      |
      v
Search Git History
      |
      v
Search Related Services
      |
      v
Search CI/CD
      |
      v
Search Deployment Files
```

---

# Configuration Variant Analysis

If one environment enables:

```text
debug=true
```

compare all environments.

```text
Development
Staging
Production
Test
```

---

# Runtime Validation

Source code tells you:

```text
What may happen
```

Runtime testing tells you:

```text
What actually happens
```

Where appropriate, validate configuration through the application.

---

# Burp Suite

Burp Suite can help validate:

```text
Security headers
Cookie attributes
CORS
Debug responses
Error handling
Host handling
Authentication
Session behaviour
API exposure
```

---

# Runtime Configuration Model

```text
Source Configuration
        |
        v
Environment Overrides
        |
        v
Infrastructure
        |
        v
Runtime Application
        |
        v
Observed Behaviour
```

---

# Example: Security Header

Source review:

```text
No CSP found
```

Runtime:

```text
CSP added by reverse proxy
```

Conclusion:

```text
No missing-CSP finding based solely on application source.
```

---

# Example: Debug Mode

Source:

```python
DEBUG = True
```

but the file is:

```text
settings/development.py
```

Production uses:

```text
settings/production.py
```

with:

```python
DEBUG = False
```

The development setting alone does not establish a production vulnerability.

---

# Example: TLS Verification

Source:

```python
requests.get(
    payment_url,
    verify=False
)
```

Trace:

```text
Is this reachable?

What data is transmitted?

Which environment uses it?

Is another HTTP adapter overriding behaviour?
```

Then determine impact.

---

# Example: Hard-Coded Secret

Source:

```text
API_KEY = "..."
```

Analysis:

```text
Is it a real secret?

Which provider?

Production or test?

Still active?

What permissions?

Is it exposed in Git history?

Can it be rotated?
```

---

# Reporting Secrets

Avoid including complete sensitive credentials in reports where unnecessary.

Prefer redaction:

```text
API key:

abcd************************wxyz
```

Provide enough evidence to identify the affected credential without unnecessarily reproducing it.

---

# Reporting Configuration Findings

A strong configuration finding should include:

```text
Affected configuration
Effective environment
Security behaviour
Evidence
Runtime validation where relevant
Impact
Remediation
```

---

# Weak Finding

Avoid:

```text
DEBUG was found in the source code.
```

This does not establish:

```text
Production debug mode is enabled.
```

---

# Stronger Finding

Prefer:

```text
The production configuration enables verbose exception
responses. Runtime testing confirmed that unhandled
exceptions return framework stack traces containing
internal filesystem paths and implementation details.
```

This connects:

```text
Configuration
+
Runtime Behaviour
+
Exposure
+
Impact
```

---

# Weak Secret Finding

Avoid:

```text
The source contains an API key.
```

without determining what it represents.

---

# Stronger Secret Finding

Prefer:

```text
A production service credential is hard-coded in the
repository configuration and remains present in Git
history. The credential is used by the application to
authenticate to the internal service.

The credential should be removed from repository history,
rotated, and stored using the organisation's approved
secret-management mechanism.
```

Only claim production usage when evidence supports it.

---

# Remediation Principles

Prefer:

```text
Remove secrets from source
Rotate exposed credentials
Use appropriate secret management
Apply least privilege
Separate environments
Use secure production defaults
Fail closed
Disable production debugging
Verify TLS
Restrict trusted proxies
Use secure session settings
Review security headers
Protect administrative endpoints
```

---

# Environment Separation

Avoid sharing:

```text
Passwords
API keys
Signing keys
Databases
Service accounts
```

across:

```text
Development
Testing
Staging
Production
```

where separation is appropriate.

---

# Production Defaults

Security-sensitive production configuration should avoid relying on insecure fallbacks.

Prefer:

```text
Missing Security Configuration
          |
          v
Application Fails to Start
```

rather than silently using:

```text
development-secret
```

for critical production security.

---

# Secret Remediation Workflow

```text
Secret Discovered
      |
      v
Determine Exposure
      |
      v
Determine Privilege
      |
      v
Revoke / Rotate
      |
      v
Remove From Source
      |
      v
Address Git History
      |
      v
Move to Secret Management
      |
      v
Review Logs / Artifacts
      |
      v
Search for Variants
```

---

# Configuration Remediation Workflow

```text
Weak Configuration
      |
      v
Determine Effective Environment
      |
      v
Understand Runtime Impact
      |
      v
Implement Secure Configuration
      |
      v
Deploy
      |
      v
Runtime Retest
      |
      v
Check Other Environments
```

---

# Repository Review Checklist

```text
[ ] Repository structure mapped
[ ] Configuration directories identified
[ ] Environment files identified
[ ] Deployment files identified
[ ] CI/CD files identified
[ ] Container files identified
[ ] Infrastructure files identified
[ ] Example configuration files reviewed
[ ] .gitignore reviewed
[ ] .dockerignore reviewed
```

---

# Secrets Checklist

```text
[ ] Hard-coded passwords searched
[ ] API keys searched
[ ] Access tokens searched
[ ] Private keys searched
[ ] Database credentials searched
[ ] Cloud credentials searched
[ ] JWT secrets searched
[ ] Session secrets searched
[ ] OAuth client secrets searched
[ ] SAML keys searched
[ ] SMTP credentials searched
[ ] Webhook secrets searched
[ ] Encryption keys searched
[ ] Package registry credentials searched
[ ] Git history searched
[ ] Secret scanner used where appropriate
```

---

# Authentication Configuration Checklist

```text
[ ] Authentication providers reviewed
[ ] Anonymous routes reviewed
[ ] JWT configuration reviewed
[ ] OAuth/OIDC configuration reviewed
[ ] SAML configuration reviewed
[ ] MFA configuration reviewed
[ ] Password reset configuration reviewed
[ ] Session configuration reviewed
[ ] Cookie configuration reviewed
```

---

# Web Security Configuration Checklist

```text
[ ] CORS reviewed
[ ] CSRF reviewed
[ ] Security headers reviewed
[ ] CSP reviewed
[ ] HSTS reviewed
[ ] Host validation reviewed
[ ] Proxy trust reviewed
[ ] Forwarded headers reviewed
[ ] Error handling reviewed
[ ] Debug mode reviewed
[ ] Rate limiting reviewed
```

---

# Transport Security Checklist

```text
[ ] Outbound TLS verification reviewed
[ ] Custom certificate validation reviewed
[ ] Trust-all implementations searched
[ ] Hostname verification reviewed
[ ] Internal service TLS reviewed where relevant
```

---

# Application Configuration Checklist

```text
[ ] Production configuration identified
[ ] Development configuration identified
[ ] Staging configuration identified
[ ] Environment overrides understood
[ ] Insecure fallback values reviewed
[ ] Fail-open behaviour reviewed
[ ] Feature flags reviewed
[ ] Security feature flags reviewed
[ ] Default accounts reviewed
[ ] Seed data reviewed
```

---

# Infrastructure Checklist

```text
[ ] Docker configuration reviewed
[ ] Docker build context reviewed
[ ] Kubernetes manifests reviewed where applicable
[ ] Kubernetes Secrets reviewed
[ ] Kubernetes ConfigMaps reviewed
[ ] Kubernetes security contexts reviewed
[ ] Service accounts reviewed
[ ] Helm values reviewed
[ ] Terraform reviewed where applicable
[ ] Administrative interfaces reviewed
```

---

# CI/CD Checklist

```text
[ ] CI/CD configuration reviewed
[ ] Secret usage reviewed
[ ] Workflow permissions reviewed
[ ] Third-party actions reviewed
[ ] Debug output reviewed
[ ] Environment variables reviewed
[ ] Deployment credentials reviewed
[ ] Build artifacts reviewed
```

---

# Frontend Checklist

```text
[ ] Frontend environment variables reviewed
[ ] JavaScript bundles considered
[ ] Source maps reviewed
[ ] Client-side API keys reviewed
[ ] Client IDs distinguished from secrets
[ ] Internal URLs reviewed
[ ] Debug flags reviewed
[ ] Client-side security controls not mistaken for server controls
```

---

# Secret Review Decision Tree

```text
Potential secret found
        |
        v
Actual credential?
     +--+--+
     |     |
    No    Yes
     |     |
     v     v
  Ignore  Identify Service
            |
            v
       Production Use?
         +--+--+
         |     |
        No    Yes
         |     |
         v     v
      Assess  Determine
      Context Privilege
               |
               v
          Still Active?
            +--+--+
            |     |
           No    Yes
            |     |
            v     v
         Historical Exposure
                      |
                      v
                  Impact
                      |
                      v
              Rotate / Remediate
```

Do not test whether a secret is active unless such verification is authorised.

---

# Configuration Review Decision Tree

```text
Security-sensitive setting
          |
          v
Which environment?
          |
          v
Is this effective configuration?
       +--+--+
       |     |
      No    Yes
       |     |
       v     v
   Document  What Behaviour?
             |
             v
       Security Weakness?
          +--+--+
          |     |
         No    Yes
          |     |
          v     v
       Continue Runtime
                Validation
                   |
                   v
               Impact
```

---

# Combined Source Review Model

Secrets and configuration should not be isolated from the rest of source review.

```text
Repository
    |
    +--------------------+
    |                    |
    v                    v
Application Code     Configuration
    |                    |
    v                    v
Routes              Environment
    |                    |
    v                    v
Sources              Secrets
    |                    |
    v                    v
Transformations      Security Settings
    |                    |
    +---------+----------+
              |
              v
       Security Controls
              |
              v
             Sink
              |
              v
          Runtime
              |
              v
           Impact
```

---

# Practical Review Workflow

A practical review can follow:

```text
1. Open repository in VS Code

2. Identify all configuration files

3. Identify production configuration

4. Understand configuration precedence

5. Search for secrets

6. Search Git history

7. Run a dedicated secret scanner where appropriate

8. Review authentication configuration

9. Review session and cookie configuration

10. Review CORS and CSRF

11. Review proxy and host trust

12. Review TLS verification

13. Review error/debug configuration

14. Review security headers

15. Review file/storage configuration

16. Review Docker/Kubernetes configuration

17. Review CI/CD

18. Review frontend configuration

19. Trace security-sensitive configuration into code

20. Validate effective behaviour at runtime where appropriate

21. Perform variant analysis

22. Document confirmed findings
```

---

# Quick ripgrep Reference

## General secrets

```bash
rg -n -i \
'password|passwd|secret|api.?key|access.?key|private.?key|client.?secret|token|credential' \
.
```

## Private keys

```bash
rg -n \
'BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY' \
.
```

## Database

```bash
rg -n -i \
'connection.?string|database.?url|db.?password|jdbc:|mongodb://|postgres://|postgresql://|mysql://' \
.
```

## JWT

```bash
rg -n -i \
'jwt.*secret|jwt.*key|signing.?key|issuer|audience' \
.
```

## OAuth

```bash
rg -n -i \
'oauth|openid|oidc|client.?secret|redirect.?uri' \
.
```

## SAML

```bash
rg -n -i \
'saml|entity.?id|metadata|assertion.?consumer|private.?key' \
.
```

## Debugging

```bash
rg -n -i \
'debug\s*[:=]|DEBUG|developer.?exception|detailed.?errors' \
.
```

## CORS

```bash
rg -n -i \
'cors|allow.?origin|allowed.?origin|Access-Control-Allow-Origin' \
.
```

## CSRF

```bash
rg -n -i \
'csrf|xsrf|antiforgery|anti-forgery' \
.
```

## Cookies

```bash
rg -n -i \
'httponly|samesite|cookie.?secure|session.?cookie' \
.
```

## TLS verification

```bash
rg -n -i \
'verify\s*=\s*false|rejectUnauthorized|TrustAll|HostnameVerifier|ServerCertificateCustomValidationCallback' \
.
```

## Proxy trust

```bash
rg -n -i \
'trust proxy|forwardedheaders|x-forwarded|proxyfix' \
.
```

## Security headers

```bash
rg -n -i \
'content-security-policy|strict-transport-security|x-content-type-options|referrer-policy|permissions-policy|x-frame-options' \
.
```

## Administrative functionality

```bash
rg -n -i \
'admin|management|actuator|debug|metrics|swagger|openapi' \
.
```

## TODO security

```bash
rg -n -i \
'TODO.*security|FIXME.*security|TODO.*auth|FIXME.*auth|bypass.?auth|mock.?auth' \
.
```

---

# Final Testing Model

```text
                      REPOSITORY
                          |
          +---------------+---------------+
          |                               |
          v                               v
     SOURCE CODE                    CONFIGURATION
          |                               |
          v                               v
        ROUTES                       ENVIRONMENTS
          |                               |
          v                               v
       SOURCES                          SECRETS
          |                               |
          v                               v
   TRANSFORMATIONS                SECURITY SETTINGS
          |                               |
          +---------------+---------------+
                          |
                          v
                   SECURITY CONTROLS
                          |
                          v
                        SINKS
                          |
                          v
                  RUNTIME BEHAVIOUR
                          |
                          v
                        IMPACT
                          |
                          v
                  VARIANT ANALYSIS
```

The important principle is:

```text
Secure source code
      +
Insecure configuration
      =
Potentially insecure application
```

and:

```text
Secret stored securely
      +
Secret leaked through logs
      =
Secret exposure
```

and:

```text
Secure default
      +
Insecure production override
      =
Insecure effective configuration
```

Always review the configuration that actually controls the deployed security behaviour.

---

# Related Source Code Review Notes

```text
docs/source-code-review/index.md
docs/source-code-review/methodology.md
docs/source-code-review/routes-and-entry-points.md
docs/source-code-review/source-to-sink-analysis.md
docs/source-code-review/authentication-authorisation.md
docs/source-code-review/variant-analysis.md

docs/source-code-review/dotnet.md
docs/source-code-review/java.md
docs/source-code-review/php.md
docs/source-code-review/python.md
docs/source-code-review/django.md
docs/source-code-review/flask.md
docs/source-code-review/nodejs.md
docs/source-code-review/javascript.md
```

---

# Related Static Analysis Notes

```text
docs/source-code-review/static-analysis/index.md
docs/source-code-review/static-analysis/ripgrep.md
docs/source-code-review/static-analysis/semgrep.md
docs/source-code-review/static-analysis/opengrep.md
docs/source-code-review/static-analysis/codeql.md
```

---

# Related Web Security Notes

```text
docs/web/authentication.md
docs/web/authorisation.md
docs/web/session-management.md
docs/web/password-reset.md
docs/web/mfa.md
docs/web/jwt.md
docs/web/oauth-oidc.md
docs/web/saml.md

docs/web/cors.md
docs/web/csrf.md
docs/web/http-security-headers.md
docs/web/host-header-attacks.md
docs/web/information-disclosure.md
docs/web/rate-limiting.md

docs/web/file-upload.md
docs/web/path-traversal.md
docs/web/ssrf.md
docs/web/xxe.md
docs/web/deserialization.md

docs/web/secrets-exposure.md
docs/web/dependency-security.md
docs/web/third-party-javascript.md
```

---

# References

## OWASP Secrets Management Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
```

## OWASP Secure Code Review Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html
```

## OWASP Configuration Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Secure_Cloud_Architecture_Cheat_Sheet.html
```

## OWASP Logging Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
```

## OWASP Transport Layer Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html
```

## OWASP HTTP Headers Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
```

## OWASP Session Management Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
```

## OWASP Cross-Origin Resource Sharing Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/CORS_Configuration_Cheat_Sheet.html
```

## OWASP CSRF Prevention Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
```

## OWASP Docker Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html
```

## OWASP Kubernetes Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html
```

## OWASP Third-Party JavaScript Management Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Third_Party_Javascript_Management_Cheat_Sheet.html
```

## OWASP Web Security Testing Guide

```text
https://owasp.org/www-project-web-security-testing-guide/
```

## Gitleaks

```text
https://github.com/gitleaks/gitleaks
```

## Gitleaks Documentation

```text
https://gitleaks.io/
```

## TruffleHog

```text
https://github.com/trufflesecurity/trufflehog
```

## GitHub Secret Scanning

```text
https://docs.github.com/en/code-security/secret-scanning
```

## GitHub Push Protection

```text
https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection
```

## Microsoft ASP.NET Core Configuration

```text
https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/
```

## Microsoft ASP.NET Core Safe Storage of App Secrets

```text
https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets
```

## Spring Boot Externalized Configuration

```text
https://docs.spring.io/spring-boot/reference/features/external-config.html
```

## Django Settings

```text
https://docs.djangoproject.com/en/stable/ref/settings/
```

## Flask Configuration

```text
https://flask.palletsprojects.com/en/stable/config/
```

## Express Production Security

```text
https://expressjs.com/en/advanced/best-practice-security.html
```

## Kubernetes Secrets

```text
https://kubernetes.io/docs/concepts/configuration/secret/
```

## Docker Build Secrets

```text
https://docs.docker.com/build/building/secrets/
```

## HashiCorp Vault

```text
https://developer.hashicorp.com/vault/docs
```

## AWS Secrets Manager

```text
https://docs.aws.amazon.com/secretsmanager/
```

## Azure Key Vault

```text
https://learn.microsoft.com/en-us/azure/key-vault/
```

## Google Secret Manager

```text
https://cloud.google.com/secret-manager/docs
```

## Semgrep

```text
https://semgrep.dev/docs/
```

## OpenGrep

```text
https://opengrep.dev/
```

## CodeQL

```text
https://codeql.github.com/docs/
```

## ripgrep

```text
https://github.com/BurntSushi/ripgrep
```

---

# Summary

Secrets and configuration review should answer:

```text
What security-sensitive configuration exists?

Which configuration is effective in production?

Where are secrets stored?

How are secrets loaded?

Where are secrets used?

Can secrets reach logs, responses, bundles, or diagnostics?

Are production security settings safe?

Can environment overrides weaken them?

Do containers or deployment manifests introduce additional risk?

Does CI/CD expose credentials?

Does runtime behaviour match the source configuration?
```

The workflow is:

```text
Discover Configuration
        |
        v
Identify Environments
        |
        v
Understand Precedence
        |
        v
Discover Secrets
        |
        v
Search Git History
        |
        v
Review Security Settings
        |
        v
Review Deployment
        |
        v
Review CI/CD
        |
        v
Trace Configuration Into Code
        |
        v
Runtime Validation
        |
        v
Variant Analysis
```

The final rule is:

```text
Do not review configuration as isolated text.

Trace it into the security behaviour it controls.
```

and:

```text
Do not report a secret-looking value solely because it
looks sensitive.

Determine what it represents, where it is used, and what
security impact its exposure creates.
```

and:

```text
Do not assume the default configuration is the deployed
configuration.

Determine the effective configuration.
```
