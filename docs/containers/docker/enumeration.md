---
title: Docker Enumeration
description: Practical Docker and container enumeration for security assessments.
---

# Docker Enumeration

Enumeration should establish whether testing is occurring on a host, inside a container or through a Docker management interface.

## Host Enumeration

```bash
docker version
docker info
docker ps -a
docker images
docker network ls
docker volume ls
```

```bash
docker inspect <container>
docker image inspect <image>
```

## Inside a Container

```bash
id
whoami
env
mount
findmnt
ps aux
cat /proc/1/cgroup
ls -l /proc/1/ns/
ls -l /proc/self/ns/
```

Review Linux capabilities:

```bash
grep Cap /proc/self/status
capsh --print 2>/dev/null
```

## Sensitive Resources

Look for host filesystem mounts, service/cloud credentials, SSH material, application secrets, Kubernetes service-account tokens and writable shared volumes.

```bash
ls -l /var/run/docker.sock 2>/dev/null
```

## Configuration Questions

Determine whether the container is privileged, which user it runs as, capabilities added/dropped, host namespaces shared, devices available, host paths mounted, root filesystem writable and security profiles applied.

!!! tip "Enumeration before exploitation"
    A container being root does not by itself prove host compromise. Record the isolation controls and identify a concrete boundary before testing an escape path.

## Related Pages

- [Docker Security](index.md)
- [Container Escape](container-escape.md)
- [Docker Socket](docker-socket.md)
