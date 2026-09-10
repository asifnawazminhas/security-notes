---
title: Interactsh
description: Practical Interactsh reference for authorised out-of-band security testing, including DNS and HTTP interaction detection, correlation, SSRF and blind-vulnerability validation, evidence handling, false-positive analysis, operational safety, and integration with wider web application testing methodology.
---

# Interactsh

Interactsh is an out-of-band interaction service from ProjectDiscovery that helps detect server-side activity which does not produce a visible response in the application.

It is especially useful for testing conditions where a target may cause an external interaction such as:

- DNS resolution;
- HTTP callback;
- blind SSRF;
- blind XXE;
- blind command execution indicators;
- callback-based template behavior;
- asynchronous backend requests;
- external fetch behavior.

Interactsh gives the tester a unique callback domain and records interactions that reach the service.

A simplified model is:

```text
Tester
  |
  v
Unique Interactsh Domain
  |
  v
Target Receives Input
  |
  v
Target Makes External Request
  |
  v
Interactsh Records Interaction
```

!!! warning "Authorised testing only"
    Use Interactsh only for explicitly authorised testing. Out-of-band payloads cause target systems or backend services to initiate external network activity. Confirm that external callbacks are permitted by the engagement and that the destination is approved before use.

---

# Where Interactsh Fits

Interactsh is most useful when direct response-based validation is difficult.

A common workflow is:

```text
Security Hypothesis
      |
      v
Inject Unique Callback Value
      |
      v
Target Processes Input
      |
      v
External Interaction
      |
      v
Interactsh
      |
      v
Correlate
      |
      v
Manual Validation
```

Related tools:

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[Nuclei](nuclei.md)

[Katana](katana.md)

[ffuf](ffuf.md)

---

# Official Project

Official project:

[Interactsh - GitHub](https://github.com/projectdiscovery/interactsh){ target="_blank" rel="noopener noreferrer" }

Official documentation:

[Interactsh Documentation](https://docs.projectdiscovery.io/tools/interactsh/overview){ target="_blank" rel="noopener noreferrer" }

Because Interactsh evolves over time, confirm current syntax with the installed client:

```bash
interactsh-client -h
```

---

# What Out-of-Band Means

An out-of-band, or OOB, test relies on an interaction that occurs outside the original HTTP response.

For example:

```text
Original Request
      |
      v
Application
      |
      v
No Visible Difference
```

but internally:

```text
Application
      |
      v
Backend Server
      |
      v
DNS / HTTP Request
      |
      v
Interactsh
```

The callback becomes supporting evidence that some component processed the supplied external destination.

---

# Why OOB Testing Is Useful

Some vulnerabilities are difficult to verify through the normal application response.

Examples include:

- blind SSRF;
- blind XXE;
- asynchronous URL fetchers;
- background processing;
- server-side callbacks.

In these cases:

```text
No application response difference
```

does not necessarily mean:

```text
No server-side behavior
```

---

# Basic Interactsh Client Workflow

Start the client:

```bash
interactsh-client
```

The client typically generates a unique interaction domain.

Conceptually:

```text
abc123.example-interact-domain
```

Use the generated value only within authorised tests.

---

# Unique Correlation Values

Each test should ideally use a unique identifier.

For example:

```text
ssrf-profile-01.<interactsh-domain>
```

or:

```text
import-test-02.<interactsh-domain>
```

This improves correlation when several tests are running.

---

# Why Unique Values Matter

Suppose you test:

```text
/avatar
/webhook
/import
```

with the same callback hostname.

One interaction appears.

You may not know which feature caused it.

Instead:

```text
avatar-01.<domain>
webhook-01.<domain>
import-01.<domain>
```

provides clearer evidence.

---

# DNS Interactions

A DNS interaction means that some system attempted to resolve the supplied hostname.

Conceptually:

```text
Application Input
      |
      v
Backend
      |
      v
DNS Resolver
      |
      v
Interactsh
```

This proves name resolution occurred.

It does not automatically prove that an HTTP request followed.

---

# HTTP Interactions

An HTTP interaction provides stronger evidence that a component made a web request to the supplied destination.

Potential evidence may include:

- timestamp;
- source IP;
- method;
- path;
- headers.

Interpret this carefully because the observed source may be a proxy, NAT gateway, or security product rather than the application host itself.

---

# DNS vs HTTP Evidence

A useful distinction is:

```text
DNS callback
  ->
Name was resolved
```

```text
HTTP callback
  ->
Web request reached interaction server
```

Do not report them as equivalent.

---

# SMTP and Other Protocols

Interactsh may support additional protocol interaction types depending on its current capabilities and deployment.

Use:

```bash
interactsh-client -h
```

and current ProjectDiscovery documentation for exact protocol support.

---

# Blind SSRF

Interactsh is commonly used to validate blind server-side request forgery.

Related note:

[Server Side Request Forgery](../../web/ssrf.md)

A simplified flow is:

```text
User-Controlled URL
      |
      v
Server-Side Fetcher
      |
      v
Interactsh URL
      |
      v
Observed Callback
```

---

# Blind SSRF Example

Suppose the application accepts:

```text
POST /api/avatar
```

with:

```json
{
  "url": "https://example.test/image.png"
}
```

A controlled OOB test may replace the URL with a unique Interactsh value.

If an external callback appears, that indicates the backend attempted to interact with the supplied destination.

The next question is:

> Which component caused the interaction, and what control does the user have over it?

---

# SSRF Is More Than a Callback

A callback alone does not establish the full impact.

Consider:

```text
Can host be controlled?

Can scheme be controlled?

Can port be controlled?

Are redirects followed?

Can internal destinations be reached?

Does DNS rebinding matter?

Are private ranges blocked?

Is response content returned?
```

OOB interaction confirms server-side behavior.

It does not automatically confirm internal-network access.

---

# Blind XXE

Out-of-band interaction can also support XML external entity testing where the XML parser causes an external lookup.

Related note:

[XML External Entity Injection](../../web/xxe.md)

The conceptual flow is:

```text
XML Input
   |
   v
Parser
   |
   v
External Entity Resolution
   |
   v
Interactsh
```

---

# XXE Callback Interpretation

A DNS or HTTP interaction may indicate that external entity resolution occurred.

However, verify:

- parser behavior;
- XML location;
- timing;
- unique correlation value.

Do not attribute a callback to XXE unless the test input and timing support that conclusion.

---

# Blind Command Execution Indicators

In some authorised research scenarios, a callback may be used as a minimal indicator that command execution or template evaluation occurred.

The same caution applies:

```text
Callback
  !=
Automatic proof of arbitrary command execution
```

The exact source of the interaction must be established.

---

# Template Injection

Some server-side template injection scenarios may allow external network interaction.

Related note:

[Server-Side Template Injection](../../web/ssti.md)

A callback can support a hypothesis, but the template engine and execution context should still be validated.

---

# Asynchronous Processing

Applications may process input later.

Examples include:

- background queues;
- scheduled jobs;
- document processors;
- email workers;
- import pipelines.

A callback may arrive:

```text
seconds
minutes
or longer
```

after the original request.

Keep timestamps.

---

# Timing Correlation

A useful evidence table is:

| Event | Timestamp |
|---|---|
| Test request sent | 14:05:10 |
| DNS callback received | 14:05:11 |
| HTTP callback received | 14:05:11 |

This creates a strong temporal correlation.

---

# Delayed Interaction

If a callback appears much later, do not automatically assume it belongs to the most recent request.

Use unique identifiers.

---

# Security Scanners

A callback may be generated by:

- email scanner;
- URL reputation scanner;
- proxy;
- WAF;
- security sandbox;
- link preview service.

This is a major source of false attribution.

---

# Scanner-Induced Callbacks

Suppose you submit:

```text
https://unique-id.<interactsh-domain>
```

to an application.

An organisation's security gateway may inspect the URL and request it before the application ever processes it.

Therefore:

```text
Callback
```

does not always mean:

```text
Target application fetched the URL
```

---

# How to Distinguish Security Scanners

Look at:

- source IP;
- User-Agent;
- headers;
- timing;
- repeated access;
- protocol.

A corporate security scanner may have very different characteristics from the application backend.

---

# Source IP Is Not Always Backend IP

Outbound traffic may pass through:

- NAT;
- egress proxy;
- cloud gateway;
- service mesh.

Therefore the observed IP may represent infrastructure rather than the exact application server.

---

# Header Analysis

HTTP callbacks may reveal headers such as:

```text
User-Agent
Accept
Host
Custom application headers
```

These can help identify the requesting component.

Do not rely on one header alone.

---

# Custom Paths

Use unique paths where possible.

Example:

```text
https://<interactsh-domain>/avatar-test-01
```

This can improve correlation.

---

# Unique Query Values

Another option is:

```text
https://<interactsh-domain>/?case=avatar-01
```

The exact callback format should match the tested application's accepted URL syntax.

---

# Multiple Variables

If a request contains several URL-like parameters, test them one at a time.

Example:

```json
{
  "avatar": "URL1",
  "callback": "URL2"
}
```

Do not modify both simultaneously if you want clear attribution.

---

# One Variable at a Time

A good testing principle is:

```text
Baseline
  |
  v
Change One Input
  |
  v
Observe
```

This improves evidence quality.

---

# Burp Suite Integration

Burp Repeater is ideal for controlled OOB testing.

Workflow:

```text
Burp Proxy
   |
   v
Capture Valid Request
   |
   v
Repeater
   |
   v
Replace One Value with Unique Interactsh URL
   |
   v
Send
   |
   v
Observe Callback
```

Related tool:

[Burp Suite](burp-suite.md)

---

# Burp Collaborator vs Interactsh

Burp Suite Professional includes Burp Collaborator functionality for OOB testing.

Interactsh provides a separate OOB interaction platform.

Conceptually:

```text
Burp Collaborator
        |
        +-- integrated with Burp Pro

Interactsh
        |
        +-- independent ProjectDiscovery workflow
```

Use whichever platform is approved and fits the workflow.

---

# Burp Community

Burp Community Edition does not provide the same integrated Collaborator workflow as Burp Professional.

Interactsh can therefore be useful in environments where a standalone OOB service is preferred.

---

# Nuclei Integration

Nuclei can use OOB interactions in relevant templates.

A simplified workflow is:

```text
Nuclei
  |
  v
OOB Template
  |
  v
Target
  |
  v
Interactsh
  |
  v
Matched Interaction
```

Related tool:

[Nuclei](nuclei.md)

---

# Nuclei OOB Results

A Nuclei match may combine:

- request logic;
- Interactsh callback;
- template matchers.

Always inspect the template.

Do not report the template ID without understanding the underlying behavior.

---

# Manual Reproduction After Nuclei

A strong workflow is:

```text
Nuclei OOB Match
      |
      v
Read Template
      |
      v
Reproduce in Burp
      |
      v
Use New Unique Interactsh Value
      |
      v
Observe Callback
```

This produces better evidence.

---

# ffuf Integration

ffuf may discover functionality such as:

```text
/webhook
/import
/fetch
/preview
/callback
```

These endpoints may later deserve OOB testing.

Related tool:

[ffuf](ffuf.md)

---

# Katana Integration

Katana may discover parameters or routes through JavaScript.

Example:

```text
POST /api/import
parameter: sourceUrl
```

That creates a potential OOB testing hypothesis.

Related tool:

[Katana](katana.md)

---

# Webhook Features

Webhooks intentionally make outbound requests.

Therefore:

```text
Webhook causes callback
```

is not a vulnerability.

The security questions may instead include:

```text
Can destination be arbitrary?

Are private network destinations blocked?

Is authentication applied?

Can headers be controlled?

Can sensitive responses be exposed?
```

---

# URL Preview Features

Applications may fetch URLs to generate:

- previews;
- screenshots;
- metadata;
- thumbnails.

A callback may simply confirm intended fetch behavior.

The vulnerability depends on missing destination restrictions or other impact.

---

# Image Fetchers

Features that accept:

```text
image URL
```

may intentionally retrieve external content.

The security question is whether the fetcher can be abused beyond the intended trust boundary.

---

# PDF Generators

Some PDF or document generation systems fetch:

- images;
- CSS;
- external assets.

OOB testing may reveal these network interactions.

Do not assume the behavior is vulnerable.

---

# Import-From-URL Features

An import feature may legitimately retrieve external content.

Test:

```text
Allowed schemes
Allowed hosts
Internal ranges
Redirect handling
Authentication
```

The callback only confirms outbound behavior.

---

# Callback Parameters

Applications may accept explicit callback URLs.

This may be intended.

Assess:

- authorization;
- validation;
- destination restrictions;
- sensitive data included in callbacks.

---

# Open Redirect vs SSRF

Do not confuse:

```text
Browser redirect
```

with:

```text
Server-side request
```

If the user's browser navigates to Interactsh, that is not SSRF.

The request must originate from a server-side component.

---

# Distinguishing Client-Side Requests

A callback might come from:

- browser;
- mobile application;
- server.

Use:

- source IP;
- headers;
- timing;
- browser network logs.

to determine the likely origin.

---

# Browser Callback

If you click a supplied Interactsh URL manually:

```text
your browser
```

will generate an interaction.

This is expected and should not be confused with application behavior.

---

# DNS Prefetch

Browsers and security tools may perform DNS prefetching.

A DNS lookup alone therefore needs careful interpretation in browser-driven workflows.

---

# Email Workflows

Links embedded in:

- support requests;
- email notifications;
- password-reset messages;

may be visited by email-security scanners.

This can create OOB interactions unrelated to the target application's backend logic.

---

# Metadata Scanners

Some systems automatically inspect URLs to generate:

- previews;
- reputation;
- anti-malware verdicts.

These can produce false attribution.

---

# Interaction Correlation

For every callback retain:

```text
Unique payload ID
Original request timestamp
Interaction timestamp
Protocol
Source IP
Headers where available
Application endpoint
Parameter
```

This allows later analysis.

---

# Correlation Example

```text
Test:
avatar-04

Application endpoint:
/api/avatar

Parameter:
url

Request time:
14:10:05

Interaction:
HTTP

Interaction time:
14:10:06

Path:
/avatar-04
```

This is stronger than:

```text
Interactsh got a hit.
```

---

# Use Separate Identifiers Per Attempt

If retrying a test:

```text
avatar-01
avatar-02
avatar-03
```

is better than reusing:

```text
avatar
```

This prevents stale callbacks from creating confusion.

---

# DNS Caching

DNS caching can affect repeated tests.

A previously resolved hostname may not generate another DNS request immediately.

Unique hostnames reduce this problem.

---

# HTTP Caching

Proxies or application caches may also suppress repeated HTTP fetches.

Unique paths and hostnames can improve repeatability.

---

# Redirect Testing

A target may:

```text
fetch initial URL
```

and then follow redirects.

A controlled test can distinguish:

```text
direct fetch
```

from:

```text
redirect-following behavior
```

Do not involve unauthorized internal or third-party targets.

---

# Redirects and SSRF

Redirect behavior matters because an application may validate:

```text
initial URL
```

but not:

```text
redirect destination
```

This can create a security issue.

Use only controlled authorised destinations during validation.

---

# Scheme Handling

Applications may support:

```text
http
https
```

and potentially other URL schemes.

Do not spray unusual schemes without a specific testing objective.

Focus on the behavior relevant to the feature.

---

# Port Handling

A URL fetcher may allow custom ports.

A callback to a controlled external service can help determine whether the port is honored.

Do not use OOB testing to probe third-party or internal ports unless that scope is explicitly authorised.

---

# Internal Network Access

One of the major SSRF impact questions is whether the server can reach private resources.

However, Interactsh is generally an external service.

It proves:

```text
outbound interaction
```

not necessarily:

```text
private network reachability
```

Additional internal validation must remain within scope.

---

# Cloud Metadata

Do not automatically test cloud metadata endpoints merely because SSRF is suspected.

Cloud metadata access can expose sensitive credentials.

Use lower-impact validation first and only test metadata services when explicitly authorised.

---

# Response Disclosure

Blind SSRF:

```text
server makes request
but
response not returned
```

Non-blind SSRF may return:

```text
fetched response
```

The security impact can differ significantly.

---

# Egress Filtering

An absent callback may mean:

```text
No vulnerability
```

or:

```text
Egress blocked
```

or:

```text
DNS blocked
```

or:

```text
Application did not process request
```

Do not interpret silence as definitive proof.

---

# Proxy Requirements

A backend service may require an outbound proxy.

If the application cannot reach Interactsh directly, a callback may not occur even though server-side URL handling exists.

---

# DNS Restrictions

Enterprise DNS controls may block interaction domains.

Again:

```text
No callback
```

does not automatically equal:

```text
No SSRF
```

---

# Asynchronous Queues

A backend job might process the URL later.

Wait long enough to match the application's known processing behavior.

Use unique IDs to avoid ambiguity.

---

# Repeated Callbacks

A single injected URL may produce multiple interactions because of:

- DNS lookup;
- HTTP request;
- redirect;
- retries;
- scanners.

Do not count each callback as a separate vulnerability.

---

# Retries

An application may retry failed outbound requests.

Example:

```text
14:10:01 HTTP
14:10:06 HTTP
14:10:16 HTTP
```

This may represent one application action with retry behavior.

---

# Resolver Behavior

A DNS callback may originate from a recursive resolver rather than the target host.

This is normal.

The resolver proves that some system attempted to resolve the name.

---

# Public Interactsh Infrastructure

Public interaction infrastructure is convenient, but organisational policy may prohibit sending target callbacks to public third-party services.

In that case, use an approved self-hosted or internal OOB service.

---

# Self-Hosting

Interactsh can be self-hosted.

This may be useful when:

- data sensitivity is high;
- public OOB services are not approved;
- internal network testing requires controlled infrastructure;
- callback logs must remain under organisational control.

Use current official documentation for deployment details.

---

# Self-Hosted Architecture

Conceptually:

```text
Authorised Target
      |
      v
Controlled DNS / HTTP OOB Infrastructure
      |
      v
Researcher
```

The infrastructure becomes part of the engagement and must be secured.

---

# Domain Control

Self-hosted OOB infrastructure normally requires control over:

- DNS;
- domain records;
- server;
- listener ports.

Protect these assets like other red team infrastructure.

---

# TLS

HTTPS callbacks may require valid TLS depending on the target client.

Use controlled certificates where required.

The exact TLS deployment depends on the OOB infrastructure.

---

# Interaction Data Sensitivity

Callback data may contain:

- source IPs;
- internal proxy details;
- User-Agent;
- authentication headers;
- query values.

Treat interaction logs as assessment evidence.

---

# Do Not Embed Secrets in Callback URLs

Avoid placing:

```text
passwords
tokens
customer data
```

inside Interactsh hostnames or paths.

Use synthetic correlation identifiers.

---

# Subdomain Length

When embedding test identifiers in DNS labels, keep values reasonably short and compatible with DNS naming rules.

Use simple identifiers such as:

```text
ssrf01
avatar02
import03
```

---

# Request Headers

Some server-side fetchers may forward:

- User-Agent;
- Referer;
- custom headers.

These can provide useful evidence.

Do not assume forwarded headers are secrets unless they actually contain sensitive values.

---

# Host Header

The OOB request's Host value normally corresponds to the supplied Interactsh domain.

This is expected.

Do not confuse it with Host header injection in the original application.

---

# User-Agent

A callback User-Agent can help identify:

- language runtime;
- HTTP library;
- security scanner;
- browser.

It is supporting evidence, not absolute attribution.

---

# Source Port

Network source ports are usually ephemeral and have limited security significance.

Do not overinterpret them.

---

# Unique Interaction IDs

Interactsh-generated identifiers should be retained for the lifetime of the test.

They help connect:

```text
request
```

to:

```text
callback
```

---

# Blind Vulnerability Model

A useful generic OOB model is:

```text
Input Controlled by Tester
      |
      v
Server-Side Processing
      |
      v
Outbound Interaction
      |
      v
Unique Callback
      |
      v
Correlation
      |
      v
Root-Cause Validation
```

---

# OOB Interaction Is Supporting Evidence

The strongest conclusion is usually not:

```text
Interactsh received DNS.
```

It is:

```text
The application caused server-side resolution of an attacker-controlled
hostname when processing the supplied input.
```

This explains the security behavior.

---

# Manual Validation

After an automated OOB result:

1. create a fresh unique callback value;
2. replay only the relevant request;
3. capture the exact timestamp;
4. observe the interaction;
5. confirm the protocol;
6. inspect headers/source;
7. repeat if necessary.

This creates stronger evidence.

---

# Reproduce One Candidate at a Time

Avoid sending many different OOB candidates before checking results.

A better workflow is:

```text
Candidate 1
    |
    v
Observe
    |
    v
Candidate 2
    |
    v
Observe
```

This makes attribution easier.

---

# False Positives

Common false-positive or false-attribution causes include:

- security scanners;
- browser prefetch;
- email link scanners;
- WAF inspection;
- reverse proxy processing;
- stale asynchronous jobs;
- reused correlation values.

Always correlate carefully.

---

# False Negatives

Possible reasons for no callback include:

- egress filtering;
- DNS filtering;
- proxy requirements;
- unsupported URL scheme;
- application validation;
- asynchronous delay;
- network outage;
- OOB infrastructure unavailable.

A clean OOB test does not prove absence of server-side URL processing.

---

# Baseline Testing

Before testing a suspected URL field, determine normal behavior.

For example:

```text
Valid public image URL
      |
      v
Does application fetch it?
```

If the feature does not fetch normal URLs, an OOB failure may be expected.

---

# Known-Good External URL

Where permitted, use a controlled known-good external resource to understand intended behavior before testing security boundaries.

This can answer:

```text
Does this feature actually perform server-side retrieval?
```

---

# Error Messages

Application errors can help interpret OOB behavior.

Examples:

```text
Unable to fetch URL
Invalid hostname
Connection timed out
Unsupported scheme
```

Combine these with OOB observations.

---

# Timeout Behavior

If the application response becomes slower when using an unreachable destination, this may indicate backend fetching.

Timing alone is weak evidence.

Use OOB correlation where possible.

---

# Redirect Chain Evidence

When testing redirect behavior, preserve:

```text
initial URL
redirect destination
callback observed
```

This can help explain how validation is performed.

---

# Nuclei Result Validation

If Nuclei reports an OOB finding:

```text
Nuclei
  |
  v
Template ID
  |
  v
Interactsh Callback
```

inspect the exact template logic before reporting.

Related tool:

[Nuclei](nuclei.md)

---

# Burp Reproduction

A clean manual reproduction might contain:

```text
Request:
POST /api/import

Parameter:
url

Value:
https://import-01.<interactsh-domain>/

Result:
HTTP 202

OOB:
HTTP GET received 1 second later
```

This is much stronger than a scanner screenshot.

---

# Evidence Collection

For each important OOB test, retain:

```text
Target:
Endpoint:
Parameter:
Authentication context:
Original request:
Unique OOB identifier:
Request timestamp:
Interaction timestamp:
Interaction protocol:
Source IP:
Headers:
Response:
Manual reproduction:
Conclusion:
```

---

# Evidence Example

```text
Target:
https://portal.example.test

Endpoint:
/api/avatar

Parameter:
url

Context:
Authenticated standard user

Payload:
https://avatar-07.<interactsh-domain>/

Request time:
14:24:11

Interaction:
HTTP GET

Interaction time:
14:24:12

Conclusion:
The backend performed an outbound HTTP request to the user-supplied
destination while processing the avatar URL.
```

Further SSRF impact assessment would still be required.

---

# Reporting Blind SSRF

Avoid:

```text
Interactsh got a DNS hit, therefore critical SSRF.
```

Prefer:

```text
The avatar URL parameter caused the application backend to resolve and
request an attacker-controlled external hostname. This confirms
server-side outbound request capability. Additional testing was
required to determine whether internal or otherwise restricted
destinations were reachable.
```

---

# Reporting DNS-Only Behavior

Example:

```text
The supplied hostname triggered an outbound DNS resolution from the
application environment. No corresponding HTTP interaction was
observed during testing. The evidence therefore confirms server-side
name resolution but does not establish successful HTTP retrieval.
```

---

# Reporting Scanner-Induced Interaction

Example:

```text
The submitted URL generated an external request, but the callback
headers and source infrastructure were consistent with the
organisation's URL inspection service rather than the application
backend. The result was therefore not treated as evidence of SSRF.
```

---

# Reporting Intended Webhook Behavior

Example:

```text
The application intentionally delivered HTTP requests to user-configured
webhook destinations. The outbound interaction itself was expected.
Security testing therefore focused on destination restrictions,
authorisation, and whether private network addresses could be targeted.
```

---

# Reporting an Unconfirmed Candidate

Example:

```text
No unique DNS or HTTP interaction was observed for the supplied callback
value. Because the environment uses restricted outbound networking, the
result was considered inconclusive rather than proof that server-side
URL processing was absent.
```

---

# Remediation

For SSRF-style issues, remediation may include:

- strict destination allowlists;
- blocking private and link-local address ranges where appropriate;
- validating resolved addresses;
- revalidating after redirects;
- restricting supported URL schemes;
- egress controls;
- dedicated fetch proxies;
- network segmentation.

The correct controls depend on the application's legitimate requirements.

---

# Allowlist Over Blocklist

Where possible, a strong design is:

```text
Application needs to fetch:
images.example-cdn.com
```

Then allow only:

```text
images.example-cdn.com
```

rather than trying to block every dangerous network range.

---

# DNS Validation

Hostname validation alone can be insufficient because DNS resolution can change.

Robust designs should consider the resolved destination.

The exact implementation depends on architecture and language.

---

# Redirect Validation

If redirects are followed:

```text
Initial URL allowed
      |
      v
Redirect
      |
      v
New Destination
```

the new destination should also satisfy security policy.

---

# Network Egress Controls

Network-level controls can reduce SSRF impact.

Examples include:

- outbound firewall rules;
- application proxies;
- segmentation;
- cloud network policies.

These are defence-in-depth controls.

They do not replace secure application validation.

---

# Metadata Services

Cloud metadata endpoints deserve specific protection in cloud environments.

Use platform-recommended metadata protections and least-privileged identity design.

Do not rely solely on application-level URL filtering.

---

# Retesting

After remediation:

1. repeat the original public callback test;
2. confirm expected legitimate behavior;
3. test blocked destinations safely;
4. test redirect validation where relevant;
5. verify OOB interactions match intended policy.

The objective is to confirm the trust boundary, not merely make Interactsh stop receiving requests.

---

# Purple Teaming

OOB testing can also validate detection of suspicious server-side outbound communication.

```text
Controlled OOB Request
      |
      v
Backend Callback
      |
      v
DNS / Proxy / Firewall Logs
      |
      v
SIEM
      |
      v
Detection Review
```

Related section:

[Purple Teaming](../../purple-teaming/index.md)

---

# Detection Engineering

Potential telemetry includes:

- DNS logs;
- proxy logs;
- firewall connections;
- cloud egress logs;
- application logs;
- WAF logs.

Detection should consider application context.

A legitimate webhook service will naturally make outbound requests.

---

# OOB Detection Context

A useful detection question is:

```text
Which application processes should make outbound connections?
```

Unexpected egress from normally isolated backend components may be more useful than detecting a specific Interactsh domain.

---

# Tool-Specific Indicators

Interactsh domains may appear in logs during testing.

These can support exercise correlation.

Long-term defensive logic should not depend only on one known OOB service domain.

---

# Operational Safety

Before OOB testing ask:

```text
Are external callbacks permitted?

Is public Interactsh permitted?

Could the feature trigger repeated background jobs?

Could the callback contain sensitive data?

Could third-party scanners interfere?
```

---

# Do Not Exfiltrate Real Data

An OOB test generally needs only:

```text
unique identifier
```

Do not include real credentials, file content, or personal data in the callback.

---

# Minimise OOB Content

Prefer:

```text
ssrf-test-01
```

over embedding:

```text
database contents
```

or other sensitive information.

---

# Out-of-Scope Network Targets

Do not test internal IPs, cloud metadata, partner systems, or unrelated infrastructure simply because the application may be able to reach them.

Reachability is not authorisation.

---

# Public Service Availability

Public OOB services can occasionally be unavailable or delayed.

Before interpreting a negative result, confirm the interaction service itself is working using a harmless local test where appropriate.

---

# Local Verification

For example, if using a generated Interactsh domain, resolving or requesting it from your own authorised workstation can confirm that the interaction channel is functioning.

Clearly distinguish these self-generated callbacks from target-generated callbacks.

---

# Self-Test Labeling

Use a unique self-test identifier such as:

```text
operator-selftest-01
```

so it cannot be confused with application callbacks.

---

# Interaction Log Hygiene

Keep only the interactions relevant to the assessment.

Public/shared OOB environments may generate unrelated noise.

Use unique identifiers and timestamps to avoid confusion.

---

# Workflow with Nuclei

A useful sequence is:

```text
Target Inventory
      |
      v
Nuclei OOB Template
      |
      v
Interaction
      |
      v
Inspect Template
      |
      v
Manual Burp Reproduction
      |
      v
Root-Cause Validation
```

---

# Workflow with Katana

```text
Katana
  |
  v
Discover /api/import?url=
  |
  v
Burp
  |
  v
Interactsh Test
  |
  v
Server-Side Callback
```

---

# Workflow with ffuf

```text
ffuf
 |
 v
Discover /webhook
 |
 v
Manual Feature Review
 |
 v
Interactsh
 |
 v
OOB Validation
```

---

# Workflow with Source Review

White-box testing can make OOB validation substantially stronger.

```text
Source Review
      |
      v
HTTP Client Sink
      |
      v
User-Controlled URL
      |
      v
Interactsh
      |
      v
Runtime Confirmation
```

Related section:

[Source Code Review Tools](../source-code-review/index.md)

---

# Source-to-Sink SSRF Analysis

A code-level flow may look like:

```text
request.json["url"]
      |
      v
validation()
      |
      v
http_client.get(url)
```

OOB testing can confirm the runtime behavior.

---

# Logs and Application Evidence

Where available, correlate OOB interactions with application logs.

Example:

```text
14:24:11 request received
14:24:11 fetch job queued
14:24:12 outbound HTTP request
14:24:12 Interactsh callback
```

This creates very strong evidence.

---

# Quick Command Reference

## Start Client

```bash
interactsh-client
```

## Help

```bash
interactsh-client -h
```

For server selection, output formats, authentication, polling, and self-hosted configuration, use the exact options documented by:

```bash
interactsh-client -h
```

and current ProjectDiscovery documentation.

---

# Interactsh Checklist

## Preparation

- [ ] Target explicitly authorised.
- [ ] External callbacks permitted.
- [ ] OOB provider approved.
- [ ] Public vs self-hosted decision made.
- [ ] Sensitive data handling understood.
- [ ] Application feature understood.
- [ ] Baseline behavior tested.

## Correlation

- [ ] Unique identifier used.
- [ ] One identifier per test.
- [ ] Original request timestamp retained.
- [ ] Interaction timestamp retained.
- [ ] Interaction protocol retained.
- [ ] Source information retained.
- [ ] Callback path/hostname retained.

## Attribution

- [ ] Browser callback ruled out.
- [ ] Security scanner callback considered.
- [ ] Email scanner considered where relevant.
- [ ] Proxy/NAT considered.
- [ ] Resolver source interpreted carefully.
- [ ] Application backend attribution supported.

## SSRF

- [ ] User control over destination understood.
- [ ] Scheme control understood.
- [ ] Host control understood.
- [ ] Port control understood where relevant.
- [ ] Redirect behavior reviewed.
- [ ] External callback not confused with internal reachability.
- [ ] Cloud metadata not tested without explicit authorisation.

## XXE / Other OOB

- [ ] Exact parser/input path known.
- [ ] Interaction tied to unique input.
- [ ] Protocol understood.
- [ ] Alternative callback causes considered.
- [ ] Root cause manually validated.

## Operational Safety

- [ ] No real secrets embedded in OOB values.
- [ ] No customer data exfiltrated.
- [ ] Out-of-scope systems not targeted.
- [ ] Background retry behavior monitored.
- [ ] Unexpected high callback volume investigated.
- [ ] Testing stopped if production impact appears.

## Evidence

- [ ] Target retained.
- [ ] Endpoint retained.
- [ ] Parameter retained.
- [ ] Authentication context retained.
- [ ] Original request retained.
- [ ] Unique callback ID retained.
- [ ] Interaction details retained.
- [ ] Manual reproduction retained.
- [ ] Sensitive values redacted.
- [ ] Final conclusion states actual behavior.

## Reporting

- [ ] DNS interaction not overstated as HTTP.
- [ ] External callback not automatically labeled SSRF.
- [ ] Intended webhook behavior distinguished from vulnerability.
- [ ] Security scanner callbacks excluded.
- [ ] Internal reachability reported only if actually validated.
- [ ] Remediation addresses destination trust.
- [ ] Retest criteria explicit.

---

# Related Tool Notes

[Web Application Testing Tools](index.md)

[Burp Suite](burp-suite.md)

[ffuf](ffuf.md)

[Katana](katana.md)

[Nuclei](nuclei.md)

[sqlmap](sqlmap.md)

---

# Related Enumeration Tools

[Web Enumeration Tools](../web-enumeration/index.md)

[WhatWeb](../web-enumeration/whatweb.md)

[Wappalyzer](../web-enumeration/wappalyzer.md)

[httpx](../web-enumeration/httpx.md)

---

# Related Source Review Tools

[Source Code Review Tools](../source-code-review/index.md)

[Semgrep](../../source-code-review/static-analysis/semgrep.md)

[OpenGrep](../../source-code-review/static-analysis/opengrep.md)

[CodeQL](../../source-code-review/static-analysis/codeql.md)

---

# Related Web Notes

[Web Application Security](../../web/index.md)

[Web Testing Methodology](../../web/methodology.md)

[Web Security Checklist](../../web/checklist.md)

[Server Side Request Forgery](../../web/ssrf.md)

[XML External Entity Injection](../../web/xxe.md)

[Server-Side Template Injection](../../web/ssti.md)

[API Security](../../web/api-security.md)

---

# Related Purple Team Notes

[Purple Teaming](../../purple-teaming/index.md)

[Detection Engineering](../../purple-teaming/detection-engineering.md)

[Continuous Validation](../../purple-teaming/continuous-validation.md)

---

# External References

## Interactsh

[Interactsh - GitHub](https://github.com/projectdiscovery/interactsh){ target="_blank" rel="noopener noreferrer" }

[Interactsh Documentation](https://docs.projectdiscovery.io/tools/interactsh/overview){ target="_blank" rel="noopener noreferrer" }

## ProjectDiscovery

[ProjectDiscovery Documentation](https://docs.projectdiscovery.io/){ target="_blank" rel="noopener noreferrer" }

## OOB Security Testing

[PortSwigger - Blind SSRF](https://portswigger.net/web-security/ssrf/blind){ target="_blank" rel="noopener noreferrer" }

[PortSwigger - Blind XXE](https://portswigger.net/web-security/xxe/blind){ target="_blank" rel="noopener noreferrer" }

[OWASP - Server Side Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

## Practical References

[HackTricks - SSRF](https://book.hacktricks.wiki/en/pentesting-web/ssrf-server-side-request-forgery/index.html){ target="_blank" rel="noopener noreferrer" }

[PortSwigger Web Security Academy](https://portswigger.net/web-security){ target="_blank" rel="noopener noreferrer" }

---

# Final Testing Model

Do not use Interactsh like this:

```text
Insert Callback URL
      |
      v
Receive DNS Hit
      |
      v
Report Critical SSRF
```

Use it like this:

```text
Understand Application Feature
      |
      v
Establish Baseline Behavior
      |
      v
Create Unique OOB Identifier
      |
      v
Modify One Controlled Input
      |
      v
Send Request
      |
      v
Record Exact Timestamp
      |
      v
Observe DNS / HTTP Interaction
      |
      v
Correlate Unique Identifier
      |
      v
Rule Out Browser / Scanner / Proxy Effects
      |
      v
Identify Server-Side Component
      |
      v
Determine Actual Destination Control
      |
      v
Assess Reachability and Security Boundary
      |
      v
Reproduce Manually
      |
      v
Capture Evidence
      |
      v
Report the Underlying Behavior
```

Interactsh is most valuable when an application performs security-relevant server-side activity that cannot be observed directly in the normal response.

The callback proves an interaction occurred.

The tester still needs to establish who caused it, why it occurred, what control the user has over it, and whether that behavior crosses a meaningful security boundary.
