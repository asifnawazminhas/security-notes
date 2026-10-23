---
title: Container Escape
description: Methodology for assessing whether a compromised container can cross the isolation boundary to the host.
---

# Container Escape

A container escape crosses the intended isolation boundary between a workload and its host or node. Root inside a container is not automatically root on the host.

!!! important "Prove the boundary"
    Report a container escape only when the workload can access or control host resources beyond the intended container boundary.

## Common Risk Conditions

Review privileged containers, dangerous Linux capabilities, host filesystem mounts, runtime sockets, host PID/network namespaces, device mounts and weak kernel/runtime isolation.

## Privileged Containers

From the Docker host:

```bash
docker inspect <container>
```

Inside a container:

```bash
grep Cap /proc/self/status
mount
ls -l /dev
```

## Capabilities

Capabilities that deserve additional review include `CAP_SYS_ADMIN`, `CAP_SYS_PTRACE`, `CAP_SYS_MODULE`, `CAP_DAC_READ_SEARCH`, `CAP_DAC_OVERRIDE` and `CAP_NET_ADMIN`.

The actual impact depends on kernel, runtime, namespaces and other controls.

## Host Mounts

Determine the source path, destination, read/write mode, sensitivity and effective container identity.

## Validation

Prefer non-destructive proof such as reading an authorised host test marker through an unintended mount, demonstrating access to a runtime control interface or showing unintended host-process visibility.

## Root Cause

Separate the escape mechanism from the initial application compromise. Identify whether the root cause is runtime configuration, excessive privilege, dangerous mount, namespace sharing, exposed runtime control or a vulnerable kernel/runtime.

## Mitigation

- avoid privileged containers;
- drop unnecessary capabilities;
- avoid sensitive host mounts;
- protect runtime sockets;
- use non-root users where practical;
- enable seccomp and mandatory access controls;
- patch the host kernel and runtime.

## Related Pages

- [Docker Enumeration](enumeration.md)
- [Docker Socket](docker-socket.md)
- [Linux Capabilities](../../linux/capabilities.md)
- [Linux Privilege Escalation](../../linux/privilege-escalation.md)
