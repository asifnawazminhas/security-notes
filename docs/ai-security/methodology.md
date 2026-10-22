---
title: AI Security Methodology
description: Structured methodology for assessing LLM applications, agents, retrieval systems and AI-enabled workflows.
---

# AI Security Methodology

AI security testing should begin with architecture and trust boundaries rather than prompt payloads.

---

## Assessment Flow

```text
Scope
  |
  v
Architecture
  |
  v
Trust Boundaries
  |
  v
Inputs and Data Sources
  |
  v
Model Capabilities
  |
  v
Tools and Actions
  |
  v
Security Hypotheses
  |
  v
Controlled Validation
  |
  v
Evidence
  |
  v
Impact
```

---

## 1. Establish Scope

Identify:

- application components;
- model providers;
- model endpoints;
- user roles;
- connected data sources;
- retrieval systems;
- plugins;
- tools;
- agents;
- APIs;
- external content;
- administrative functions.

Confirm which systems and integrations are authorised for testing.

---

## 2. Map the Architecture

Document the path from user input to application action.

```text
User
 |
 v
Application
 |
 +--> System Instructions
 |
 +--> LLM
 |
 +--> Retrieval
 |
 +--> Memory
 |
 +--> Tools / APIs
 |
 +--> External Content
 |
 v
Output / Action
```

---

## 3. Identify Trust Boundaries

Important boundaries include:

- user to model;
- retrieved document to model;
- web content to agent;
- model to tool;
- tool to backend;
- model output to browser;
- model output to database;
- model output to interpreter;
- tenant to tenant;
- low-privilege user to privileged workflow.

---

## 4. Enumerate Inputs

Identify where instructions or data can enter the system:

- chat input;
- uploaded documents;
- URLs;
- emails;
- retrieved knowledge;
- API responses;
- tool output;
- memory;
- database content;
- hidden metadata.

---

## 5. Enumerate Capabilities

Determine what the AI component can actually do.

Examples:

- answer questions;
- retrieve documents;
- browse;
- send messages;
- modify records;
- execute code;
- call APIs;
- create files;
- access secrets;
- perform actions on behalf of users.

Capability determines potential impact.

---

## 6. Build Security Hypotheses

Example:

```text
Untrusted Document
      |
      v
Model Follows Embedded Instruction
      |
      v
Privileged Tool Invoked
```

Another example:

```text
Model Output
      |
      v
Rendered Without Safe Handling
      |
      v
Downstream Injection
```

---

## 7. Validate Safely

Use benign markers and controlled actions first.

For example:

```text
AI_SECURITY_TEST_2026
```

Prefer synthetic secrets and test records over real sensitive information.

Increase test depth only when required to establish the security boundary.

---

## 8. Separate Behaviour from Impact

A model following an unexpected instruction is behaviour.

A security finding requires evidence that the behaviour affects:

- confidentiality;
- integrity;
- availability;
- authorisation;
- tenant isolation;
- privileged actions;
- trusted downstream systems.

---

## 9. Record Reproducibility

Record:

```text
Application:
Model:
Date:
User Role:
Input:
Context:
Retrieved Content:
Tools Available:
Observed Behaviour:
Downstream Action:
Security Boundary:
Reproduction Rate:
Evidence:
```

LLM behaviour may be probabilistic.

Repeat important tests where appropriate.

---

## 10. Determine Root Cause

Ask:

```text
Why Was This Possible?
        |
        +--> Excessive Model Privilege?
        |
        +--> Missing Backend Authorisation?
        |
        +--> Untrusted Retrieval?
        |
        +--> Unsafe Output Handling?
        |
        +--> Excessive Tool Access?
        |
        +--> Cross-Tenant Data Access?
```

Avoid attributing every AI security problem simply to the model.

---

## 11. Report the Security Condition

Avoid:

> The AI was jailbroken.

Prefer:

> Untrusted document content was interpreted as instructions and caused the application to invoke an authorised tool outside the intended workflow.

Describe the actual affected security boundary.

---

## Related Pages

[Prompt Injection](prompt-injection.md)

[Indirect Prompt Injection](indirect-prompt-injection.md)

[Sensitive Information Disclosure](sensitive-information-disclosure.md)

[Improper Output Handling](improper-output-handling.md)

[Excessive Agency](excessive-agency.md)
