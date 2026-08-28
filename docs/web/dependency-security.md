# Dependency Security

Dependency security is the process of identifying, assessing, maintaining, and securely consuming third-party software components used by an application.

Modern applications rarely consist entirely of code written by the organisation developing them.

Instead, applications commonly depend on:

```text
Open-source libraries
Frameworks
Package-manager modules
SDKs
Runtime libraries
Operating-system packages
Container base images
Build plugins
CI/CD actions
Third-party components
Transitive dependencies
```

A typical application may therefore look like:

```text
Application
    |
    +-- Application Code
    |
    +-- Framework
    |
    +-- Direct Dependency A
    |       |
    |       +-- Transitive Dependency A1
    |       +-- Transitive Dependency A2
    |
    +-- Direct Dependency B
    |       |
    |       +-- Transitive Dependency B1
    |
    +-- Runtime
    |
    +-- Operating-System Packages
```

A security weakness anywhere in this dependency graph can potentially affect the application.

!!! warning "Authorised Security Testing"
    Only scan repositories, package registries, container images, build systems, CI/CD environments, and infrastructure that are explicitly within the authorised assessment scope. Dependency analysis itself is generally passive, but package installation, build execution, dependency resolution, or running project scripts may execute third-party code.

---

# Why Dependency Security Matters

Third-party components can introduce vulnerabilities even when the application's own code is secure.

Examples include:

```text
Remote code execution
Cross-site scripting
Prototype pollution
Path traversal
Authentication bypass
Deserialization vulnerabilities
SQL injection
Server-side request forgery
Denial of service
Information disclosure
Cryptographic weaknesses
Privilege escalation
```

The basic problem is:

```text
Application
     |
     v
Uses Dependency
     |
     v
Dependency Contains Vulnerability
     |
     v
Application Uses Affected Functionality
     |
     v
Vulnerability May Become Reachable
```

However:

```text
Vulnerable dependency detected
```

does not always mean:

```text
Application is exploitable
```

The dependency must be assessed in context.

---

# Dependency Security vs Software Supply Chain Security

Dependency security is part of the larger software supply chain security problem.

Dependency security primarily focuses on:

```text
What components does the application use?

Are they vulnerable?

Are they maintained?

Are they trustworthy?

Are versions controlled?

Can they be safely updated?
```

Software supply chain security is broader:

```text
Source Code
    |
    v
Version Control
    |
    v
Dependencies
    |
    v
Build System
    |
    v
CI/CD
    |
    v
Artifact Repository
    |
    v
Container Registry
    |
    v
Deployment
    |
    v
Production
```

Threats can occur at every stage.

---

# Dependency Threat Model

Dependency-related security issues can be divided into several broad categories:

```text
Known Vulnerabilities
        |
        +-- CVEs
        +-- Security advisories
        +-- Vulnerable versions

Outdated Components
        |
        +-- Unsupported versions
        +-- End-of-life software
        +-- Abandoned packages

Dependency Resolution Attacks
        |
        +-- Dependency confusion
        +-- Typosquatting
        +-- Namespace confusion

Compromised Dependencies
        |
        +-- Maintainer compromise
        +-- Malicious package update
        +-- Registry compromise

Build-Time Risks
        |
        +-- Installation scripts
        +-- Build scripts
        +-- Plugins
        +-- CI/CD dependencies

Integrity Risks
        |
        +-- Modified packages
        +-- Missing integrity verification
        +-- Untrusted registries
```

---

# Direct Dependencies

A direct dependency is explicitly declared by the application.

Example:

```json
{
  "dependencies": {
    "express": "5.1.0"
  }
}
```

Conceptually:

```text
Application
    |
    v
Express
```

The application developer intentionally selected the dependency.

---

# Transitive Dependencies

Dependencies frequently depend on other dependencies.

Example:

```text
Application
    |
    v
Package A
    |
    v
Package B
    |
    v
Package C
```

The application may never explicitly declare:

```text
Package B
Package C
```

but they are still part of the application's dependency graph.

This is important because vulnerabilities frequently exist in transitive dependencies.

---

# Dependency Graph

A dependency graph shows the relationships between software components.

Example:

```text
                     Application
                         |
             +-----------+-----------+
             |                       |
             v                       v
         Framework                 SDK
             |                       |
       +-----+-----+                 |
       |           |                 |
       v           v                 v
   Library A   Library B         Library C
       |                             |
       v                             v
   Library D                     Library E
```

Security testing should therefore consider:

```text
Direct dependencies
+
Transitive dependencies
```

---

# Manifest Files

Package managers normally use manifest files to describe dependencies.

Common examples:

```text
JavaScript / Node.js
package.json

Python
requirements.txt
pyproject.toml
Pipfile

Java
pom.xml
build.gradle
build.gradle.kts

.NET
*.csproj
packages.config

PHP
composer.json

Ruby
Gemfile

Rust
Cargo.toml

Go
go.mod
```

These files often describe:

```text
Requested dependency ranges
Direct dependencies
Development dependencies
Package metadata
Build configuration
```

---

# Lockfiles

Lockfiles record resolved dependency versions.

Examples:

```text
package-lock.json
yarn.lock
pnpm-lock.yaml

Pipfile.lock
poetry.lock

Cargo.lock

composer.lock

Gemfile.lock
```

Conceptually:

```text
Manifest
   |
   | requests
   v
package >= 1.0
   |
   v
Dependency Resolution
   |
   v
package 1.4.7
   |
   v
Lockfile
```

Lockfiles improve reproducibility by recording resolved versions.

---

# Why Lockfiles Matter

Without reliable dependency locking:

```text
Build Today
    |
    v
Dependency 1.2.1
```

may differ from:

```text
Build Next Month
    |
    v
Dependency 1.3.0
```

even when application source code has not changed.

This can introduce:

```text
Unexpected behaviour
New vulnerabilities
Compatibility issues
Supply-chain risk
```

Lockfiles help make builds more deterministic.

---

# Pinning Dependencies

Dependency pinning controls which versions may be installed.

Examples:

```text
Exact:

1.2.3
```

versus ranges such as:

```text
>=1.2
```

or ecosystem-specific range syntax.

Pinning can improve reproducibility, but it creates an important responsibility:

```text
Pinned dependencies must still be updated.
```

Otherwise:

```text
Version pinning
      |
      v
Never updated
      |
      v
Known vulnerabilities accumulate
```

Therefore:

```text
Pinning
+
Automated monitoring
+
Controlled updates
```

is stronger than pinning alone.

---

# Known Vulnerable Components

A dependency may have publicly known vulnerabilities.

Example:

```text
Application
    |
    v
Library 2.4.1
    |
    v
Security Advisory
    |
    v
Versions < 2.4.5 affected
```

The first question is:

```text
Is the installed version affected?
```

The second is:

```text
Does the application expose the vulnerable functionality?
```

---

# Vulnerability Databases

Dependency scanners may use vulnerability information from sources such as:

```text
OSV
NVD
GitHub Security Advisories
Vendor advisories
Language-specific advisory databases
CISA KEV
```

Different scanners may produce different results because they may use:

```text
Different databases
Different package identification
Different version matching
Different severity information
Different update schedules
```

For important findings, review the original advisory.

---

# CVE

CVE stands for:

```text
Common Vulnerabilities and Exposures
```

A CVE identifier resembles:

```text
CVE-2025-12345
```

A CVE identifies a vulnerability.

It does not by itself tell you:

```text
Whether your application is affected

Whether the vulnerable code is reachable

Whether exploitation is possible

Whether compensating controls exist
```

---

# CVSS

CVSS can provide a standardised vulnerability severity score.

For example:

```text
CVSS 9.8 Critical
```

However:

```text
CVSS score of upstream vulnerability
```

is not automatically:

```text
Risk to this application
```

Application context still matters.

---

# CISA Known Exploited Vulnerabilities

The CISA Known Exploited Vulnerabilities catalogue identifies vulnerabilities known to have been exploited in the wild.

Conceptually:

```text
Known vulnerability
      |
      v
Known exploitation?
      |
   +--+--+
   |     |
  NO    YES
   |     |
   v     v
Normal   Increased
triage   priority
```

Presence in a known-exploited catalogue can significantly influence remediation priority.

---

# Reachability

A vulnerable dependency may contain vulnerable functionality that the application never calls.

Example:

```text
Application
    |
    v
Dependency
    |
    +-- safe_function()
    |
    +-- vulnerable_function()
```

If the application only uses:

```text
safe_function()
```

the vulnerability may not currently be reachable.

However, this does not necessarily mean the dependency should remain unpatched.

Future code changes could make the vulnerable path reachable.

---

# Reachability Analysis

A stronger assessment asks:

```text
Is dependency installed?

        |
        v

Is affected version installed?

        |
        v

Is vulnerable component loaded?

        |
        v

Is vulnerable function reachable?

        |
        v

Can attacker-controlled data reach it?

        |
        v

Are exploitation conditions satisfied?
```

This provides more useful information than simply reporting every CVE discovered by a scanner.

---

# Runtime vs Development Dependencies

Some ecosystems distinguish:

```text
Runtime dependencies
```

from:

```text
Development dependencies
```

Development dependencies may include:

```text
Test frameworks
Linters
Build tools
Bundlers
Documentation generators
Developer utilities
```

A vulnerable development dependency may not be shipped into production.

However, it can still matter because it may execute inside:

```text
Developer workstations
Build environments
CI/CD pipelines
```

Therefore:

```text
Not present in production
```

does not automatically mean:

```text
No security impact
```

---

# Build-Time Dependencies

Build systems may execute dependency code.

Examples:

```text
npm lifecycle scripts
Maven plugins
Gradle plugins
Python build backends
GitHub Actions
CI plugins
Container build tools
```

This creates a separate attack surface:

```text
Malicious Dependency
        |
        v
Package Installation
        |
        v
Build Script Executes
        |
        v
CI Runner Compromised
```

This is a software supply chain risk rather than simply a runtime application vulnerability.

---

# Outdated Dependencies

A dependency can be risky even when no currently known CVE applies.

Reasons include:

```text
No longer maintained
Unsupported
End-of-life
No security patches
Abandoned repository
Deprecated
```

Conceptually:

```text
Old Dependency
      |
      v
No Maintainer
      |
      v
New Vulnerability Found
      |
      v
No Patch Available
```

This creates long-term security risk.

---

# End-of-Life Components

An end-of-life component is no longer supported by its vendor or maintainers.

Examples may include:

```text
Old frameworks
Old runtimes
Old operating systems
Deprecated libraries
```

Security testing should identify:

```text
Component
Version
Support status
Upgrade path
```

---

# Dependency Confusion

Dependency confusion is a dependency-resolution attack.

Consider an organisation using an internal package:

```text
company-auth
```

The build system searches:

```text
Internal Registry
+
Public Registry
```

If resolution is unsafe:

```text
Attacker publishes:

company-auth

to public registry
```

The package manager may select the attacker-controlled package.

Conceptually:

```text
Build System
      |
      +----------------+
      |                |
      v                v
Internal Registry   Public Registry
company-auth        company-auth
1.0.0               99.0.0
      |                |
      +-------+--------+
              |
              v
      Unsafe Resolution
              |
              v
      Malicious Package
```

---

# Dependency Confusion Preconditions

Typical conditions include:

```text
Private package namespace

Public registry also queried

Package name discoverable

Resolution rules prefer or allow public package

Attacker can publish matching name
```

Modern package managers and repository configurations differ considerably.

Always determine the actual resolution behaviour before concluding that dependency confusion is possible.

---

# Testing Dependency Confusion Safely

Do not publish packages matching an organisation's internal dependencies to a public registry unless this is explicitly authorised.

A safer assessment approach is:

```text
Identify private package names
        |
        v
Inspect registry configuration
        |
        v
Understand package resolution
        |
        v
Check namespace protections
        |
        v
Use controlled internal test package
        |
        v
Verify resolution safely
```

Avoid creating packages that could accidentally be installed by production systems.

---

# Typosquatting

Typosquatting involves malicious packages with names resembling legitimate packages.

Example concept:

```text
legitimate-package
```

versus:

```text
legitmate-package
```

or:

```text
legitimate_packagе
```

where visually similar characters may be involved.

The goal is to cause developers or automated systems to install the wrong package.

---

# Package Namespace Security

Package ecosystems use different namespace models.

Examples include:

```text
Scoped packages
Organisation namespaces
Package ownership
Registry-level namespaces
```

Where available, organisations should reserve and protect package namespaces.

---

# Malicious Packages

Not all package risk comes from accidental vulnerabilities.

A package may intentionally contain malicious behaviour.

Examples:

```text
Credential theft
Environment-variable collection
SSH key collection
Backdoors
Cryptocurrency mining
CI token theft
Network callbacks
Malicious install scripts
```

Traditional CVE scanning may not detect this.

---

# Maintainer Compromise

A legitimate package can become malicious if a maintainer account is compromised.

Conceptually:

```text
Trusted Package
      |
      v
Maintainer Account Compromised
      |
      v
Malicious Version Published
      |
      v
Automatic Dependency Update
      |
      v
Consumers Install It
```

This is why dependency security requires more than vulnerability scanning.

---

# Package Ownership Changes

Security review should consider significant project changes such as:

```text
New maintainers
Repository transfer
Namespace transfer
Package ownership changes
Sudden release activity
Unexpected dependency additions
```

These are not automatically malicious.

They are signals that may justify additional review.

---

# Package Installation Scripts

Some package ecosystems allow code execution during installation.

Examples include:

```text
preinstall
install
postinstall
build hooks
setup hooks
plugins
```

This means:

```text
Installing an untrusted package
```

can itself be dangerous.

!!! warning "Do Not Install Unknown Packages Casually"
    When investigating suspicious packages, avoid installing or building them directly on your normal workstation. Use an isolated analysis environment and understand whether installation or build operations execute package-controlled code.

---

# JavaScript and Node.js

Common dependency files:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
```

Inspect:

```bash
cat package.json
```

Look for:

```text
dependencies
devDependencies
optionalDependencies
scripts
```

---

# npm audit

For npm projects:

```bash
npm audit
```

This audits dependencies described by the npm project and lockfile against vulnerability information available through the configured registry.

JSON output:

```bash
npm audit --json
```

A CI-oriented threshold can be specified:

```bash
npm audit --audit-level=high
```

This affects the exit behaviour based on vulnerability severity.

---

# Be Careful With npm audit fix

npm can attempt remediation:

```bash
npm audit fix
```

However, during a penetration test or code review, do not immediately modify the client's project.

Instead:

```text
Scan
  |
  v
Understand vulnerability
  |
  v
Identify fixed version
  |
  v
Document recommendation
```

If remediation testing is authorised, changes should be performed in a controlled branch or test environment.

---

# npm audit --force

Be especially cautious with:

```bash
npm audit fix --force
```

This may install updates outside the normal dependency range and can introduce breaking changes.

Do not run it casually against client code.

---

# npm Dependency Tree

List installed packages:

```bash
npm list
```

A specific dependency:

```bash
npm list lodash
```

This can help identify:

```text
Why is this package installed?

Is it direct?

Which package depends on it?
```

---

# npm Outdated

Check for outdated packages:

```bash
npm outdated
```

Remember:

```text
Outdated
```

does not automatically mean:

```text
Vulnerable
```

and:

```text
Current
```

does not automatically mean:

```text
Secure
```

These are different properties.

---

# Python Dependencies

Common Python dependency files include:

```text
requirements.txt
pyproject.toml
Pipfile
Pipfile.lock
poetry.lock
```

A simple requirements file might contain:

```text
Django==5.2.1
requests==2.32.3
```

---

# pip-audit

`pip-audit` is maintained under the Python Packaging Authority and audits Python environments and requirements-style dependency files for known vulnerabilities.

Install:

```bash
python3 -m pip install pip-audit
```

Audit the current Python environment:

```bash
pip-audit
```

Audit a requirements file:

```bash
pip-audit -r requirements.txt
```

---

# pip-audit JSON Output

For machine-readable results:

```bash
pip-audit -r requirements.txt -f json
```

Save:

```bash
pip-audit -r requirements.txt \
  -f json > pip-audit-results.json
```

---

# pip-audit Fixing

`pip-audit` supports automatic fixes:

```bash
pip-audit --fix
```

During assessment work, avoid modifying the target project unless remediation testing is explicitly intended.

Prefer:

```text
Identify
Assess
Recommend
Retest
```

---

# Java Dependencies

Common Java dependency systems include:

```text
Maven
Gradle
```

Maven:

```text
pom.xml
```

Gradle:

```text
build.gradle
build.gradle.kts
```

---

# Maven Dependency Tree

For Maven:

```bash
mvn dependency:tree
```

This helps identify transitive dependencies.

Example concept:

```text
application
  |
  +-- framework
       |
       +-- vulnerable-library
```

The vulnerable library may not appear directly in:

```text
pom.xml
```

---

# Gradle Dependencies

For Gradle:

```bash
./gradlew dependencies
```

This can show dependency relationships and resolved versions.

!!! warning
    Running Maven or Gradle tasks can invoke build logic, plugins, or other project-controlled behaviour. Treat untrusted repositories as potentially executable code and use an isolated environment where appropriate.

---

# PHP Dependencies

Composer projects commonly contain:

```text
composer.json
composer.lock
```

Composer provides:

```bash
composer audit
```

for checking installed packages against security advisories.

Inspect the dependency tree with:

```bash
composer show --tree
```

---

# Ruby Dependencies

Ruby projects commonly use:

```text
Gemfile
Gemfile.lock
```

Dependency security tools in the Ruby ecosystem can inspect gems and advisories.

The important principle remains:

```text
Manifest
+
Resolved versions
+
Advisories
+
Reachability/context
```

---

# Go Dependencies

Go modules commonly use:

```text
go.mod
go.sum
```

List dependencies:

```bash
go list -m all
```

Go vulnerability analysis can also be performed using ecosystem tooling such as:

```text
govulncheck
OSV-Scanner
```

---

# Rust Dependencies

Rust projects commonly use:

```text
Cargo.toml
Cargo.lock
```

The lockfile records resolved crate versions.

Dependency analysis should include:

```text
Direct crates
Transitive crates
Build dependencies
Features
Target-specific dependencies
```

---

# .NET Dependencies

.NET projects may use:

```text
.csproj
packages.config
packages.lock.json
```

The .NET CLI can identify vulnerable packages in supported SDK versions.

Consult the installed SDK's current package-list command help because command naming and output can differ between SDK generations.

---

# OSV

OSV provides vulnerability information designed around open-source package ecosystems.

OSV advisories can precisely represent affected package versions and ecosystems.

Examples include:

```text
npm
PyPI
Maven
Go
crates.io
RubyGems
NuGet
Packagist
```

Official service:

```text
https://osv.dev/
```

---

# OSV-Scanner

OSV-Scanner is Google's open-source scanner for identifying known vulnerabilities in project dependencies.

Official repository:

```text
https://github.com/google/osv-scanner
```

Modern OSV-Scanner uses commands such as:

```bash
osv-scanner scan source .
```

The shorter default form can also be used:

```bash
osv-scanner .
```

---

# Recursive OSV Scan

Scan a project recursively:

```bash
osv-scanner scan source -r .
```

This searches supported dependency information such as:

```text
Lockfiles
SBOMs
Project dependency metadata
```

---

# Scan Specific Lockfiles

Example:

```bash
osv-scanner scan source \
  --lockfile=package-lock.json
```

Multiple lockfiles can be supplied.

This is useful for repositories containing multiple applications.

---

# OSV-Scanner Output

OSV-Scanner can produce machine-readable output.

For example:

```bash
osv-scanner scan source \
  --format=json \
  -r .
```

Save it:

```bash
osv-scanner scan source \
  --format=json \
  -r . > osv-results.json
```

---

# OSV Reachability and Call Analysis

OSV-Scanner supports call analysis for some ecosystems.

This can help distinguish:

```text
Dependency contains vulnerable function
```

from:

```text
Application actually calls vulnerable function
```

Support differs by language and can evolve.

!!! warning
    Some call-analysis modes may compile project or dependency code. In particular, build systems can execute project-controlled scripts. Review the current OSV-Scanner documentation and use an isolated environment before enabling compilation-based analysis on untrusted code.

---

# OWASP Dependency-Check

OWASP Dependency-Check is a Software Composition Analysis tool designed to identify publicly disclosed vulnerabilities in project dependencies.

Official project:

```text
https://owasp.org/www-project-dependency-check/
```

Documentation:

```text
https://dependency-check.github.io/DependencyCheck/
```

It is especially established in ecosystems such as:

```text
Java
.NET
```

with varying support for other package ecosystems.

---

# Dependency-Check Concept

```text
Project
   |
   v
Dependency-Check
   |
   v
Identify Components
   |
   v
Match Vulnerability Data
   |
   v
Potential Vulnerabilities
   |
   v
Manual Review
```

Dependency matching is not infallible.

False positives and false negatives are possible.

---

# Dependency-Check CLI

After installing the Dependency-Check CLI, a typical scan resembles:

```bash
dependency-check.sh \
  --scan /path/to/project \
  --out ./dependency-check-report
```

Depending on installation method, the executable name and location may differ.

Always verify:

```bash
dependency-check.sh --help
```

against the installed version.

---

# Dependency-Check Reports

Dependency-Check can produce reports containing information such as:

```text
Dependency
Version
Identifiers
CVE
Severity
Evidence
Vulnerability details
```

Treat automated component identification as evidence to review, not unquestionable proof.

---

# Trivy

Trivy is a security scanner maintained by Aqua Security.

It can scan several target types, including:

```text
Filesystems
Repositories
Container images
SBOMs
```

It can detect areas such as:

```text
Known vulnerabilities
Secrets
Misconfigurations
Licensing information
```

Official documentation:

```text
https://trivy.dev/
```

---

# Trivy Filesystem Scan

Scan a local project:

```bash
trivy fs /path/to/project
```

For example:

```bash
trivy fs .
```

Trivy can identify vulnerable packages from supported lockfiles and package metadata.

---

# Trivy Vulnerability-Only Scan

Where explicit scanner selection is useful:

```bash
trivy fs \
  --scanners vuln \
  .
```

This focuses the filesystem scan on known vulnerabilities.

---

# Trivy Severity Filtering

For prioritisation:

```bash
trivy fs \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  .
```

Do not ignore lower-severity vulnerabilities automatically.

Severity should be interpreted in application context.

---

# Trivy JSON Output

```bash
trivy fs \
  --scanners vuln \
  --format json \
  --output trivy-results.json \
  .
```

Scanner output may contain sensitive project information and should be protected as assessment evidence.

---

# Container Dependency Security

Containers combine multiple dependency layers:

```text
Container Image
      |
      +-- Base OS
      |
      +-- OS Packages
      |
      +-- Language Runtime
      |
      +-- Application Dependencies
      |
      +-- Application Code
```

A vulnerability may exist in any of these layers.

---

# Trivy Container Scan

A common container scan is:

```bash
trivy image example/application:latest
```

This can identify known vulnerabilities in supported operating-system and language packages contained in the image.

---

# Base Images

Consider:

```dockerfile
FROM node:20
```

The application inherits:

```text
Operating system
Runtime
System libraries
Certificates
Package-manager components
```

from the base image.

Therefore base-image maintenance is part of dependency security.

---

# Floating Container Tags

A tag such as:

```text
latest
```

does not provide strong build reproducibility.

For higher assurance, organisations may use:

```text
Specific version tags
Image digests
Controlled internal registries
```

depending on their deployment model.

---

# Image Digests

Container images can be referenced using immutable digests.

Conceptually:

```text
Image Tag
    |
    v
May point to different image later
```

versus:

```text
Image Digest
    |
    v
Specific image content
```

Digest pinning improves reproducibility but still requires a process to update images when vulnerabilities are fixed.

---

# Software Bill of Materials

SBOM stands for:

```text
Software Bill of Materials
```

An SBOM provides an inventory of software components.

Conceptually:

```text
Application
    |
    v
SBOM
    |
    +-- Component A
    +-- Component B
    +-- Component C
    +-- Component D
```

This helps answer:

```text
What software are we actually using?
```

---

# Why SBOMs Matter

Without an inventory:

```text
New vulnerability announced
        |
        v
Are we affected?
        |
        v
Unknown
```

With an accurate SBOM:

```text
New vulnerability announced
        |
        v
Search component inventory
        |
        v
Affected projects identified
        |
        v
Prioritise remediation
```

---

# SBOM Formats

Common SBOM formats include:

```text
CycloneDX
SPDX
```

Both are widely used standards.

---

# CycloneDX

CycloneDX is an OWASP standard for bill-of-materials and software supply chain information.

Common CycloneDX filenames include:

```text
bom.json
bom.xml
*.cdx.json
*.cdx.xml
```

Official project:

```text
https://cyclonedx.org/
```

---

# Example SBOM Concept

An SBOM may contain:

```json
{
  "components": [
    {
      "type": "library",
      "name": "example-library",
      "version": "1.2.3"
    }
  ]
}
```

Actual CycloneDX and SPDX documents contain additional metadata and structure.

---

# SBOM Is Not a Vulnerability Report

An SBOM primarily answers:

```text
What components exist?
```

A vulnerability scanner answers:

```text
Are known vulnerabilities associated with them?
```

Conceptually:

```text
SBOM
  |
  v
Component Inventory
  |
  v
Vulnerability Intelligence
  |
  v
Risk Findings
```

---

# SBOM Accuracy

An incomplete SBOM can create false confidence.

Verify whether the SBOM includes:

```text
Direct dependencies
Transitive dependencies
Runtime dependencies
Container packages
Vendored components
Generated components
```

depending on the intended scope.

---

# OWASP Dependency-Track

OWASP Dependency-Track is an open-source component analysis platform designed around software supply chain and SBOM analysis.

Official project:

```text
https://dependencytrack.org/
```

It can ingest SBOMs and continuously track components against vulnerability and policy information.

Conceptually:

```text
Projects
   |
   v
SBOMs
   |
   v
Dependency-Track
   |
   +-- Component Inventory
   +-- Vulnerabilities
   +-- Policies
   +-- Portfolio Risk
   |
   v
Continuous Monitoring
```

---

# Dependency-Track vs Dependency-Check

These tools solve related but different problems.

```text
Dependency-Check
        |
        v
Scan project dependencies
        |
        v
Find known vulnerabilities
```

versus:

```text
Dependency-Track
        |
        v
Consume SBOMs
        |
        v
Maintain portfolio inventory
        |
        v
Continuously monitor risk
```

They can complement each other.

---

# Continuous Monitoring

Dependency security is not a one-time scan.

Consider:

```text
Monday:

Dependency 1.2.3
No known vulnerability
```

Then:

```text
Friday:

New CVE published
Dependency 1.2.3 affected
```

The application did not change.

Its known risk did.

Therefore:

```text
Continuous monitoring
```

is necessary.

---

# SCA

SCA stands for:

```text
Software Composition Analysis
```

SCA tools identify third-party software and correlate components with security or licensing information.

Examples include:

```text
OWASP Dependency-Check
OWASP Dependency-Track
OSV-Scanner
Trivy
Snyk
GitHub dependency scanning
Other commercial SCA platforms
```

Different tools have different strengths and coverage.

---

# Scanner Comparison

A useful conceptual comparison:

```text
npm audit
    |
    +-- npm ecosystem

pip-audit
    |
    +-- Python ecosystem

OSV-Scanner
    |
    +-- Multiple ecosystems
    +-- OSV data
    +-- Lockfiles / SBOMs

Dependency-Check
    |
    +-- SCA
    +-- Strong Java/.NET use cases

Trivy
    |
    +-- Application dependencies
    +-- Containers
    +-- Filesystems
    +-- OS packages

Dependency-Track
    |
    +-- SBOM ingestion
    +-- Portfolio monitoring
```

Using more than one source may reveal differences in coverage.

---

# Burp Suite and Dependency Security

Burp is not a full source-code SCA platform.

However, it is useful for detecting dependencies exposed through the running web application.

Conceptually:

```text
Browser
   |
   v
Application
   |
   v
HTTP Responses
   |
   +-- JavaScript libraries
   +-- Framework versions
   +-- Server headers
   +-- Component fingerprints
   |
   v
Burp
```

Burp can therefore complement source-based dependency analysis.

---

# Burp Proxy Workflow

Browse the application normally.

Use Proxy HTTP history to identify:

```text
JavaScript files
CSS
Framework resources
Versioned assets
Headers
Error messages
API responses
```

Examples:

```text
/jquery-3.4.1.min.js

/bootstrap-4.3.1.min.js

/angular-1.6.0.js
```

Version information can then be investigated.

---

# Do Not Trust Filenames Alone

A filename such as:

```text
jquery-3.4.1.min.js
```

suggests a version.

It does not prove the file actually contains that version.

Likewise:

```text
jquery-latest.js
```

provides little reliable version information.

Use multiple indicators where possible.

---

# JavaScript Fingerprinting

Possible version indicators include:

```text
Filename
Banner comment
Library metadata
Source content
Known hashes
Source map
Global version property
Build metadata
```

The reliability of each technique varies.

---

# Retire.js Burp Extension

The Burp BApp Store currently contains:

```text
Retire.js
```

The extension passively analyses JavaScript resources and uses Retire.js signatures to identify vulnerable JavaScript libraries.

BApp Store:

```text
https://portswigger.net/bappstore/36238b534a78494db9bf2d03f112265c
```

It can identify libraries using indicators such as:

```text
URL
Filename
File content
Hash
```

!!! note
    The Retire.js BApp is still available in the BApp Store, but the BApp Store entry shows that this Burp extension itself was last updated in December 2021. Treat its results as leads and verify findings against current vulnerability information.

---

# Retire.js Workflow

```text
Burp Proxy
    |
    v
Application JavaScript
    |
    v
Retire.js Extension
    |
    v
Library Fingerprint
    |
    v
Known Vulnerability Match
    |
    v
Manual Verification
```

For every result verify:

```text
Library identity

Version

Vulnerability advisory

Affected version range

Application use

Exploitability
```

---

# Software Vulnerability Scanner Burp Extension

A more recent BApp Store extension relevant to component fingerprinting is:

```text
Software Vulnerability Scanner
```

BApp Store:

```text
https://portswigger.net/bappstore/c9fb79369b56407792a7104e3c4352fb
```

The extension fingerprints software from HTTP responses and correlates detected versions with vulnerability information from Vulners.

It can provide:

```text
Detected software
Versions
CVEs
Security advisories
Potentially relevant paths
```

!!! note
    This is a third-party Burp extension and uses Vulners data. Findings should be independently verified before reporting.

---

# Burp Extension Safety

Burp extensions can access sensitive assessment traffic.

Before installing:

```text
Review publisher
Review source where possible
Review permissions and behaviour
Understand external API communication
Avoid unnecessary extensions
```

PortSwigger explicitly notes that BApp Store extensions are third-party software and recommends reviewing extension code.

---

# Burp Scanner

Burp Scanner can identify some vulnerable JavaScript dependencies during application scanning.

However:

```text
Burp Scanner
```

should not replace:

```text
Repository SCA
SBOM analysis
Lockfile analysis
Container scanning
```

because Burp only observes what is exposed through the web application.

---

# Browser DevTools

Browser DevTools can complement Burp.

Inspect:

```text
Network
Sources
Loaded JavaScript
Source maps
Runtime objects
Response headers
```

This can help identify client-side libraries and frameworks.

---

# Client-Side Dependency Security

JavaScript dependencies execute in the user's browser.

Potential impact includes:

```text
DOM XSS
Prototype pollution
Client-side injection
Unsafe URL handling
Object manipulation
Data leakage
```

Refer to:

```text
docs/web/xss.md
docs/web/dom-based-vulnerabilities.md
docs/web/prototype-pollution.md
```

---

# Third-Party JavaScript

Third-party JavaScript introduces a particularly important trust relationship.

Example:

```html
<script src="https://cdn.example.net/library.js"></script>
```

Conceptually:

```text
Application
     |
     v
Third-Party Script
     |
     v
Executes in Application Origin
     |
     v
Can interact with page
```

This topic deserves separate treatment and is covered in:

```text
docs/web/third-party-javascript.md
```

---

# Subresource Integrity

Subresource Integrity, or SRI, can allow browsers to verify that certain externally loaded resources match an expected cryptographic hash.

Example:

```html
<script
  src="https://cdn.example.net/library.js"
  integrity="sha384-BASE64_HASH"
  crossorigin="anonymous">
</script>
```

Conceptually:

```text
Browser downloads resource
        |
        v
Calculate hash
        |
        v
Compare with integrity value
        |
     +--+--+
     |     |
   Match  Different
     |     |
     v     v
 Execute  Reject
```

SRI is particularly relevant for static third-party scripts and styles loaded from external origins.

---

# SRI Limitations

SRI is not a universal dependency-security solution.

It does not replace:

```text
Dependency updates
Vulnerability scanning
Package integrity
Secure build systems
Registry security
SBOMs
```

It protects a specific browser resource-loading scenario.

---

# Integrity Files

Package managers may maintain integrity information in lockfiles.

For example, npm lockfiles can contain package integrity metadata.

This helps detect unexpected package-content changes under supported workflows.

Integrity controls are valuable, but they do not prove:

```text
Package is non-malicious
```

A malicious package published legitimately can still have a valid integrity hash.

---

# Package Provenance

Software provenance provides information about:

```text
Where software came from

How it was built

Which source produced it

Which build process created it
```

This can improve supply-chain assurance.

Conceptually:

```text
Source
  |
  v
Trusted Build
  |
  v
Artifact
  |
  v
Provenance
  |
  v
Verification
```

---

# Signed Artifacts

Cryptographic signatures can help verify:

```text
Publisher identity
Artifact integrity
```

depending on the ecosystem.

However:

```text
Valid signature
```

does not guarantee:

```text
No vulnerabilities
No malicious code
```

It primarily helps answer whether the artifact came from the expected signer and remained unchanged.

---

# Package Registries

Applications may use:

```text
npm registry
PyPI
Maven Central
NuGet
RubyGems
crates.io
Packagist
Internal registries
Artifact repositories
```

Security review should determine:

```text
Which registries are trusted?

Are public registries allowed?

Are internal packages isolated?

Are credentials protected?

Is TLS enforced?

Are packages cached internally?

Are package sources explicitly configured?
```

---

# Internal Artifact Repositories

Organisations often use internal repositories such as:

```text
Artifact proxies
Package registries
Container registries
```

Benefits can include:

```text
Centralised policy
Package allowlisting
Caching
Malware scanning
Audit logging
Controlled external access
```

The repository itself becomes security-critical infrastructure.

---

# Dependency Allowlisting

High-assurance environments may restrict which dependencies can be introduced.

Possible controls:

```text
Approved package list
Approved versions
License policy
Maintainer review
Security review
Package-age policy
Source repository review
Integrity requirements
```

This reduces uncontrolled dependency growth.

---

# Dependency Minimisation

Every dependency increases:

```text
Attack surface
Maintenance burden
Supply-chain exposure
Update requirements
```

Before adding a package ask:

```text
Do we actually need it?
```

A package imported for a trivial function may not justify its dependency tree.

---

# Remove Unused Dependencies

Unused dependencies should generally be removed.

Benefits include:

```text
Smaller attack surface
Fewer vulnerabilities
Smaller builds
Simpler SBOM
Reduced maintenance
Reduced supply-chain exposure
```

---

# Vendored Dependencies

Some applications copy third-party source code directly into the repository.

Example:

```text
vendor/
third_party/
lib/
```

These dependencies may not appear in normal package-manager manifests.

Therefore SCA based solely on lockfiles may miss them.

---

# Forked Dependencies

Organisations may maintain internal forks.

Example:

```text
upstream-library
       |
       v
Internal Fork
       |
       v
Application
```

Security teams must track:

```text
Upstream vulnerabilities
Internal modifications
Patch divergence
Update process
```

Otherwise security fixes from upstream may never reach the fork.

---

# Monorepos

A monorepo may contain many dependency ecosystems.

Example:

```text
repository/
|
+-- frontend/
|   +-- package.json
|
+-- backend/
|   +-- pom.xml
|
+-- worker/
|   +-- requirements.txt
|
+-- tooling/
    +-- go.mod
```

Recursive scanners such as OSV-Scanner or Trivy can be useful, but verify that every relevant project and lockfile was discovered.

---

# Generated Code

Generated code may introduce dependencies that are not obvious from manually written source.

Examples:

```text
Generated SDKs
Protocol clients
ORM code
Build output
Vendor bundles
```

Determine whether generated artifacts are:

```text
Built internally
Downloaded
Committed
Vendored
Generated during CI
```

---

# CI/CD Dependency Scanning

A strong workflow is:

```text
Developer
    |
    v
Commit
    |
    v
Pull Request
    |
    v
Dependency Scan
    |
    +-- Vulnerability?
    +-- Policy violation?
    +-- New dependency?
    |
    v
Review
    |
    v
Build
```

This catches issues before deployment.

---

# CI Security Gate

Example policy:

```text
Critical vulnerability
        |
        v
Fail build
```

But simplistic severity-only gates can cause problems.

A better policy may consider:

```text
Severity
Exploitability
Reachability
Known exploitation
Internet exposure
Fix availability
Business criticality
Accepted risk
```

---

# Dependency Update Automation

Automated dependency-update tools can reduce patch latency.

Examples include:

```text
Dependabot
Renovate
Platform-specific update automation
```

Conceptually:

```text
New Dependency Version
        |
        v
Automation Detects Update
        |
        v
Pull Request
        |
        v
Tests + Security Checks
        |
        v
Review
        |
        v
Merge
```

Automation should not mean:

```text
Automatically deploy every update without testing
```

---

# Vulnerability Prioritisation

When a scanner reports a vulnerability, consider:

```text
Severity
Exploitability
Reachability
Internet exposure
Authentication requirements
Privileges required
Known exploitation
Fix availability
Application criticality
Data sensitivity
Compensating controls
```

---

# Example Prioritisation

```text
CVE A
CVSS: 9.8
Vulnerable function not reachable
Internal test tool only

CVE B
CVSS: 7.5
Internet-facing
Unauthenticated
Known exploitation
Reachable code path
```

CVE B may deserve faster remediation despite the lower base score.

---

# Exploitability

Do not automatically download or execute public exploits.

Start with:

```text
Vendor advisory
CVE description
Affected versions
Patch commit
Technical analysis
Reachability
Application behaviour
```

If exploitation is required to confirm impact:

```text
Use authorised target
Use controlled payload
Avoid destructive actions
Collect minimum evidence
```

---

# False Positives

Dependency scanners can produce false positives.

Common causes include:

```text
Incorrect package identification
Wrong version detection
Vendored patched copy
Backported security patch
Different package with same name
Unreachable vulnerable code
Incorrect CPE mapping
Platform-specific differences
```

Always verify important findings.

---

# False Negatives

Scanners can also miss vulnerabilities.

Possible causes:

```text
Unknown vulnerability
Missing advisory
Unsupported ecosystem
Vendored dependency
Custom fork
Incorrect SBOM
Dynamically downloaded dependency
Runtime plugin
Manually copied library
```

Therefore:

```text
No scanner findings
```

does not prove:

```text
No dependency risk
```

---

# Backported Patches

Some vendors patch vulnerabilities without changing to the upstream version normally associated with the fix.

This is common in some operating-system distributions.

Example concept:

```text
Upstream:

1.2.3 vulnerable
1.2.4 fixed
```

but distributor may provide:

```text
1.2.3-distribution5
```

with the security patch backported.

Do not report based solely on the upstream version string without considering vendor security advisories.

---

# Version Detection

When testing a deployed web application, possible version sources include:

```text
JavaScript banners
HTTP headers
Error messages
Static filenames
Package metadata
Source maps
API responses
Debug pages
SBOMs
Lockfiles
Container metadata
```

Rank evidence by reliability.

---

# Version Disclosure vs Vulnerable Dependency

These are different findings.

```text
Server reveals:

Framework 5.2.1
```

may be:

```text
Information disclosure
```

But if:

```text
Framework 5.2.1
```

has an applicable known vulnerability, that may support:

```text
Vulnerable dependency/component
```

Do not combine them automatically.

---

# Pentesting Workflow

A practical dependency-security assessment can follow:

```text
1. Identify technology stack
        |
        v
2. Obtain dependency manifests
        |
        v
3. Obtain lockfiles
        |
        v
4. Build dependency inventory
        |
        v
5. Identify transitive dependencies
        |
        v
6. Run ecosystem scanners
        |
        v
7. Run general SCA scanner
        |
        v
8. Scan container if available
        |
        v
9. Review SBOM if available
        |
        v
10. Correlate vulnerabilities
        |
        v
11. Check reachability
        |
        v
12. Check known exploitation
        |
        v
13. Assess application exposure
        |
        v
14. Validate safely
        |
        v
15. Report
```

---

# Black-Box Workflow

When source code is unavailable:

```text
Target
  |
  v
Technology Fingerprinting
  |
  +-- HTTP headers
  +-- JavaScript
  +-- Static assets
  +-- Errors
  +-- Source maps
  |
  v
Identify Components
  |
  v
Identify Versions
  |
  v
Research Advisories
  |
  v
Verify Version Evidence
  |
  v
Assess Applicability
```

Useful tools include:

```text
Burp Suite
Retire.js BApp
Software Vulnerability Scanner BApp
Browser DevTools
Technology fingerprinting tools
```

---

# White-Box Workflow

With source access:

```text
Repository
    |
    +-- Manifest files
    +-- Lockfiles
    +-- Vendored code
    +-- Containers
    +-- CI/CD
    +-- IaC
    |
    v
Dependency Inventory
    |
    +-- npm audit
    +-- pip-audit
    +-- OSV-Scanner
    +-- Dependency-Check
    +-- Trivy
    |
    v
Manual Validation
```

---

# Quick Scanner Workflow

For a repository containing multiple technologies:

```bash
osv-scanner scan source -r .
```

Then:

```bash
trivy fs --scanners vuln .
```

For Node.js projects:

```bash
npm audit
```

For Python:

```bash
pip-audit -r requirements.txt
```

For Maven:

```bash
mvn dependency:tree
```

These tools overlap.

That is useful because they can provide different visibility.

---

# Do Not Blindly Run Build Commands

Commands such as:

```text
npm install
pip install
mvn package
gradle build
cargo build
```

may execute code or scripts from:

```text
Dependencies
Build plugins
Project configuration
Install hooks
```

When assessing an untrusted repository:

```text
Prefer static analysis first.
```

If execution is necessary:

```text
Use an isolated environment.
```

---

# Evidence Collection

For each dependency finding record:

```text
Application
Component
Installed version
Affected version range
Fixed version
Dependency type
Direct / transitive
Manifest
Lockfile
Dependency path
Advisory
CVE
Severity
Known exploitation
Reachability
Runtime exposure
Evidence
Remediation
```

---

# Dependency Path Evidence

For a transitive dependency, document why it exists.

Example:

```text
application
  -> framework 4.2.0
      -> parser 2.1.3
          -> vulnerable-library 1.0.2
```

This makes remediation easier.

---

# Example Finding: Vulnerable JavaScript Library

```text
Finding:
Vulnerable JavaScript Dependency

Affected resource:
https://example.com/assets/jquery-3.4.1.min.js

Observed:
The application loads a JavaScript library version associated with publicly documented security vulnerabilities.

The library identity and version were confirmed using multiple indicators rather than relying solely on the filename.

Applicability:
The relevant advisory was reviewed to determine whether the affected functionality is present in the deployed application.

Impact:
Depending on how the affected library functionality is used, exploitation may allow client-side security impact such as cross-site scripting.

Recommendation:
Upgrade the dependency to a currently supported version containing the relevant security fixes. Regression-test functionality affected by the upgrade and remove unused libraries.
```

---

# Example Finding: Vulnerable Transitive Dependency

```text
Finding:
Known Vulnerability in Transitive Application Dependency

Observed:
Software composition analysis identified a vulnerable component that is not declared directly by the application.

Dependency path:

application
 -> framework
 -> parser
 -> vulnerable-component

The installed version falls within the affected range documented by the upstream security advisory.

Impact:
The vulnerable component is included in the application dependency graph and may expose the application to the documented vulnerability where the affected functionality is reachable.

Recommendation:
Upgrade the direct dependency to a version that resolves the vulnerable transitive component, apply an appropriate dependency override where supported, or follow the vendor's recommended remediation.
```

---

# Example Finding: End-of-Life Framework

```text
Finding:
Unsupported Application Framework in Use

Observed:
The application uses a framework version that is no longer supported by the upstream project.

Impact:
Security vulnerabilities discovered in the unsupported branch may not receive patches, increasing long-term security and maintenance risk.

Recommendation:
Migrate the application to a currently supported framework release and establish lifecycle monitoring for major application dependencies.
```

---

# Example Finding: Vulnerable Container Base Image

```text
Finding:
Known Vulnerabilities in Container Base Image

Observed:
Container analysis identified multiple known vulnerabilities in operating-system packages inherited from the configured base image.

Impact:
The application inherits the affected packages from its base image. Exploitability depends on whether affected functionality is present and reachable in the deployed container.

Recommendation:
Rebuild the application using a currently maintained base image containing the relevant security updates. Implement regular container rebuilds and continuous image vulnerability monitoring.
```

---

# Example Finding: Dependency Confusion Risk

```text
Finding:
Unsafe Dependency Resolution Allows Potential Public Package Substitution

Observed:
The build configuration references private package names while also permitting resolution from a public package registry.

Testing in the authorised isolated environment demonstrated that the configured resolution policy could select an externally sourced package matching an internal dependency name.

Impact:
An attacker capable of publishing a matching package under applicable registry conditions may be able to introduce attacker-controlled code into the build process.

Recommendation:
Use protected namespaces, explicitly configure trusted registries for private packages, prevent unintended public fallback, and enforce package-source policies within CI/CD.
```

---

# Finding Titles

Useful report titles include:

```text
Vulnerable Third-Party Dependency

Vulnerable JavaScript Dependency

Known Vulnerability in Transitive Dependency

Unsupported Third-Party Component

End-of-Life Application Framework

Vulnerable Container Base Image

Known Vulnerabilities in Container Packages

Outdated Security-Critical Dependency

Unsafe Dependency Resolution

Potential Dependency Confusion

Unpinned Build Dependency

Missing Dependency Integrity Controls

Unmaintained Third-Party Component

Incomplete Software Bill of Materials

Vulnerable Build-Time Dependency

Known Exploited Vulnerability in Application Dependency
```

---

# Severity

Severity depends on context.

Possible factors:

```text
Upstream severity
Reachability
Internet exposure
Authentication
Privileges required
Known exploitation
Exploit maturity
Data sensitivity
Application criticality
Fix availability
Compensating controls
```

Example:

```text
Vulnerable package exists
but affected code not used

-> Lower practical risk
```

versus:

```text
Internet-facing application
+
Unauthenticated vulnerable endpoint
+
Known exploited CVE
+
Reliable exploit path

-> High / Critical
```

---

# Remediation

## Upgrade Vulnerable Dependencies

Preferred remediation is usually:

```text
Upgrade to fixed supported version
```

rather than attempting to patch around the dependency indefinitely.

---

# Remove Unused Dependencies

If a dependency is not required:

```text
Remove it.
```

This eliminates:

```text
Vulnerability exposure
Supply-chain exposure
Maintenance burden
```

---

# Replace Abandoned Dependencies

If a dependency is no longer maintained:

```text
Identify supported alternative
        |
        v
Evaluate compatibility
        |
        v
Migrate
        |
        v
Remove abandoned component
```

---

# Maintain Lockfiles

Use lockfiles where appropriate and commit them according to the package ecosystem's recommended workflow.

Then:

```text
Review
Update
Test
Regenerate
Monitor
```

them as dependencies change.

---

# Automate Vulnerability Monitoring

Integrate dependency scanning into:

```text
Pull requests
CI/CD
Scheduled scans
Repository monitoring
Container pipelines
SBOM platforms
```

---

# Maintain an SBOM

Generate and maintain an accurate SBOM.

The SBOM should evolve with the application.

```text
Build
  |
  v
Generate SBOM
  |
  v
Store SBOM
  |
  v
Monitor Components
  |
  v
New Advisory
  |
  v
Identify Affected Builds
```

---

# Protect Package Sources

Use:

```text
Trusted registries
Namespace controls
TLS
Authentication
Repository policies
Integrity validation
Controlled mirrors
```

where appropriate.

---

# Restrict Build Environments

Build systems frequently contain valuable credentials.

Apply:

```text
Least privilege
Ephemeral runners
Network restrictions
Secret isolation
Minimal credentials
Branch protection
Dependency controls
```

---

# Review New Dependencies

Before adopting a new dependency consider:

```text
Is it maintained?

Is the repository active?

Who maintains it?

How many transitive dependencies does it introduce?

Does it execute installation scripts?

Is the licence acceptable?

Are releases signed or otherwise verifiable?

Are vulnerabilities handled responsibly?

Could existing platform functionality replace it?
```

---

# Patch Management

Dependency patching should have defined expectations.

Example:

```text
Critical
    |
    v
Immediate prioritisation

High
    |
    v
Accelerated remediation

Medium / Low
    |
    v
Risk-based remediation
```

Exact SLAs should reflect organisational risk and should not rely on severity alone.

---

# Pentesting Checklist

## Discovery

```text
[ ] Technology stack identified
[ ] Frameworks identified
[ ] Runtime versions identified
[ ] Client-side libraries identified
[ ] Server-side components identified
[ ] Container base image identified where available
```

---

## Dependency Files

```text
[ ] package.json
[ ] package-lock.json
[ ] yarn.lock
[ ] pnpm-lock.yaml
[ ] requirements.txt
[ ] pyproject.toml
[ ] Pipfile
[ ] Pipfile.lock
[ ] poetry.lock
[ ] pom.xml
[ ] build.gradle
[ ] build.gradle.kts
[ ] composer.json
[ ] composer.lock
[ ] Gemfile
[ ] Gemfile.lock
[ ] go.mod
[ ] go.sum
[ ] Cargo.toml
[ ] Cargo.lock
[ ] .csproj
[ ] packages.lock.json
```

---

## Dependency Graph

```text
[ ] Direct dependencies identified
[ ] Transitive dependencies identified
[ ] Development dependencies identified
[ ] Runtime dependencies identified
[ ] Build dependencies identified
[ ] Vendored dependencies considered
[ ] Forked dependencies considered
```

---

## Vulnerability Scanning

```text
[ ] Ecosystem-native scanner used
[ ] OSV-Scanner considered
[ ] OWASP Dependency-Check considered
[ ] Trivy considered
[ ] Container scan performed where applicable
[ ] Results manually validated
[ ] Original advisories reviewed
```

---

## JavaScript

```text
[ ] Loaded JavaScript inventoried
[ ] Library versions identified
[ ] Burp Retire.js considered
[ ] Software Vulnerability Scanner considered
[ ] Source maps reviewed
[ ] Vulnerability applicability checked
[ ] Third-party scripts identified
[ ] SRI considered
```

---

## Supply Chain

```text
[ ] Public registries identified
[ ] Internal registries identified
[ ] Private package names identified
[ ] Dependency confusion considered
[ ] Namespace protections reviewed
[ ] Package integrity considered
[ ] Installation scripts considered
[ ] Build plugins considered
```

---

## SBOM

```text
[ ] SBOM available?
[ ] SBOM format identified
[ ] Direct dependencies included
[ ] Transitive dependencies included
[ ] Component versions present
[ ] SBOM reflects current build
[ ] Vulnerability monitoring integrated
```

---

## CI/CD

```text
[ ] Dependency scanning automated
[ ] New dependencies reviewed
[ ] Security thresholds defined
[ ] Build dependencies reviewed
[ ] Update automation configured
[ ] Dependency alerts monitored
[ ] Build environment isolated
```

---

## Validation

```text
[ ] Component identity confirmed
[ ] Version confirmed
[ ] Advisory confirmed
[ ] Affected version range confirmed
[ ] Fixed version identified
[ ] Reachability considered
[ ] Known exploitation checked
[ ] Application exposure assessed
[ ] False positive considered
```

---

# Quick Reference

```text
APPLICATION
    |
    v
DEPENDENCY INVENTORY
    |
    +-- Manifest
    +-- Lockfile
    +-- SBOM
    +-- Container
    +-- Vendored Code
    |
    v
DEPENDENCY GRAPH
    |
    +-- Direct
    +-- Transitive
    +-- Runtime
    +-- Development
    +-- Build
    |
    v
SCANNING
    |
    +-- npm audit
    +-- pip-audit
    +-- OSV-Scanner
    +-- Dependency-Check
    +-- Trivy
    +-- Burp / Retire.js
    |
    v
FINDING
    |
    v
VERIFY
    |
    +-- Component?
    +-- Version?
    +-- Advisory?
    +-- Affected range?
    +-- Reachable?
    +-- Exploitable?
    |
    v
PRIORITISE
    |
    +-- Severity
    +-- Exposure
    +-- Known exploitation
    +-- Criticality
    |
    v
REMEDIATE
    |
    +-- Upgrade
    +-- Remove
    +-- Replace
    +-- Mitigate
    |
    v
CONTINUOUS MONITORING
```

---

# Final Testing Model

```text
                           DEPENDENCY SECURITY
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
          DISCOVERY           ANALYSIS            SUPPLY CHAIN
              |                   |                   |
      +-------+------+      +-----+------+       +----+-----+
      |       |      |      |     |      |       |          |
      v       v      v      v     v      v       v          v
  Manifest Lockfile SBOM   SCA   CVE  Reachability Registry  Build
      |       |      |      |     |      |       |          |
      +-------+------+      +-----+------+       +----+-----+
              |                   |                   |
              v                   v                   v
        COMPONENT INVENTORY   RISK CONTEXT       TRUST MODEL
              |                   |                   |
              +-------------------+-------------------+
                                  |
                                  v
                             FINDING
                                  |
                                  v
                        Is component identified?
                                  |
                              +---+---+
                              |       |
                             NO      YES
                              |       |
                              v       v
                           Verify   Is version
                           first    affected?
                                      |
                                  +---+---+
                                  |       |
                                 NO      YES
                                  |       |
                                  v       v
                               Close   Is vulnerable
                                       path relevant?
                                          |
                                      +---+---+
                                      |       |
                                     NO      YES
                                      |       |
                                      v       v
                                  Lower     Assess
                                  Risk      Exploitability
                                              |
                                              v
                                      Known Exploitation?
                                              |
                                              v
                                      Application Exposure
                                              |
                                              v
                                           Impact
                                              |
                                              v
                                           Report
                                              |
                                              v
                                       Upgrade / Remove
                                              |
                                              v
                                           Retest
                                              |
                                              v
                                  Continuous Monitoring
```

The most important principle is:

> **A scanner finding is a starting point for dependency analysis, not automatic proof that the application is exploitable.**

For each vulnerable component ask:

```text
What is the component?

What version is actually installed?

Is it direct or transitive?

What introduces it?

Which advisory applies?

Is this exact version affected?

Is a vendor patch backported?

Is the vulnerable functionality present?

Does the application call it?

Can attacker-controlled input reach it?

Is exploitation known in the wild?

Is the component present in production?

What privileges would exploitation provide?

What version fixes it?

Can the dependency be removed entirely?
```

A strong baseline workflow is:

```text
Dependency inventory
        +
Lockfile analysis
        +
SBOM
        +
Ecosystem-native scanner
        +
OSV-Scanner
        +
Trivy / container analysis
        +
Burp client-side fingerprinting
        +
Manual advisory review
        +
Reachability analysis
        +
Risk-based remediation
```

---

# References

## OWASP Vulnerable Dependency Management Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html
```

---

## OWASP Software Supply Chain Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html
```

---

## OWASP CI/CD Security Cheat Sheet

```text
https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html
```

---

## OWASP Dependency-Check

```text
https://owasp.org/www-project-dependency-check/
```

Documentation:

```text
https://dependency-check.github.io/DependencyCheck/
```

---

## OWASP Dependency-Track

```text
https://dependencytrack.org/
```

---

## OSV

```text
https://osv.dev/
```

---

## OSV-Scanner

```text
https://github.com/google/osv-scanner
```

---

## Trivy

```text
https://trivy.dev/
```

---

## pip-audit

```text
https://github.com/pypa/pip-audit
```

---

## npm audit

```text
https://docs.npmjs.com/cli/v11/commands/npm-audit/
```

---

## CycloneDX

```text
https://cyclonedx.org/
```

---

## SPDX

```text
https://spdx.dev/
```

---

## CISA Known Exploited Vulnerabilities Catalogue

```text
https://www.cisa.gov/known-exploited-vulnerabilities-catalog
```

---

## Burp Retire.js

```text
https://portswigger.net/bappstore/36238b534a78494db9bf2d03f112265c
```

---

## Burp Software Vulnerability Scanner

```text
https://portswigger.net/bappstore/c9fb79369b56407792a7104e3c4352fb
```

---

## PortSwigger Vulnerable JavaScript Dependency

```text
https://portswigger.net/kb/issues/00500080_vulnerable-javascript-dependency
```

---

# Related Notes

```text
docs/web/reconnaissance/technology-identification.md
docs/web/reconnaissance/javascript-analysis.md
docs/web/information-disclosure.md
docs/web/secrets-exposure.md
docs/web/prototype-pollution.md
docs/web/dom-based-vulnerabilities.md
docs/web/xss.md
docs/web/third-party-javascript.md
```
