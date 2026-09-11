# Secrets Exposure

Secrets exposure occurs when credentials, tokens, private keys, signing material, connection strings, or other security-sensitive values are disclosed to an unauthorised party or placed where an unintended party can retrieve them.

!!! warning "Authorised assessment"
	Test only systems, repositories, storage locations, and accounts included in the engagement scope. Do not use a discovered secret against production or a third party merely to prove that it works. Redact secrets in notes and reports, preserve the original value only in an approved secure evidence store, and follow the incident process when a live credential is encountered.

The assessment model is:

```text
Observation
	-> Candidate secret
	-> Controlled validation
	-> Minimum necessary evidence
	-> Security conclusion
```

A scanner match, a string that looks like a key, or a public file containing a token is a candidate, not automatically a finding. Establish what the value is, who could obtain it, whether it is active, what it authorises, and whether the exposure is in scope.

## Discovery Sources

Review both the application and the places that support its delivery:

- HTML, JavaScript bundles, source maps, mobile configuration, and public API documentation
- HTTP responses, error pages, debug output, logs, cookies, local storage, and downloaded files
- Repository history, branches, tags, pull requests, build artifacts, package manifests, and CI logs
- Environment files, deployment manifests, container images, IaC, backups, archives, and shared drives
- Cloud secret stores, object storage, registries, monitoring systems, ticket attachments, and documentation
- Server configuration, application configuration, database connection strings, and integration settings

Use targeted searches rather than only generic keyword searches. Search for provider-specific prefixes, private-key markers, JWT-like values, connection-string schemes, and references to environment variables. Tools such as secret scanners can accelerate discovery, but their output requires manual classification and validation.

Related workflows:

- [Attack Surface Analysis](attack-surface-analysis.md)
- [Third-Party JavaScript](third-party-javascript.md)
- [Information Disclosure](information-disclosure.md)
- [Burp Suite Testing Workflows](burp-suite/workflows.md)
- [Burp Suite Extensions](burp-suite/extensions.md)
- [Secret-scanning source review](../source-code-review/secrets-and-configuration.md)

## Secret Types and Classification

Classify a candidate by both its function and its exposure:

| Type | Examples | Questions to answer |
|---|---|---|
| Authentication | Password, API key, session token, refresh token | Which identity does it represent? |
| Authorisation | Cloud access key, service token, deploy token | Which actions and scopes are allowed? |
| Cryptographic | Private key, signing key, encryption key | Can it forge, decrypt, or impersonate? |
| Integration | Webhook secret, SMTP credential, database string | Which external system or data does it reach? |
| Recovery material | Backup code, reset token, recovery link | Is it single-use, time-limited, or already consumed? |
| Internal configuration | Debug key, test credential, feature flag secret | Is it security-sensitive in this deployment? |

Record classification, location, intended owner, apparent scope, exposure duration, and whether the value is unique to the environment. A public identifier, a salted hash, and a bearer token must not be reported as equivalent.

## Candidate Triage

For every candidate, record:

```text
Location and access path
Value type and owning system
Environment: development, test, staging, or production
Likely principal and permissions
First and last known exposure
Rotation or expiry metadata
Whether the value is duplicated elsewhere
```

Common false positives include example values, test fixtures, documentation placeholders, public identifiers, revoked values, and encrypted material without an available key. A value that matches a regular expression is only an observation until these questions are answered.

## Controlled Validation

Prefer non-authenticating checks first:

1. Compare the candidate with approved documentation, configuration, and ownership records.
2. Check metadata such as expiry, revocation, last-used time, scope, and environment.
3. Ask the system owner or use an approved read-only introspection endpoint to confirm status.
4. If active validation is explicitly authorised, use the least privileged, least destructive request possible.
5. Use a dedicated test identity or harmless read-only operation where available.
6. Stop when the security conclusion is established; do not enumerate unrelated resources.

Distinguish these outcomes:

| Result | Establishes | Does not establish |
|---|---|---|
| Secret-shaped string found | Possible exposure | That it is valid or privileged |
| Authentication succeeds | The value is accepted for an identity | Broad resource access or administrative rights |
| Read-only identity metadata returned | Identity and some scope | Write, delete, or code-execution capability |
| Expired or revoked value rejected | The value is not currently usable | That historical exposure had no impact |
| Owner confirms rotation | Current use may be prevented | That copies, logs, forks, or caches are gone |

Never place a discovered bearer token in a third-party scanner, public URL, issue, or chat transcript. Redact it before using screenshots or HTTP examples.

## Active, Expired, and Revoked Secrets

An inactive secret can still represent a security issue when it was exposed while active, remains in backups or history, or indicates a broader secret-management failure. Establish the timeline where possible:

```text
Exposed -> Active during exposure? -> Used? -> Revoked/expired -> Copies removed? -> Retested
```

Do not infer inactivity solely from a failed request. Failure may indicate a wrong endpoint, missing scope, network restriction, malformed request, clock skew, or an already-invalidated session. Capture the response category without retaining the secret value and ask the owner to verify lifecycle state through an authoritative control plane.

## Evidence and Impact

Evidence should prove exposure and consequence without unnecessarily reproducing the credential:

- File, URL, response, repository commit, artifact, or log location
- Redacted excerpt showing the secret type and surrounding context
- Identity, scope, environment, and lifecycle status
- Timestamp and account used for any approved validation
- Request and response metadata with values and personal data redacted
- Owner confirmation, revocation record, or control-plane result

Explain impact as a chain:

```text
Observed secret
	-> Unauthorised party can obtain it
	-> Secret is accepted by a scoped service
	-> Permitted action or data access
	-> Security boundary crossed
```

Do not claim account takeover, tenant compromise, data exposure, or code execution unless the evidence supports that conclusion. Authentication success is not equivalent to authorisation or execution.

## Remediation and Retesting

Immediate actions may include revocation, rotation, session invalidation, certificate replacement, removal from public locations, and review of access logs. Longer-term controls include secret managers, short-lived scoped credentials, environment separation, pre-commit and CI scanning, protected logs, least privilege, and prevention of secrets in client-delivered assets.

Retest the complete exposure path:

1. Confirm the old value is rejected or no longer grants the previously demonstrated capability.
2. Confirm the replacement is scoped and stored in the intended secret-management system.
3. Remove copies from repositories, artifacts, caches, logs, and backups according to retention policy.
4. Re-run discovery searches and inspect the deployment actually served to users.
5. Record residual historical risk separately from current exploitability.

## References

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [OWASP Credential Stuffing Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [GitHub Secret Scanning documentation](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning){ target="_blank" rel="noopener noreferrer" }
- [NIST SP 800-57 Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final){ target="_blank" rel="noopener noreferrer" }

## Related Notes

- [Web Application Testing Methodology](methodology.md)
- [Information Disclosure](information-disclosure.md)
- [Authentication](authentication.md)
- [Session Management](session-management.md)
