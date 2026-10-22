---
title: Retrieval Manipulation
description: Testing whether attacker-controlled queries, metadata or content can manipulate RAG retrieval behaviour.
---

# Retrieval Manipulation

Retrieval manipulation occurs when an attacker can influence which information a RAG system selects and supplies to the model.

The weakness may exist in the query transformation, metadata filters, ranking process or underlying data permissions.

## Data Flow

```text
User Query
    |
    v
Query Transformation
    |
    v
Search / Vector Retrieval
    |
    v
Filtering and Ranking
    |
    v
Retrieved Context
```

## Assessment Areas

Review:

- query rewriting;
- semantic search;
- keyword search;
- metadata filters;
- tenant filters;
- ranking;
- reranking;
- document permissions;
- result limits.

## Security Questions

Determine whether a user can:

- influence retrieval outside the intended scope;
- bypass metadata restrictions;
- retrieve hidden documents;
- retrieve documents belonging to another user;
- retrieve another tenant's information;
- cause irrelevant attacker-controlled content to outrank trusted content.

## Controlled Validation

Use synthetic documents with unique markers.

```text
TENANT_A_TEST_7319
TENANT_B_TEST_2841
```

Verify that each identity retrieves only the content it is authorised to access.

## Root Cause

Do not assume the LLM is responsible.

Potential causes include:

```text
Missing ACL Filter
      |
      +--> Incorrect Metadata
      |
      +--> Weak Tenant Isolation
      |
      +--> Retrieval Configuration
      |
      +--> Application Logic
```

## Mitigation

- enforce ACLs during retrieval;
- enforce tenant boundaries server-side;
- validate metadata filters;
- minimise retrieval scope;
- retain source provenance;
- test retrieval independently of model output;
- monitor anomalous retrieval patterns.

## Related Pages

[RAG Security](index.md)

[Knowledge Base Poisoning](knowledge-base-poisoning.md)

[Sensitive Information Disclosure](../sensitive-information-disclosure.md)
