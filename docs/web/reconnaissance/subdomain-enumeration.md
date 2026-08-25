# Subdomain Enumeration

Subdomain enumeration is the process of identifying subdomains associated with a target domain.

During a web application penetration test, subdomain enumeration can reveal additional applications, APIs, administrative interfaces, development environments, staging systems and other assets that may not be linked from the primary website.

The goal is not simply to collect as many hostnames as possible. The objective is to produce a validated and organised list of assets that can be investigated during the rest of the assessment.

!!! warning "Authorised Security Testing"

    Perform subdomain enumeration only against domains and systems that are within the authorised scope of the security assessment.

---

## Workflow

A practical subdomain enumeration workflow can be organised as:

```text
                         Target Domain
                              |
          +-------------------+-------------------+
          |                   |                   |
      Subfinder             Amass             Assetfinder
          |                   |                   |
          +-------------------+-------------------+
                              |
                       CT / Passive Sources
                              |
                              v
                       Combine Results
                              |
                              v
                         Deduplicate
                              |
                              v
                        DNS Resolution
                            dnsx
                              |
                              v
                         HTTP Probing
                            httpx
                              |
                              v
                       Live Web Targets
                              |
                              v
                    Further Reconnaissance
```

Using multiple sources is important because different tools and data sources frequently discover different subdomains.

---

# 1. Create a Workspace

Keeping reconnaissance output organised makes it easier to reproduce the assessment and use the results in later stages.

```bash
mkdir -p recon/subdomains
cd recon/subdomains
```

A typical directory may eventually contain:

```text
recon/
└── subdomains/
    ├── subfinder.txt
    ├── amass.txt
    ├── assetfinder.txt
    ├── ct.txt
    ├── subdomains.txt
    ├── resolved-subdomains.txt
    └── alive-hosts.txt
```

---

# 2. Subfinder

Subfinder performs passive subdomain enumeration using multiple online data sources.

Basic usage:

```bash
subfinder -d example.com -silent
```

Save the results:

```bash
subfinder -d example.com -silent -o subfinder.txt
```

For broader passive enumeration:

```bash
subfinder -d example.com -all -recursive -silent -o subfinder.txt
```

The results may look like:

```text
www.example.com
api.example.com
portal.example.com
login.example.com
dev.example.com
```

Subfinder is often a good first source because it is fast and integrates multiple passive data providers.

---

# 3. Amass

Amass can be used as another independent source for discovering subdomains.

Passive enumeration:

```bash
amass enum -passive -d example.com -o amass.txt
```

Passive mode is useful when direct enumeration against the target should be minimised.

The results can later be combined with Subfinder and other sources.

---

# 4. Assetfinder

Assetfinder provides another lightweight source of subdomain information.

```bash
assetfinder --subs-only example.com
```

Save the results:

```bash
assetfinder --subs-only example.com > assetfinder.txt
```

Using several independent tools increases coverage because each may use different sources.

---

# 5. Certificate Transparency

Certificate Transparency logs are an important source of historical and current hostname information.

Certificates issued for an organisation may contain hostnames such as:

```text
www.example.com
api.example.com
vpn.example.com
portal.example.com
mail.example.com
```

Certificate Transparency data can therefore reveal subdomains that are not easily discovered through other passive sources.

Useful sources include:

* crt.sh
* Certificate Transparency search services
* Search engine certificate datasets
* Passive DNS platforms

When reviewing Certificate Transparency results, remember that a hostname appearing in a certificate does not necessarily mean the hostname still exists.

Always validate discovered assets.

---

# 6. crt.sh from the Command Line

Certificate Transparency information can also be collected from the command line.

For example:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json"
```

If `jq` is available, names can be extracted with:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' \
  | sed 's/\*\.//g' \
  | sort -u
```

Save the results:

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' \
  | sed 's/\*\.//g' \
  | sort -u > ct.txt
```

Certificate Transparency should normally be treated as another discovery source rather than as proof that a host is currently active.

---

# 7. Combine Results

After collecting results from multiple sources, combine them into one list.

```bash
cat subfinder.txt amass.txt assetfinder.txt ct.txt > combined.txt
```

Then remove duplicates:

```bash
sort -u combined.txt > subdomains.txt
```

This can also be performed directly:

```bash
cat subfinder.txt amass.txt assetfinder.txt ct.txt \
  | sort -u \
  > subdomains.txt
```

Count the discovered hostnames:

```bash
wc -l subdomains.txt
```

Example:

```text
842 subdomains.txt
```

At this point, the list represents discovered candidate hostnames.

It does **not** mean that all of them currently resolve or expose a web service.

---

# 8. Scope Filtering

Before performing active validation, make sure the discovered hostnames remain within the authorised scope.

For a scope limited to:

```text
*.example.com
```

you can review the list using:

```bash
grep -E '(^|\.)example\.com$' subdomains.txt
```

Save the filtered list:

```bash
grep -E '(^|\.)example\.com$' subdomains.txt \
  | sort -u \
  > scoped-subdomains.txt
```

!!! important "Scope"

    A hostname being related to an organisation does not automatically mean it is authorised for testing. Always follow the defined engagement scope.

---

# 9. DNS Resolution with dnsx

The next stage is determining which discovered hostnames currently resolve.

```bash
dnsx -l scoped-subdomains.txt -silent
```

Save resolving hosts:

```bash
dnsx -l scoped-subdomains.txt \
  -silent \
  > resolved-subdomains.txt
```

Count them:

```bash
wc -l resolved-subdomains.txt
```

The workflow is now:

```text
Discovered Subdomains
        |
        v
   Scope Filtering
        |
        v
   DNS Resolution
        |
        v
Resolving Subdomains
```

This removes many historical or stale hostnames before HTTP probing.

---

# 10. Inspect DNS Records

DNS information can reveal useful infrastructure relationships.

For example:

```bash
dnsx -l scoped-subdomains.txt \
  -a \
  -aaaa \
  -cname \
  -resp
```

Interesting records include:

```text
A
AAAA
CNAME
MX
TXT
NS
```

CNAME records are particularly interesting because they can reveal:

* Cloud services
* CDNs
* SaaS platforms
* Third-party hosting
* External application platforms

Example:

```text
portal.example.com
        |
        v
customer.vendor-platform.example
```

This helps identify where applications are actually hosted.

---

# 11. HTTP Probing with httpx

A resolving hostname does not necessarily expose a web application.

Use httpx to identify HTTP and HTTPS services:

```bash
httpx -l resolved-subdomains.txt -silent
```

Save live web targets:

```bash
httpx -l resolved-subdomains.txt \
  -silent \
  > alive-hosts.txt
```

Count the results:

```bash
wc -l alive-hosts.txt
```

The pipeline now becomes:

```text
Candidate Subdomains
        |
        v
      dnsx
        |
        v
Resolving Subdomains
        |
        v
      httpx
        |
        v
Live Web Applications
```

---

# 12. Collect Useful HTTP Metadata

Instead of collecting only URLs, httpx can collect additional information.

```bash
httpx -l resolved-subdomains.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect
```

Additional useful options include:

```bash
httpx -l resolved-subdomains.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -server \
  -ip \
  -cname
```

Example output might look like:

```text
https://portal.example.com [200] [Customer Portal] [nginx] [React]
https://api.example.com [403] [Forbidden] [nginx]
https://dev.example.com [302] [Login] [Apache]
```

This makes prioritisation much easier than working from a plain hostname list.

---

# 13. Do Not Ignore Interesting Status Codes

A common mistake is to focus only on HTTP `200` responses.

Other responses can also reveal valuable targets:

```text
200    Application available
301    Permanent redirect
302    Redirect
401    Authentication required
403    Access forbidden
404    Host exists but requested path not found
500    Server-side error
```

For example, a `403` response may indicate:

* Administrative functionality
* IP restrictions
* Authentication controls
* Reverse proxy restrictions
* Access control at the web server

Therefore, avoid discarding hosts solely because they do not return HTTP `200`.

---

# 14. Redirects

Redirects can reveal application relationships.

For example:

```text
portal.example.com
        |
        v
login.example.com
        |
        v
sso.example.com
```

Following redirects can help identify:

* Central authentication services
* SSO infrastructure
* Canonical applications
* External identity providers
* Legacy domains

When appropriate:

```bash
httpx -l resolved-subdomains.txt \
  -silent \
  -follow-redirects \
  -status-code \
  -title
```

---

# 15. Wildcard DNS

Wildcard DNS can create misleading enumeration results.

For example, if:

```text
random-does-not-exist.example.com
```

still resolves, the domain may use wildcard DNS.

Test with a random hostname:

```bash
dig random-does-not-exist-12345.example.com
```

or:

```bash
nslookup random-does-not-exist-12345.example.com
```

If random hostnames consistently resolve to the same infrastructure, enumeration results should be interpreted carefully.

Wildcard DNS does not necessarily make discovered hosts useless, but it changes how they should be validated.

---

# 16. Duplicate Applications

Different subdomains may point to the same application.

For example:

```text
www.example.com
portal.example.com
app.example.com
```

may all redirect to:

```text
https://login.example.com/
```

HTTP metadata can help identify these relationships.

Useful comparison points include:

* IP address
* CNAME
* Page title
* Response size
* Redirect destination
* Server header
* Technology fingerprint

This can reduce unnecessary duplicate testing.

---

# 17. Development and Staging Systems

Subdomain enumeration frequently reveals environments such as:

```text
dev.example.com
development.example.com
test.example.com
testing.example.com
stage.example.com
staging.example.com
uat.example.com
qa.example.com
preprod.example.com
demo.example.com
```

These environments may differ from production in important ways.

Things to review include:

* Authentication
* Debug functionality
* Test accounts
* Error handling
* Software versions
* Exposed documentation
* Administrative functionality
* Security controls

These systems should only be tested when they are explicitly within scope.

---

# 18. Interesting Subdomain Names

Certain names may deserve additional attention during triage.

Examples include:

```text
admin
api
auth
backup
beta
cms
console
dashboard
demo
dev
developer
files
git
internal
jenkins
login
manage
monitor
old
portal
preprod
qa
sso
stage
staging
test
uat
upload
vpn
```

Search the discovered list:

```bash
grep -Ei \
'admin|api|auth|backup|beta|console|dashboard|dev|internal|login|portal|qa|stage|staging|test|uat|upload|vpn' \
subdomains.txt
```

This is useful for prioritisation, but hostnames should not be considered vulnerable based on their names alone.

---

# 19. Recursive Enumeration

A discovered subdomain may itself contain additional subdomains.

For example:

```text
example.com
   |
   +-- dev.example.com
          |
          +-- api.dev.example.com
          |
          +-- admin.dev.example.com
```

This means enumeration can become iterative:

```text
Initial Enumeration
        |
        v
Discover Subdomains
        |
        v
Identify Interesting Subdomains
        |
        v
Enumerate Deeper
        |
        v
New Subdomains
```

Recursive discovery can be particularly useful in larger environments.

---

# 20. Search Engine Discovery

Search engines can sometimes reveal subdomains through indexed content.

A basic search pattern is:

```text
site:example.com
```

Results may reveal:

* Applications
* Subdomains
* Documents
* Login portals
* Development environments
* Cached pages

Search engine results should be validated before being added to the active attack surface.

---

# 21. Public Code Repositories

Public repositories may contain references to infrastructure.

Look for:

```text
example.com
*.example.com
api.example.com
dev.example.com
internal.example.com
```

Potential sources include:

* Configuration files
* Documentation
* CI/CD configuration
* Deployment scripts
* Environment templates
* JavaScript
* Infrastructure-as-code files

The purpose is asset discovery. Any discovered asset must still be checked against the authorised scope before active testing.

---

# 22. Historical Data

Historical URL sources may reveal additional subdomains.

For example:

```bash
waybackurls example.com
```

or:

```bash
gau example.com
```

Extract hostnames:

```bash
waybackurls example.com \
  | awk -F/ '{print $3}' \
  | sort -u
```

These results can then be added to the candidate list and validated.

A hostname found in historical data may no longer exist, so DNS resolution remains important.

---

# 23. Combining Historical Discovery

Historical sources can be incorporated into the enumeration pipeline.

For example:

```bash
waybackurls example.com \
  | awk -F/ '{print $3}' \
  | sort -u \
  > wayback-subdomains.txt
```

Then combine:

```bash
cat \
  subfinder.txt \
  amass.txt \
  assetfinder.txt \
  ct.txt \
  wayback-subdomains.txt \
  | sort -u \
  > subdomains.txt
```

This creates a broader candidate set.

---

# 24. One Practical Passive Pipeline

A simple workflow can be:

```bash
subfinder -d example.com -all -recursive -silent -o subfinder.txt

amass enum -passive -d example.com -o amass.txt

assetfinder --subs-only example.com > assetfinder.txt

cat subfinder.txt amass.txt assetfinder.txt \
  | sort -u \
  > subdomains.txt

dnsx -l subdomains.txt \
  -silent \
  > resolved-subdomains.txt

httpx -l resolved-subdomains.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect
```

Conceptually:

```text
subfinder ────┐
              |
amass ────────+──> sort -u
              |        |
assetfinder ──┘        v
                  subdomains.txt
                        |
                        v
                      dnsx
                        |
                        v
             resolved-subdomains.txt
                        |
                        v
                      httpx
                        |
                        v
                Live Web Targets
```

---

# 25. Extended Pipeline

For broader reconnaissance:

```bash
subfinder -d example.com -all -recursive -silent -o subfinder.txt

amass enum -passive -d example.com -o amass.txt

assetfinder --subs-only example.com > assetfinder.txt

curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' \
  | sed 's/\*\.//g' \
  | sort -u \
  > ct.txt

waybackurls example.com \
  | awk -F/ '{print $3}' \
  | sort -u \
  > wayback-subdomains.txt

cat \
  subfinder.txt \
  amass.txt \
  assetfinder.txt \
  ct.txt \
  wayback-subdomains.txt \
  | sort -u \
  > subdomains.txt

dnsx -l subdomains.txt \
  -silent \
  > resolved-subdomains.txt

httpx -l resolved-subdomains.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -server \
  -ip \
  -cname \
  > alive-hosts.txt
```

This creates a useful starting dataset for the next reconnaissance stages.

---

# 26. Analyse the Results

Do not stop after generating `alive-hosts.txt`.

Review the output and ask:

* Which hosts return `200`?
* Which return `401` or `403`?
* Which hosts redirect?
* Are there administrative interfaces?
* Are there development environments?
* Are there staging environments?
* Are there APIs?
* Are there authentication portals?
* Which technologies are exposed?
* Are different software versions present?
* Are there unusual CNAME records?
* Are multiple applications hosted on the same IP?
* Are any hosts significantly different from the primary application?

Reconnaissance becomes valuable when the results influence what you test next.

---

# 27. Prioritisation

A simple prioritisation approach is:

```text
                    Discovered Hosts
                           |
             +-------------+-------------+
             |             |             |
          Production   Development     Legacy
             |             |             |
             +-------------+-------------+
                           |
                           v
                    Authentication?
                           |
                           v
                       API / Admin?
                           |
                           v
                  Technology / Version
                           |
                           v
                    Testing Priority
```

Interesting targets may include:

* Administrative portals
* APIs
* Development systems
* Staging systems
* Legacy applications
* Authentication services
* File-processing applications
* Applications running unusual technologies

---

# 28. Feed Discoveries Back into Reconnaissance

Subdomain enumeration should not be treated as a one-time task.

Suppose JavaScript analysis later reveals:

```text
https://internal-api.example.com
```

That hostname should be added to the reconnaissance dataset and validated.

Similarly, a discovered application may reveal:

```text
api.eu.example.com
auth.eu.example.com
files.eu.example.com
```

These discoveries can lead to additional enumeration.

The process therefore becomes:

```text
Enumerate
    |
    v
Validate
    |
    v
Investigate
    |
    v
Discover More
    |
    +---------> Enumerate Again
```

---

# 29. Recommended Output Files

A useful structure is:

```text
recon/
└── subdomains/
    ├── subfinder.txt
    ├── amass.txt
    ├── assetfinder.txt
    ├── ct.txt
    ├── wayback-subdomains.txt
    ├── combined.txt
    ├── subdomains.txt
    ├── scoped-subdomains.txt
    ├── resolved-subdomains.txt
    └── alive-hosts.txt
```

Each file represents a specific stage of the reconnaissance pipeline.

This makes troubleshooting and reproducing results much easier than continuously overwriting a single file.

---

# 30. Tool Summary

| Tool | Purpose |
| --- | --- |
| Subfinder | Passive subdomain enumeration |
| Amass | Asset and subdomain discovery |
| Assetfinder | Passive subdomain discovery |
| crt.sh | Certificate Transparency discovery |
| dnsx | DNS validation and record inspection |
| httpx | HTTP probing and metadata collection |
| waybackurls | Historical URL discovery |
| gau | Historical and indexed URL discovery |
| jq | JSON processing |
| sort | Deduplication and organisation |

No single source provides complete coverage.

The strongest workflow combines multiple sources and validates the results.

---

# 31. Quick Reference

## Subfinder

```bash
subfinder -d example.com -all -recursive -silent -o subfinder.txt
```

## Amass

```bash
amass enum -passive -d example.com -o amass.txt
```

## Assetfinder

```bash
assetfinder --subs-only example.com > assetfinder.txt
```

## Certificate Transparency

```bash
curl -s "https://crt.sh/?q=%25.example.com&output=json" \
  | jq -r '.[].name_value' \
  | sed 's/\*\.//g' \
  | sort -u \
  > ct.txt
```

## Combine

```bash
cat subfinder.txt amass.txt assetfinder.txt ct.txt \
  | sort -u \
  > subdomains.txt
```

## DNS Resolution

```bash
dnsx -l subdomains.txt -silent > resolved-subdomains.txt
```

## HTTP Probing

```bash
httpx -l resolved-subdomains.txt \
  -silent \
  -status-code \
  -title \
  -tech-detect \
  -server \
  -ip \
  -cname
```

---

# 32. Final Workflow

The complete process can be summarised as:

```text
                         example.com
                              |
          +-------------------+-------------------+
          |                   |                   |
      Subfinder             Amass             Assetfinder
          |                   |                   |
          +-------------------+-------------------+
                              |
                         CT / Archives
                              |
                              v
                         sort -u
                              |
                              v
                       subdomains.txt
                              |
                              v
                            dnsx
                              |
                              v
                 resolved-subdomains.txt
                              |
                              v
                            httpx
                              |
                              v
                       Live Web Targets
                              |
          +-------------------+-------------------+
          |                   |                   |
     Technology           Content            JavaScript
    Identification        Discovery            Analysis
          |                   |                   |
          +-------------------+-------------------+
                              |
                              v
                     Expanded Attack Surface
```

Subdomain enumeration is therefore not an isolated reconnaissance task. It is the first stage in building a broader understanding of the target's web attack surface.

---

## Related Notes

* [Reconnaissance Overview](index.md)
* [Technology Identification](technology-identification.md)
* [Content Discovery](content-discovery.md)
* [Parameter Discovery](parameter-discovery.md)
* [JavaScript Analysis](javascript-analysis.md)
* [Web Application Testing Methodology](../methodology.md)
* [Web Application Pentesting Checklist](../checklist.md)
