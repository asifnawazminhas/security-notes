---
title: RAG Security
description: Security testing of retrieval-augmented generation systems, retrieval pipelines and external knowledge sources.
---

# RAG Security

Retrieval-augmented generation (RAG) extends an AI application with information retrieved from external knowledge sources.

This introduces security boundaries beyond the model itself.

```mermaid
flowchart LR
    A[User Query] --> B[Retriever]
    B --> C[Knowledge Source]
    C --> D[Retrieved Context]
    D --> E[LLM]
    E --> F[Response]
```

## Security Objectives

Assess whether:

- retrieval respects user and tenant permissions;
- untrusted content can influence model behaviour;
- sensitive documents can be retrieved by unauthorised users;
- knowledge sources can be poisoned;
- retrieved content retains provenance;
- model output safely represents retrieved information.

## Attack Surface

Review:

- document ingestion;
- chunking;
- embeddings;
- vector databases;
- metadata;
- retrieval filters;
- access-control filters;
- reranking;
- prompt construction;
- citations and provenance;
- external knowledge connectors.

## Core Trust Boundary

Retrieved content should normally be treated as **data**, not trusted instructions.

```text
External Content
      |
      v
Retrieval Pipeline
      |
      v
Untrusted Context
      |
      v
Model
```

## Testing Questions

- Can one user retrieve another user's documents?
- Can one tenant retrieve another tenant's content?
- Can attacker-controlled documents enter the knowledge base?
- Can retrieved text alter model instructions?
- Are metadata filters enforced server-side?
- Can sensitive information be inferred through repeated retrieval?
- Can stale or deleted content remain retrievable?

## Evidence

Record:

- querying identity;
- query;
- expected access;
- retrieved document;
- document owner or tenant;
- retrieval metadata;
- model response;
- resulting security impact.

## Related Pages

[Retrieval Manipulation](retrieval-manipulation.md)

[Knowledge Base Poisoning](knowledge-base-poisoning.md)

[Indirect Prompt Injection](../indirect-prompt-injection.md)

[Sensitive Information Disclosure](../sensitive-information-disclosure.md)
