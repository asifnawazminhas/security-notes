---
title: Kubernetes Enumeration
description: Practical enumeration of Kubernetes context, workloads, namespaces, identities and permissions.
---

# Kubernetes Enumeration

Kubernetes enumeration should establish both **what exists** and **what the current identity is authorised to do**.

## Current Context

```bash
kubectl config current-context
kubectl config view --minify
kubectl config get-contexts
```

## Cluster and Namespace

```bash
kubectl cluster-info
kubectl get namespaces
kubectl get nodes
```

The ability to run these commands depends on RBAC.

## Workloads

```bash
kubectl get pods
kubectl get deployments
kubectl get services
```

When authorised:

```bash
kubectl get pods -A
kubectl get deployments -A
kubectl get services -A
```

## Detailed Workload Review

```bash
kubectl describe pod <pod>
kubectl get pod <pod> -o yaml
```

Review image, service account, security context, capabilities, volumes, hostPath, hostPID, hostNetwork, privileged containers, environment variables and secret references.

## Identity and Permissions

```bash
kubectl auth can-i --list
kubectl auth can-i get secrets
kubectl auth can-i create pods
kubectl auth can-i create rolebindings
```

When authorised to test another identity:

```bash
kubectl auth can-i get pods --as=<identity>
```

## Service Accounts and RBAC

```bash
kubectl get serviceaccounts
kubectl get roles
kubectl get rolebindings
kubectl get clusterroles
kubectl get clusterrolebindings
```

## Secrets

List metadata only when authorised:

```bash
kubectl get secrets
```

Do not extract secret values unless required and explicitly authorised.

!!! tip "Permissions matter more than visibility"
    A limited resource view can still represent a high-impact identity if it can create workloads, bind roles, access secrets or modify security-sensitive resources.

## Related Pages

- [Kubernetes Security](index.md)
- [RBAC](rbac.md)
- [Service Accounts](service-accounts.md)
- [Pod Security](pod-security.md)
