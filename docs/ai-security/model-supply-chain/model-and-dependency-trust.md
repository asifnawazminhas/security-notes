---
title: Model and Dependency Trust
description: Assessing provenance, integrity and trust decisions for models and dependencies in AI systems.
---

# Model and Dependency Trust

AI components should not be trusted solely because they are available from a public repository or popular ecosystem.

Trust should be based on provenance, integrity and controlled deployment.

## Trust Questions

For each model or dependency determine:

- source;
- publisher;
- version;
- integrity;
- update mechanism;
- licence;
- deployment owner;
- security review status.

## Model Artefacts

Potential artefacts include:

- model weights;
- adapters;
- fine-tunes;
- tokenisers;
- configuration;
- custom code;
- prompt templates.

## Dependency Risks

Consider:

- dependency confusion;
- compromised packages;
- malicious custom code;
- unexpected model updates;
- unverified community artefacts;
- vulnerable libraries;
- insecure deserialisation formats.

## Deployment Principle

```text
Download
   |
   v
Verify
   |
   v
Review
   |
   v
Test
   |
   v
Deploy
```

## Mitigation

- use approved sources;
- pin versions;
- verify hashes or signatures where available;
- isolate evaluation environments;
- review custom code;
- maintain an inventory;
- monitor upstream security advisories;
- control promotion into production.

## Related Pages

[Model Supply Chain](index.md)

[AI Security Methodology](../methodology.md)
