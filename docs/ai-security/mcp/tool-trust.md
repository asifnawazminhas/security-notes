---
title: Tool Trust
description: Evaluating trust, provenance and security boundaries for tools exposed to AI systems through MCP or other integrations.
---

# Tool Trust

Tools should be evaluated as security-sensitive integrations rather than simple model extensions.

A tool may access systems that the model itself cannot directly reach.

## Trust Model

```text
Model
  |
  v
Tool Description
  |
  v
Tool Selection
  |
  v
Tool Implementation
  |
  v
External Resource
```

## Assessment Questions

- Who developed the tool?
- Who controls its configuration?
- What identity does it use?
- What resources can it access?
- Can its description or metadata be modified?
- Are inputs validated?
- Are outputs trusted by the model?
- Can it perform write operations?
- Is provenance retained?

## Tool Metadata

Tool descriptions influence how an AI system selects and uses capabilities.

Treat descriptions and schemas as security-relevant configuration.

## Output Trust

Tool output may itself contain untrusted data.

```text
External System
      |
      v
Tool Output
      |
      v
Model Context
```

Do not automatically treat tool output as trusted instructions.

## Mitigation

- review tool provenance;
- protect tool definitions;
- minimise privileges;
- constrain inputs;
- validate outputs where appropriate;
- separate read and write operations;
- enforce backend authorisation;
- log sensitive actions.

## Related Pages

[MCP Security](index.md)

[MCP Servers](mcp-servers.md)

[Tool Abuse](../agents/tool-abuse.md)
