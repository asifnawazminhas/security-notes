# Insecure Deserialization

Insecure deserialization vulnerabilities occur when an application processes serialized data that can be influenced by an attacker.

Serialization converts an object or data structure into a format that can be stored or transmitted.

Deserialization performs the reverse operation.

```text
Application Object
       ↓
Serialization
       ↓
Serialized Data
       ↓
Storage / HTTP / Queue / File
       ↓
Deserialization
       ↓
Application Object
```

The security problem appears when an application trusts serialized data from an untrusted source.

Depending on the technology and application, insecure deserialization can potentially lead to:

```text
Authentication bypass
Authorisation bypass
Object manipulation
Application logic manipulation
Privilege escalation
Arbitrary file operations
Server-side request behaviour
Denial of service
Remote code execution
```

The exact impact depends heavily on the serialization format, available classes or libraries, and how the resulting object is used.

!!! warning "Authorised Security Testing"
    Perform deserialization testing only against systems for which you have explicit authorisation. Start with non-destructive modifications and establish whether serialized data is trusted before attempting higher-impact validation.

---

# Understanding Serialization

Applications frequently need to transfer complex data between different components.

Instead of transmitting an in-memory object directly, the application converts it into a representation suitable for transmission or storage.

For example:

```text
Object
  ↓
Serialize
  ↓
Bytes / Text
  ↓
Transport
  ↓
Deserialize
  ↓
Object
```

Serialized data may appear in:

```text
Cookies
HTTP parameters
POST bodies
API requests
Hidden form fields
WebSockets
Files
Message queues
Caches
Session storage
Database records
Inter-service communication
```

The representation depends on the technology being used.

---

# Why Deserialization Becomes Dangerous

Consider an application that creates an object containing information about the current user:

```text
User
├── username = alice
├── role = user
└── authenticated = true
```

The application serializes this object and sends it to the client.

Conceptually:

```text
User Object
     ↓
Serialization
     ↓
Client-Controlled Data
     ↓
HTTP Request
     ↓
Deserialization
     ↓
Trusted User Object
```

If the client can modify the serialized representation and the server does not verify its integrity, the application may trust attacker-controlled properties.

For example:

```text
role=user
```

might become:

```text
role=admin
```

This represents a relatively simple form of object manipulation.

Some serialization frameworks introduce considerably more dangerous behaviour because object reconstruction can trigger:

```text
Constructors
Magic methods
Property accessors
Callbacks
Reflection
Object hooks
Library methods
Nested object chains
```

This is why insecure deserialization can sometimes become a code execution vulnerability.

---

# Deserialization Testing Methodology

A useful workflow is:

```text
Identify Serialized Data
        ↓
Determine Format
        ↓
Determine Technology
        ↓
Decode Safely
        ↓
Understand Object Structure
        ↓
Modify Non-Sensitive Property
        ↓
Re-encode
        ↓
Replay Request
        ↓
Observe Behaviour
        ↓
Test Integrity Protection
        ↓
Investigate Object Processing
        ↓
Determine Security Impact
```

Do not immediately assume every opaque value is serialized data.

First determine what the application is actually processing.

---

# Finding Serialized Data

During an assessment, inspect:

```text
Cookies
Session values
Hidden parameters
POST parameters
JSON properties
Base64-looking values
Binary request bodies
API requests
WebSocket messages
Uploaded files
Downloadable application state
Framework-specific parameters
```

Potential indicators include:

```text
Long Base64 values
Binary data
Recognisable object names
Class names
Type metadata
Structured key/value pairs
Framework-specific signatures
```

---

# Start With Burp Suite

A practical workflow begins with:

```text
Burp Proxy
    ↓
HTTP History
    ↓
Inspect Request
    ↓
Identify Suspicious Value
    ↓
Send to Repeater
    ↓
Decode
    ↓
Modify
    ↓
Encode
    ↓
Replay
    ↓
Compare Response
```

Burp Suite Decoder can help when values are encoded using:

```text
Base64
URL encoding
Hex
HTML encoding
```

For more complicated formats, external tools or Burp extensions may be required.

---

# Encoding Is Not Serialization

An important distinction is:

```text
Encoding ≠ Serialization
```

For example:

```text
YWRtaW49ZmFsc2U=
```

is Base64.

Decoding it reveals:

```text
admin=false
```

That does not automatically mean the value contains a serialized object.

Similarly:

```text
URL encoding
Base64
Hex
Compression
Encryption
Serialization
```

are different concepts.

Multiple layers may also exist:

```text
Object
 ↓
Serialization
 ↓
Compression
 ↓
Base64
 ↓
URL Encoding
```

Testing therefore sometimes requires reversing several transformations.

---

# Identifying Serialization Formats

Different technologies use different formats.

Common environments include:

```text
Java
PHP
.NET
Python
Ruby
Node.js
```

The first goal is fingerprinting.

Ask:

```text
What generated this value?

What framework is being used?

Does the data contain type information?

Can the value be decoded?

Is integrity protection present?

Does changing one byte break processing?
```

---

# Java Serialization

Java native serialization commonly begins with the hexadecimal bytes:

```text
AC ED 00 05
```

A Base64-encoded Java serialized object frequently begins with:

```text
rO0AB
```

This is a useful indicator during HTTP traffic analysis.

Example:

```text
rO0ABXNy...
```

Conceptually:

```text
Java Object
    ↓
ObjectOutputStream
    ↓
Serialized Byte Stream
    ↓
ObjectInputStream
    ↓
Java Object
```

Interesting Java APIs include:

```text
ObjectInputStream
readObject()
readUnshared()
XMLDecoder
```

During source-code review, searching for deserialization APIs can quickly identify potential sinks.

```bash
grep -RniE 'ObjectInputStream|readObject|readUnshared|XMLDecoder' .
```

---

# Java `readObject()`

A particularly important method is:

```java
readObject()
```

For example:

```java
ObjectInputStream in =
    new ObjectInputStream(request.getInputStream());

Object obj = in.readObject();
```

If the input originates from an untrusted source, this should receive careful review.

The important data flow is:

```text
HTTP Request
     ↓
request.getInputStream()
     ↓
ObjectInputStream
     ↓
readObject()
     ↓
Object Reconstruction
```

The presence of `readObject()` does not by itself prove exploitability.

You still need to establish:

```text
Input controllability
Reachability
Allowed classes
Class path
Filtering
Integrity controls
Application behaviour
```

---

# Java Gadget Chains

Java deserialization vulnerabilities are commonly discussed in relation to gadget chains.

A gadget is existing code within the application or one of its dependencies that performs some useful operation when invoked in a particular way.

Conceptually:

```text
Deserialization
      ↓
Method A
      ↓
Method B
      ↓
Library Behaviour
      ↓
Sensitive Sink
```

A collection of connected gadgets forms a gadget chain.

The application does not necessarily contain deliberately malicious code.

Instead, existing classes may be connected in an unintended way during object reconstruction.

Potentially sensitive sinks include:

```text
Process execution
Reflection
File operations
Network operations
Class loading
Expression evaluation
Script execution
```

---

# ysoserial

A well-known research tool for studying Java deserialization gadget chains is `ysoserial`.

Repository:

https://github.com/frohoff/ysoserial

It contains implementations of gadget chains associated with various Java libraries.

A useful starting command is:

```bash
java -jar ysoserial.jar
```

This displays the gadget chains supported by the installed version.

The general research workflow should be:

```text
Identify Java Serialization
        ↓
Identify Application Libraries
        ↓
Identify Versions
        ↓
Review Known Gadget Candidates
        ↓
Determine Reachability
        ↓
Use Non-Destructive Validation
        ↓
Establish Impact
```

Do not treat gadget generators as a substitute for understanding the application.

---

# Java Dependency Identification

Potential gadget chains often depend on particular libraries being present.

Look for:

```text
pom.xml
build.gradle
WEB-INF/lib/
JAR files
Dependency manifests
Application archives
```

Useful commands include:

```bash
find . -type f -name "*.jar"
```

and:

```bash
find . -type f \( -name "pom.xml" -o -name "build.gradle" \)
```

For extracted Java web applications:

```bash
find WEB-INF/lib -type f -name "*.jar"
```

You can inspect a JAR:

```bash
jar tf application.jar | less
```

Search for a particular class:

```bash
jar tf application.jar | grep -i "classname"
```

The class path matters because a gadget chain requiring a library that is not installed is generally not useful against that application.

---

# PHP Serialization

PHP supports native object serialization.

A simple serialized value may look like:

```text
a:2:{s:8:"username";s:5:"alice";s:4:"role";s:4:"user";}
```

PHP objects may contain representations beginning with:

```text
O:
```

For example:

```text
O:4:"User":2:{...}
```

Interesting PHP functions include:

```php
serialize()
unserialize()
```

A potentially dangerous pattern is:

```php
$data = unserialize($_COOKIE['session']);
```

The trust boundary is immediately interesting:

```text
Cookie
  ↓
unserialize()
  ↓
PHP Object
```

---

# Reading PHP Serialized Data

Consider:

```text
a:2:{s:8:"username";s:5:"alice";s:4:"role";s:4:"user";}
```

Some common markers are:

```text
a = array
s = string
i = integer
b = boolean
O = object
N = NULL
```

For example:

```text
s:5:"alice";
```

means a string containing five characters.

Understanding this format manually can be useful when reviewing simple objects.

---

# PHP Object Injection

PHP object injection occurs when attacker-controlled serialized data causes arbitrary PHP objects to be instantiated.

The impact depends on available classes and their magic methods.

Important PHP magic methods include:

```text
__construct()
__destruct()
__wakeup()
__sleep()
__toString()
__call()
__get()
__set()
__invoke()
```

For example:

```php
class LogFile
{
    public $filename;

    public function __destruct()
    {
        unlink($this->filename);
    }
}
```

If an attacker can control the object's `filename` property through unsafe deserialization, the destructor becomes security relevant.

Conceptually:

```text
Attacker-Controlled Serialized Object
              ↓
          unserialize()
              ↓
         Object Created
              ↓
          __destruct()
              ↓
       Sensitive Operation
```

This illustrates why reviewing application classes is essential.

---

# PHP Source Review

Search for deserialization:

```bash
grep -Rni "unserialize(" .
```

Then determine where the input originates.

For example:

```php
$value = $_COOKIE['data'];
$obj = unserialize($value);
```

Trace:

```text
$_COOKIE
   ↓
$value
   ↓
unserialize()
```

Then inspect the application's classes for relevant magic methods.

```bash
grep -RniE '__destruct|__wakeup|__toString|__call|__get|__set|__invoke' .
```

You can combine several interesting searches:

```bash
grep -RniE 'unserialize|serialize|__destruct|__wakeup|__toString|__invoke' .
```

---

# PHPGGC

PHPGGC is a library of PHP `unserialize()` gadget chains.

Repository:

https://github.com/ambionics/phpggc

It is particularly useful when researching applications built using common PHP frameworks and libraries.

List available gadget chains:

```bash
./phpggc -l
```

Search the list for a framework:

```bash
./phpggc -l | grep -i laravel
```

or:

```bash
./phpggc -l | grep -i symfony
```

The important requirement remains:

```text
Relevant library exists
        +
Relevant version is compatible
        +
Unsafe deserialization is reachable
        +
Attacker input reaches the sink
```

---

# .NET Deserialization

.NET applications historically supported several serialization mechanisms.

During source review, potentially interesting APIs include:

```text
BinaryFormatter
LosFormatter
ObjectStateFormatter
NetDataContractSerializer
SoapFormatter
JavaScriptSerializer
DataContractSerializer
```

Some APIs are considerably more dangerous than others.

`BinaryFormatter` in particular has a long history of security concerns and should not be used with untrusted data.

Look for patterns such as:

```csharp
BinaryFormatter formatter = new BinaryFormatter();
object value = formatter.Deserialize(stream);
```

Trace:

```text
Untrusted Stream
      ↓
BinaryFormatter
      ↓
Deserialize()
      ↓
Object Graph
```

---

# Searching .NET Source Code

Useful searches include:

```bash
grep -RniE 'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|SoapFormatter' .
```

Also search specifically for:

```bash
grep -Rni "\.Deserialize(" .
```

Then manually determine whether the source is attacker controlled.

---

# ASP.NET ViewState

ASP.NET applications may use ViewState to preserve page state.

A common parameter is:

```text
__VIEWSTATE
```

Example:

```http
POST /page.aspx HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded

__VIEWSTATE=...
```

ViewState itself is not automatically vulnerable.

Important questions include:

```text
Is integrity protection enabled?

Is a MAC applied?

Is encryption used?

Can the value be modified?

Is the application's machine key exposed?

Is unsafe object deserialization reachable?
```

Do not infer vulnerability merely because `__VIEWSTATE` exists.

---

# ysoserial.net

For authorised .NET deserialization research, another commonly referenced project is `ysoserial.net`.

Repository:

https://github.com/pwntester/ysoserial.net

It is designed to help researchers investigate known .NET deserialization gadget chains and formatter behaviour.

The same principle applies as with Java gadget tooling:

```text
Identify Formatter
      ↓
Understand Input
      ↓
Identify Available Types
      ↓
Determine Reachability
      ↓
Validate Safely
```

---

# Python Deserialization

Python applications may use serialization mechanisms such as:

```text
pickle
cPickle
PyYAML
marshal
shelve
```

Python `pickle` deserves particular attention because loading an untrusted pickle can result in arbitrary behaviour.

Interesting functions include:

```python
pickle.loads()
pickle.load()
```

Example:

```python
data = request.get_data()
obj = pickle.loads(data)
```

Trust boundary:

```text
HTTP Request
     ↓
request.get_data()
     ↓
pickle.loads()
     ↓
Python Object
```

Untrusted pickle data should not be deserialized.

---

# Python Pickle Identification

Pickle data may appear as binary data or as Base64 when transported through HTTP.

A potential workflow is:

```text
HTTP Parameter
      ↓
Base64 Decode
      ↓
Binary Data
      ↓
Identify Pickle
```

Python provides tools for inspecting pickle structures without treating every value as ordinary text.

During assessment, focus first on determining whether the application is actually using pickle.

---

# Searching Python Source

Search for:

```bash
grep -RniE 'pickle\.load|pickle\.loads|yaml\.load|marshal\.load|shelve' .
```

You can also search broadly:

```bash
grep -RniE 'import pickle|from pickle|pickle\.' .
```

Trace the input backwards.

For example:

```text
pickle.loads(data)
       ↑
      data
       ↑
request.cookies
```

This establishes whether an attacker-controlled source reaches the deserialization sink.

---

# YAML Deserialization

YAML itself is a data serialization format.

The risk depends on the parser and configuration.

During review, inspect code such as:

```python
yaml.load(...)
```

and determine which loader is configured.

The desired model for ordinary configuration data is:

```text
YAML
 ↓
Primitive Data
 ↓
Dictionary / List / String / Number
```

rather than:

```text
YAML
 ↓
Arbitrary Object Construction
```

Safer implementations should restrict YAML processing to expected data types.

---

# Ruby Deserialization

Ruby applications may use:

```text
Marshal
YAML
```

Potentially interesting operations include:

```ruby
Marshal.load()
YAML.load()
```

During source review:

```bash
grep -RniE 'Marshal\.load|YAML\.load' .
```

Again, determine whether attacker-controlled data can reach these operations.

---

# Node.js

Node.js applications usually rely heavily on JSON, which does not inherently provide the same arbitrary object reconstruction behaviour as native Java or PHP object serialization.

However, dangerous behaviour can still appear through:

```text
Custom serialization libraries
Unsafe object merging
Prototype pollution
Dynamic evaluation
Function serialization
Framework-specific mechanisms
```

Do not classify normal:

```javascript
JSON.parse()
```

as equivalent to unsafe native object deserialization.

Instead, inspect what happens after parsing.

For example:

```text
JSON Input
   ↓
JSON.parse()
   ↓
Object Merge
   ↓
Prototype Modification
   ↓
Application Behaviour
```

---

# JSON and Deserialization

JSON is commonly used for serialized data:

```json
{
  "username": "alice",
  "role": "user"
}
```

Simply changing:

```json
"role": "user"
```

to:

```json
"role": "admin"
```

tests object trust or mass assignment rather than traditional native object deserialization.

However, it remains worth testing because applications may incorrectly trust client-provided object properties.

Possible classifications include:

```text
Mass assignment
Broken access control
Parameter tampering
Insecure deserialization
Prototype pollution
Business logic vulnerability
```

depending on the underlying cause.

---

# Integrity Protection

Serialized client-side state should generally be protected from modification.

An application might use:

```text
Serialized Data
      +
HMAC
```

Conceptually:

```text
Object
  ↓
Serialize
  ↓
Serialized Value
  ↓
HMAC(secret, value)
```

When the server receives the value:

```text
Value
  ↓
Calculate HMAC
  ↓
Compare Signature
  ↓
Accept / Reject
```

If the attacker cannot generate a valid signature, arbitrary modification should fail.

---

# Testing Integrity Protection

Start with a harmless modification.

For example:

```text
Original:

theme=dark

Modified:

theme=light
```

Observe whether:

```text
Request accepted
Request rejected
Session invalidated
Signature error returned
Server error generated
Value ignored
```

This can reveal whether serialized state has integrity protection.

Do not immediately modify security-sensitive properties.

---

# Encryption Is Not Integrity

A common misconception is:

```text
Encrypted = Tamper Proof
```

That is not necessarily true.

Security controls should provide appropriate confidentiality and integrity.

Conceptually:

```text
Confidentiality
      +
Integrity
```

Modern authenticated encryption schemes can provide both.

During testing, focus on observed application behaviour rather than assuming security from an opaque value.

---

# Base64 Encoded Objects

A common pattern is:

```text
Cookie:
session=ZXlKMWMyVnlJam9pWVd4cFkyVWlmUT09
```

Workflow:

```text
Cookie
 ↓
URL Decode
 ↓
Base64 Decode
 ↓
Inspect Data
```

From the terminal:

```bash
echo 'VALUE' | base64 -d
```

If decoding fails, consider:

```text
URL-safe Base64
Missing padding
Compression
Multiple encoding layers
Binary serialization
Encryption
```

---

# Identifying Data With Linux

The `file` command can help identify binary content.

```bash
file serialized.bin
```

Hexadecimal inspection:

```bash
xxd serialized.bin | head
```

Extract printable strings:

```bash
strings serialized.bin | head -50
```

These techniques can reveal:

```text
Class names
Package names
Framework names
Property names
File signatures
```

---

# Testing With Burp Repeater

Suppose the application sends:

```http
Cookie: profile=<serialized-value>
```

A safe initial workflow is:

```text
1. Send request to Repeater
2. Copy the serialized value
3. Decode it
4. Identify its structure
5. Modify a harmless property
6. Re-encode it
7. Replace the original value
8. Send the request
9. Compare the response
```

Useful harmless properties may include:

```text
Display preference
Language
Theme
Sort order
Non-security UI setting
```

This establishes whether the object can be manipulated.

---

# Burp Comparer

Burp Comparer can help identify differences between:

```text
Original Response
        vs
Modified Response
```

This can be useful when changes are subtle.

For example:

```text
Response length
Headers
Redirects
Cookies
HTML content
Error messages
```

---

# Burp Decoder

Decoder is useful for transformations such as:

```text
URL Decode
Base64 Decode
Hex Decode
URL Encode
Base64 Encode
```

Typical workflow:

```text
Repeater
   ↓
Copy Value
   ↓
Decoder
   ↓
Decode
   ↓
Modify
   ↓
Encode
   ↓
Repeater
```

---

# Burp Extensions

Burp extensions can assist when analysing particular serialization formats.

Search the BApp Store for extensions related to:

```text
Java serialization
.NET ViewState
Serialized objects
JSON
JWT
MessagePack
Protocol Buffers
```

Do not rely solely on extension output.

Use extensions to accelerate analysis while still understanding the underlying request and serialization format.

---

# Error Messages

Malformed serialized data can produce useful technology fingerprints.

Errors may expose:

```text
Class names
Package names
Namespaces
Serialization libraries
Framework versions
Stack traces
Expected types
Parser names
```

For example, an error mentioning:

```text
java.io.ObjectInputStream
```

strongly suggests Java object deserialization is involved.

Likewise:

```text
unserialize()
```

may indicate PHP.

A Python traceback mentioning:

```text
_pickle.UnpicklingError
```

may indicate pickle processing.

A .NET error referencing:

```text
BinaryFormatter
```

may identify the formatter.

Do not deliberately cause excessive errors against production systems.

A small number of controlled malformed requests is normally sufficient for fingerprinting.

---

# Object Property Manipulation

Before researching complex gadget chains, test whether ordinary properties can be modified.

Potential properties include:

```text
username
userId
role
isAdmin
authenticated
accountId
tenantId
permissions
discount
price
subscription
```

However, modify sensitive properties only when permitted by the assessment scope.

A vulnerability might be as simple as:

```text
Client Controls Serialized Object
        ↓
Server Trusts role Property
        ↓
Authorisation Bypass
```

No gadget chain is required.

---

# Nested Objects

Serialized objects frequently contain nested structures.

For example:

```json
{
  "user": {
    "id": 1001,
    "role": "user"
  },
  "organisation": {
    "id": 50
  }
}
```

Test whether nested identifiers are trusted.

Potential issues include:

```text
Horizontal privilege escalation
Vertical privilege escalation
Tenant escape
Object ownership bypass
Business logic manipulation
```

These may be better classified as access control issues depending on the root cause.

---

# Type Manipulation

Some serializers include explicit type information.

Conceptually:

```text
{
    "type": "User",
    "properties": {...}
}
```

If an attacker can influence the type being instantiated, the security implications may become significantly greater.

Look for indicators such as:

```text
$type
@class
@type
__type
typeName
className
```

These names are only indicators.

Their presence does not automatically establish vulnerability.

---

# Polymorphic Deserialization

Some serialization frameworks support polymorphism.

For example, an application expects:

```text
Animal
```

but the serialized data specifies:

```text
Dog
```

or:

```text
Cat
```

The framework dynamically selects a concrete class.

Conceptually:

```text
Serialized Type Metadata
          ↓
Deserializer
          ↓
Dynamic Class Selection
          ↓
Object Construction
```

If arbitrary or overly broad class selection is permitted, this can increase attack surface.

Secure implementations should restrict which types can be instantiated.

---

# Gadget Chain Analysis

When investigating a possible gadget chain, think in terms of:

```text
ENTRY POINT
     ↓
DESERIALIZATION
     ↓
MAGIC METHOD / CALLBACK
     ↓
GADGET
     ↓
GADGET
     ↓
SENSITIVE SINK
```

The central question is:

> Can attacker-controlled object state reach a dangerous operation during or after deserialization?

Useful sink categories include:

```text
Command execution
Expression evaluation
Template execution
File writing
File deletion
Network requests
Dynamic class loading
Reflection
Database operations
```

---

# Source-to-Sink Analysis

During white-box testing, map the complete path.

Example:

```text
HTTP Cookie
    ↓
Base64 Decode
    ↓
ObjectInputStream
    ↓
readObject()
    ↓
Object Method
    ↓
Library Method
    ↓
Sensitive Sink
```

Document each step.

This is much stronger evidence than simply identifying a dangerous API.

---

# Sources

Potential attacker-controlled sources include:

```text
HTTP parameters
Cookies
HTTP headers
Request bodies
Uploaded files
WebSocket messages
Message queues
Database values originally supplied by users
Cache entries
External APIs
```

---

# Sinks

Potential deserialization sinks include:

## Java

```text
ObjectInputStream.readObject()
ObjectInputStream.readUnshared()
XMLDecoder.readObject()
```

## PHP

```text
unserialize()
```

## Python

```text
pickle.load()
pickle.loads()
yaml.load()
```

## Ruby

```text
Marshal.load()
YAML.load()
```

## .NET

```text
BinaryFormatter.Deserialize()
LosFormatter.Deserialize()
ObjectStateFormatter.Deserialize()
NetDataContractSerializer.Deserialize()
```

The presence of a sink does not automatically mean the application is vulnerable.

You must establish that untrusted data reaches it.

---

# Useful Grep Searches

## Java

```bash
grep -RniE 'ObjectInputStream|readObject|readUnshared|XMLDecoder' .
```

## PHP

```bash
grep -RniE 'unserialize|__wakeup|__destruct|__toString|__invoke' .
```

## .NET

```bash
grep -RniE 'BinaryFormatter|LosFormatter|ObjectStateFormatter|NetDataContractSerializer|SoapFormatter|Deserialize' .
```

## Python

```bash
grep -RniE 'pickle\.load|pickle\.loads|yaml\.load|marshal\.load|shelve' .
```

## Ruby

```bash
grep -RniE 'Marshal\.load|YAML\.load' .
```

These searches identify review candidates rather than confirmed vulnerabilities.

---

# File-Based Deserialization

Deserialization does not have to occur directly inside an HTTP parameter.

Applications may deserialize uploaded files.

Example:

```text
Upload File
    ↓
Application Stores File
    ↓
Background Processor
    ↓
Deserialize
    ↓
Object Processing
```

Interesting upload formats may include:

```text
Application exports
Configuration backups
Session exports
Cached objects
Binary application formats
Framework-specific files
```

This overlaps with file upload testing.

---

# Background Processing

Some deserialization vulnerabilities are asynchronous.

For example:

```text
HTTP Request
    ↓
Message Queue
    ↓
Worker
    ↓
Deserialize
    ↓
Process Object
```

This means the immediate HTTP response may not reveal the result.

Investigate:

```text
Workers
Queues
Scheduled tasks
Background jobs
Import processors
Notification systems
```

when architecture information is available.

---

# API Deserialization

Modern APIs commonly deserialize request bodies automatically.

For example:

```http
POST /api/profile HTTP/1.1
Host: target.example
Content-Type: application/json

{
  "username": "alice"
}
```

Framework behaviour might be:

```text
JSON
 ↓
Framework Binder
 ↓
Application Object
```

This is normal.

Security issues arise when the framework allows:

```text
Unexpected properties
Sensitive property assignment
Arbitrary type selection
Unsafe converters
Dangerous object hooks
```

Related vulnerability classes include:

```text
Mass assignment
Over-posting
Prototype pollution
Polymorphic deserialization
Insecure deserialization
```

---

# Authentication and Deserialization

Serialized data sometimes contains authentication state.

Example:

```text
{
    username: alice,
    authenticated: true,
    role: user
}
```

If this object is stored client side without adequate integrity protection, modification may affect authentication.

Testing workflow:

```text
Capture Object
     ↓
Decode
     ↓
Understand Structure
     ↓
Modify Non-Sensitive Property
     ↓
Confirm Tampering
     ↓
Test Authentication-Relevant Property
     ↓
Observe Server-Side Verification
```

Only proceed to security-sensitive modifications when permitted by scope.

---

# Authorisation and Deserialization

Look for properties such as:

```text
role
permissions
group
tenant
account
userId
isAdmin
accessLevel
```

The server should independently enforce authorisation.

Client-provided object state must not be the sole source of authority.

Expected secure design:

```text
Client Request
     ↓
Authenticated Identity
     ↓
Server-Side Authorisation
     ↓
Requested Resource
```

Not:

```text
Client Says "admin=true"
          ↓
Server Trusts Client
          ↓
Administrative Access
```

---

# Session Deserialization

Session frameworks may serialize session state.

Potential locations include:

```text
Client-side session cookies
Redis
Memcached
Database sessions
Filesystem sessions
Distributed caches
```

A key question is whether an attacker can control the serialized content before the application deserializes it.

For server-side sessions:

```text
Random Session ID
       ↓
Server-Side Session Store
       ↓
Serialized Object
```

the client may never directly control the serialized object.

Therefore, merely discovering serialized session data in Redis does not automatically create a remotely exploitable vulnerability.

---

# Cookies

Cookies are particularly important during deserialization testing because developers sometimes store application state directly inside them.

Example:

```http
Cookie: user=rO0ABXNy...
```

or:

```http
Cookie: preferences=Tzo0OiJVc2VyIjoyOnt...
```

Workflow:

```text
Cookie
  ↓
Identify Encoding
  ↓
Decode
  ↓
Identify Serialization Format
  ↓
Determine Integrity Protection
  ↓
Modify Safely
  ↓
Replay
```

Check every application cookie rather than focusing exclusively on the main session identifier.

---

# Hidden Form Fields

Applications sometimes store state in hidden fields.

Example:

```html
<input type="hidden" name="state" value="...">
```

The browser returning the value does not make it trustworthy.

Conceptually:

```text
Server Creates State
       ↓
Hidden Form Field
       ↓
Browser
       ↓
Attacker Modifies Value
       ↓
Server Receives Value
```

Any security-sensitive state returned by the client must be independently validated.

---

# Message Queues

Modern distributed applications may deserialize objects received from message queues.

Examples include architectures using:

```text
RabbitMQ
Kafka
ActiveMQ
Cloud messaging services
Internal job queues
```

Conceptually:

```text
Frontend
   ↓
Message
   ↓
Queue
   ↓
Worker
   ↓
Deserialize
   ↓
Process
```

During architecture review, determine who can write to the queue and whether message contents can originate from untrusted input.

---

# Cache Poisoning and Deserialization

Serialized objects may be stored in:

```text
Redis
Memcached
Filesystem caches
Distributed caches
```

If another vulnerability allows an attacker to modify cached serialized objects, deserialization may become part of an exploit chain.

For example:

```text
Attacker Controls Cache Entry
          ↓
Application Reads Cache
          ↓
Deserialize
          ↓
Object Processing
```

This demonstrates why deserialization issues sometimes require chaining with another vulnerability.

---

# Chaining Vulnerabilities

Insecure deserialization may interact with other weaknesses.

Possible chains include:

```text
SSRF
 ↓
Internal Cache Access
 ↓
Serialized Object Modification
 ↓
Deserialization
```

or:

```text
File Upload
 ↓
Application Import
 ↓
Deserialization
```

or:

```text
SQL Injection
 ↓
Modify Serialized Database Value
 ↓
Application Reads Record
 ↓
Deserialize
```

or:

```text
Authentication Weakness
 ↓
Access Internal Function
 ↓
Submit Serialized Object
 ↓
Deserialization
```

Understanding architecture is therefore important.

---

# Deserialization Quick Workflow

```text
Interesting Opaque Value
          ↓
Can It Be Decoded?
          ↓
What Format Is It?
          ↓
What Technology Produced It?
          ↓
Is It Serialized?
          ↓
Can It Be Modified?
          ↓
Is Integrity Checked?
          ↓
What Object Is Created?
          ↓
Can Properties Be Controlled?
          ↓
Can Types Be Controlled?
          ↓
What Methods Run?
          ↓
Are Useful Gadgets Available?
          ↓
What Security Impact Exists?
```

---

# Testing Checklist

## Discovery

```text
[ ] Inspect cookies
[ ] Inspect hidden parameters
[ ] Inspect POST bodies
[ ] Inspect API requests
[ ] Inspect WebSocket traffic
[ ] Inspect uploaded/imported files
[ ] Look for Base64
[ ] Look for binary data
[ ] Look for class names
[ ] Look for type metadata
[ ] Identify framework
[ ] Identify language
```

## Analysis

```text
[ ] Determine encoding layers
[ ] Decode serialized data
[ ] Identify object structure
[ ] Identify security-sensitive properties
[ ] Determine whether integrity protection exists
[ ] Identify deserialization library
[ ] Identify deserialization sink
[ ] Identify reachable classes
[ ] Review dependencies
```

## Testing

```text
[ ] Modify harmless property
[ ] Replay request
[ ] Compare response
[ ] Test malformed object
[ ] Observe error handling
[ ] Test integrity controls
[ ] Test object property trust
[ ] Investigate type control
[ ] Investigate nested objects
```

## White-Box Review

```text
[ ] Locate deserialization functions
[ ] Trace attacker-controlled input
[ ] Identify object callbacks
[ ] Identify magic methods
[ ] Identify sensitive sinks
[ ] Review dependency versions
[ ] Map complete source-to-sink path
```

---

# Common Indicators

During testing, pay attention to:

```text
rO0AB
AC ED 00 05
O:
a:
__VIEWSTATE
$type
@class
@type
BinaryFormatter
ObjectInputStream
readObject
unserialize
pickle
Marshal
```

These are indicators only.

They should trigger further investigation rather than an immediate vulnerability finding.

---

# Common Mistakes

## Assuming Base64 Means Deserialization

Incorrect:

```text
Base64 Value
     =
Deserialization Vulnerability
```

Correct:

```text
Base64
  ↓
Decode
  ↓
Determine Actual Format
```

---

## Assuming `JSON.parse()` Is Dangerous Deserialization

Normal JSON parsing is not equivalent to native object deserialization.

Investigate what the application does with the resulting object.

---

## Running Gadget Generators Immediately

Do not begin with gadget-chain tooling.

Start with:

```text
Fingerprint
 ↓
Decode
 ↓
Understand
 ↓
Modify
 ↓
Observe
 ↓
Investigate
```

---

## Ignoring Integrity Protection

A serialized object may be visible but cryptographically protected against modification.

Determine whether changes are accepted before spending time analysing exploitation possibilities.

---

## Ignoring Application Dependencies

Gadget chains depend on available code.

Always ask:

```text
Is the required class actually present?
```

---

## Confusing Potential Impact With Demonstrated Impact

Finding:

```text
ObjectInputStream.readObject()
```

does not automatically mean:

```text
Remote Code Execution
```

Likewise:

```text
PHP unserialize()
```

does not automatically prove PHP object injection is exploitable.

The complete chain must be established.

---

# Evidence Collection

For each interesting serialized object, record:

```text
Endpoint
HTTP method
Parameter / cookie
Original value
Encoding
Serialization format
Technology
Modified value
Response difference
Integrity protection
Object properties
Relevant classes
Relevant dependencies
Source
Sink
Security impact
```

A simple tracking format can be:

```text
DESER-001
Endpoint: /account
Location: profile cookie
Encoding: Base64
Format: Java serialization
Indicator: rO0AB
Modification: harmless property
Result: accepted
Status: investigate further
```

---

# Reporting

A deserialization finding should clearly document:

```text
Affected endpoint
Affected parameter / cookie / body
Serialization format
Application technology
How the value was identified
How the value was decoded
Whether integrity protection exists
Controlled modification performed
Observed application behaviour
Security impact
Affected user role
Required privileges
Relevant source-to-sink path
Remediation
```

---

# Example Finding

## Title

```text
Insecure Deserialization of Client-Controlled Session Data
```

## Description

```text
The application deserializes client-controlled session data without
adequately verifying its integrity.

Testing demonstrated that properties contained within the serialized
object could be modified before the object was returned to the server.

The server subsequently trusted the modified object state.
```

## Impact

Depending on the affected properties, this may allow:

```text
Application state manipulation
Authentication bypass
Authorisation bypass
Privilege escalation
Access to another user's data
```

The reported impact should reflect what was actually demonstrated.

---

# Impact

The impact of insecure deserialization depends on what the attacker can influence.

Potential consequences include:

```text
Application state manipulation
Authentication bypass
Authorisation bypass
Privilege escalation
Data modification
File manipulation
Server-side requests
Denial of service
Remote code execution
```

A finding should describe the demonstrated impact rather than automatically assigning the worst possible outcome.

For example:

```text
Insecure Deserialization Allows Modification of User Role
```

is more accurate than:

```text
Remote Code Execution
```

if code execution was neither demonstrated nor established.

---

# Remediation

The strongest remediation is:

> Do not deserialize untrusted objects.

Where possible, use simple data formats containing only expected primitive values.

Preferred model:

```text
Untrusted Input
      ↓
Strict Parser
      ↓
Primitive Data
      ↓
Schema Validation
      ↓
Application Logic
```

rather than:

```text
Untrusted Input
      ↓
Native Object Deserializer
      ↓
Arbitrary Object Graph
```

---

# Use Strict Schemas

Define exactly which properties are permitted.

For example:

```json
{
  "language": "en",
  "theme": "dark"
}
```

Reject unexpected properties.

Conceptually:

```text
Incoming Data
     ↓
Schema Validation
     ↓
Allowed Fields Only
     ↓
Application
```

---

# Avoid Dangerous Native Serialization

Avoid using unsafe native object serialization formats across trust boundaries.

Examples requiring particular caution include:

```text
Java native serialization
PHP unserialize()
Python pickle
.NET BinaryFormatter
Ruby Marshal
```

especially when the input can be influenced by an attacker.

---

# Apply Integrity Protection

If application state must be stored client side, protect it against modification.

Use modern cryptographic mechanisms designed to provide integrity and, where appropriate, confidentiality.

Do not rely on:

```text
Base64
Obfuscation
Custom encoding
Compression
```

as security controls.

---

# Restrict Types

Where polymorphic deserialization is required:

```text
Allowlist expected types
Reject unexpected classes
Avoid unrestricted type metadata
Avoid arbitrary class resolution
```

Use the narrowest possible set of types.

---

# Keep Dependencies Updated

Dependencies may contain classes that form known gadget chains.

Maintain:

```text
Dependency inventory
Version tracking
Security updates
Unused dependency removal
Software composition analysis
```

Reducing unnecessary libraries also reduces available attack surface.

---

# Server-Side Authorisation

Never trust authorisation properties simply because they are part of a serialized object.

Always validate privileges server side.

For example:

```text
Request
  ↓
Session Identity
  ↓
Server-Side Permission Check
  ↓
Resource
```

---

# Deserialization Prevention Model

A useful defensive model is:

```text
Can Native Deserialization Be Removed?
             ↓
            YES
             ↓
Use Simple Structured Data
             ↓
Strict Schema Validation
             ↓
Server-Side Security Decisions
```

If native serialization cannot be removed:

```text
Untrusted Input
      ↓
Integrity Verification
      ↓
Strict Type Allowlist
      ↓
Restricted Deserializer
      ↓
Object Validation
      ↓
Application
```

---

# Quick Reference

## Java

Look for:

```text
rO0AB
AC ED 00 05
ObjectInputStream
readObject()
```

Research tool:

```text
ysoserial
```

---

## PHP

Look for:

```text
O:
a:
unserialize()
__wakeup()
__destruct()
```

Research tool:

```text
PHPGGC
```

---

## .NET

Look for:

```text
__VIEWSTATE
BinaryFormatter
LosFormatter
ObjectStateFormatter
Deserialize()
```

Research tool:

```text
ysoserial.net
```

---

## Python

Look for:

```text
pickle
pickle.loads()
pickle.load()
yaml.load()
```

---

## Ruby

Look for:

```text
Marshal.load()
YAML.load()
```

---

# Deserialization Mindset

When you encounter an unusual application value, work through the following questions:

```text
What is this?
     ↓
How is it encoded?
     ↓
What serialization format is used?
     ↓
Which technology created it?
     ↓
Who controls it?
     ↓
Where is it deserialized?
     ↓
Can I change it?
     ↓
Is integrity verified?
     ↓
Which properties can I influence?
     ↓
Which classes can be instantiated?
     ↓
Which methods execute?
     ↓
Can controlled data reach a sensitive sink?
     ↓
What is the actual security impact?
```

This approach is considerably more reliable than immediately trying random serialized payloads.

---

# Tools

Useful tools during deserialization research include:

```text
Burp Suite
Burp Repeater
Burp Decoder
Burp Comparer
Browser Developer Tools
CyberChef
grep
ripgrep
strings
xxd
file
jar
ysoserial
PHPGGC
ysoserial.net
```

---

# References

## PortSwigger Web Security Academy

Deserialization vulnerabilities:

https://portswigger.net/web-security/deserialization

PortSwigger provides practical labs covering insecure deserialization, object modification, PHP object injection and Java gadget chains.

---

## OWASP Deserialization Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html

Useful defensive guidance covering secure deserialization patterns and technology-specific considerations.

---

## OWASP Java Deserialization

https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data

Background information about the risks associated with deserializing untrusted data.

---

## ysoserial

Java deserialization research tool:

https://github.com/frohoff/ysoserial

Useful for studying known Java gadget chains in authorised labs and security assessments.

---

## PHPGGC

PHP Generic Gadget Chains:

https://github.com/ambionics/phpggc

Useful for researching PHP object injection and gadget chains in supported PHP frameworks and libraries.

---

## ysoserial.net

.NET deserialization research tool:

https://github.com/pwntester/ysoserial.net

Useful for studying .NET formatter and gadget-chain behaviour in controlled environments.

---

## Microsoft BinaryFormatter Security Guide

https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide

Microsoft guidance explaining the security risks associated with `BinaryFormatter`.

---

# Final Testing Workflow

```text
Application
     ↓
Proxy Traffic Through Burp
     ↓
Inspect Cookies / Parameters / Bodies
     ↓
Identify Encoded or Binary Values
     ↓
Decode Values
     ↓
Fingerprint Serialization Format
     ↓
Identify Technology
     ↓
Determine Trust Boundary
     ↓
Modify Harmless Property
     ↓
Replay Request
     ↓
Check Integrity Protection
     ↓
Map Object Structure
     ↓
Identify Security-Sensitive Properties
     ↓
Identify Deserialization Sink
     ↓
Review Available Classes / Dependencies
     ↓
Map Source to Sink
     ↓
Investigate Gadget Behaviour Where Relevant
     ↓
Validate Minimum Necessary Impact
     ↓
Collect Evidence
     ↓
Report
```

The key principle is:

> Finding serialized data is only the beginning. Determine whether an attacker can control the data, whether the application trusts it during deserialization, what code becomes reachable and what security impact can actually be demonstrated.
