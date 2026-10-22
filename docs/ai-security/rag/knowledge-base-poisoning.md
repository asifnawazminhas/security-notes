---
title: Knowledge Base Poisoning
description: Assessing whether attacker-controlled content can poison AI knowledge sources and influence RAG responses or actions.
---

# Knowledge Base Poisoning

Knowledge base poisoning occurs when attacker-controlled or insufficiently trusted content enters a source used by an AI retrieval system.

The content may influence later responses even when the attacker is no longer interacting with the application.

## Attack Path

```text
Attacker-Controlled Content
          |
          v
Knowledge Source
          |
          v
Ingestion Pipeline
          |
          v
Index / Vector Database
          |
          v
Victim Query
          |
          v
Retrieved Poisoned Content
          |
          v
Model Behaviour
```

## Potential Sources

- shared documents;
- knowledge bases;
- tickets;
- wikis;
- websites;
- repositories;
- emails;
- uploaded files;
- database records.

## Assessment Questions

- Who can add content?
- Who can modify existing content?
- Is ingestion automatic?
- Is source trust recorded?
- Are documents reviewed before indexing?
- Can untrusted text contain instructions?
- Can poisoned content influence tool-enabled workflows?
- Can removed content remain in an index?

## Controlled Validation

Insert a harmless marker into an authorised test source:

```text
RAG_POISON_TEST_6042
```

Determine whether it is ingested, retrieved and subsequently influences the model.

Escalate only as required to demonstrate the affected security boundary.

## Impact

Impact increases when poisoned content can influence:

- security-sensitive decisions;
- privileged users;
- automated agents;
- tool invocation;
- external communication;
- administrative workflows.

## Mitigation

- classify source trust;
- restrict ingestion permissions;
- validate ingestion sources;
- separate instructions from retrieved content;
- retain provenance;
- require approval for high-risk knowledge sources;
- monitor index changes;
- support removal and re-indexing.

## Related Pages

[RAG Security](index.md)

[Retrieval Manipulation](retrieval-manipulation.md)

[Indirect Prompt Injection](../indirect-prompt-injection.md)
