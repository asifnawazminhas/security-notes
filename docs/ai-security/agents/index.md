---
title: Agent Security
description: Security methodology for autonomous and semi-autonomous AI agents with tools, memory and external integrations.
---

# Agent Security

AI agents combine model reasoning with capabilities such as tools, memory, external data and repeated decision loops.

The attack surface therefore extends beyond prompt handling.

```text
Input
  |
  v
Agent
  |
  +--> Memory
  |
  +--> Retrieval
  |
  +--> Tools
  |
  +--> Other Agents
  |
  v
Action
```

## Security Objectives

Assess whether the agent:

- operates with least privilege;
- distinguishes trusted instructions from untrusted data;
- requires confirmation for sensitive actions;
- validates tool parameters;
- preserves user and tenant boundaries;
- limits autonomous loops;
- records security-relevant actions.

## Agent Components

Map:

- model;
- system instructions;
- memory;
- planning;
- retrieval;
- tools;
- credentials;
- external APIs;
- other agents;
- human approval points.

## High-Risk Capabilities

Risk increases when agents can:

- execute code;
- modify files;
- send messages;
- access confidential data;
- change infrastructure;
- perform administrative actions;
- invoke tools using privileged identities.

## Testing Principle

Test the complete action chain.

```text
Input
  |
  v
Decision
  |
  v
Tool Selection
  |
  v
Parameters
  |
  v
Authorisation
  |
  v
Action
```

## Related Pages

[Tool Abuse](tool-abuse.md)

[Multi-Agent Security](multi-agent-security.md)

[Excessive Agency](../excessive-agency.md)

[Indirect Prompt Injection](../indirect-prompt-injection.md)
