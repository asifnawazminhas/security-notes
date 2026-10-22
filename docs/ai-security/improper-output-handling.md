---
title: Improper Output Handling
description: Testing whether AI-generated output is safely handled before reaching browsers, interpreters, databases, APIs or other downstream systems.
---

# Improper Output Handling

AI-generated output should be treated as untrusted data.

A model may produce content that becomes dangerous when passed directly into another interpreter or security-sensitive component.

---

## Data Flow

```text
User / External Data
        |
        v
       LLM
        |
        v
Generated Output
        |
        v
Downstream Consumer
        |
        v
Security-Sensitive Interpretation
```

The downstream consumer may include:

- HTML renderer;
- shell;
- SQL query;
- template engine;
- file path;
- API;
- code interpreter;
- automation workflow.

---

## Assessment Questions

Determine:

- where model output is sent;
- whether output is encoded;
- whether it is validated;
- whether structured schemas are enforced;
- whether dangerous operations are parameterised;
- whether the downstream system has unnecessary privileges.

---

## Web Rendering

If model output is displayed in a browser, verify that untrusted content is handled according to its context.

```text
Model Output
    |
    v
HTML Rendering
    |
    v
Context-Specific Encoding
```

Do not rely on the model to promise that it will generate safe HTML.

---

## Tool and API Calls

Prefer constrained structured parameters over free-form model-generated commands.

Security-sensitive decisions should be validated by deterministic application logic.

---

## Validation

Use benign markers to establish whether output reaches a downstream interpreter.

Then test the specific boundary in a controlled manner.

The goal is to prove the unsafe data flow, not to cause unnecessary impact.

---

## Mitigation

- treat model output as untrusted;
- use context-specific output encoding;
- use parameterised APIs and queries;
- enforce schemas;
- validate tool arguments;
- sandbox interpreters;
- minimise downstream privileges;
- require confirmation for high-impact actions.

---

## Related Pages

[Prompt Injection](prompt-injection.md)

[Excessive Agency](excessive-agency.md)

[AI Security Methodology](methodology.md)
