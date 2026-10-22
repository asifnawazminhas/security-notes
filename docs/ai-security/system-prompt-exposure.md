---
title: System Prompt Exposure
description: Assessing exposure of system instructions and determining when it creates meaningful security impact.
---

# System Prompt Exposure

A system prompt contains instructions supplied by an AI application to influence model behaviour.

Users may attempt to recover or infer these instructions.

Exposure is not automatically a vulnerability.

---

## Security Question

Ask:

> Does the exposed instruction contain information or capabilities that create a real security consequence?

```text
System Prompt Revealed
        |
        v
Sensitive Content Present?
        |
   +----+----+
   |         |
  No        Yes
   |         |
   v         v
Low/No    Validate
Impact     Impact
```

---

## Potentially Sensitive Content

Security relevance increases if the prompt exposes:

- credentials;
- API keys;
- internal-only URLs;
- confidential business data;
- private user information;
- security-sensitive workflow details;
- secrets that grant access elsewhere.

Security through obscurity should not be the primary protection for application capabilities.

---

## Testing Approach

Use controlled attempts to determine whether hidden instructions can be reproduced.

Then analyse the recovered content rather than assuming exposure alone is critical.

---

## What Not to Conclude

Do not automatically report:

```text
System Prompt Visible
        =
Authentication Bypass
```

or:

```text
System Prompt Visible
        =
Application Compromise
```

Impact must be demonstrated independently.

---

## Mitigation

- Never place credentials or durable secrets in prompts.
- Assume model instructions may become observable.
- Enforce authorisation outside the prompt.
- Minimise sensitive implementation details.
- Use proper secret-management systems.
- Restrict tool permissions independently of model instructions.

---

## Reporting

Describe:

- what was exposed;
- why the content was sensitive;
- which boundary was affected;
- whether the information enabled another action;
- whether the result was reproducible.

---

## Related Pages

[Sensitive Information Disclosure](sensitive-information-disclosure.md)

[Prompt Injection](prompt-injection.md)
