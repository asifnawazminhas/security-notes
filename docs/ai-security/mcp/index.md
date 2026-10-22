---
title: MCP Security
description: Security methodology for Model Context Protocol environments, servers, tools, resources and trust boundaries.
---

# MCP Security

The Model Context Protocol (MCP) provides a structured way for AI applications to interact with external tools, resources and services.

From a security perspective, MCP expands the model's reachable attack surface.

## Architecture

```text
AI Application
      |
      v
MCP Client
      |
      v
MCP Server
      |
   +--+--+
   |     |
   v     v
 Tools Resources
   |
   v
External Systems
```

## Assessment Objectives

Identify:

- MCP servers;
- exposed tools;
- resources;
- prompts;
- authentication;
- credentials;
- permissions;
- transport security;
- server trust;
- tool trust.

## Security Questions

- Who can configure MCP servers?
- How is a server authenticated?
- What privileges does each server possess?
- Can untrusted content influence tool selection?
- Can tools access resources outside their intended scope?
- Are tool parameters validated?
- Can a malicious server return hostile instructions or data?

## Principle

Treat MCP servers and their outputs according to their actual trust level.

```text
Connected
   !=
Trusted
```

## Related Pages

[MCP Servers](mcp-servers.md)

[Tool Trust](tool-trust.md)

[Tool Abuse](../agents/tool-abuse.md)

[Excessive Agency](../excessive-agency.md)
