---
title: Tool Abuse
description: Assessing whether AI-controlled tools can be invoked with unsafe parameters, excessive permissions or insufficient authorisation.
---

# Tool Abuse

Tool-enabled AI systems can interact with APIs, databases, files, browsers, code interpreters and other services.

Security should not depend on the model choosing to use these tools safely.

## Tool Boundary

```text
Model
  |
  v
Tool Request
  |
  v
Parameter Validation
  |
  v
Authorisation
  |
  v
Tool
  |
  v
External System
```

## Inventory

For each tool record:

```text
Tool:
Purpose:
Identity:
Permissions:
Allowed Parameters:
Sensitive Actions:
Confirmation Required:
Logging:
```

## Assessment Questions

- Can the model invoke unnecessary tools?
- Can tool parameters reference unauthorised resources?
- Is authorisation checked by the backend?
- Does the tool use a shared privileged identity?
- Can one tool's output influence another tool?
- Are sensitive operations confirmed?
- Are tool responses broader than required?

## Controlled Validation

Start with harmless test resources.

Verify:

```text
Allowed Action       -> Allowed
Unauthorised Action  -> Blocked
Sensitive Action     -> Confirmation / Policy
```

## Common Root Causes

- excessive tool permissions;
- missing backend authorisation;
- unconstrained parameters;
- shared credentials;
- over-broad API responses;
- automatic execution of model decisions.

## Mitigation

- minimise tools;
- use least-privilege identities;
- constrain schemas;
- validate resource ownership;
- enforce authorisation outside the model;
- require confirmation for sensitive actions;
- log requests and results;
- separate read and write capabilities.

## Related Pages

[Agent Security](index.md)

[Excessive Agency](../excessive-agency.md)

[Improper Output Handling](../improper-output-handling.md)
