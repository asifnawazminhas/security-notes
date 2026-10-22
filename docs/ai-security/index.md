---
title: AI Security
description: Practical security methodology for LLM applications, AI agents, RAG systems, tools and AI-enabled applications.
---

# AI Security

AI security testing evaluates the security boundaries created when applications use large language models, retrieval systems, tools, agents and external data sources.

The important distinction is:

```text
Model Behaviour
      !=
Security Impact
```

A surprising model response is not automatically a vulnerability.

Testing should establish which trust boundary was crossed, what capability became available and what security impact can be reproduced.

---

## Scope

This section focuses on:

- prompt injection;
- indirect prompt injection;
- sensitive information disclosure;
- system prompt exposure;
- unsafe model output handling;
- excessive agency;
- AI agents;
- tool integrations;
- retrieval-augmented generation;
- MCP;
- AI-specific attack-surface analysis;
- validation and reporting.

---

## Core Model

```text
Untrusted Input
      |
      v
AI Component
      |
      v
Context / Retrieval / Tools
      |
      v
Model Decision
      |
      v
Application Action
      |
      v
Security Impact
```

The most important testing question is not whether the model can be persuaded to say something unusual.

Ask instead:

> Can untrusted content influence a security-sensitive decision, disclose protected information, invoke a privileged capability or cause unsafe downstream behaviour?

---

## Start Here

[AI Security Methodology](methodology.md)

[Prompt Injection](prompt-injection.md)

[Indirect Prompt Injection](indirect-prompt-injection.md)

[Sensitive Information Disclosure](sensitive-information-disclosure.md)

[System Prompt Exposure](system-prompt-exposure.md)

[Improper Output Handling](improper-output-handling.md)

[Excessive Agency](excessive-agency.md)

---

## AI Attack Surface

A modern AI application may include considerably more than a model.

```text
                    User
                      |
                      v
                 Application
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Prompt       Memory       Files
          |           |           |
          +-----------+-----------+
                      |
                      v
                     LLM
                      |
       +--------------+--------------+
       |              |              |
       v              v              v
      RAG           Tools          Agents
       |              |              |
       v              v              v
 Vector DB          APIs        Other Agents
       |              |              |
       +--------------+--------------+
                      |
                      v
              External Systems
```

Each connection creates a potential trust boundary.

---

## Testing Principle

Do not treat:

```text
Jailbreak
   =
Vulnerability
```

Instead establish:

```text
Input
  +
Trust Boundary
  +
Security-Sensitive Behaviour
  +
Reproducible Impact
  =
Supported Finding
```

---

## AI Security vs AI-Assisted Security

These are separate disciplines.

### AI Security

Testing AI-enabled applications themselves.

Examples:

- prompt injection;
- RAG poisoning;
- agent security;
- tool abuse;
- excessive agency;
- sensitive data exposure.

### AI-Assisted Security

Using AI to support security testing.

Examples:

- source-code analysis;
- payload reasoning;
- log analysis;
- vulnerability research;
- reporting assistance.

The existing tooling pages remain under:

[AI-Assisted Security Tools](../tools/ai/index.md)

---

## Evidence

Useful evidence includes:

- exact input;
- conversation context;
- retrieved content;
- tool calls;
- application response;
- affected identity;
- effective permissions;
- downstream action;
- resulting state;
- reproducibility;
- relevant logs.

---

## Related Sections

[Web Application Security](../web/index.md)

[Source Code Review](../source-code-review/index.md)

[Red Teaming](../red-teaming/index.md)

[AI-Assisted Security Tools](../tools/ai/index.md)
