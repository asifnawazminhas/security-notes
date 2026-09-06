---
title: Insecure Deserialization Cheatsheet
description: Practical insecure deserialization cheatsheet for authorised application security testing covering discovery, serialized data identification, Java, .NET, PHP, Python, Ruby, Node.js, integrity protection, source review, Burp Suite, evidence, remediation and retesting.
---

# Insecure Deserialization Cheatsheet

Insecure deserialization occurs when an application deserializes attacker-controlled data in a way that allows the data to influence application objects, program behaviour or dangerous code paths.

A simplified flow is:

```text
Attacker-Controlled Data
          |
          v
      Decoder
          |
          v
    Deserializer
          |
          v
     Object Graph
          |
          v
Application Behaviour
```

The fundamental security question is:

```text
Can an attacker control serialized data that crosses
a trust boundary and is reconstructed into application objects?
```

Potential consequences depend heavily on the platform and implementation.

They may include:

```text
Object manipulation

Authorization bypass

Application logic manipulation

Integrity violations

Sensitive data exposure

Unexpected method invocation

Denial of service

Code execution
```

!!! warning "Authorised Security Testing"

    Perform deserialization testing only against systems explicitly included in the assessment scope. Start by identifying formats, trust boundaries and integrity controls. Do not deploy destructive gadget chains, execute operating-system commands, establish shells or modify production data simply to demonstrate unsafe deserialization.


# Core Concept

Serialization converts application state into a transferable or storable representation.

```text
Object
  |
  v
Serialize
  |
  v
Bytes / Text
```

Deserialization performs the reverse operation.

```text
Bytes / Text
     |
     v
Deserialize
     |
     v
Object
```


# Safe Trust Model

```text
Trusted Data
    |
    v
Deserializer
    |
    v
Expected Type
```


# Dangerous Trust Model

```text
Untrusted Data
      |
      v
Generic / Unsafe Deserializer
      |
      v
Object Construction
      |
      v
Unexpected Behaviour
```


# Important Distinction

Deserialization itself is normal application behaviour.

The problem arises when:

```text
Untrusted Input
      +
Unsafe Deserialization Behaviour
      +
Useful Security Impact
```

are combined.


# Quick Candidate Locations

Review:

```text
Cookies

Session tokens

Hidden form fields

API parameters

HTTP request bodies

Base64 values

Message queues

WebSocket messages

Cached objects

Uploaded files

Import/export functionality

Background jobs

RPC messages

Internal service messages

Database blobs

Signed application state
```


# Common Serialization Technologies

Potential formats and mechanisms include:

```text
Java native serialization

.NET BinaryFormatter

PHP serialize()

Python pickle

Ruby Marshal

YAML object deserialization

JSON polymorphic deserialization

XML object serialization

MessagePack

Protocol-specific object formats

Framework-specific state formats
```


# Serialization Is Not Encryption

A serialized value may be:

```text
Encoded

Compressed

Signed

Encrypted

Plaintext
```

These are different properties.


# Example

```text
Base64
```

does not mean:

```text
Encrypted
```


# Base64 Identification

Typical characters:

```text
A-Z

a-z

0-9

+

/

=
```


# Decode Suspicious Values

```bash
printf '%s' 'VALUE' | base64 -d
```


# Hex View

```bash
printf '%s' 'VALUE' | base64 -d | xxd
```


# File Identification

```bash
printf '%s' 'VALUE' | base64 -d > /tmp/object.bin
file /tmp/object.bin
```


# Strings

```bash
strings /tmp/object.bin | head -50
```


# Do Not Modify First

Initial workflow:

```text
Capture
  |
  v
Identify Encoding
  |
  v
Decode
  |
  v
Identify Format
  |
  v
Understand Integrity
  |
  v
Only Then Modify
```


# Discovery Workflow

```text
Application Traffic
        |
        v
Opaque / Structured Value
        |
        v
Encoding?
        |
        v
Serialization Format?
        |
        v
Integrity Protection?
        |
        v
Server Deserializes It?
        |
        v
Attacker Influence?
```


# Baseline First

Suppose the application sends:

```http
Cookie: session=BASE64_VALUE
```

Record:

```text
Original request

Original cookie

Original response

Authentication state

User identity

Response length

Response status
```


# Replay Unmodified

Before changing anything, replay the original request.

This verifies:

```text
The session is still valid

The request is reproducible

The baseline is stable
```


# Mutation Strategy

Do not begin with an exploitation payload.

Start with controlled mutations.

For example:

```text
Change one byte

Change one field

Remove one field

Change a type marker

Corrupt the end of the object
```


# Observe

Possible outcomes:

```text
Request accepted

Session invalidated

400 response

500 response

Deserializer error

Signature error

Application logic changes
```


# Interpretation Matters

A 500 error after changing opaque data does not prove insecure deserialization.

It may indicate:

```text
Invalid encoding

Invalid compression

Invalid signature

Parser failure

Deserializer failure

Application exception
```


# Integrity Protection

Serialized client-side state should normally have integrity protection if the server trusts it.

Possible controls include:

```text
MAC

Digital signature

Authenticated encryption

Server-side storage
```


# Integrity Model

```text
Serialized Data
      |
      +--> Integrity Tag
      |
      v
Server
      |
      v
Verify Integrity
      |
      +--> Valid -> Process
      |
      +--> Invalid -> Reject
```


# Integrity Before Deserialization

A strong design verifies integrity before dangerous object reconstruction.

Conceptually:

```text
Receive
  |
  v
Verify
  |
  v
Deserialize
```


# Dangerous Order

```text
Receive
  |
  v
Deserialize
  |
  v
Verify
```

If deserialization itself can trigger dangerous behaviour, verification afterwards may be too late.


# Signed Does Not Always Mean Safe

A signed serialized object may still be dangerous if:

```text
The attacker can obtain the signing key

The signing key is predictable

The application signs attacker-selected objects

Verification is flawed

Another service shares the key insecurely
```


# Encryption Does Not Replace Integrity

Encryption without authentication may not provide reliable tamper protection.

Prefer authenticated encryption where confidentiality and integrity are both required.


# Server-Side Sessions

A safer architecture often stores sensitive session state server-side.

Client:

```text
Random Session Identifier
```

Server:

```text
Session ID
   |
   v
Server-Side Session Store
```


# Client-Side State

If state must be client-side:

```text
Data
  |
  v
Strict Format
  |
  v
Authenticated Integrity Protection
```


# Java Native Serialization

Java native serialized streams commonly begin with the magic bytes:

```text
AC ED 00 05
```


# Base64 Representation

A Java serialized stream often begins with a Base64 prefix resembling:

```text
rO0AB
```

This is a useful indicator, not absolute proof.


# Identify

```bash
printf '%s' 'VALUE' | base64 -d | xxd | head
```


# Representative Output

```text
00000000: aced 0005 ...
```


# Interpretation

This strongly suggests:

```text
Java native serialization
```


# Java Source Search

```bash
rg -ni 'ObjectInputStream|readObject|readUnshared|ObjectOutputStream|writeObject' -g '*.java' .
```


# High-Interest Java Pattern

```java
ObjectInputStream input =
    new ObjectInputStream(request.getInputStream());

Object value = input.readObject();
```


# Source-to-Sink

```text
HTTP Request
     |
     v
ObjectInputStream
     |
     v
readObject()
     |
     v
Object Graph
```


# Java Review Questions

Ask:

```text
Can an external user reach readObject()?

What classes are available?

Is an ObjectInputFilter configured?

Are only expected classes permitted?

Is the data integrity-protected?

Can an attacker supply arbitrary serialized bytes?
```


# Java Object Filters

Modern Java provides object deserialization filtering mechanisms.

Review for:

```text
ObjectInputFilter
```

Search:

```bash
rg -ni 'ObjectInputFilter|setObjectInputFilter|setSerialFilter' -g '*.java' .
```


# Filtering Goal

Prefer:

```text
Expected Classes Only
```

rather than:

```text
Block Known Bad Classes
```


# Java Dependency Review

Potential impact can depend on classes available on the classpath.

Review:

```text
pom.xml

build.gradle

build.gradle.kts
```


# Search Dependencies

```bash
rg -ni 'commons-collections|commons-beanutils|groovy|spring|hibernate|xalan' pom.xml build.gradle build.gradle.kts
```


# Important

The presence of a library does not prove exploitability.

You still need:

```text
Reachable deserialization

Attacker control

Compatible object graph

Relevant security impact
```


# Java Errors

Useful indicators may include:

```text
java.io.StreamCorruptedException

java.io.InvalidClassException

java.io.OptionalDataException

java.lang.ClassNotFoundException
```


# Error Interpretation

A deserialization-related exception supports:

```text
Serialized data reached a Java deserialization path.
```

It does not automatically prove code execution.


# .NET Deserialization

Historically dangerous .NET mechanisms include:

```text
BinaryFormatter

LosFormatter

NetDataContractSerializer

ObjectStateFormatter
```

Security characteristics differ across serializers and framework versions.


# .NET Source Search

```bash
rg -ni 'BinaryFormatter|LosFormatter|NetDataContractSerializer|ObjectStateFormatter|Deserialize\(' -g '*.cs' .
```


# High-Risk Pattern

Conceptually:

```csharp
var formatter = new BinaryFormatter();
var obj = formatter.Deserialize(stream);
```


# Source-to-Sink

```text
Untrusted Stream
      |
      v
BinaryFormatter
      |
      v
Deserialize()
```


# BinaryFormatter

For modern .NET development, `BinaryFormatter` should not be used for untrusted data.

Do not attempt to make unsafe BinaryFormatter use safe through a simple type check after deserialization.


# .NET JSON

JSON deserialization is not automatically safe or unsafe.

Review:

```text
Type handling

Polymorphism

Custom converters

Binder configuration

Allowed types
```


# Newtonsoft.Json Search

```bash
rg -ni 'JsonConvert\.DeserializeObject|TypeNameHandling|SerializationBinder|ISerializationBinder' -g '*.cs' .
```


# High-Interest Setting

```text
TypeNameHandling
```

requires careful review when attacker-controlled JSON is deserialized.


# Example Concept

Attacker-controlled type metadata may allow the deserializer to choose unexpected runtime types when unsafe polymorphic settings are enabled.


# System.Text.Json

Search:

```bash
rg -ni 'JsonSerializer\.Deserialize|JsonPolymorphic|JsonDerivedType|TypeInfoResolver' -g '*.cs' .
```


# Review

Determine whether polymorphism is:

```text
Explicitly allowlisted

Bound to known derived types

Dynamically resolved
```


# ASP.NET ViewState

Legacy ASP.NET applications may expose:

```text
__VIEWSTATE
```

in forms.


# ViewState Is Not Automatically Vulnerable

Review:

```text
MAC validation

Machine keys

Encryption where required

Application configuration

Framework version
```


# Useful Fields

```text
__VIEWSTATE

__VIEWSTATEGENERATOR

__EVENTVALIDATION
```


# Do Not Disable Integrity Validation

A properly protected ViewState should reject tampering.


# PHP Serialization

PHP provides:

```text
serialize()

unserialize()
```


# Example Serialized Structure

```text
a:1:{s:4:"role";s:4:"user";}
```


# Common Markers

Examples include:

```text
a:
s:
i:
b:
O:
```


# Object Marker

```text
O:
```

may indicate a serialized PHP object.


# PHP Source Search

```bash
rg -ni 'serialize\(|unserialize\(' -g '*.php' .
```


# High-Risk Pattern

```php
$data = unserialize($_COOKIE['session']);
```


# Source-to-Sink

```text
Cookie
  |
  v
unserialize()
  |
  v
PHP Value / Object
```


# PHP Object Injection

PHP object deserialization becomes especially important when attacker-controlled data can instantiate classes with relevant magic methods.


# Magic Methods

Review:

```text
__construct

__destruct

__wakeup

__unserialize

__toString

__call

__get

__set
```


# Search Magic Methods

```bash
rg -n 'function\s+__(construct|destruct|wakeup|unserialize|toString|call|get|set)' -g '*.php' .
```


# PHP Review Workflow

```text
unserialize()
    |
    v
Attacker-Controlled?
    |
    v
Objects Allowed?
    |
    v
Available Classes
    |
    v
Magic Methods
    |
    v
Security-Relevant Side Effects?
```


# `allowed_classes`

PHP supports restricting classes during unserialization.

Review code using:

```text
allowed_classes
```


# Search

```bash
rg -n -C 5 'unserialize\(' -g '*.php' .
```


# Important

Class restrictions can reduce risk but replacing unsafe object serialization with a simpler data format is generally preferable for untrusted input.


# Python Pickle

Python's `pickle` format is designed to serialize Python object structures.

It is unsafe for untrusted input.


# Python Search

```bash
rg -ni 'pickle\.loads|pickle\.load|cPickle|dill\.loads|dill\.load' -g '*.py' .
```


# High-Risk Pattern

```python
import pickle

obj = pickle.loads(request.data)
```


# Source-to-Sink

```text
HTTP Body
   |
   v
pickle.loads()
   |
   v
Python Object Reconstruction
```


# Security Principle

Do not unpickle data received from an untrusted party.


# Base64-Wrapped Pickle

Applications sometimes:

```text
Serialize with pickle

Base64 encode

Send to client
```


# Model

```text
Object
  |
  v
pickle
  |
  v
Base64
  |
  v
Cookie
```

Base64 does not make pickle safe.


# Python `marshal`

Search:

```bash
rg -ni 'marshal\.loads|marshal\.load' -g '*.py' .
```


# YAML Deserialization

YAML parsers can support object construction depending on language and configuration.


# Python PyYAML Search

```bash
rg -ni 'yaml\.load|yaml\.unsafe_load|yaml\.full_load|yaml\.safe_load' -g '*.py' .
```


# Prefer

```python
yaml.safe_load(data)
```

for ordinary untrusted YAML data where YAML is required.


# Important

Even safe parsers still require:

```text
Schema validation

Business validation

Resource limits
```


# Ruby Marshal

Ruby supports:

```text
Marshal.dump

Marshal.load
```


# Search

```bash
rg -ni 'Marshal\.load|Marshal\.restore|Marshal\.dump' -g '*.rb' .
```


# High-Risk Pattern

```ruby
Marshal.load(user_data)
```


# YAML in Ruby

Search:

```bash
rg -ni 'YAML\.load|YAML\.unsafe_load|Psych\.load|safe_load' -g '*.rb' .
```


# Prefer Safe Loading

Use restricted deserialization appropriate to the application and Ruby/Psych version.


# Node.js

JavaScript applications more commonly exchange:

```text
JSON
```

than native object serialization.

However, unsafe deserialization may still occur through:

```text
Third-party serialization packages

YAML parsers

Custom object reconstruction

Dynamic type resolution
```


# Search Dependencies

```bash
rg -ni 'serialize|deserialize|yaml|js-yaml' package.json package-lock.json yarn.lock pnpm-lock.yaml
```


# Search Code

```bash
rg -ni 'deserialize|unserialize|yaml\.load|JSON\.parse' -g '*.js' -g '*.ts' .
```


# JSON.parse Is Not Equivalent to Native Object Deserialization

Normal:

```javascript
JSON.parse(userInput)
```

produces JSON-compatible values.

It does not inherently reconstruct arbitrary executable application classes.


# But Review Downstream Use

A parsed object may still become dangerous through:

```text
Prototype pollution

Dynamic module loading

Unsafe property assignment

Dynamic function invocation

Command construction
```


# JSON Deserialization

JSON is generally preferable to native object serialization for untrusted data because it represents simpler data structures.

However:

```text
JSON
```

does not mean:

```text
Secure application logic
```


# JSON Security Questions

Review:

```text
Is the schema validated?

Are unknown properties rejected?

Can users set privileged fields?

Is polymorphic type metadata accepted?

Are object prototypes affected?

Are values passed into dangerous sinks?
```


# JSON Polymorphism

Some frameworks allow a JSON field to determine the concrete object type.

Conceptually:

```json
{
  "type": "SomeClass",
  "data": {}
}
```


# Safe Model

```text
External Type Identifier
        |
        v
Explicit Allowlist
        |
        v
Known Application Type
```


# Dangerous Model

```text
External Type Identifier
        |
        v
Arbitrary Runtime Type Resolution
```


# XML Object Deserialization

XML can be used to represent object graphs in some frameworks.

Do not confuse:

```text
Unsafe Object Deserialization
```

with:

```text
XXE
```


# Different Risks

```text
XML Parser
   |
   +--> External Entity Handling -> XXE
   |
   +--> Object Reconstruction -> Deserialization Risk
```


# Message Queues

Serialized objects may enter applications through:

```text
RabbitMQ

Kafka

Redis queues

Cloud messaging

Background job systems
```


# Internal Does Not Mean Trusted

Ask:

```text
Who can publish messages?

Are producers authenticated?

Can a compromised service inject messages?

Is message integrity protected?

Does the consumer deserialize native objects?
```


# Background Jobs

Frameworks may serialize job parameters.

Review whether users can influence:

```text
Job class

Method name

Arguments

Object type

Queue payload
```


# Database Deserialization

Applications may store serialized blobs in databases.

Potential flow:

```text
User Input
   |
   v
Database
   |
   v
Serialized Blob
   |
   v
Later Deserialization
```


# Second-Order Deserialization

The initial input may not trigger immediate processing.

Example:

```text
Import Data
    |
    v
Store
    |
    v
Background Worker
    |
    v
Deserialize
```


# Import Functionality

Review file imports for:

```text
Serialized Java objects

Pickle files

PHP serialized objects

Ruby Marshal data

YAML

Framework backup formats
```


# Uploaded Files

A file upload may be:

```text
Accepted
```

and later:

```text
Deserialized by a background worker
```

This is different from ordinary file upload execution.


# Cookies

Cookies are a high-value location because applications sometimes store client-side state such as:

```text
User ID

Role

Preferences

Shopping cart

Session state
```


# Inspect Cookie Values

Look for:

```text
Base64

URL encoding

Hex

JSON

Compression

Known serialization signatures
```


# URL Decode

```bash
python3 - <<'PY'
from urllib.parse import unquote

value = "VALUE"
print(unquote(value))
PY
```


# Base64 Decode

```bash
printf '%s' 'VALUE' | base64 -d
```


# JWT Is Different

A JWT typically looks like:

```text
xxxxx.yyyyy.zzzzz
```

It is a structured signed or encrypted token format.

Do not classify every client-side token as insecure deserialization.


# JWT Model

```text
Header.Payload.Signature
```

JWT security is covered separately.


# Burp Suite Workflow

```text
Proxy
  |
  v
Identify Opaque / Structured Data
  |
  v
Send to Repeater
  |
  v
Replay Baseline
  |
  v
Decode Copy
  |
  v
Identify Format
  |
  v
Controlled Mutation
  |
  v
Observe Response
  |
  v
Correlate With Source / Errors
  |
  v
Capture Evidence
```


# Burp Decoder

Useful for:

```text
Base64

URL encoding

Hex
```


# Workflow

```text
Cookie
  |
  v
Decoder
  |
  v
Base64 Decode
  |
  v
Inspect
```


# Keep Original Value

Always preserve:

```text
Original encoded value

Decoded copy

Modified copy
```


# Burp Repeater

Use Repeater for controlled mutation.

Example baseline:

```http
GET /account HTTP/1.1
Host: target.example
Cookie: state=ORIGINAL_VALUE
```


# Replay

Verify:

```text
200 OK

Expected account

Expected session
```


# Controlled Mutation

Modify only one part of the decoded object.

Then re-encode using the same representation.


# Compare

Observe:

```text
Status code

Response body

Response length

Error

Authentication state

Authorization state
```


# Burp Comparer

Comparer can help identify subtle changes between:

```text
Original response

Mutated response
```


# Burp Scanner

Treat automated insecure deserialization findings as candidates requiring manual verification.


# Burp Extensions

Extensions can help inspect specific serialization formats.

Before using one:

```text
Verify source

Verify maintenance status

Understand what it modifies

Avoid sending sensitive data to external services
```


# Tamper Testing

A useful initial question is:

```text
Can I modify this client-side state without detection?
```


# Example Concept

Original decoded state:

```json
{
  "user": "alice",
  "role": "user"
}
```


# Controlled Mutation

```json
{
  "user": "alice",
  "role": "test"
}
```


# Possible Outcomes

```text
Rejected due to integrity check

Accepted but ignored

Accepted and application state changes

Deserializer error
```


# Important

If changing:

```text
role=user
```

to:

```text
role=admin
```

changes privileges, the finding may primarily be:

```text
Client-side authorization state manipulation
```

or:

```text
Broken access control
```

The serialized format is part of the mechanism.


# Do Not Conflate Findings

Ask:

```text
Is unsafe object reconstruction the vulnerability?

Is missing integrity protection the vulnerability?

Is authorization based on client-controlled state the vulnerability?

Are several issues combined?
```


# Error-Based Detection

Malformed serialized input may generate revealing errors.


# Java

Examples:

```text
StreamCorruptedException

InvalidClassException
```


# PHP

Examples may mention:

```text
unserialize()

offset

allowed memory
```


# Python

Examples may mention:

```text
_pickle.UnpicklingError

pickle data
```


# .NET

Errors may expose:

```text
BinaryFormatter

SerializationException

type resolution
```


# Error-Based Evidence

Useful for identifying the processing path.

Not sufficient alone to prove dangerous exploitability.


# Controlled Type Mutation

Where the serialization format contains explicit type information, changing it to another harmless invalid type can reveal whether type resolution occurs.


# Example Outcome

```text
Type 'Example.DoesNotExist' could not be resolved
```


# Interpretation

This can support:

```text
Attacker-controlled type metadata reaches a type resolver.
```


# Do Not Jump to Dangerous Types

A nonexistent test type is often sufficient to establish type resolution behaviour.


# Integrity Test

A single-byte mutation can answer:

```text
Is this object integrity-protected?
```


# Strong Integrity Response

```text
Invalid signature
```

or equivalent rejection.


# Weak Integrity Behaviour

If modified serialized state is accepted, investigate what the application trusts from it.


# MAC vs Hash

A plain hash such as:

```text
SHA256(data)
```

does not provide authenticity if an attacker can recompute it.


# Preferred

Use a keyed MAC such as:

```text
HMAC
```

or an authenticated encryption construction.


# Cryptographic Keys

Keys should be:

```text
Random

Secret

Appropriately scoped

Rotatable

Stored securely
```


# Shared Keys

If many applications share the same serialization signing key, compromise of one application may affect others.

Review key scope.


# Source Review Workflow

```text
Find Deserializer
       |
       v
Identify Data Source
       |
       v
External Control?
       |
       v
Integrity Verification?
       |
       v
Verification Before Deserialize?
       |
       v
Type Restrictions?
       |
       v
Dangerous Object Behaviour?
       |
       v
Security Impact
```


# Generic Source Search

```bash
rg -ni 'deserialize|unserialize|ObjectInputStream|readObject|BinaryFormatter|pickle\.load|Marshal\.load|yaml\.load' .
```


# Search With Context

```bash
rg -n -C 8 'ObjectInputStream|readObject|BinaryFormatter|unserialize\(|pickle\.loads|pickle\.load|Marshal\.load|yaml\.load' .
```


# Trace Sources

Look for:

```text
Request body

Cookie

Header

Query parameter

Uploaded file

Queue message

Database field
```


# Source-to-Sink Example

```text
Cookie
  |
  v
Base64 Decode
  |
  v
pickle.loads()
```


# Strong White-Box Finding

```text
Attacker-Controlled Input
        |
        v
Unsafe Deserializer
        |
        v
No Integrity Validation
```


# Type Allowlisting

Where object deserialization cannot be eliminated, permit only required types.

Prefer:

```text
Allow:
ExpectedTypeA
ExpectedTypeB
```

over:

```text
Block:
KnownBadType1
KnownBadType2
```


# Why Denylists Fail

Application dependencies change.

New dangerous types may become available.

An allowlist defines the intended object model.


# Schema Validation

For data formats such as JSON:

```text
Parse
  |
  v
Schema Validate
  |
  v
Map to Known Data Structure
```


# Prefer Data Transfer Objects

Use simple DTOs containing expected data rather than arbitrary application object graphs.


# Safe Architecture

```text
Untrusted JSON
     |
     v
JSON Parser
     |
     v
Strict Schema
     |
     v
DTO
     |
     v
Business Logic
```


# Avoid Native Object Graphs

Do not expose language-native object serialization formats across untrusted boundaries where simpler data formats are sufficient.


# Application Trust Boundaries

Document:

```text
Internet -> Application

Browser -> Server

Service -> Service

Queue -> Worker

Database -> Application

File Import -> Parser
```


# Internal Trust Boundaries

A message from another service may still be attacker-influenced.

Trace the original source rather than assuming:

```text
Internal = trusted
```


# Authentication Does Not Make Data Trusted

An authenticated normal user may still be able to submit malicious serialized data.


# Authorization Context

Determine:

```text
Unauthenticated

Normal user

Privileged user

Administrator

Internal service
```


# Multi-Tenant Systems

Ask:

```text
Can one tenant submit serialized objects?

Are tenant identifiers inside the serialized object?

Does the server trust them?

Can object state reference another tenant?
```


# Denial of Service

Deserialization can also introduce resource-consumption risks.

Examples:

```text
Deep nesting

Huge collections

Recursive structures

Large object graphs
```


# Use Minimal Resource Testing

Do not intentionally exhaust production resources.

Review:

```text
Size limits

Depth limits

Object count limits

Timeouts
```


# Deserialization and Gadget Chains

A gadget is existing code that performs security-relevant behaviour when triggered during or after deserialization.

Conceptually:

```text
Attacker Data
    |
    v
Deserializer
    |
    v
Existing Classes
    |
    v
Method Chain
    |
    v
Security-Relevant Effect
```


# Important

The presence of:

```text
Unsafe deserializer
```

does not automatically prove:

```text
A working code-execution gadget chain exists.
```


# Gadget Chain Assessment

Consider:

```text
Platform

Runtime version

Dependencies

Available classes

Deserializer behaviour

Security controls
```


# Safe Validation Strategy

Prefer:

```text
Format identification

Controlled corruption

Type resolution evidence

Source review

Harmless application-state change
```

before considering gadget-specific validation.


# Exploit Tools

Tools exist for generating serialized payloads for some ecosystems.

They should not replace understanding of:

```text
The actual deserializer

Available dependencies

Input transformations

Integrity controls

Application trust boundary
```


# Do Not Blindly Fire Payload Collections

Large serialized payload sets can cause:

```text
Application crashes

Resource exhaustion

Unexpected side effects

Monitoring noise
```


# False Positive - Base64

Observation:

```text
Cookie is Base64.
```

Conclusion:

```text
Encoding identified.
```

Not:

```text
Insecure deserialization.
```


# False Positive - Serialized Format

Observation:

```text
Cookie contains Java serialized bytes.
```

Conclusion:

```text
Java serialization appears to be used.
```

Not automatically:

```text
Exploitable insecure deserialization.
```


# False Positive - 500 Error

A malformed object causing:

```text
500 Internal Server Error
```

only establishes that the input caused an exception.


# False Positive - Class Name in Response

A class name may be present because:

```text
The application serialized it

A debugging feature exposed it

It is ordinary metadata
```


# False Positive - Signed Object

A signed object that rejects all modifications may not expose an attacker-controlled deserialization boundary.

Still review key management and verification order where relevant.


# False Positive - JSON

JSON parsing alone is not native object deserialization.


# False Positive - Scanner

Automated scanners may identify:

```text
Serialization signatures

Framework markers

Error strings
```

without proving exploitable behaviour.


# Evidence Collection

Capture:

```text
Finding ID

Endpoint

Method

Parameter / Cookie / Header

Authentication context

Original encoded value

Decoded format

Serialization technology

Integrity mechanism

Controlled mutation

Server response

Relevant error

Source-to-sink path

Deserializer API

Timestamp
```


# Sensitive Serialized Data

Do not place full:

```text
Session tokens

Secrets

Personal data

Authentication material
```

in screenshots or reports unnecessarily.


# Redact

Example:

```text
session=rO0AB...<redacted>...==
```


# Strong Black-Box Evidence

A defensible chain might be:

```text
1. Client receives serialized state.

2. Format is identified.

3. Controlled modification is made.

4. Modified object is accepted.

5. Server reconstructs attacker-controlled state.

6. Security-relevant application behaviour changes.

7. Result is repeatable.
```


# Strong White-Box Evidence

```text
1. External request value identified.

2. Value is decoded.

3. Data flows directly to unsafe deserializer.

4. No prior integrity verification exists.

5. Deserializer permits dangerous object reconstruction.

6. Reachability is confirmed.
```


# Reporting Example - Unsafe Native Deserialization

> The application deserializes attacker-controlled data using a native object deserialization mechanism. The serialized value is accepted from the client and reaches the deserializer without an appropriate trusted-data boundary. Controlled mutations confirmed that client-supplied serialized state is processed by the server. Native object deserialization should not be used for untrusted input.


# Reporting Example - Client-Side Serialized State

> The application stores security-relevant state in a client-controlled serialized object. The object can be modified and re-submitted without effective integrity validation. A controlled change to the serialized state was accepted by the server and altered application behaviour. Security-sensitive state should not be trusted from the client without cryptographic integrity protection and server-side authorization.


# Reporting Example - Java

> The application passes attacker-controlled serialized data to `ObjectInputStream.readObject()`. The input reaches Java native deserialization before any effective trust validation. This exposes the application to unsafe object reconstruction and should be replaced with a constrained data format and explicit schema validation.


# Reporting Example - Python

> Attacker-controlled request data is passed to `pickle.loads()`. Python pickle is capable of reconstructing arbitrary Python objects and is not designed for untrusted input. The application should replace pickle at this trust boundary with a data-only format such as JSON and explicit schema validation.


# Reporting Example - PHP

> The application passes a client-controlled value to PHP `unserialize()`. The deserializer is therefore able to reconstruct values and potentially objects based on attacker-controlled serialized input. The application should avoid PHP object serialization across untrusted boundaries and use a constrained data representation instead.


# Reporting Example - .NET

> The application deserializes attacker-controlled input using `BinaryFormatter`. This API is unsuitable for untrusted data because object reconstruction can invoke unexpected runtime behaviour. The serialized interface should be redesigned using a constrained serializer and explicitly defined data types.


# Reporting Example - Polymorphic JSON

> The API accepts attacker-controlled type metadata during JSON deserialization. The configured deserializer can resolve runtime types based on values supplied in the request rather than restricting deserialization to an explicit set of application types. Polymorphic deserialization should be constrained to an allowlist of known types.


# Reporting Actual Impact

Separate:

```text
Mechanism
```

from:

```text
Impact
```


# Example

Mechanism:

```text
Unsafe Java native deserialization
```

Demonstrated impact:

```text
Attacker-controlled object reconstruction
```

Potential impact:

```text
Further impact depends on available classes and runtime configuration.
```


# Avoid

```text
This vulnerability allows remote code execution.
```

unless remote code execution was actually established and was necessary to demonstrate severity.


# Severity Considerations

Assess:

```text
Remote reachability

Authentication required

Integrity protection

Deserializer type

Available classes

Application privileges

Sensitive state

Network access

Tenant boundaries

Demonstrated impact
```


# Remediation Priority

The strongest remediation is usually:

```text
Remove unsafe native object deserialization
from untrusted boundaries.
```


# Prefer Data-Only Formats

Examples:

```text
JSON

Protocol Buffers

Explicit message schemas
```

The important property is:

```text
Known Data Structure
```

rather than arbitrary runtime object reconstruction.


# JSON Example

Instead of:

```text
Serialized User Object
```

use:

```json
{
  "user_id": "12345",
  "preferences": {
    "language": "en"
  }
}
```


# Validate Schema

Expected:

```text
user_id -> string

preferences -> object

language -> allowlisted string
```


# Reject Unknown Fields Where Appropriate

This can reduce:

```text
Mass assignment

Unexpected state manipulation

Type confusion
```


# Do Not Trust Authorization Fields

Even with safe JSON:

```json
{
  "role": "admin"
}
```

must not become authoritative simply because it parsed successfully.


# Authorization Must Be Server-Side

```text
Authenticated Identity
       |
       v
Server Authorization Data
       |
       v
Access Decision
```


# Integrity Protection

If client-side state is unavoidable:

```text
Serialize Data
    |
    v
MAC / Authenticated Encryption
    |
    v
Client
```

On return:

```text
Client Value
    |
    v
Verify Integrity
    |
    v
Parse
```


# Key Rotation

Design for:

```text
Key rotation

Key versioning

Session invalidation

Limited key scope
```


# Least Privilege

Run deserialization components with minimal:

```text
Filesystem access

Network access

Process privileges

Cloud permissions
```


# Dependency Reduction

Reducing unnecessary dependencies can reduce the number of classes and behaviours available to dangerous deserialization paths.

This is defence in depth.


# Error Handling

Do not expose:

```text
Classpaths

Stack traces

Framework internals

Serializer configuration
```

to external users.


# Monitoring

Potential detection signals include:

```text
Repeated malformed serialized objects

Unexpected type names

Deserializer exceptions

Large serialized payloads

Unusual object graphs

Repeated integrity failures
```


# Retesting

Retest the original data path.


# Retest Baseline

Confirm legitimate functionality still works.


# Retest Original Serialized Object

If the application was redesigned:

```text
Legacy serialized format should no longer be accepted.
```


# Retest Mutation

A modified client-side state value should either:

```text
Fail integrity validation
```

or:

```text
Be treated purely as non-authoritative data
```


# Retest Type Injection

Unexpected type identifiers should be rejected before object construction.


# Retest Source

Verify:

```text
Unsafe deserializer removed

Schema validation added

Explicit types used

Integrity checked before parsing where appropriate
```


# Retest Authorization

If the original object contained:

```text
Role

User ID

Tenant ID

Permission
```

verify that changing these values cannot alter authorization decisions.


# Root Cause Review

After finding one deserialization issue, search the entire codebase.


# Java

```bash
rg -ni 'ObjectInputStream|readObject|readUnshared|XMLDecoder' -g '*.java' .
```


# .NET

```bash
rg -ni 'BinaryFormatter|LosFormatter|NetDataContractSerializer|ObjectStateFormatter|Deserialize\(|TypeNameHandling' -g '*.cs' .
```


# PHP

```bash
rg -ni 'unserialize\(' -g '*.php' .
```


# Python

```bash
rg -ni 'pickle\.load|pickle\.loads|cPickle|dill\.load|dill\.loads|marshal\.load|marshal\.loads|yaml\.load|yaml\.unsafe_load' -g '*.py' .
```


# Ruby

```bash
rg -ni 'Marshal\.load|Marshal\.restore|YAML\.load|YAML\.unsafe_load' -g '*.rb' .
```


# Node.js

```bash
rg -ni 'deserialize|unserialize|yaml\.load|js-yaml' -g '*.js' -g '*.ts' .
```


# Generic

```bash
rg -ni 'deserialize|unserialize|readObject|BinaryFormatter|pickle|Marshal\.load|yaml\.load' .
```


# Review Integrity Controls

Search:

```bash
rg -ni 'HMAC|MAC|signature|verify|signed|encrypt|decrypt|AES|GCM' src/
```


# Do Not Assume Nearby Crypto Protects the Object

Trace:

```text
Exact Data

Exact Key

Exact Verification

Exact Order of Operations
```


# Practical Deserialization Checklist

## Discovery

- [ ] Cookies reviewed
- [ ] Session state reviewed
- [ ] Hidden fields reviewed
- [ ] Request bodies reviewed
- [ ] API parameters reviewed
- [ ] WebSocket messages reviewed
- [ ] Upload/import formats reviewed
- [ ] Message queues reviewed
- [ ] Background jobs reviewed
- [ ] Database blobs reviewed
- [ ] Base64 values reviewed
- [ ] Framework-specific state reviewed

## Identification

- [ ] Encoding identified
- [ ] Compression considered
- [ ] Serialization format identified
- [ ] Runtime/language identified
- [ ] Raw bytes inspected
- [ ] Original value preserved

## Baseline

- [ ] Original request replayed
- [ ] Authentication state recorded
- [ ] User identity recorded
- [ ] Response status recorded
- [ ] Response length recorded
- [ ] Baseline confirmed stable

## Integrity

- [ ] Controlled mutation performed
- [ ] Integrity rejection checked
- [ ] MAC/signature identified
- [ ] Verification order reviewed
- [ ] Key scope considered
- [ ] Encryption distinguished from integrity

## Java

- [ ] Native serialization identified
- [ ] `ObjectInputStream` searched
- [ ] `readObject()` searched
- [ ] Object filters reviewed
- [ ] Dependencies reviewed
- [ ] Reachability confirmed

## .NET

- [ ] `BinaryFormatter` searched
- [ ] Legacy formatters reviewed
- [ ] JSON polymorphism reviewed
- [ ] `TypeNameHandling` reviewed
- [ ] Type restrictions reviewed
- [ ] ViewState configuration reviewed where relevant

## PHP

- [ ] `unserialize()` searched
- [ ] Object input identified
- [ ] Magic methods reviewed
- [ ] `allowed_classes` reviewed
- [ ] Relevant classes reviewed

## Python

- [ ] `pickle` searched
- [ ] `dill` searched
- [ ] `marshal` searched
- [ ] unsafe YAML loading reviewed
- [ ] External input traced

## Ruby

- [ ] `Marshal.load` searched
- [ ] unsafe YAML loading reviewed
- [ ] External input traced

## JSON

- [ ] Schema validation reviewed
- [ ] Unknown fields reviewed
- [ ] Polymorphism reviewed
- [ ] Runtime type resolution reviewed
- [ ] Authorization fields reviewed
- [ ] Mass assignment considered

## Evidence

- [ ] Endpoint
- [ ] Parameter/cookie/header
- [ ] Authentication context
- [ ] Original encoded value
- [ ] Serialization format
- [ ] Controlled mutation
- [ ] Response
- [ ] Relevant error
- [ ] Source-to-sink path
- [ ] Integrity mechanism
- [ ] Timestamp
- [ ] Sensitive values redacted

## Remediation

- [ ] Native object deserialization removed where possible
- [ ] Data-only format used
- [ ] Schema validation implemented
- [ ] Explicit type allowlist implemented
- [ ] Integrity protection implemented where required
- [ ] Integrity verified before dangerous processing
- [ ] Authorization moved server-side
- [ ] Least privilege reviewed
- [ ] Dependencies reviewed

## Retest

- [ ] Legitimate functionality works
- [ ] Legacy unsafe format rejected
- [ ] Controlled mutation rejected
- [ ] Unexpected type rejected
- [ ] Authorization manipulation fails
- [ ] Source fix verified
- [ ] Equivalent sinks reviewed


# Serialization Technology Matrix

| Platform | High-Interest Mechanisms |
|---|---|
| Java | Native serialization, `ObjectInputStream`, `readObject()` |
| .NET | `BinaryFormatter`, legacy formatters, unsafe polymorphic JSON |
| PHP | `serialize()`, `unserialize()` |
| Python | `pickle`, `dill`, `marshal`, unsafe YAML loading |
| Ruby | `Marshal`, unsafe YAML loading |
| Node.js | Third-party serializers, YAML, custom reconstruction |
| Cross-platform | JSON polymorphism, XML object mapping, message formats |


# Input Location Matrix

| Location | Why Review It |
|---|---|
| Cookie | Client-controlled application/session state |
| Hidden field | State may round-trip through browser |
| Request body | Direct parser/deserializer input |
| API field | Type or object data may be externally supplied |
| WebSocket | Structured state may bypass ordinary HTTP review |
| Uploaded file | Import processor may deserialize content |
| Queue message | Worker may trust producer data |
| Database blob | Potential second-order deserialization |
| Cache | Serialized objects may cross trust boundaries |


# Observation Matrix

| Observation | Supports | Does Not Automatically Prove |
|---|---|---|
| Base64 value | Encoding | Serialization |
| Java magic bytes | Java serialization format | Exploitability |
| PHP serialized syntax | PHP serialization | Object injection impact |
| Pickle use in source | Python serialization | External reachability |
| Deserializer error | Deserialization path | Code execution |
| Modified state accepted | Weak/missing integrity | Native object exploitability |
| Type resolution error | Dynamic type processing | Gadget availability |
| Unsafe sink + external input | Strong candidate | Specific impact until validated |


# Trust Matrix

| Data Source | Trust Assumption |
|---|---|
| Browser cookie | Untrusted |
| HTTP body | Untrusted |
| Query parameter | Untrusted |
| Uploaded file | Untrusted |
| Authenticated user input | Untrusted |
| Database value derived from user input | Untrusted |
| Queue message from externally influenced producer | Potentially untrusted |
| Hard-coded server object | Trusted by origin, subject to code integrity |


# Deserialization vs Related Issues

| Behaviour | Likely Classification |
|---|---|
| Native object reconstruction from attacker data | Insecure Deserialization |
| Client changes role field and server trusts it | Broken Access Control / State Integrity |
| JSON automatically binds unexpected fields | Mass Assignment |
| XML resolves external entity | XXE |
| YAML constructs unsafe runtime object | Unsafe Deserialization |
| User controls runtime type selection | Polymorphic Deserialization Risk |
| Encoded cookie reveals data | Information Disclosure / Client-Side State |
| Signed state uses weak key | Cryptographic / Integrity Issue |


# Source Review Priority Matrix

| Pattern | Priority |
|---|---:|
| JSON to fixed DTO + schema validation | Lower |
| Explicit polymorphic allowlist | Review |
| Signed serialized state | Review verification and key management |
| Native deserializer on server-only trusted file | Context dependent |
| Native deserializer on client data | Very High |
| `pickle.loads(request.data)` | Very High |
| `unserialize($_COOKIE[...])` | Very High |
| `ObjectInputStream` on request body | Very High |
| `BinaryFormatter.Deserialize()` on external input | Very High |
| Dynamic runtime type resolution from request | Very High |


# Remediation Matrix

| Control | Purpose |
|---|---|
| Remove native object serialization | Eliminate dangerous object reconstruction |
| Data-only format | Reduce object behaviour |
| Schema validation | Restrict accepted structure |
| Explicit type allowlist | Prevent arbitrary runtime types |
| Server-side session state | Remove trusted state from client |
| HMAC/authenticated encryption | Protect client-side state integrity |
| Verification before parsing | Reject tampering before dangerous processing |
| Least privilege | Reduce impact |
| Resource limits | Reduce deserialization DoS |
| Dependency reduction | Reduce available dangerous behaviour |


# Burp Quick Workflow

```text
              OPAQUE / STRUCTURED VALUE
                        |
                        v
                     BASELINE
                        |
                        v
                      DECODE
                        |
                        v
                 IDENTIFY FORMAT
                        |
             +----------+----------+
             |                     |
             v                     v
      INTEGRITY CHECK?        NO INTEGRITY?
             |                     |
             v                     v
      CONTROLLED MUTATION    CONTROLLED MUTATION
             |                     |
             +----------+----------+
                        |
                        v
                 OBSERVE RESULT
                        |
                        v
                 IDENTIFY SINK
                        |
                        v
                  CAPTURE EVIDENCE
```


# White-Box Review Model

```text
                   EXTERNAL INPUT
                        |
                        v
                 DECODING LAYER
                        |
                        v
                INTEGRITY CHECK?
                        |
             +----------+----------+
             |                     |
             v                     v
            YES                    NO
             |                     |
             v                     |
       VERIFY FIRST                |
             |                     |
             +----------+----------+
                        |
                        v
                   DESERIALIZER
                        |
                        v
                 TYPE RESTRICTION?
                        |
             +----------+----------+
             |                     |
             v                     v
          STRICT                GENERIC
             |                     |
             v                     v
       EXPECTED DATA        OBJECT GRAPH
```


# Secure Design Model

```text
                UNTRUSTED INPUT
                      |
                      v
                DATA FORMAT
                      |
                      v
               STRICT PARSER
                      |
                      v
              SCHEMA VALIDATION
                      |
                      v
                    DTO
                      |
                      v
              BUSINESS LOGIC
                      |
                      v
          SERVER-SIDE AUTHORIZATION
```


# Client-Side State Model

```text
                 APPLICATION STATE
                        |
                        v
                  SERIALIZE DATA
                        |
                        v
                INTEGRITY PROTECT
                        |
                        v
                     CLIENT
                        |
                        v
                  RETURN VALUE
                        |
                        v
                VERIFY INTEGRITY
                        |
                        v
                    PARSE DATA
```


# Practical Validation Model

```text
Prerequisites
     |
     v
Capture Baseline
     |
     v
Identify Encoding
     |
     v
Identify Serialization
     |
     v
Determine Trust Boundary
     |
     v
Check Integrity
     |
     v
Controlled Mutation
     |
     v
Interpret Result
     |
     v
Source-to-Sink Validation
     |
     v
Conclusion
     |
     v
Remediation
     |
     v
Retest
```


# Final Testing Principle

The key question is not:

```text
Is this value serialized?
```

It is:

```text
CAN ATTACKER-CONTROLLED DATA
           |
           v
CROSS A TRUST BOUNDARY
           |
           v
REACH AN OBJECT DESERIALIZER
           |
           v
AND INFLUENCE SECURITY-RELEVANT BEHAVIOUR?
```

A strong workflow is:

```text
Identify Candidate State
        |
        v
Preserve Original
        |
        v
Decode
        |
        v
Identify Format
        |
        v
Identify Deserializer
        |
        v
Determine Integrity Protection
        |
        v
Perform Controlled Mutation
        |
        v
Observe Server Behaviour
        |
        v
Trace Source to Sink
        |
        v
Determine Actual Impact
        |
        v
Capture Evidence
        |
        v
Replace Unsafe Object Deserialization
        |
        v
Retest
```

For every deserialization candidate ask:

```text
Where did this value originate?

Can an attacker control it?

Is it merely encoded?

Is it encrypted?

Is it integrity-protected?

What serialization format is used?

Which runtime deserializes it?

Which API performs deserialization?

Does verification happen before deserialization?

Can the attacker influence object types?

Are types explicitly allowlisted?

Does the format reconstruct native objects?

Are dangerous magic methods or callbacks available?

Are third-party classes involved?

Is this a client-side state problem instead?

Is authorization based on values inside the object?

Could this be second-order?

Does a queue or worker deserialize it later?

Can I demonstrate the issue with a harmless mutation?

Is a gadget chain actually required to prove impact?

Am I claiming RCE without demonstrating it?

Could a simpler data-only format replace this mechanism?

Can authorization state be moved server-side?

Have equivalent deserialization sinks been reviewed?
```

The strongest conclusion is not:

```text
The cookie contains serialized data.
```

It is:

```text
ATTACKER-CONTROLLED DATA
          |
          v
CROSSES TRUST BOUNDARY
          |
          v
UNSAFE DESERIALIZATION
          |
          v
SECURITY-RELEVANT BEHAVIOUR
          |
          v
REPEATABLE RESULT
```


# Related Cheatsheets

- [Web Application Security Cheatsheet](web.md)
- [Burp Suite Cheatsheet](burp-suite.md)
- [Git and ripgrep Cheatsheet](git-ripgrep.md)
- [Server-Side Template Injection Cheatsheet](ssti.md)
- [OS Command Injection Cheatsheet](command-injection.md)
- [File Upload Security Cheatsheet](file-upload.md)
- [XML External Entity Injection (XXE) Cheatsheet](xxe.md)


# Related Notes

- [Insecure Deserialization](../web/deserialization.md)
- [Source Code Review](../source-code-review/index.md)


# References

- [PortSwigger Web Security Academy - Insecure Deserialization](https://portswigger.net/web-security/deserialization){ target="_blank" rel="noopener noreferrer" }
- [OWASP Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html){ target="_blank" rel="noopener noreferrer" }
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/){ target="_blank" rel="noopener noreferrer" }
- [CWE-502 - Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html){ target="_blank" rel="noopener noreferrer" }
- [Java Serialization Filtering](https://docs.oracle.com/en/java/javase/17/core/serialization-filtering1.html){ target="_blank" rel="noopener noreferrer" }
- [Python pickle Documentation](https://docs.python.org/3/library/pickle.html){ target="_blank" rel="noopener noreferrer" }
- [PHP unserialize Documentation](https://www.php.net/manual/en/function.unserialize.php){ target="_blank" rel="noopener noreferrer" }
- [.NET BinaryFormatter Security Guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide){ target="_blank" rel="noopener noreferrer" }


!!! tip "Identify the trust boundary first"

    A serialization format is not a vulnerability by itself. Determine whether attacker-controlled data actually crosses a trust boundary and reaches a deserializer.


!!! tip "Use controlled mutations"

    A one-field or one-byte change can reveal integrity protection, parsing behaviour and server trust without requiring dangerous gadget chains.


!!! tip "Separate the mechanism from the impact"

    Unsafe native deserialization, missing state integrity and broken authorization can appear together but are not identical vulnerabilities. Report the root cause and demonstrated impact accurately.


!!! tip "Prefer data, not objects"

    Untrusted interfaces should normally exchange explicitly defined data structures rather than serialized runtime object graphs.


!!! warning "Base64 is not a security control"

    Encoding serialized data does not provide confidentiality, integrity or authenticity.


!!! warning "Do not prove deserialization with command execution"

    If controlled mutations, type-resolution behaviour or source-to-sink analysis already establish unsafe deserialization, operating-system command execution usually adds unnecessary risk without improving the technical conclusion.
