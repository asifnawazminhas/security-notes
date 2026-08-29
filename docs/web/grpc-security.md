# gRPC Security

gRPC is a high-performance Remote Procedure Call framework commonly used for communication between microservices, backend systems, mobile applications, and distributed services.

Unlike a traditional REST API where you might interact with endpoints such as:

```text
GET /api/users/123
POST /api/orders
DELETE /api/files/456
```

gRPC exposes **services containing callable methods**.

Conceptually:

```text
REST

Client
  |
  | GET /api/users/123
  v
HTTP API
  |
  v
JSON Response
```

gRPC instead looks more like:

```text
gRPC

Client
  |
  | UserService/GetUser
  v
gRPC Server
  |
  | Protocol Buffer message
  v
Response
```

A simplified gRPC architecture is:

```text
Client
  |
  | RPC call
  v
gRPC Service
  |
  +-- HTTP/2 transport
  |
  +-- Metadata
  |     |
  |     +-- Authentication
  |     +-- Tracing
  |     +-- Custom metadata
  |
  +-- Protocol Buffer message
  |
  v
Service Method
  |
  +-- Authentication
  +-- Authorisation
  +-- Input validation
  +-- Business logic
  |
  v
gRPC Response
  |
  +-- Protobuf message
  +-- Metadata / trailers
  +-- gRPC status
  |
  v
Client
```

!!! warning "Authorised Security Testing"
    Perform gRPC security testing only against systems you are explicitly authorised to assess. gRPC services are frequently internal production services, and unsafe testing of streaming methods, large messages, concurrency, deadlines, or resource limits can affect service availability. Use controlled accounts, controlled objects and conservative request rates.

---

# Why gRPC Matters to Pentesters

gRPC is common in:

```text
Microservices
Internal APIs
Cloud-native applications
Kubernetes environments
Mobile backends
Service-to-service communication
Distributed systems
High-performance APIs
```

A web application may look like:

```text
Browser
   |
   v
Frontend
   |
   v
REST / GraphQL Gateway
   |
   v
Internal gRPC Services
   |
   +-- UserService
   +-- PaymentService
   +-- FileService
   +-- AdminService
   +-- NotificationService
```

A vulnerability in an internal gRPC service can therefore affect the security of the entire application.

---

# gRPC Is Not Simply REST With Binary Data

A common mistake is to approach gRPC exactly like a REST API.

There are similarities:

```text
Authentication
Authorisation
Input validation
Business logic
Rate limiting
Transport security
```

but there are important architectural differences.

REST often uses:

```text
HTTP methods
URLs
JSON
HTTP status codes
```

gRPC commonly uses:

```text
Service definitions
RPC methods
Protocol Buffers
HTTP/2
gRPC metadata
gRPC status codes
Streaming
```

---

# Remote Procedure Calls

RPC stands for:

```text
Remote Procedure Call
```

The basic idea is that a client invokes a function implemented on another system.

Conceptually:

```text
Local programming:

getUser(123)
```

With RPC:

```text
Client
   |
   | GetUser(123)
   v
Remote Server
   |
   v
GetUser()
   |
   v
Response
```

The network interaction is abstracted into something resembling a normal method call.

---

# gRPC Service Definitions

gRPC services are commonly defined using Protocol Buffers.

A `.proto` file might contain:

```protobuf
syntax = "proto3";

package users;

service UserService {

    rpc GetUser (
        GetUserRequest
    ) returns (
        GetUserResponse
    );

}

message GetUserRequest {

    int64 id = 1;

}

message GetUserResponse {

    int64 id = 1;
    string username = 2;
    string email = 3;

}
```

This describes:

```text
Package:
users

Service:
UserService

Method:
GetUser

Request:
GetUserRequest

Response:
GetUserResponse
```

---

# RPC Method Naming

A gRPC method can conceptually be represented as:

```text
package.Service/Method
```

For example:

```text
users.UserService/GetUser
```

Another example:

```text
payments.PaymentService/CreatePayment
```

or:

```text
admin.AdminService/DeleteUser
```

This is one of the first major differences from REST.

Instead of looking only for:

```text
/api/users
/api/orders
/api/admin
```

you should also think in terms of:

```text
Services
Methods
Messages
Fields
```

---

# Protocol Buffers

Protocol Buffers, commonly called:

```text
protobuf
```

are Google's language-neutral structured data serialization mechanism and are the default Interface Definition Language and message format used by gRPC.

A protobuf message might be:

```protobuf
message User {

    int64 id = 1;

    string username = 2;

    string email = 3;

    bool admin = 4;

}
```

The numbers:

```text
1
2
3
4
```

are field numbers.

They are part of the protobuf wire format.

---

# Protobuf Is Binary on the Wire

Unlike a typical JSON REST request:

```json
{
    "id": 123,
    "username": "alice"
}
```

native gRPC commonly transmits protobuf messages in binary form.

Conceptually:

```text
Human-readable object
        |
        v
Protobuf serialization
        |
        v
Binary message
        |
        v
HTTP/2
        |
        v
gRPC server
```

This is why ordinary `curl` is generally not convenient for interacting with native gRPC services.

Tools such as:

```text
grpcurl
```

understand gRPC and protobuf.

---

# grpcurl

`grpcurl` is one of the most useful command-line tools for testing gRPC services.

Conceptually:

```text
curl
   |
   +-- HTTP APIs

grpcurl
   |
   +-- gRPC APIs
```

Official project:

```text
https://github.com/fullstorydev/grpcurl
```

---

# Installing grpcurl

Check your package manager first.

On systems with Go installed:

```bash
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest
```

Then verify:

```bash
grpcurl -help
```

If Go installs binaries into:

```text
~/go/bin
```

ensure that directory is in your `PATH`.

---

# Four Types of gRPC RPCs

Understanding the four RPC models is essential.

They are:

```text
1. Unary RPC
2. Server-streaming RPC
3. Client-streaming RPC
4. Bidirectional-streaming RPC
```

---

# Unary RPC

Unary RPC is the simplest model.

```text
One request
     |
     v
Server
     |
     v
One response
```

Conceptually:

```text
Client                    Server

  |                          |
  |------ Request ---------->|
  |                          |
  |<----- Response ----------|
  |                          |
```

Example:

```protobuf
rpc GetUser (
    GetUserRequest
) returns (
    GetUserResponse
);
```

This resembles a traditional request/response API.

---

# Server Streaming

The client sends one request and receives multiple responses.

```text
Client                    Server

  |                          |
  |------ Request ---------->|
  |                          |
  |<----- Response 1 --------|
  |<----- Response 2 --------|
  |<----- Response 3 --------|
  |<----- Response 4 --------|
  |                          |
```

Example:

```protobuf
rpc ListEvents (
    EventRequest
) returns (
    stream Event
);
```

Potential use cases include:

```text
Event feeds
Logs
Notifications
Large result sets
Monitoring
```

---

# Client Streaming

The client sends multiple messages and receives one response.

```text
Client                    Server

  |                          |
  |------ Message 1 -------->|
  |------ Message 2 -------->|
  |------ Message 3 -------->|
  |                          |
  |<----- Response ----------|
```

Example:

```protobuf
rpc Upload (
    stream UploadChunk
) returns (
    UploadResult
);
```

Potential use cases include:

```text
File uploads
Telemetry
Bulk data
Aggregations
```

---

# Bidirectional Streaming

Both sides send streams of messages.

```text
Client                    Server

  |------ Message 1 -------->|
  |<----- Message A ---------|
  |------ Message 2 -------->|
  |<----- Message B ---------|
  |------ Message 3 -------->|
  |<----- Message C ---------|
```

Example:

```protobuf
rpc Chat (
    stream ChatMessage
) returns (
    stream ChatMessage
);
```

Potential uses:

```text
Chat
Realtime events
Interactive applications
Long-lived service communication
```

---

# Why Streaming Matters for Security

Streaming introduces additional questions:

```text
Is authentication checked when stream starts?

Is authorisation checked for every relevant message?

Can permissions change while a stream remains open?

Are message counts limited?

Are message sizes limited?

Are idle streams terminated?

Are deadlines enforced?

Can a client hold large numbers of streams open?

Can the stream consume excessive memory or CPU?
```

Do not treat a long-lived stream exactly like a single REST request.

---

# HTTP/2

Native gRPC uses HTTP/2.

HTTP/2 supports:

```text
Multiplexing
Streams
Binary framing
Header compression
Long-lived connections
```

Multiple RPCs can therefore operate over the same underlying connection.

Conceptually:

```text
TCP/TLS Connection
       |
       +-- HTTP/2 Stream 1
       |       |
       |       +-- RPC A
       |
       +-- HTTP/2 Stream 3
       |       |
       |       +-- RPC B
       |
       +-- HTTP/2 Stream 5
               |
               +-- RPC C
```

---

# gRPC Content Type

Native gRPC commonly uses:

```http
Content-Type: application/grpc
```

You may therefore identify potential gRPC traffic by looking for:

```text
HTTP/2
application/grpc
grpc-status
grpc-message
```

among other gRPC-specific characteristics.

---

# gRPC-Web Is Different

Browsers historically cannot use native gRPC in exactly the same manner as normal backend gRPC clients.

gRPC-Web provides a browser-compatible protocol for communicating with gRPC services, commonly through a proxy or compatible server.

Conceptually:

```text
Browser
   |
   | gRPC-Web
   v
Proxy / Gateway
   |
   | Native gRPC
   v
Backend gRPC Service
```

Do not assume:

```text
gRPC-Web
=
native gRPC
```

They are related but distinct protocols.

---

# Identifying gRPC-Web

Potential content types include:

```text
application/grpc-web
application/grpc-web+proto
application/grpc-web-text
application/grpc-web-text+proto
```

Exact implementation behaviour can vary.

---

# gRPC-Web Security

When testing gRPC-Web consider:

```text
Browser authentication
CORS
CSRF where applicable
Gateway behaviour
Protobuf messages
Authorisation
Service exposure
Method exposure
Error disclosure
```

The browser-facing layer may introduce vulnerabilities that do not exist in the underlying native gRPC service.

---

# .proto Files

`.proto` files are extremely valuable during security assessments because they describe the API schema.

For example:

```protobuf
service AccountService {

    rpc GetAccount(
        GetAccountRequest
    ) returns (
        Account
    );

    rpc UpdateAccount(
        UpdateAccountRequest
    ) returns (
        Account
    );

    rpc DeleteAccount(
        DeleteAccountRequest
    ) returns (
        Empty
    );

}
```

This immediately reveals:

```text
Service names
Method names
Request types
Response types
Fields
Data types
Streaming behaviour
```

---

# Finding .proto Files

During an authorised assessment look for `.proto` files in:

```text
Source repositories
Mobile applications
JavaScript bundles
Developer packages
SDKs
Documentation
Docker images
Build artefacts
CI/CD artefacts
API documentation
Public repositories
```

Also search source code for:

```text
.proto
grpc
protobuf
protoc
grpc-js
grpcio
Google.Protobuf
io.grpc
```

---

# Protocol Descriptor Sets

Instead of `.proto` source files, you may encounter:

```text
protoset
```

or:

```text
FileDescriptorSet
```

data.

`grpcurl` can use descriptor sets to understand the service schema.

Example:

```bash
grpcurl \
  -protoset service.protoset \
  target.example:443 \
  list
```

---

# gRPC Server Reflection

gRPC reflection allows a client to discover service definitions at runtime.

Conceptually:

```text
Client
   |
   | What services exist?
   v
Reflection Service
   |
   v
Service descriptors
```

This can make development and debugging considerably easier.

It also makes reconnaissance easier during a security assessment.

---

# Testing Reflection

For an authorised target:

```bash
grpcurl target.example:443 list
```

If reflection is enabled, this may return services such as:

```text
grpc.reflection.v1.ServerReflection
users.UserService
payments.PaymentService
admin.AdminService
```

---

# Reflection and Plaintext

If the service intentionally uses unencrypted HTTP/2:

```bash
grpcurl \
  -plaintext \
  target.example:50051 \
  list
```

Important:

```text
-plaintext
```

means:

```text
Use plaintext HTTP/2 without TLS
```

It does **not** mean:

```text
Ignore certificate validation
```

---

# TLS Certificate Verification

For TLS endpoints, normal usage is:

```bash
grpcurl \
  target.example:443 \
  list
```

If testing an authorised development environment with a self-signed certificate, `grpcurl` supports:

```bash
grpcurl \
  -insecure \
  target.example:443 \
  list
```

!!! warning
    `-insecure` disables server certificate and hostname verification. It is useful for controlled testing but should not be treated as a secure production configuration.

---

# Reflection Is Not Automatically a Vulnerability

Do not report:

```text
gRPC reflection enabled
```

automatically as:

```text
Critical vulnerability
```

Reflection exposes information about:

```text
Services
Methods
Messages
Schemas
```

which increases attack-surface visibility.

Whether this is reportable depends on:

```text
Environment
Threat model
Exposure
Sensitivity
Production policy
Additional vulnerabilities
```

For production services, reducing unnecessary reflection exposure is generally good hardening.

---

# Enumerating Services

When reflection is available:

```bash
grpcurl \
  target.example:443 \
  list
```

Example:

```text
grpc.health.v1.Health
grpc.reflection.v1.ServerReflection
users.UserService
payments.PaymentService
```

Record all services.

---

# Enumerating Methods

To list methods in a service:

```bash
grpcurl \
  target.example:443 \
  list users.UserService
```

Possible result:

```text
users.UserService.CreateUser
users.UserService.DeleteUser
users.UserService.GetUser
users.UserService.ListUsers
users.UserService.UpdateUser
```

This creates an initial attack surface.

---

# Describing a Service

Use:

```bash
grpcurl \
  target.example:443 \
  describe users.UserService
```

This may show an equivalent protobuf definition.

---

# Describing a Method

Example:

```bash
grpcurl \
  target.example:443 \
  describe users.UserService.GetUser
```

This helps identify:

```text
Request type
Response type
Streaming direction
```

---

# Describing a Message

Example:

```bash
grpcurl \
  target.example:443 \
  describe users.GetUserRequest
```

Potential output:

```protobuf
message GetUserRequest {

    int64 id = 1;

}
```

This tells you what input the method expects.

---

# Reflection Requires Authentication Sometimes

Some services may protect reflection.

If authorised credentials are required, metadata can be supplied.

For example:

```bash
grpcurl \
  -H "Authorization: Bearer TOKEN" \
  target.example:443 \
  list
```

Do not assume reflection is globally accessible simply because authenticated users can use it.

---

# Using .proto Files Without Reflection

If reflection is disabled but you have an authorised `.proto` file:

```bash
grpcurl \
  -import-path ./proto \
  -proto users.proto \
  target.example:443 \
  list
```

Invoke a method:

```bash
grpcurl \
  -import-path ./proto \
  -proto users.proto \
  -d '{"id":123}' \
  target.example:443 \
  users.UserService/GetUser
```

---

# Basic grpcurl Invocation

Suppose:

```protobuf
message GetUserRequest {

    int64 id = 1;

}
```

Then:

```bash
grpcurl \
  -d '{"id":123}' \
  target.example:443 \
  users.UserService/GetUser
```

`grpcurl` accepts JSON input and converts it into the protobuf message expected by the service.

---

# Empty Request

If the RPC accepts an empty message:

```bash
grpcurl \
  target.example:443 \
  users.UserService/ListUsers
```

or, where required:

```bash
grpcurl \
  -d '{}' \
  target.example:443 \
  users.UserService/ListUsers
```

---

# Pretty JSON Input

For more complex requests:

```bash
grpcurl \
  -d '{
    "username": "test-user",
    "email": "test@example.com"
  }' \
  target.example:443 \
  users.UserService/CreateUser
```

---

# Reading Input From stdin

`grpcurl` supports:

```text
-d @
```

Example:

```bash
cat request.json | \
grpcurl \
  -d @ \
  target.example:443 \
  users.UserService/CreateUser
```

This is useful for repeatable testing.

---

# gRPC Metadata

Metadata is extremely important in gRPC security.

Metadata consists of key-value information associated with an RPC.

It can contain:

```text
Authentication credentials
JWTs
Tracing information
Request identifiers
Tenant identifiers
Application-specific values
```

Metadata is transported using HTTP/2 headers and trailers.

---

# Authentication Metadata

A service may use:

```text
Authorization
```

metadata.

For example:

```http
authorization: Bearer eyJ...
```

With `grpcurl`:

```bash
grpcurl \
  -H "Authorization: Bearer TOKEN" \
  -d '{"id":123}' \
  target.example:443 \
  users.UserService/GetUser
```

---

# Custom Metadata

Applications may use custom values such as:

```text
x-user-id
x-tenant-id
x-role
x-request-id
x-client-id
```

Example:

```bash
grpcurl \
  -H "x-tenant-id: 100" \
  target.example:443 \
  tenant.TenantService/GetSettings
```

Treat security-sensitive client-controlled metadata with suspicion.

---

# Metadata Trust Boundaries

A dangerous architecture might accept:

```text
x-user-id: 100
x-role: admin
x-tenant-id: 5
```

directly from an untrusted client and trust those values for authorisation.

Conceptually:

```text
Client
   |
   | x-role: admin
   v
Service
   |
   | blindly trusts metadata
   v
Admin privileges
```

Security-sensitive identity should be derived from trusted authentication context, not arbitrary user-controlled metadata.

---

# Metadata Testing Checklist

Look for:

```text
authorization
x-user-id
x-role
x-admin
x-tenant-id
x-account-id
x-client-id
x-forwarded-user
x-authenticated-user
```

Test whether modifying them affects:

```text
Identity
Role
Tenant
Authorisation
Object ownership
Business logic
```

using controlled accounts.

---

# Authentication

gRPC does not remove the need for authentication.

Authentication may use:

```text
OAuth 2.0 access tokens
JWTs
API keys
mTLS client certificates
Custom credentials
Service identities
```

A typical authenticated RPC:

```text
Client
   |
   | Authorization: Bearer TOKEN
   v
gRPC Server
   |
   v
Authentication Interceptor
   |
   +-- valid
   |
   v
RPC Handler
```

---

# Authentication Interceptors

Many gRPC implementations use interceptors or middleware to perform cross-cutting security checks.

Conceptually:

```text
RPC
 |
 v
Authentication Interceptor
 |
 v
Authorisation Interceptor
 |
 v
Logging / Rate Limiting
 |
 v
Service Method
```

A security issue may occur when:

```text
Some services use interceptor
Some services do not
```

or:

```text
Some methods are excluded accidentally
```

---

# Authentication Testing

Create a method matrix:

| Method | No Token | Valid Token | Invalid Token | Expired Token |
|---|---|---|---|---|
| GetUser | Test | Test | Test | Test |
| UpdateUser | Test | Test | Test | Test |
| DeleteUser | Test | Test | Test | Test |
| AdminList | Test | Test | Test | Test |

Look for inconsistent enforcement.

---

# Unauthenticated Request

For a safe read-only method:

```bash
grpcurl \
  -d '{"id":123}' \
  target.example:443 \
  users.UserService/GetUser
```

Compare with:

```bash
grpcurl \
  -H "Authorization: Bearer VALID_TOKEN" \
  -d '{"id":123}' \
  target.example:443 \
  users.UserService/GetUser
```

If sensitive information is returned without authentication:

```text
Potential missing authentication
```

---

# Authorisation

Authentication answers:

```text
Who are you?
```

Authorisation answers:

```text
What are you allowed to do?
```

gRPC services require both.

---

# Object-Level Authorisation

Suppose:

```protobuf
rpc GetInvoice(
    GetInvoiceRequest
) returns (
    Invoice
);

message GetInvoiceRequest {

    int64 invoice_id = 1;

}
```

Account A owns:

```text
invoice_id = 1001
```

Account B owns:

```text
invoice_id = 2001
```

Test:

```text
Account A token
+
invoice_id 1001
```

then:

```text
Account A token
+
invoice_id 2001
```

If Account A receives Account B's invoice:

```text
BOLA / IDOR
```

Refer to:

[IDOR and BOLA](idor-bola.md)

---

# grpcurl BOLA Example

Controlled Account A:

```bash
grpcurl \
  -H "Authorization: Bearer ACCOUNT_A_TOKEN" \
  -d '{"invoiceId":"1001"}' \
  target.example:443 \
  billing.InvoiceService/GetInvoice
```

Then:

```bash
grpcurl \
  -H "Authorization: Bearer ACCOUNT_A_TOKEN" \
  -d '{"invoiceId":"2001"}' \
  target.example:443 \
  billing.InvoiceService/GetInvoice
```

Use only controlled objects.

---

# Function-Level Authorisation

A normal user may discover:

```text
admin.AdminService/ListUsers
admin.AdminService/DeleteUser
admin.AdminService/ChangeRole
```

The presence of these methods is not itself a vulnerability.

Test whether the server enforces role restrictions.

Conceptually:

```text
Standard User
     |
     | ChangeRole()
     v
Authorisation Check
     |
     +---- DENY
```

If it instead reaches:

```text
Role changed
```

there may be broken function-level authorisation.

---

# Authorisation Matrix

Build a matrix:

| Method | Anonymous | User A | User B | Admin |
|---|---:|---:|---:|---:|
| GetProfile | Deny | Own | Own | Any |
| UpdateProfile | Deny | Own | Own | Any |
| GetInvoice | Deny | Own | Own | Any |
| DeleteUser | Deny | Deny | Deny | Allow |
| ChangeRole | Deny | Deny | Deny | Allow |

Then compare observed behaviour with expected behaviour.

---

# Tenant Isolation

gRPC is commonly used in multi-tenant systems.

Look for fields such as:

```text
tenant_id
organisation_id
organization_id
workspace_id
account_id
customer_id
project_id
```

and metadata such as:

```text
x-tenant-id
```

Test:

```text
Tenant A credentials
+
Tenant B controlled identifier
```

The service must derive and validate tenant boundaries server-side.

---

# Mass Assignment

Protobuf messages may contain fields that should not be user-controlled.

Example:

```protobuf
message UpdateUserRequest {

    int64 id = 1;

    string display_name = 2;

    string email = 3;

    bool admin = 4;

    string role = 5;

}
```

If the application directly maps this message into an internal user object:

```text
admin
role
```

might become security-sensitive mass-assignment candidates.

Refer to:

[Mass Assignment](mass-assignment.md)

---

# Mass Assignment Test

Expected legitimate request:

```json
{
    "id": "123",
    "displayName": "Test User"
}
```

Controlled test:

```json
{
    "id": "123",
    "displayName": "Test User",
    "admin": true
}
```

The important step is:

```text
Verify server-side state
```

Do not assume success because the field is accepted syntactically.

---

# Protobuf Unknown Fields

Modern protobuf implementations generally preserve or ignore unknown fields depending on language/runtime and processing path.

Do not assume:

```text
Unknown field accepted by JSON parser
=
server state changed
```

Always verify the resulting state.

---

# Field Presence

Protobuf field presence has nuances that differ from ordinary JSON.

Depending on protobuf version and field definition, there can be important differences between:

```text
Field absent
```

and:

```text
Field present with default value
```

For security testing, test where relevant:

```text
Missing value
Default value
Explicit zero
Explicit false
Empty string
Empty message
```

and verify how the application interprets them.

---

# Default Values

Examples of protobuf scalar defaults include concepts such as:

```text
Numeric -> 0
Boolean -> false
String -> empty string
```

Application logic must not confuse:

```text
default value
```

with:

```text
authorised or valid value
```

---

# Enumeration Fields

A protobuf enum might be:

```protobuf
enum Role {

    ROLE_UNSPECIFIED = 0;

    ROLE_USER = 1;

    ROLE_ADMIN = 2;

}
```

Security testing should determine whether clients can improperly select privileged enum values.

Example candidate:

```json
{
    "role": "ROLE_ADMIN"
}
```

The server must enforce authorisation independently of protobuf type validity.

---

# Nested Messages

Messages may contain nested structures:

```protobuf
message UpdateAccountRequest {

    int64 account_id = 1;

    Settings settings = 2;

}

message Settings {

    bool public_profile = 1;

    string role = 2;

}
```

Inspect nested fields carefully.

Security-sensitive properties can be hidden several levels deep.

---

# Repeated Fields

Protobuf supports repeated values:

```protobuf
message AddMembersRequest {

    int64 group_id = 1;

    repeated int64 user_ids = 2;

}
```

Test authorisation for:

```text
Every supplied object
```

not merely the first.

A service must not validate:

```text
user_ids[0]
```

and then trust the rest.

---

# Maps

Protobuf supports maps:

```protobuf
map<string, string> metadata = 1;
```

Review map-based fields for:

```text
Unexpected keys
Security-sensitive configuration
Internal metadata
Privilege-related values
```

---

# Oneof Fields

Protobuf supports:

```text
oneof
```

where one of several fields may be selected.

Example:

```protobuf
oneof identifier {

    int64 user_id = 1;

    string email = 2;

}
```

Test each supported variant.

Different code paths may have different security checks.

---

# Input Validation

Protobuf provides:

```text
Structure
Types
Field definitions
```

but protobuf schema validation is not the same as application security validation.

For example:

```protobuf
string filename = 1;
```

only means:

```text
This field contains a string
```

It does not mean the value is safe for:

```text
Filesystem access
SQL
LDAP
Shell commands
Templates
URLs
HTML
```

---

# Injection Testing

gRPC services can still be vulnerable to:

```text
SQL injection
NoSQL injection
Command injection
LDAP injection
SSTI
Path traversal
SSRF
```

if protobuf fields reach unsafe sinks.

The binary transport does not prevent injection.

---

# SQL Injection Concept

```text
Protobuf string
     |
     v
gRPC Handler
     |
     v
SQL Query Construction
     |
     v
Database
```

If the handler performs unsafe query construction:

```text
SQL injection remains possible
```

Refer to:

[SQL Injection](sql-injection.md)

---

# Command Injection Concept

```text
RPC field
   |
   v
Service handler
   |
   v
Shell command
```

Example risky application logic:

```text
filename
   |
   v
"convert " + filename
```

The gRPC transport provides no protection against unsafe command construction.

Refer to:

[OS Command Injection](command-injection.md)

---

# SSRF

A protobuf field might contain:

```protobuf
string url = 1;
```

Example service:

```text
PreviewURL()
FetchRemoteImage()
ImportDocument()
SendWebhook()
```

These are potential SSRF candidates.

Refer to:

[Server Side Request Forgery](ssrf.md)

---

# Path Traversal

Look for fields such as:

```text
filename
path
directory
template
archive
export_path
```

Example:

```protobuf
message DownloadRequest {

    string filename = 1;

}
```

If the service directly joins this value with a filesystem path:

```text
Potential path traversal
```

Refer to:

[Path Traversal](path-traversal.md)

---

# Error Handling

gRPC has its own status model.

Common gRPC status codes include:

```text
OK
CANCELLED
UNKNOWN
INVALID_ARGUMENT
DEADLINE_EXCEEDED
NOT_FOUND
ALREADY_EXISTS
PERMISSION_DENIED
RESOURCE_EXHAUSTED
FAILED_PRECONDITION
ABORTED
OUT_OF_RANGE
UNIMPLEMENTED
INTERNAL
UNAVAILABLE
DATA_LOSS
UNAUTHENTICATED
```

---

# UNAUTHENTICATED vs PERMISSION_DENIED

A useful conceptual distinction is:

```text
UNAUTHENTICATED
→ Valid authentication credentials are absent or invalid

PERMISSION_DENIED
→ Identity is known but lacks permission
```

Applications should use status codes consistently.

---

# HTTP Status Is Not the Whole Story

Do not evaluate a gRPC call using only the HTTP status.

gRPC communicates RPC status separately.

Conceptually:

```text
HTTP transport
       |
       v
gRPC protocol
       |
       v
grpc-status
       |
       v
RPC result
```

Therefore:

```text
HTTP 200
```

does not necessarily mean:

```text
RPC succeeded
```

---

# grpc-status

gRPC status information may appear in trailers.

For example:

```text
grpc-status: 0
```

means:

```text
OK
```

A non-zero status indicates a gRPC error.

Always inspect:

```text
gRPC status
gRPC message
Response data
Trailers
```

rather than relying only on HTTP status.

---

# Error Information Disclosure

Poor error handling may reveal:

```text
Stack traces
Database errors
Filesystem paths
Internal hostnames
Service names
Package names
Source paths
SQL statements
Internal object IDs
Debug information
```

Example:

```text
rpc error:
code = Internal
desc = database connection failed:
postgres://db-internal:5432/users
```

This can expose useful internal information.

---

# Error Testing

Send controlled invalid values:

```text
Missing required business value
Invalid identifier
Out-of-range value
Invalid enum
Malformed application data
```

Observe:

```text
gRPC status
Error description
Metadata
Trailers
Server stability
```

Do not deliberately crash production services.

---

# Transport Security

Production gRPC services should generally use TLS where network trust cannot otherwise be assured.

Conceptually:

```text
Client
   |
   | TLS
   v
gRPC Server
```

Without appropriate transport protection:

```text
Credentials
RPC messages
Metadata
Tokens
Business data
```

may be exposed to network attackers depending on the environment.

---

# Testing TLS

Normal secure connection:

```bash
grpcurl \
  target.example:443 \
  list
```

Plaintext connection:

```bash
grpcurl \
  -plaintext \
  target.example:50051 \
  list
```

If an externally reachable sensitive production service accepts plaintext gRPC unexpectedly, investigate the architecture and impact.

---

# Mutual TLS

mTLS means:

```text
Server proves identity to client
+
Client proves identity to server
```

Conceptually:

```text
Client Certificate
        |
        v
      Server
        ^
        |
Server Certificate
```

mTLS is commonly useful for:

```text
Service-to-service authentication
Internal infrastructure
Zero-trust architectures
High-trust backend services
```

---

# grpcurl With Client Certificates

A controlled mTLS test may use:

```bash
grpcurl \
  -cert client.crt \
  -key client.key \
  -cacert ca.crt \
  target.example:443 \
  list
```

Protect client private keys carefully.

---

# mTLS Is Not Authorisation

Even when mTLS is used:

```text
Authenticated service
```

does not automatically mean:

```text
Authorised for every method
```

The application may still require:

```text
Service identity checks
Method permissions
Object permissions
Tenant permissions
```

---

# Deadlines

gRPC supports deadlines.

A deadline tells the system how long the client is willing to wait for an RPC.

Conceptually:

```text
Client
  |
  | Request
  | Deadline: 2 seconds
  v
Server
```

If the deadline is exceeded:

```text
DEADLINE_EXCEEDED
```

may be returned.

---

# Why Deadlines Matter

Without appropriate deadlines:

```text
Slow requests
Long-running operations
Blocked dependencies
```

can consume resources unnecessarily.

Security and reliability overlap here.

---

# Cancellation

gRPC supports cancellation.

A client or server may cancel an RPC.

Important:

```text
Cancellation does not automatically roll back
application changes already performed.
```

Therefore application developers must consider transactional behaviour carefully.

---

# Cancellation Testing

For state-changing operations, understand:

```text
When does the state change?

What happens if the client disconnects?

Is the operation idempotent?

Is partial state possible?
```

Do not intentionally create inconsistent production data.

Use controlled test objects.

---

# Rate Limiting

gRPC endpoints need rate limiting just like other APIs.

Potential abuse includes:

```text
Login attempts
OTP verification
Password reset
Search
Resource enumeration
Expensive calculations
Streaming
File operations
Administrative methods
```

Refer to:

[Rate Limiting and Anti-Automation](rate-limiting.md)

when that page exists.

---

# Rate-Limit Scope

Test whether limits are applied by:

```text
IP
Account
Token
Method
Tenant
Service
Connection
```

Weak implementations may only rate-limit:

```text
HTTP connection
```

while allowing many RPC streams over another connection.

---

# HTTP/2 Multiplexing

Because HTTP/2 supports multiple concurrent streams:

```text
One connection
       |
       +-- RPC 1
       +-- RPC 2
       +-- RPC 3
       +-- RPC 4
```

rate limiting should not assume:

```text
One connection
=
one request
```

---

# Resource Exhaustion

gRPC services should protect against excessive resource consumption.

Potential areas include:

```text
Large messages
Many concurrent RPCs
Long-lived streams
Large metadata
Expensive methods
Unbounded repeated fields
Unbounded search results
Compression
File uploads
```

Testing these areas can affect availability.

Use conservative tests.

---

# Message Size Limits

Servers and clients can configure message size limits.

A service accepting unexpectedly large messages may consume:

```text
Memory
CPU
Bandwidth
```

Do not perform large-volume denial-of-service testing without explicit permission.

A normal pentest should generally identify configuration and demonstrate risk using minimal safe input.

---

# Metadata Size

Metadata also consumes resources.

Applications and infrastructure should enforce reasonable metadata limits.

Do not send extremely large metadata values to production services unless explicit stress-testing permission exists.

---

# Streaming Resource Exhaustion

Potential problems include:

```text
Unlimited streams
Unlimited messages per stream
No idle timeout
No deadline
No per-user stream limit
Expensive processing per message
```

A safer assessment asks:

```text
What controls exist?
```

before attempting high-volume validation.

---

# Authentication During Streams

Consider:

```text
Stream opened at 10:00

Token expires at 10:05

Stream remains open until 15:00
```

Ask:

```text
Should the stream remain authorised?

Are permissions re-evaluated?

What happens if account is disabled?

What happens if role changes?
```

The correct answer depends on the application's security model.

---

# Per-Message Authorisation

Suppose a bidirectional stream accepts:

```protobuf
message Command {

    int64 object_id = 1;

    string action = 2;

}
```

The server should not merely authorise:

```text
Stream creation
```

and then trust every later:

```text
object_id
```

Each security-sensitive operation may require appropriate authorisation.

---

# Server Reflection Security

Reflection can reveal:

```text
Hidden services
Administrative methods
Internal message fields
Debug methods
Deprecated methods
Service structure
```

Example:

```text
admin.InternalAdminService
debug.DebugService
migration.MigrationService
```

These are useful reconnaissance findings.

But again:

```text
Discovery
≠
Exploit
```

---

# Health Checking

gRPC has a standard health-checking service.

You may encounter:

```text
grpc.health.v1.Health
```

Example:

```bash
grpcurl \
  target.example:443 \
  grpc.health.v1.Health/Check
```

Depending on the schema/tool invocation, a service name may be supplied.

Health endpoints can reveal:

```text
Service availability
Service names
Internal architecture
```

but exposure is not automatically a high-severity vulnerability.

---

# Debug and Administrative Services

Pay special attention to service names containing:

```text
Admin
Debug
Internal
Management
Test
Dev
Health
Reflection
Migration
Maintenance
Diagnostics
```

Example:

```text
admin.AdminService
debug.DebugService
```

Test whether they are:

```text
Reachable
Authenticated
Authorised
Intended for the environment
```

---

# Deprecated Methods

A `.proto` definition may contain older methods still reachable by clients.

For example:

```text
LoginV1
LoginV2
LegacyLogin
OldUpdateUser
```

Older methods may lack security controls added to newer versions.

Always compare:

```text
Current method
vs
Legacy method
```

---

# Versioning

gRPC APIs may encode versions in:

```text
Package names
Service names
Method names
```

Examples:

```text
users.v1.UserService
users.v2.UserService
```

Test whether older versions remain accessible.

---

# Business Logic

gRPC applications can have the same business logic vulnerabilities as REST applications.

Examples:

```text
Negative quantity
Duplicate coupon
Invalid state transition
Repeated refund
Bypassed approval
Skipped workflow step
Unexpected object state
```

Refer to:

[Business Logic Vulnerabilities](business-logic.md)

---

# Race Conditions

Concurrent RPCs may create race conditions.

Example:

```text
RPC A:
RedeemCoupon()

RPC B:
RedeemCoupon()
```

If both execute before shared state is updated:

```text
Coupon redeemed twice
```

HTTP/2 multiplexing and gRPC concurrency make race-condition testing relevant.

Refer to:

[Race Conditions](race-conditions.md)

Use controlled accounts and minimal concurrency.

---

# Authentication Bypass Through Alternate Services

A common architectural risk is inconsistent security between services.

For example:

```text
Public Gateway
    |
    +-- Authentication enforced
    |
    v
UserService
```

but:

```text
Direct Internal gRPC Port
    |
    +-- No authentication
    |
    v
UserService
```

If the internal service becomes reachable from an untrusted network, gateway-only authentication may be bypassed.

---

# Trusting the Gateway

Some architectures assume:

```text
Only gateway can reach gRPC service
```

and therefore trust metadata such as:

```text
x-user-id
x-role
```

This can be safe only if the network and service architecture genuinely enforce that trust boundary.

If an attacker can directly reach the backend:

```text
Gateway security may be bypassed
```

---

# Network Exposure

During reconnaissance identify gRPC ports.

Common examples may include:

```text
443
50051
50052
```

but gRPC can run on any configured port.

Do not rely solely on default ports.

---

# TLS / ALPN

Native secure gRPC commonly negotiates HTTP/2 using TLS ALPN.

During service identification, look for:

```text
h2
```

support.

For example:

```bash
openssl s_client \
  -connect target.example:443 \
  -alpn h2
```

This only demonstrates HTTP/2 negotiation capability.

It does not prove the endpoint is gRPC.

---

# nmap Reconnaissance

Basic authorised service reconnaissance:

```bash
nmap \
  -sV \
  -p 443,50051 \
  target.example
```

If HTTP/2 is detected, investigate further.

Again:

```text
HTTP/2
≠
gRPC
```

---

# grpcurl Discovery Workflow

A practical workflow:

```text
Target
  |
  v
Is port reachable?
  |
  v
TLS or plaintext?
  |
  v
Try reflection
  |
  +-- Reflection works
  |       |
  |       v
  |   Enumerate services
  |
  +-- Reflection unavailable
          |
          v
    Obtain .proto / protoset
          |
          v
    Enumerate schema
```

---

# grpcurl Quick Recon

TLS:

```bash
grpcurl \
  target.example:443 \
  list
```

Plaintext:

```bash
grpcurl \
  -plaintext \
  target.example:50051 \
  list
```

Describe:

```bash
grpcurl \
  target.example:443 \
  describe package.Service
```

Methods:

```bash
grpcurl \
  target.example:443 \
  list package.Service
```

Invoke:

```bash
grpcurl \
  -d '{"id":"123"}' \
  target.example:443 \
  package.Service/GetObject
```

---

# Authenticated grpcurl Workflow

Set a shell variable:

```bash
TOKEN='REDACTED'
```

Then:

```bash
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  target.example:443 \
  list
```

Invoke:

```bash
grpcurl \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"id":"123"}' \
  target.example:443 \
  users.UserService/GetUser
```

Avoid putting sensitive real tokens into:

```text
Shell history
Screenshots
Git repositories
Reports
```

without appropriate redaction.

---

# Two-Account Testing

For authorisation testing use:

```text
Account A
Account B
```

Set:

```bash
TOKEN_A='REDACTED'
TOKEN_B='REDACTED'
```

Controlled object owned by A:

```text
1001
```

Controlled object owned by B:

```text
2001
```

Test:

```bash
grpcurl \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"id":"1001"}' \
  target.example:443 \
  objects.ObjectService/GetObject
```

Then:

```bash
grpcurl \
  -H "Authorization: Bearer $TOKEN_A" \
  -d '{"id":"2001"}' \
  target.example:443 \
  objects.ObjectService/GetObject
```

Expected:

```text
Denied
```

for the second request unless Account A legitimately has access.

---

# grpcurl Verbose Mode

`grpcurl` provides verbose output options.

Check:

```bash
grpcurl -help
```

for the exact options supported by your installed version.

Verbose output can help inspect:

```text
Headers
Response metadata
Trailers
Timing
Status
```

---

# Burp Suite and gRPC

Burp Suite is fundamentally an HTTP testing platform.

Because native gRPC uses HTTP/2 and binary protobuf messages, the workflow is not always as straightforward as editing JSON REST traffic.

Burp can still be valuable for:

```text
HTTP/2 inspection
Metadata
Gateway traffic
gRPC-Web
Authentication
CORS
Headers
Protobuf-assisted workflows
```

---

# Burp Proxy

When the client supports proxying and TLS interception, Burp can help observe:

```text
HTTP/2 requests
Metadata
Authorization headers
Content-Type
gRPC-Web traffic
Gateway requests
```

Native gRPC client proxy support varies by implementation.

Do not assume every gRPC client honours:

```text
HTTP_PROXY
HTTPS_PROXY
```

in the same manner as a browser.

---

# Burp and Binary Protobuf

Raw protobuf data is not naturally human-readable.

Conceptually:

```text
Burp
  |
  v
Binary protobuf
  |
  v
Need schema / decoder
```

Having:

```text
.proto files
```

greatly improves your ability to understand messages.

---

# Burp Extensions

Check the current BApp Store:

```text
https://portswigger.net/bappstore
```

Potentially useful categories include:

```text
Protobuf decoding
gRPC-Web decoding
HTTP/2 tooling
```

One known BApp is:

```text
Protobuf Decoder
```

which can help decode and beautify protobuf responses.

Because extensions are third-party software, review their current status and source before relying on them.

---

# gRPC-Web Coder

For applications using:

```text
gRPC-Web
```

a gRPC-Web-specific Burp extension may help decode or encode traffic.

Always confirm:

```text
Native gRPC
or
gRPC-Web
```

before selecting tooling.

Do not apply gRPC-Web tooling blindly to native gRPC traffic.

---

# Burp Is Not Always the Primary Tool

For native gRPC:

```text
grpcurl
```

is often more practical than trying to force every interaction through Burp.

A useful combination is:

```text
grpcurl
    +
.proto files
    +
Burp
    +
Source review
    +
Application client
```

---

# Mobile Applications

Mobile applications frequently use gRPC.

Useful artefacts may include:

```text
Generated protobuf classes
Service stubs
Descriptor data
API hostnames
Authentication metadata
Certificate configuration
```

Search decompiled applications for:

```text
grpc
protobuf
proto
Channel
ManagedChannel
Authorization
Bearer
```

Only assess applications you are authorised to test.

---

# Source Code Review

When source code is available, search for:

```text
service
rpc
grpc
RegisterService
interceptor
metadata
authorization
role
tenant
permission
```

Also inspect generated code carefully.

Generated protobuf code can be large, so locate:

```text
.proto
```

sources first where possible.

---

# Interceptors

Search for authentication and authorisation interceptors.

Examples vary by language.

Conceptually:

```text
UnaryInterceptor
StreamInterceptor
ServerInterceptor
```

Important question:

```text
Are unary and streaming RPCs protected consistently?
```

An application might secure unary methods while forgetting streaming handlers.

---

# Unary vs Streaming Security

Build separate matrices:

```text
Unary methods
```

and:

```text
Streaming methods
```

because middleware registration can differ.

Example:

| RPC | Type | Authentication | Authorisation |
|---|---|---|---|
| GetUser | Unary | Yes | Yes |
| WatchUsers | Server stream | Yes | ? |
| Upload | Client stream | Yes | ? |
| Chat | Bidirectional | ? | ? |

---

# Server-Side Validation

The service should validate:

```text
Field format
Field length
Allowed values
Object relationships
Business rules
Authorisation
```

Do not rely only on:

```text
protobuf type
```

for validation.

---

# Integer Boundary Testing

For numeric fields, safe controlled tests can include:

```text
0
1
-1
Expected minimum
Expected maximum
Just outside expected range
```

Avoid intentionally causing resource exhaustion.

---

# String Boundary Testing

For string fields test:

```text
Empty string
Normal value
Whitespace
Unexpected Unicode
Reasonable boundary length
```

Then apply vulnerability-specific tests only when the field reaches a relevant sink.

---

# Boolean Fields

Test:

```text
true
false
absent
```

where field presence semantics matter.

Security-sensitive examples:

```text
admin
enabled
verified
approved
internal
```

should never be trusted merely because the client sends them.

---

# Sensitive Fields

Pay particular attention to:

```text
admin
role
permissions
owner_id
user_id
account_id
tenant_id
organisation_id
verified
approved
status
price
balance
discount
internal
is_staff
```

These fields are not vulnerabilities by themselves.

They are:

```text
Authorisation and business-logic candidates
```

---

# Secrets in Protobuf Definitions

`.proto` files may reveal:

```text
Internal service names
Hidden administrative functionality
Deprecated fields
Internal identifiers
Comments
Architecture
```

Do not place secrets directly in schema comments or generated client packages.

---

# Sensitive Data in Metadata

Metadata may accidentally contain:

```text
JWTs
API keys
Session identifiers
Internal tokens
Tracing data
User identifiers
```

Review logging systems to ensure metadata is not unnecessarily recorded.

---

# Logging

gRPC services should log security-relevant events such as:

```text
Authentication failures
Authorisation failures
Administrative actions
Sensitive state changes
Rate-limit events
Suspicious method use
```

but should avoid logging:

```text
Passwords
Access tokens
Private keys
Full sensitive request bodies
```

---

# Monitoring

Useful telemetry can include:

```text
Service
Method
Status
Latency
Authentication identity
Authorisation decision
Request volume
Error rate
Stream count
```

This helps detect abuse.

---

# gRPC and JWT

JWTs are commonly transported through metadata:

```http
authorization: Bearer TOKEN
```

All normal JWT security concerns still apply:

```text
Signature verification
Algorithm handling
Issuer validation
Audience validation
Expiration
Key management
Claims
Authorisation
```

Refer to:

[JSON Web Token Security](jwt.md)

---

# gRPC and OAuth

OAuth access tokens may also be passed through gRPC metadata.

The gRPC service must validate:

```text
Token signature or introspection
Issuer
Audience
Scope
Expiration
```

as appropriate.

Refer to:

[OAuth 2.0 and OpenID Connect Security](oauth-oidc.md)

---

# gRPC and API Security

Many standard API security issues apply directly:

```text
Broken Object Level Authorisation
Broken Authentication
Broken Function Level Authorisation
Unrestricted Resource Consumption
Business Logic Vulnerabilities
SSRF
Security Misconfiguration
```

Refer to:

[API Security](api-security.md)

---

# gRPC-Web and CORS

Because gRPC-Web is browser-facing, CORS becomes relevant.

Inspect:

```text
Access-Control-Allow-Origin
Access-Control-Allow-Credentials
Access-Control-Allow-Headers
Access-Control-Allow-Methods
```

Refer to:

[Cross-Origin Resource Sharing (CORS)](cors.md)

---

# gRPC-Web and CSRF

Whether CSRF is relevant depends on:

```text
Authentication mechanism
Cookie behaviour
Request format
CORS
Gateway
Application design
```

Do not assume:

```text
gRPC-Web
=
immune to CSRF
```

Refer to:

[Cross-Site Request Forgery](csrf.md)

---

# Service Inventory

Create a service inventory:

```text
users.UserService

    GetUser
    UpdateUser
    DeleteUser
    ListUsers

billing.InvoiceService

    GetInvoice
    CreateInvoice
    RefundInvoice

admin.AdminService

    ListUsers
    ChangeRole
    DisableUser
```

Then classify:

```text
Public
Authenticated
Privileged
Internal
Administrative
```

---

# Method Inventory

For each method record:

```text
Service
Method
RPC type
Request message
Response message
Authentication
Required role
Object identifiers
Tenant identifiers
Sensitive fields
State-changing?
Rate-limited?
```

---

# Example Method Matrix

| Service | Method | Type | Auth | Role | State Change |
|---|---|---|---|---|---|
| UserService | GetUser | Unary | Yes | User | No |
| UserService | UpdateUser | Unary | Yes | User | Yes |
| AdminService | ChangeRole | Unary | Yes | Admin | Yes |
| EventService | WatchEvents | Server stream | Yes | User | No |
| UploadService | Upload | Client stream | Yes | User | Yes |

This becomes the foundation of the assessment.

---

# gRPC Security Testing Workflow

A comprehensive workflow:

```text
Identify gRPC Endpoint
        |
        v
Determine Native gRPC or gRPC-Web
        |
        v
Determine TLS / Plaintext
        |
        v
Check Reflection
        |
        +-------------------+
        |                   |
        v                   v
 Reflection Works      Reflection Disabled
        |                   |
        v                   v
 Enumerate          Obtain .proto/protoset
        |                   |
        +---------+---------+
                  |
                  v
          Map Services
                  |
                  v
           Map Methods
                  |
                  v
          Map Messages
                  |
                  v
          Map Metadata
                  |
                  v
       Test Authentication
                  |
                  v
       Test Authorisation
                  |
                  v
       Test Object Access
                  |
                  v
       Test Sensitive Fields
                  |
                  v
       Test Input Validation
                  |
                  v
       Test Business Logic
                  |
                  v
        Test Rate Limits
                  |
                  v
        Review Streaming
                  |
                  v
        Review TLS / mTLS
                  |
                  v
       Review Error Handling
                  |
                  v
       Review Resource Limits
                  |
                  v
        Collect Evidence
                  |
                  v
             Report
```

---

# Phase 1: Discovery Checklist

```text
[ ] gRPC endpoint identified
[ ] Port identified
[ ] Native gRPC vs gRPC-Web determined
[ ] HTTP/2 confirmed where relevant
[ ] TLS configuration understood
[ ] Reflection tested
[ ] .proto files searched
[ ] Protoset files searched
[ ] Service names collected
[ ] Method names collected
[ ] RPC types recorded
```

---

# Phase 2: Schema Checklist

```text
[ ] Request messages mapped
[ ] Response messages mapped
[ ] Object IDs identified
[ ] User IDs identified
[ ] Tenant IDs identified
[ ] Role fields identified
[ ] Privilege fields identified
[ ] Nested messages reviewed
[ ] Repeated fields reviewed
[ ] Maps reviewed
[ ] oneof fields reviewed
[ ] Enums reviewed
```

---

# Phase 3: Authentication Checklist

```text
[ ] Anonymous calls tested
[ ] Valid credentials tested
[ ] Invalid credentials tested
[ ] Expired credentials tested
[ ] Missing metadata tested
[ ] Authentication interceptor identified
[ ] Unary methods checked
[ ] Streaming methods checked
[ ] Legacy methods checked
```

---

# Phase 4: Authorisation Checklist

```text
[ ] Horizontal access tested
[ ] Vertical access tested
[ ] Object ownership tested
[ ] Tenant isolation tested
[ ] Administrative methods tested
[ ] Hidden methods tested
[ ] Legacy methods tested
[ ] Per-message stream authorisation reviewed
```

---

# Phase 5: Input Checklist

```text
[ ] Empty values
[ ] Missing values
[ ] Default values
[ ] Numeric boundaries
[ ] Boolean values
[ ] Enum values
[ ] Nested fields
[ ] Repeated fields
[ ] Sensitive fields
[ ] Injection sinks
[ ] URL fields
[ ] File/path fields
```

---

# Phase 6: Transport Checklist

```text
[ ] TLS used where required
[ ] Certificate validated
[ ] Hostname validated
[ ] Weak plaintext exposure checked
[ ] mTLS requirement understood
[ ] Client certificate permissions reviewed
```

---

# Phase 7: Streaming Checklist

```text
[ ] Server streaming identified
[ ] Client streaming identified
[ ] Bidirectional streaming identified
[ ] Authentication at stream creation checked
[ ] Per-message authorisation checked
[ ] Idle timeout reviewed
[ ] Deadline reviewed
[ ] Message count limits reviewed
[ ] Message size limits reviewed
[ ] Concurrent stream limits reviewed
```

---

# Phase 8: Resource Checklist

```text
[ ] Message size limits
[ ] Metadata limits
[ ] Request rate limits
[ ] Per-user limits
[ ] Per-method limits
[ ] Stream limits
[ ] Deadlines
[ ] Expensive operations
[ ] Pagination
[ ] Result limits
```

---

# Phase 9: Information Disclosure Checklist

```text
[ ] Reflection exposure
[ ] Health service exposure
[ ] Debug services
[ ] Internal services
[ ] Error messages
[ ] Stack traces
[ ] Internal hostnames
[ ] Database errors
[ ] Source paths
[ ] Sensitive metadata
```

---

# Phase 10: Business Logic Checklist

```text
[ ] Workflow order
[ ] State transitions
[ ] Duplicate operations
[ ] Race conditions
[ ] Price manipulation
[ ] Quantity manipulation
[ ] Approval bypass
[ ] Refund logic
[ ] Role changes
[ ] Account state
```

---

# Quick grpcurl Cheatsheet

## List Services

```bash
grpcurl \
  target.example:443 \
  list
```

---

## Plaintext Service

```bash
grpcurl \
  -plaintext \
  target.example:50051 \
  list
```

---

## Ignore Certificate Validation

Controlled testing only:

```bash
grpcurl \
  -insecure \
  target.example:443 \
  list
```

---

## List Methods

```bash
grpcurl \
  target.example:443 \
  list package.Service
```

---

## Describe Service

```bash
grpcurl \
  target.example:443 \
  describe package.Service
```

---

## Describe Message

```bash
grpcurl \
  target.example:443 \
  describe package.Message
```

---

## Invoke RPC

```bash
grpcurl \
  -d '{"id":"123"}' \
  target.example:443 \
  package.Service/GetObject
```

---

## Add Bearer Token

```bash
grpcurl \
  -H "Authorization: Bearer TOKEN" \
  -d '{"id":"123"}' \
  target.example:443 \
  package.Service/GetObject
```

---

## Custom Metadata

```bash
grpcurl \
  -H "x-tenant-id: 100" \
  -d '{"id":"123"}' \
  target.example:443 \
  package.Service/GetObject
```

---

## Use Proto File

```bash
grpcurl \
  -import-path ./proto \
  -proto service.proto \
  target.example:443 \
  list
```

---

## Use Protoset

```bash
grpcurl \
  -protoset service.protoset \
  target.example:443 \
  list
```

---

## Read Request From File

```bash
grpcurl \
  -d @ \
  target.example:443 \
  package.Service/Method \
  < request.json
```

---

# Testing Without Reflection

If:

```bash
grpcurl \
  target.example:443 \
  list
```

returns a reflection-related error, do not conclude:

```text
No gRPC services exist
```

It may simply mean:

```text
Reflection unavailable
```

Look for:

```text
.proto files
protosets
generated client code
SDKs
mobile application code
documentation
source code
```

---

# Testing With a Proto File

Suppose:

```text
users.proto
```

contains the service definition.

Use:

```bash
grpcurl \
  -import-path . \
  -proto users.proto \
  target.example:443 \
  list
```

Then:

```bash
grpcurl \
  -import-path . \
  -proto users.proto \
  target.example:443 \
  list users.UserService
```

Then:

```bash
grpcurl \
  -import-path . \
  -proto users.proto \
  -d '{"id":"123"}' \
  target.example:443 \
  users.UserService/GetUser
```

---

# Safe Enumeration Principle

Do not automatically invoke every discovered method.

For example:

```text
GetUser
ListUsers
GetStatus
```

may be relatively safe read operations.

But:

```text
DeleteUser
ResetDatabase
Shutdown
Migrate
Refund
DisableAccount
```

may have significant effects.

Discovery and invocation are separate steps.

---

# State-Changing Methods

Before invoking:

```text
Create
Update
Delete
Reset
Refund
Disable
Enable
Change
Execute
Run
Import
Migrate
```

determine:

```text
What will happen?
Can a controlled object be used?
Can the operation be reversed?
```

---

# Evidence Collection

For each confirmed issue record:

```text
Target host
Port
TLS/plaintext
Service
Method
RPC type
Request message
Authentication state
Account
Object ownership
Request metadata
Request data
Response
gRPC status
Relevant trailers
Observed state change
```

---

# Redacting Evidence

Redact:

```text
JWTs
API keys
Session tokens
Client private keys
Passwords
Sensitive personal data
```

unless the reporting process specifically requires them.

---

# Example Finding: Missing Object-Level Authorisation

```text
Finding:
Broken Object Level Authorisation in gRPC GetInvoice Method

Affected service:
billing.InvoiceService

Affected method:
GetInvoice

Observed:
The GetInvoice RPC accepts an invoice identifier in the request message.

Testing was performed using two controlled accounts.

Account A owned invoice 1001.
Account B owned invoice 2001.

Using Account A's valid authentication token, changing the invoice identifier from 1001 to 2001 caused the service to return Account B's controlled invoice.

Impact:
An authenticated user can access invoice objects belonging to another user by modifying the invoice identifier supplied to the RPC.

Recommendation:
Perform server-side object-level authorisation for every requested invoice. Derive the authenticated user from trusted authentication context and verify that the user is authorised to access the requested invoice before returning it.
```

---

# Example Finding: Missing Function-Level Authorisation

```text
Finding:
Standard Users Can Invoke Administrative gRPC Method

Affected service:
admin.AdminService

Affected method:
ChangeRole

Observed:
A standard controlled user account was able to invoke the ChangeRole RPC successfully.

The method accepted a target user identifier and role value and did not enforce the expected administrator requirement.

Impact:
A standard user may be able to modify user privileges, potentially resulting in privilege escalation.

Recommendation:
Enforce server-side function-level authorisation before executing administrative RPC methods. Do not rely on client-side UI restrictions or knowledge of method names.
```

---

# Example Finding: Unauthenticated gRPC Method

```text
Finding:
Sensitive gRPC Method Accessible Without Authentication

Affected service:
users.UserService

Affected method:
GetUser

Observed:
The method returned user information when invoked without authentication metadata.

The same method was expected to require an authenticated application user.

Impact:
An unauthenticated attacker with network access to the gRPC service may retrieve user information.

Recommendation:
Require authentication for the affected RPC and ensure authentication middleware or interceptors are applied consistently across all sensitive services and methods.
```

---

# Example Finding: Reflection Exposure

```text
Finding:
Production gRPC Service Exposes Server Reflection

Observed:
The externally reachable production gRPC endpoint exposes the gRPC reflection service.

An unauthenticated client was able to enumerate service and method definitions.

The exposed schema included administrative and internal service names.

Impact:
Reflection significantly simplifies reconnaissance by exposing the gRPC API surface and message schemas.

No direct unauthorised access to administrative functionality was demonstrated through reflection alone.

Recommendation:
Disable or restrict gRPC reflection in production where runtime schema discovery is not required. If reflection is operationally required, restrict access according to the application's trust model.
```

Severity should be based on:

```text
Actual exposure
Sensitivity
Environment
Attack-chain value
```

Do not automatically classify reflection as high severity.

---

# Example Finding: Sensitive Metadata Trusted

```text
Finding:
Client-Controlled gRPC Metadata Influences Authorisation

Observed:
The service accepts an x-role metadata value from the client.

Changing:

x-role: user

to:

x-role: admin

caused the controlled account to gain access to an administrative method.

Impact:
An authenticated user can manipulate client-controlled metadata to influence the server's authorisation decision and escalate privileges.

Recommendation:
Do not trust client-supplied role or identity metadata. Derive identity and permissions from validated authentication credentials or a trusted upstream identity mechanism protected by an enforced network trust boundary.
```

---

# Example Finding: Excessive Error Disclosure

```text
Finding:
gRPC Error Responses Disclose Internal Infrastructure Information

Observed:
Invalid input to the affected RPC caused the service to return detailed internal error information.

The response exposed internal service names and database connection details.

Impact:
An attacker may use the disclosed information to map internal infrastructure and identify additional attack targets or technologies.

Recommendation:
Return generic client-facing gRPC error descriptions while logging detailed diagnostic information only to appropriately protected server-side logging systems.
```

---

# Example Finding Titles

Useful titles include:

```text
Broken Object Level Authorisation in gRPC GetInvoice Method

Missing Function-Level Authorisation in Administrative gRPC Service

Sensitive gRPC Method Accessible Without Authentication

Production gRPC Service Exposes Server Reflection

Client-Controlled gRPC Metadata Enables Privilege Escalation

gRPC Error Responses Disclose Internal Infrastructure Details

Sensitive gRPC Service Exposed Over Unencrypted Transport

Missing Rate Limiting on gRPC Authentication Method

gRPC Streaming Method Does Not Enforce Object Authorisation

Legacy gRPC Service Bypasses Current Authorisation Controls

Cross-Tenant Access Through gRPC Object Identifier Manipulation
```

---

# Remediation

A strong gRPC security model combines multiple controls.

```text
                    gRPC SECURITY
                         |
        +----------------+----------------+
        |                |                |
        v                v                v
     Transport      Authentication    Authorisation
        |                |                |
       TLS              JWT            Method
       mTLS             OAuth          Object
                                         Tenant
        |                |                |
        +----------------+----------------+
                         |
                         v
                    Validation
                         |
             +-----------+-----------+
             |                       |
             v                       v
        Input Safety            Business Rules
             |                       |
             +-----------+-----------+
                         |
                         v
                  Resource Controls
                         |
               +---------+---------+
               |         |         |
               v         v         v
             Rate      Size      Streams
             Limit     Limit     Deadlines
                         |
                         v
                  Safe Error Handling
                         |
                         v
                 Logging / Monitoring
```

---

# Recommended Security Principles

## Use TLS

Protect sensitive production traffic with appropriate transport security.

---

## Consider mTLS for Service Identity

Where architecture requires strong service-to-service identity:

```text
mTLS
```

can provide mutual authentication.

Still enforce application-level authorisation.

---

## Authenticate Every Sensitive RPC

Do not assume:

```text
Internal network
=
trusted user
```

Apply authentication according to the service trust model.

---

## Authorise Every Sensitive Operation

Check:

```text
Method permission
Object permission
Tenant permission
Business permission
```

server-side.

---

## Do Not Trust Client Metadata

Values such as:

```text
x-user-id
x-role
x-tenant-id
```

must not be trusted unless they come through a genuinely enforced trusted boundary.

---

## Validate Application Data

Protobuf types are not sufficient security validation.

Validate:

```text
Length
Range
Format
Relationships
Allowed state
Ownership
```

---

## Limit Resources

Configure appropriate:

```text
Message size
Metadata size
Concurrent RPCs
Streams
Rate limits
Deadlines
Idle timeouts
```

---

## Restrict Reflection

Disable or appropriately restrict production reflection when runtime schema discovery is unnecessary.

---

## Protect Administrative Services

Administrative and debugging services should have strong:

```text
Network restrictions
Authentication
Authorisation
Monitoring
```

---

## Handle Errors Safely

Return enough information for legitimate clients without exposing:

```text
Stack traces
Database strings
Internal hostnames
Source paths
Secrets
```

---

## Secure Streaming Separately

Do not assume security applied to unary RPCs automatically protects streams.

Review:

```text
Stream creation
Each sensitive message
Long-lived authentication state
Resource consumption
Cancellation
Timeouts
```

---

# Quick Mental Model

When you see:

```text
users.UserService/GetUser
```

think:

```text
WHO?
 |
 +-- Is caller authenticated?

WHAT FUNCTION?
 |
 +-- Is caller allowed to use GetUser?

WHAT OBJECT?
 |
 +-- Which user ID?

WHO OWNS IT?
 |
 +-- Is caller allowed to access that user?

WHAT INPUT?
 |
 +-- Are fields validated?

WHAT TRANSPORT?
 |
 +-- TLS?

WHAT METADATA?
 |
 +-- JWT?
 +-- Tenant?
 +-- Role?
 +-- Trusted?

WHAT RESPONSE?
 |
 +-- Sensitive fields?
 +-- Errors?
 +-- Status?

WHAT RESOURCE COST?
 |
 +-- Expensive?
 +-- Rate limited?
 +-- Bounded?
```

---

# Pentester Quick Workflow

```text
1. Identify gRPC

2. Determine native gRPC or gRPC-Web

3. Determine TLS or plaintext

4. Try reflection

5. Obtain .proto/protoset if needed

6. List services

7. List methods

8. Describe messages

9. Classify methods

10. Identify metadata

11. Test authentication

12. Build role matrix

13. Test BOLA/IDOR

14. Test tenant isolation

15. Test privileged methods

16. Test sensitive fields

17. Test input validation

18. Review injection sinks

19. Review business logic

20. Review rate limits

21. Review streaming methods

22. Review message/resource limits

23. Review error handling

24. Review reflection/debug exposure

25. Collect minimal evidence

26. Report

27. Retest
```

---

# gRPC Decision Tree

```text
             TARGET SERVICE
                   |
                   v
              HTTP/2?
                   |
             +-----+-----+
             |           |
            NO          YES
             |           |
       Investigate       v
                    gRPC indicators?
                         |
                   +-----+-----+
                   |           |
                  NO          YES
                   |           |
             Other HTTP/2      v
                         Native or Web?
                              |
                    +---------+---------+
                    |                   |
                 Native              gRPC-Web
                    |                   |
                    v                   v
               grpcurl          Burp + browser
                    |                   |
                    +---------+---------+
                              |
                              v
                        Reflection?
                              |
                    +---------+---------+
                    |                   |
                   YES                  NO
                    |                   |
                    v                   v
             Enumerate schema      Find .proto
                                   or protoset
                    |                   |
                    +---------+---------+
                              |
                              v
                       Map Services
                              |
                              v
                        Map Methods
                              |
                              v
                       Authentication
                              |
                              v
                        Authorisation
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
              Function                  Object
               Access                   Access
                  |                       |
                  +-----------+-----------+
                              |
                              v
                       Tenant Isolation
                              |
                              v
                      Input Validation
                              |
                              v
                       Business Logic
                              |
                              v
                         Streaming
                              |
                              v
                     Resource Controls
                              |
                              v
                      Error Disclosure
                              |
                              v
                         Evidence
                              |
                              v
                          Report
```

---

# What Not to Assume

Do not assume:

```text
Reflection enabled
=
critical vulnerability
```

Do not assume:

```text
HTTP 200
=
successful RPC
```

Do not assume:

```text
Protobuf
=
input is safe
```

Do not assume:

```text
mTLS
=
authorisation is solved
```

Do not assume:

```text
Internal service
=
trusted service
```

Do not assume:

```text
gRPC-Web
=
native gRPC
```

Do not assume:

```text
Unknown field
=
mass assignment
```

Do not assume:

```text
HTTP/2
=
gRPC
```

Do not assume:

```text
Authenticated stream
=
every message is authorised
```

These distinctions prevent many incorrect findings.

---

# Relationship With Other Notes

gRPC should be tested alongside:

```text
API Security
    |
    +-- docs/web/api-security.md

Authentication
    |
    +-- docs/web/authentication.md

Authorisation
    |
    +-- docs/web/authorisation.md

IDOR / BOLA
    |
    +-- docs/web/idor-bola.md

Mass Assignment
    |
    +-- docs/web/mass-assignment.md

JWT
    |
    +-- docs/web/jwt.md

OAuth
    |
    +-- docs/web/oauth-oidc.md

CORS
    |
    +-- docs/web/cors.md

CSRF
    |
    +-- docs/web/csrf.md

Business Logic
    |
    +-- docs/web/business-logic.md

Race Conditions
    |
    +-- docs/web/race-conditions.md

SQL Injection
    |
    +-- docs/web/sql-injection.md

Command Injection
    |
    +-- docs/web/command-injection.md

SSRF
    |
    +-- docs/web/ssrf.md

Path Traversal
    |
    +-- docs/web/path-traversal.md
```

---

# References

## OWASP gRPC Security Cheat Sheet

[OWASP gRPC Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/gRPC_Security_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }

Use this as one of the primary security references.

It covers areas including:

```text
Transport security
Authentication
Authorisation
Input validation
Rate limiting
Resource protection
Error handling
Monitoring
Security testing
```

---

## Official gRPC Documentation

[docs](https://grpc.io/docs/){ target="_blank" rel="noopener noreferrer" }

---

## gRPC Core Concepts

[gRPC Core Concepts](https://grpc.io/docs/what-is-grpc/core-concepts/){ target="_blank" rel="noopener noreferrer" }

Use this for:

```text
Service definitions
RPC types
Metadata
Channels
RPC lifecycle
Cancellation
```

---

## gRPC Guides

[gRPC Guides](https://grpc.io/docs/guides/){ target="_blank" rel="noopener noreferrer" }

Official guides covering:

```text
Authentication
Metadata
Reflection
Status codes
Retry
Health checking
Deadlines
Keepalive
```

---

## gRPC Authentication

[gRPC Authentication](https://grpc.io/docs/guides/auth/){ target="_blank" rel="noopener noreferrer" }

---

## gRPC Metadata

[gRPC Metadata](https://grpc.io/docs/guides/metadata/){ target="_blank" rel="noopener noreferrer" }

Important for understanding:

```text
Authentication metadata
Custom metadata
Headers
Trailers
```

---

## gRPC Reflection

[gRPC Reflection](https://grpc.io/docs/guides/reflection/){ target="_blank" rel="noopener noreferrer" }

---

## gRPC Status Codes

[gRPC Status Codes](https://grpc.io/docs/guides/status-codes/){ target="_blank" rel="noopener noreferrer" }

---

## gRPC Deadlines

[gRPC Deadlines](https://grpc.io/docs/guides/deadlines/){ target="_blank" rel="noopener noreferrer" }

---

## gRPC Cancellation

[gRPC Cancellation](https://grpc.io/docs/guides/cancellation/){ target="_blank" rel="noopener noreferrer" }

---

## gRPC Health Checking

[gRPC Health Checking](https://grpc.io/docs/guides/health-checking/){ target="_blank" rel="noopener noreferrer" }

---

## Protocol Buffers

[Protocol Buffers](https://protobuf.dev/){ target="_blank" rel="noopener noreferrer" }

---

## Protocol Buffers Programming Guides

[Protocol Buffers Programming Guides](https://protobuf.dev/programming-guides/){ target="_blank" rel="noopener noreferrer" }

---

## grpcurl

[grpcurl](https://github.com/fullstorydev/grpcurl){ target="_blank" rel="noopener noreferrer" }

`grpcurl` supports:

```text
Service reflection
.proto files
Protosets
JSON request input
Metadata
TLS
mTLS
Unary RPCs
Streaming RPCs
```

---

## Burp Suite BApp Store

[Burp Suite BApp Store](https://portswigger.net/bappstore){ target="_blank" rel="noopener noreferrer" }

Look for current extensions relevant to:

```text
Protocol Buffers
gRPC-Web
HTTP/2
```

Always verify the current extension version and maintenance status before relying on it.

---

## OWASP API Security

[OWASP API Security](https://owasp.org/API-Security/){ target="_blank" rel="noopener noreferrer" }

Many API security principles apply directly to gRPC services.

---

# Final Testing Model

```text
                         gRPC
                           |
                           v
                    IDENTIFICATION
                           |
              +------------+------------+
              |                         |
              v                         v
          Native gRPC                gRPC-Web
              |                         |
              v                         v
           grpcurl                 Browser/Burp
              |                         |
              +------------+------------+
                           |
                           v
                        SCHEMA
                           |
              +------------+------------+
              |                         |
              v                         v
          Reflection               .proto/protoset
              |                         |
              +------------+------------+
                           |
                           v
                     SERVICE MAP
                           |
              +------------+------------+
              |                         |
              v                         v
           Services                  Methods
                                        |
                                        v
                                    RPC Types
                                        |
                +----------+------------+-----------+
                |          |            |           |
                v          v            v           v
              Unary      Server       Client       Bidi
                         Stream       Stream       Stream
                |          |            |           |
                +----------+------------+-----------+
                           |
                           v
                     TRUST BOUNDARY
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
    Authentication     Metadata        Transport
          |                |                |
          v                v                v
        JWT/API       Identity/Tenant      TLS
          |             Headers            mTLS
          +----------------+----------------+
                           |
                           v
                     AUTHORISATION
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
       Method            Object           Tenant
          |                |                |
          +----------------+----------------+
                           |
                           v
                        INPUT
                           |
         +-----------------+------------------+
         |                 |                  |
         v                 v                  v
       Fields            Nested             Repeated
         |                Data               Data
         +-----------------+------------------+
                           |
                           v
                   SECURITY SINKS
                           |
      +----------+---------+---------+----------+
      |          |         |         |          |
      v          v         v         v          v
     SQL        OS        URL       File     Business
              Command     Fetch     Path      Logic
      |          |         |         |          |
      +----------+---------+---------+----------+
                           |
                           v
                       STREAMING
                           |
            +--------------+--------------+
            |              |              |
            v              v              v
         Per-message    Lifetime       Resources
           AuthZ         Auth          / Limits
            |              |              |
            +--------------+--------------+
                           |
                           v
                     RESILIENCE
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      Rate Limits      Deadlines       Size Limits
          |                |                |
          +----------------+----------------+
                           |
                           v
                    ERROR HANDLING
                           |
                           v
                     INFORMATION
                      DISCLOSURE
                           |
                           v
                       EVIDENCE
                           |
                           v
                        REPORT
                           |
                           v
                        RETEST
```

The central security question is:

> **Can a client invoke a gRPC service or method, manipulate its metadata or protobuf message, or interact with its streaming behaviour in a way that crosses an authentication, authorisation, tenant, object, input-validation, business-logic, or resource-control boundary?**

When testing gRPC, do not focus only on finding hidden methods.

The important model is:

```text
Service
   |
   v
Method
   |
   v
Authentication
   |
   v
Authorisation
   |
   v
Message
   |
   v
Business Logic
   |
   v
Resource
   |
   v
Response
```

For every RPC, ask:

```text
Who can call it?

Which object can they specify?

Which tenant can they specify?

Which fields can they control?

Which metadata can they control?

What server-side operation occurs?

What happens during a long-lived stream?

What resource cost does the call have?

What information does the response reveal?
```

That model makes gRPC security testing much easier to understand because the underlying vulnerabilities are often familiar web/API security problems expressed through a different protocol and application architecture.
