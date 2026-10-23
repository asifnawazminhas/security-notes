---
title: Image Security
description: Security assessment of container images, registries, build processes, secrets and software supply-chain trust.
---

# Image Security

Container images are part of the software supply chain. Assess what enters an image, where it comes from and whether its contents can be trusted.

## Image Lifecycle

```mermaid
flowchart LR
    A[Source] --> B[Build]
    B --> C[Image]
    C --> D[Registry]
    D --> E[Deployment]
    E --> F[Runtime]
```

## Assessment Areas

Review base image source, immutable digests, package versions, build dependencies, Dockerfile instructions, embedded secrets, unnecessary tools, image user, registry permissions, provenance/signatures and CI/CD.

## Image Inspection

```bash
docker image inspect <image>
docker history <image>
```

## Secrets

Do not assume deleting a file in a later Dockerfile layer removes it from earlier layers.

Review for API keys, passwords, tokens, private keys, registry/cloud credentials, `.env` files and build-time secrets.

See [Secrets Exposure](../../web/secrets-exposure.md).

## Tags and Digests

Mutable tags such as `latest` make it harder to establish exactly which artefact was deployed. Prefer immutable references where appropriate and record image digests.

## Runtime Configuration

A secure image can still be deployed with privileged mode, dangerous capabilities, host mounts, excessive secrets or a root user.

## Mitigation

- use approved base images;
- minimise image contents;
- pin and verify dependencies;
- use multi-stage builds;
- keep secrets out of image layers;
- use non-root users where practical;
- scan images and dependencies;
- restrict registry write access;
- retain provenance.

## Related Pages

- [Docker Security](index.md)
- [Model and Dependency Trust](../../ai-security/model-supply-chain/model-and-dependency-trust.md)
- [Dependency Security](../../web/dependency-security.md)
