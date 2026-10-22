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

```mermaid
flowchart LR
    A[Download] --> B[Verify]
    B --> C[Review]
    C --> D[Test]
    D --> E[Deploy]
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

## Artefact Verification

Where supported, record and verify:

- immutable version or commit;
- cryptographic hash;
- publisher or repository provenance;
- signature or attestation;
- whether loading the artefact executes custom code;
- serialisation or deserialisation format;
- dependency lock state;
- promotion path from evaluation to production.

!!! warning "Model files can be executable risk"
    Treat formats, loaders and repositories according to their real behaviour. A model artefact or its loader may introduce code-execution or deserialisation risk independently of model inference.

## Practical Workflow

1. Identify the exact artefact and source.
2. Pin the version or immutable reference.
3. Verify integrity where verification data is available.
4. Review required custom code and loader behaviour.
5. Evaluate in an isolated environment.
6. Record the trust decision before production promotion.

## Related Pages

[Model Supply Chain](index.md)

[AI Security Methodology](../methodology.md)
