---
title: AI Security Checklist
description: Practical checklist for assessing LLM applications, RAG systems, agents, tools, MCP integrations and AI supply chains.
---

# AI Security Checklist

Use this checklist as a structured companion to the AI security methodology.

## Architecture

- [ ] Identify models and providers.
- [ ] Identify user roles.
- [ ] Identify trust boundaries.
- [ ] Identify external data sources.
- [ ] Identify retrieval systems.
- [ ] Identify tools and APIs.
- [ ] Identify agents.
- [ ] Identify MCP servers.
- [ ] Identify sensitive data.
- [ ] Identify privileged actions.

## Prompt and Instruction Security

- [ ] Test direct prompt injection.
- [ ] Test indirect prompt injection.
- [ ] Identify instruction/data confusion.
- [ ] Determine whether untrusted content can influence decisions.
- [ ] Determine whether untrusted content can influence tool calls.

## Data Security

- [ ] Verify user-level data access.
- [ ] Verify tenant isolation.
- [ ] Test retrieval ACLs.
- [ ] Check for sensitive prompt content.
- [ ] Check tool responses for excessive data.
- [ ] Review logging and memory behaviour.

## RAG

- [ ] Identify ingestion sources.
- [ ] Test retrieval boundaries.
- [ ] Test metadata filters.
- [ ] Test knowledge-base poisoning.
- [ ] Verify source provenance.
- [ ] Verify deleted content is removed from retrieval where required.

## Agents

- [ ] Inventory agent capabilities.
- [ ] Inventory tools.
- [ ] Identify effective tool identities.
- [ ] Test tool parameter restrictions.
- [ ] Test backend authorisation.
- [ ] Test confirmation boundaries.
- [ ] Review autonomous loops.
- [ ] Review agent-to-agent trust.

## MCP

- [ ] Inventory MCP servers.
- [ ] Verify server provenance.
- [ ] Review authentication.
- [ ] Review exposed tools.
- [ ] Review exposed resources.
- [ ] Review server permissions.
- [ ] Test tool trust boundaries.
- [ ] Protect MCP configuration.

## Output Handling

- [ ] Identify downstream consumers.
- [ ] Verify context-specific encoding.
- [ ] Verify structured schemas.
- [ ] Verify parameterised APIs and queries.
- [ ] Review code or command execution boundaries.
- [ ] Review file and path handling.

## Supply Chain

- [ ] Inventory models and adapters.
- [ ] Record sources and versions.
- [ ] Verify artefact integrity.
- [ ] Review custom model code.
- [ ] Review dependencies.
- [ ] Review registries.
- [ ] Review build and deployment pipelines.

## Evidence

- [ ] Record exact input.
- [ ] Record user role.
- [ ] Record relevant model/version.
- [ ] Record retrieved content.
- [ ] Record tool calls.
- [ ] Record resulting state changes.
- [ ] Record security boundary crossed.
- [ ] Repeat important probabilistic tests.

## Reporting

- [ ] Separate unexpected behaviour from security impact.
- [ ] Identify root cause.
- [ ] Describe preconditions.
- [ ] Describe affected privileges.
- [ ] Provide reproducible evidence.
- [ ] Recommend deterministic security controls.
- [ ] Retest remediation.

## Related Pages

[AI Security Methodology](../methodology.md)

[AI Red Teaming](ai-red-teaming.md)

[RAG Security](../rag/index.md)

[Agent Security](../agents/index.md)

[MCP Security](../mcp/index.md)
