---
title: MCP Servers
description: Assessing the configuration, identity, permissions and attack surface of MCP servers.
---

# MCP Servers

An MCP server may expose tools and resources to an AI application.

Its effective privileges can determine the impact of an AI security weakness.

## Inventory

For every server record:

```text
Server:
Owner:
Purpose:
Transport:
Authentication:
Credentials:
Tools:
Resources:
Effective Permissions:
Data Classification:
```

## Assessment Areas

Review:

- server origin;
- configuration;
- authentication;
- transport;
- credentials;
- exposed tools;
- exposed resources;
- effective operating-system or service identity;
- update and dependency process.

## Trust Boundary

```text
AI Client
   |
   v
MCP Server
   |
   v
Tool / Resource
   |
   v
Protected System
```

Each boundary should have explicit security controls.

## Security Questions

- Can an unauthorised server be added?
- Can server configuration be modified?
- Does the server expose unnecessary tools?
- Are credentials over-privileged?
- Can resources expose sensitive data?
- Are actions independently authorised?
- Are server responses treated as trusted instructions?

## Mitigation

- allowlist trusted servers;
- use least-privilege credentials;
- minimise exposed capabilities;
- authenticate connections;
- protect configuration;
- validate tool arguments;
- monitor server changes;
- log security-sensitive calls.

## Related Pages

[MCP Security](index.md)

[Tool Trust](tool-trust.md)
