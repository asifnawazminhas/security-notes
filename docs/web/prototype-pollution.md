# Prototype Pollution

Prototype pollution is a JavaScript vulnerability in which an attacker modifies properties of an object's prototype.

Because JavaScript objects can inherit properties from prototypes, modifying a shared prototype can unexpectedly influence other objects throughout an application.

Prototype pollution can occur:

```text
Client-side
Server-side
```

Depending on where the vulnerable JavaScript executes.

Potential impact includes:

```text
DOM-based XSS
Authentication bypass
Authorisation bypass
Configuration manipulation
Application logic manipulation
Privilege escalation
Denial of service
Server-side code execution in specific circumstances
```

The vulnerability itself is usually a primitive.

The important question is:

> What security-sensitive behaviour can be influenced after the prototype has been polluted?

A simplified attack chain is:

```text
Attacker-Controlled Input
          ↓
Unsafe Object Operation
          ↓
Object Prototype Modified
          ↓
Another Object Inherits Property
          ↓
Application Uses Property
          ↓
Security-Sensitive Sink
```

!!! warning "Authorised Security Testing"
    Perform prototype pollution testing only against applications included in the authorised assessment scope. Begin with harmless canary properties and avoid changing properties that may destabilise a production application.

---

# JavaScript Prototypes

JavaScript uses prototype-based inheritance.

Consider:

```javascript
const user = {
    username: "alice"
};
```

The object contains:

```text
username
```

but it also inherits properties and methods from its prototype.

For example:

```javascript
user.toString()
```

works even though `toString` was not explicitly defined on `user`.

Conceptually:

```text
user
 ↓
Object.prototype
 ↓
Inherited Properties
```

---

# The Prototype Chain

JavaScript looks for properties through the prototype chain.

For example:

```javascript
const user = {};
```

Accessing:

```javascript
user.example
```

first checks:

```text
user
```

If the property does not exist, JavaScript checks the prototype.

Conceptually:

```text
user.example
     ↓
Property on user?
     ↓
     NO
     ↓
Object.prototype.example?
     ↓
Return inherited value
```

---

# Object.prototype

Many ordinary JavaScript objects ultimately inherit from:

```javascript
Object.prototype
```

Example:

```javascript
const a = {};
const b = {};

console.log(Object.getPrototypeOf(a) === Object.prototype);
console.log(Object.getPrototypeOf(b) === Object.prototype);
```

Both objects normally share the same prototype.

This shared inheritance model is what makes prototype pollution security-relevant.

---

# Harmless Prototype Demonstration

In a local JavaScript environment:

```javascript
const first = {};
const second = {};

Object.prototype.demo = "AM-PROTOTYPE-TEST";

console.log(first.demo);
console.log(second.demo);
```

Both objects can inherit:

```text
AM-PROTOTYPE-TEST
```

even though the property was never explicitly assigned to either object.

Clean up afterwards:

```javascript
delete Object.prototype.demo;
```

---

# Own vs Inherited Properties

Consider:

```javascript
const user = {
    username: "alice"
};
```

Then:

```javascript
user.hasOwnProperty("username")
```

returns:

```text
true
```

But an inherited property may exist without being an own property.

For example:

```javascript
Object.prototype.isAdmin = true;

const user = {};

console.log(user.isAdmin);
console.log(Object.hasOwn(user, "isAdmin"));
```

Conceptually:

```text
user.isAdmin
      ↓
Own property?
      ↓
NO
      ↓
Prototype
      ↓
isAdmin = true
```

This distinction is extremely important when analysing prototype pollution.

---

# What Is Prototype Pollution?

Prototype pollution occurs when attacker-controlled input is able to modify properties associated with an object's prototype.

A simplified vulnerable operation may look like:

```javascript
target[key] = value;
```

If the attacker controls:

```text
key
```

or nested property paths, dangerous property names may reach prototype-related structures.

The resulting primitive can conceptually become:

```text
Input
 ↓
Property Assignment
 ↓
Prototype Modified
 ↓
Other Objects Inherit Property
```

---

# Sources and Sinks

Prototype pollution analysis is easier when divided into:

```text
SOURCE
 ↓
POLLUTION SOURCE / GADGET
 ↓
PROTOTYPE
 ↓
SINK
```

---

# Source

A source is attacker-controlled data.

Examples include:

```text
URL query parameters
URL fragments
JSON
POST parameters
Cookies
WebSocket messages
Configuration objects
API request bodies
Object merge input
```

---

# Pollution Source

The vulnerable operation takes attacker-controlled properties and writes them into an object in an unsafe way.

Common patterns include:

```text
Recursive object merge
Property assignment
Query-string parsing
Object cloning
Configuration merging
Deep-copy functions
```

---

# Prototype

The attacker-controlled property reaches a prototype.

Conceptually:

```text
Attacker Input
     ↓
__proto__
     ↓
Object.prototype
     ↓
Injected Property
```

---

# Sink

A sink is where the polluted property produces security impact.

Examples may include:

```text
DOM manipulation
HTML generation
Script creation
Configuration decisions
Authentication checks
Authorisation checks
Command construction
Template configuration
Network request options
```

Prototype pollution without an exploitable sink may have limited security impact.

---

# Prototype Pollution Testing Model

A useful mental model is:

```text
Can I Pollute?
      ↓
     YES
      ↓
What Property Can I Create?
      ↓
Where Is It Read?
      ↓
Does It Reach a Gadget?
      ↓
Does Gadget Reach Dangerous Sink?
      ↓
Can Security Impact Be Demonstrated?
```

---

# Client-Side Prototype Pollution

Client-side prototype pollution occurs in JavaScript running in the browser.

A common attack surface is:

```text
URL
 ↓
JavaScript Parser
 ↓
Object
 ↓
Prototype Pollution
 ↓
DOM Gadget
 ↓
DOM XSS
```

Potential sources include:

```text
Query strings
URL fragments
postMessage
Cookies
Local storage
API responses
```

---

# Server-Side Prototype Pollution

Server-side prototype pollution occurs in server-side JavaScript, most commonly Node.js applications.

A simplified flow is:

```text
HTTP Request
      ↓
JSON / Parameters
      ↓
Object Merge
      ↓
Prototype Pollution
      ↓
Application Configuration
      ↓
Security-Sensitive Behaviour
```

Potential impact can be significantly different from browser-side pollution.

---

# Prototype Pollution vs DOM XSS

Prototype pollution and DOM XSS are not the same vulnerability.

Prototype pollution:

```text
Attacker
 ↓
Prototype
 ↓
Property
```

DOM XSS:

```text
Attacker
 ↓
DOM Source
 ↓
Dangerous Sink
 ↓
JavaScript Execution
```

However, prototype pollution may provide the source for a DOM XSS gadget.

Combined:

```text
Prototype Pollution
       ↓
Polluted Property
       ↓
DOM Gadget
       ↓
Dangerous Sink
       ↓
DOM XSS
```

---

# Prototype Pollution Terminology

Important terms include:

```text
Source
Prototype
Property
Pollution
Gadget
Sink
Prototype chain
Own property
Inherited property
```

Understanding these terms makes analysis considerably easier.

---

# __proto__

Historically, one of the most important prototype-related properties is:

```text
__proto__
```

It can provide access to an object's prototype in many JavaScript environments.

For example:

```javascript
const obj = {};

console.log(obj.__proto__ === Object.prototype);
```

During testing, determine whether attacker-controlled property paths containing:

```text
__proto__
```

are accepted and processed.

---

# constructor.prototype

Filtering only:

```text
__proto__
```

is not always sufficient.

Another important path is:

```text
constructor.prototype
```

Conceptually:

```text
object
  ↓
constructor
  ↓
Object
  ↓
prototype
  ↓
Object.prototype
```

Therefore, testing should consider whether application logic permits prototype access through alternate paths.

---

# Common Property Paths

Prototype pollution research commonly considers structures such as:

```text
__proto__.property
constructor.prototype.property
```

The exact representation depends on how the application parses input.

For example:

```text
Dot notation
Bracket notation
Nested JSON
Query-string parsing
Custom object paths
```

---

# Safe Canary Property

During authorised testing, start with a unique harmless property.

For example:

```text
amPrototypeTest
```

with a value such as:

```text
AM-PP-123456
```

Then determine whether a newly created object unexpectedly inherits it.

The goal is:

```text
Canary
  ↓
Prototype
  ↓
Fresh Object
  ↓
Canary Inherited?
```

---

# Browser Console Verification

After sending a suspected pollution input, open the browser developer console.

Test:

```javascript
({}).amPrototypeTest
```

If the result is:

```text
AM-PP-123456
```

then prototype pollution may have occurred.

Another test:

```javascript
Object.prototype.amPrototypeTest
```

Be careful when testing production applications.

---

# Cleanup

If your testing directly modifies a prototype in a controlled local environment, remove the test property afterwards:

```javascript
delete Object.prototype.amPrototypeTest;
```

For web applications, refreshing the page may restore a clean JavaScript context for client-side pollution.

Do not assume that server-side pollution will be cleared by refreshing the browser.

---

# Query String Prototype Pollution

A common client-side source is query-string parsing.

Conceptually:

```text
https://target.example/?parameter=value
                 ↓
           Query Parser
                 ↓
              Object
```

If the parser supports nested object notation and handles prototype-related keys unsafely:

```text
URL
 ↓
Parser
 ↓
Prototype
```

may become possible.

---

# Example Testing Concept

Suppose an application parses nested parameters.

A controlled test may investigate whether a structure equivalent to:

```text
__proto__
    ↓
amPrototypeTest
    ↓
AM-PP-123456
```

can reach the prototype.

After the request is processed, test:

```javascript
({}).amPrototypeTest
```

The exact syntax required depends entirely on the application's parser.

---

# JSON Prototype Pollution

JSON-based APIs may expose another potential source.

Example application input:

```json
{
  "profile": {
    "displayName": "Alice"
  }
}
```

If the server recursively merges arbitrary object properties, prototype-related properties deserve investigation.

A harmless testing structure can conceptually represent:

```text
prototype path
      ↓
unique canary property
      ↓
unique canary value
```

Do not immediately attempt to modify application security properties.

First establish whether pollution itself is possible.

---

# Recursive Merge Functions

Custom recursive merge functions are a common place to look during source-code review.

Example:

```javascript
function merge(target, source) {
    for (const key in source) {
        if (typeof source[key] === "object") {
            if (!target[key]) {
                target[key] = {};
            }

            merge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }

    return target;
}
```

The security question is:

> Can attacker-controlled keys cause the recursion to traverse into prototype-related objects?

---

# Object Merge Operations

Search source code for operations involving:

```text
merge
extend
clone
assign
defaults
deepMerge
set
copy
```

Pay particular attention when:

```text
Attacker-controlled object
```

is recursively merged into:

```text
Application object
Configuration object
Default object
Request object
```

---

# Object.assign

`Object.assign()` itself should not automatically be labelled vulnerable.

Example:

```javascript
Object.assign(target, source);
```

The actual security behaviour depends on:

```text
Source object
Target object
Runtime behaviour
Property definitions
Application logic
```

Analyse the complete data flow rather than flagging the function name alone.

---

# for...in

Loops such as:

```javascript
for (const key in object) {
    target[key] = object[key];
}
```

deserve attention because `for...in` can enumerate inherited enumerable properties.

Safer code often needs to distinguish:

```text
Own properties
```

from:

```text
Inherited properties
```

---

# Object.keys

Using:

```javascript
Object.keys(object)
```

returns the object's own enumerable property names.

This can reduce some prototype-related risks compared with blindly iterating inherited properties.

However, it does not automatically make arbitrary object merging secure.

---

# Object.hasOwn

Modern JavaScript provides:

```javascript
Object.hasOwn(object, property)
```

Example:

```javascript
if (Object.hasOwn(user, "isAdmin")) {
    // process explicitly defined property
}
```

This avoids trusting a property merely because it exists somewhere in the prototype chain.

---

# hasOwnProperty

Older code commonly uses:

```javascript
object.hasOwnProperty("property")
```

However:

```javascript
Object.hasOwn(object, "property")
```

is generally clearer and avoids relying on the target object's inherited `hasOwnProperty` method.

---

# Prototype Pollution Gadgets

Successfully polluting a prototype does not necessarily produce meaningful impact.

The next step is gadget discovery.

A gadget is application code that uses a potentially polluted property in a security-sensitive way.

Conceptually:

```text
Polluted Property
       ↓
Application Reads Property
       ↓
Property Changes Behaviour
       ↓
Security Impact
```

---

# Client-Side Gadgets

Potential browser-side gadgets include code that constructs or modifies:

```text
HTML
Scripts
iframes
URLs
DOM elements
Event handlers
Configuration objects
```

Interesting sinks may include:

```javascript
innerHTML
outerHTML
document.write()
insertAdjacentHTML()
eval()
new Function()
setTimeout()
setInterval()
```

The presence of one of these functions does not automatically prove exploitability.

Trace attacker influence into the sink.

---

# Example Gadget Concept

Suppose application code behaves conceptually like:

```javascript
const config = {};

if (config.transport_url) {
    const script = document.createElement("script");
    script.src = config.transport_url;
    document.body.appendChild(script);
}
```

If:

```text
config.transport_url
```

does not exist as an own property, JavaScript may search the prototype chain.

Conceptually:

```text
Object.prototype.transport_url
            ↓
config.transport_url
            ↓
script.src
            ↓
External Script
```

This creates a potentially interesting prototype pollution gadget.

---

# DOM XSS Gadget Discovery

A useful workflow is:

```text
Confirm Pollution
      ↓
Search JavaScript
      ↓
Identify Reads of Missing Properties
      ↓
Trace Property
      ↓
Find DOM Sink
      ↓
Determine Context
      ↓
Validate Safely
```

---

# Search JavaScript

Use browser developer tools or downloaded JavaScript files.

Search for:

```text
innerHTML
outerHTML
document.write
insertAdjacentHTML
createElement
script.src
iframe.src
eval
Function
setTimeout
setInterval
```

Also search for configuration-style properties:

```text
url
src
href
html
template
callback
transport
script
```

These are leads, not confirmed vulnerabilities.

---

# Browser DevTools

Browser DevTools are extremely useful for prototype pollution analysis.

Useful areas include:

```text
Console
Sources
Network
Debugger
DOM inspector
Search
```

The console can help verify whether a property has reached:

```javascript
Object.prototype
```

while Sources can help identify gadgets.

---

# Breakpoints

JavaScript breakpoints can help determine:

```text
Where property is read
What object contains it
Whether property is inherited
Where value flows next
```

This is particularly useful for complicated bundled JavaScript.

---

# Source Maps

If source maps are available:

```text
.js.map
```

they can make gadget analysis substantially easier.

Source maps may reveal:

```text
Original source files
Function names
Module structure
Configuration objects
Readable variable names
```

Refer to:

[JavaScript Analysis](reconnaissance/javascript-analysis.md)

---

# Server-Side Gadgets

Server-side prototype pollution may influence:

```text
Application configuration
Authentication logic
Authorisation logic
HTTP request options
Template settings
Process options
File operations
Logging
Child process configuration
```

The exact impact is application-specific.

Do not assume that server-side prototype pollution automatically leads to remote code execution.

---

# Server-Side Detection Challenges

Client-side pollution can often be checked with:

```javascript
({}).property
```

Server-side pollution is harder because you cannot directly inspect the server's JavaScript runtime.

Instead, you may need to observe changes in application behaviour.

For example:

```text
Request
 ↓
Pollution Attempt
 ↓
Second Request
 ↓
Behaviour Changed?
```

---

# Non-Destructive Server-Side Detection

Prefer properties that cause harmless observable changes.

Potential categories include:

```text
Response formatting
Status behaviour
JSON structure
Configuration defaults
Debug-style behaviour
```

Only use properties you understand.

Avoid guessing dangerous runtime properties on production systems.

---

# Persistence

Server-side pollution may persist:

```text
For one request
Across requests
Until worker restart
Until process restart
```

depending on the vulnerable object and application architecture.

This makes server-side testing potentially disruptive.

---

# Worker Processes

Node.js applications may use:

```text
Multiple workers
Clusters
Containers
Serverless functions
```

A polluted prototype may therefore affect only one execution context.

Testing may appear inconsistent:

```text
Request 1 → affected worker
Request 2 → different worker
Request 3 → affected worker
```

Do not immediately conclude that inconsistent results are false positives.

---

# Denial of Service

Prototype pollution can sometimes destabilise an application.

For example, changing properties expected to contain:

```text
Numbers
Strings
Booleans
Functions
Objects
```

may cause unexpected exceptions.

During authorised testing:

```text
Avoid destructive properties
Use harmless canaries
Stop after sufficient evidence
```

---

# Authentication Logic

Consider insecure logic such as:

```javascript
if (user.isAdmin) {
    showAdminPanel();
}
```

If:

```text
isAdmin
```

is not explicitly defined on the object, inherited values may influence the check.

Secure logic should not depend on prototype inheritance for security-sensitive properties.

---

# Authorisation Logic

The same principle applies to:

```text
role
permissions
isAdmin
isStaff
isOwner
canDelete
canApprove
```

A secure application should derive authorisation from trusted server-side state.

Prototype pollution should never be able to create an authorisation decision.

---

# Example Authorisation Pattern

Potentially dangerous conceptual pattern:

```javascript
const user = {};

if (user.isAdmin) {
    allow();
}
```

If:

```text
Object.prototype.isAdmin
```

can be influenced, the property lookup may produce an unexpected result.

Safer logic should use explicit trusted properties and robust authorisation checks.

---

# Configuration Objects

Configuration objects are particularly interesting.

Example:

```javascript
const options = {};

performAction(options);
```

If downstream code checks:

```javascript
options.someSetting
```

without ensuring it is an own property, an inherited value may influence behaviour.

---

# Default Values

Prototype pollution can interact with default-value logic.

Example:

```javascript
if (!config.mode) {
    config.mode = "safe";
}
```

If:

```text
config.mode
```

is inherited, the default may never be assigned.

This can alter application behaviour unexpectedly.

---

# Property Existence Checks

Be cautious with:

```javascript
if (object.property) {
```

when the property controls security-sensitive behaviour.

This checks both:

```text
Own properties
Inherited properties
```

Where appropriate, explicitly check ownership.

---

# The `in` Operator

Example:

```javascript
"property" in object
```

returns true for both own and inherited properties.

Therefore:

```javascript
"isAdmin" in user
```

does not establish that `isAdmin` was explicitly assigned to the user object.

---

# Prototype Pollution and JSON

An important nuance is that JSON parsing and prototype mutation are separate concepts.

A JSON document containing a property named:

```text
__proto__
```

does not necessarily pollute the prototype simply by being parsed.

The danger often appears later when parsed data is:

```text
Merged
Copied
Assigned
Traversed
```

into another object.

Think:

```text
JSON Input
   ↓
JSON.parse()
   ↓
Ordinary Object
   ↓
Unsafe Merge
   ↓
Prototype Pollution
```

---

# Prototype Pollution and Query Parsers

Libraries that transform:

```text
a[b][c]=value
```

into nested JavaScript objects deserve attention.

Conceptually:

```text
Query String
     ↓
Parser
     ↓
Nested Object
```

The parser must safely handle prototype-related property names.

Modern versions of many libraries include protections, but outdated or custom implementations may behave differently.

---

# Dependency Review

During source-assisted testing, inspect JavaScript dependencies.

Look for:

```text
Package name
Package version
Known prototype pollution history
Custom wrappers
Unsafe configuration
```

Do not report a vulnerability solely because a dependency version has historically been associated with prototype pollution.

Confirm whether the vulnerable functionality is actually reachable.

---

# package.json

For Node.js applications, review:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
```

These can help identify:

```text
Libraries
Versions
Dependency chains
Parsing libraries
Merge libraries
```

---

# npm audit

In a controlled source-code environment:

```bash
npm audit
```

may identify known dependency vulnerabilities.

Treat results as leads.

You still need to determine:

```text
Is vulnerable version present?
Is vulnerable functionality used?
Is attacker-controlled input reachable?
Is security impact possible?
```

---

# Static Source Search

Useful search terms include:

```text
__proto__
prototype
constructor
merge
deepMerge
extend
clone
set
defaults
Object.assign
for...in
```

Example:

```bash
grep -RniE "__proto__|constructor|prototype|merge|extend|deepMerge" .
```

For JavaScript-heavy projects:

```bash
grep -RniE "innerHTML|outerHTML|document\.write|insertAdjacentHTML|eval|new Function" .
```

---

# Client-Side Testing Workflow

A practical client-side workflow is:

```text
Browse Application
      ↓
Identify JavaScript
      ↓
Identify URL Parsing
      ↓
Test Harmless Canary
      ↓
Check Object.prototype
      ↓
Pollution Confirmed?
      ↓
YES
      ↓
Search for Gadgets
      ↓
Trace Polluted Property
      ↓
Dangerous Sink?
      ↓
Validate Impact
```

---

# Server-Side Testing Workflow

```text
Identify JSON / Nested Input
       ↓
Understand Object Processing
       ↓
Use Harmless Canary
       ↓
Submit Pollution Attempt
       ↓
Observe Current Response
       ↓
Send Follow-Up Request
       ↓
Behaviour Changed?
       ↓
Identify Affected Property
       ↓
Trace Application Behaviour
       ↓
Assess Security Impact
```

---

# Burp Suite Workflow

Burp Suite can help systematically test prototype pollution sources.

A practical workflow is:

```text
Proxy
  ↓
HTTP History
  ↓
Identify JSON / Query Input
  ↓
Send to Repeater
  ↓
Baseline Request
  ↓
Insert Harmless Prototype Canary
  ↓
Send
  ↓
Observe Response
  ↓
Browser Console / Follow-Up Request
  ↓
Confirm Pollution
  ↓
Investigate Gadget
```

---

# Burp Repeater

Repeater is particularly useful for:

```text
JSON APIs
Nested parameters
Query strings
Configuration endpoints
Profile updates
Application settings
```

Start with a baseline request and change only the suspected prototype-related structure.

---

# Burp Proxy

Proxy helps identify endpoints accepting:

```text
JSON objects
Nested parameters
Configuration
User preferences
Metadata
Filters
Search options
```

These can become useful prototype pollution entry points.

---

# Burp DOM Invader

Burp Suite's browser includes:

```text
DOM Invader
```

DOM Invader is particularly useful for client-side vulnerability research.

It can assist with:

```text
DOM XSS
Prototype pollution
DOM clobbering
Web message analysis
```

For prototype pollution, it can help identify:

```text
Sources
Pollution
Potential gadgets
```

---

# DOM Invader Workflow

A useful workflow is:

```text
Open Burp Browser
      ↓
Enable DOM Invader
      ↓
Browse Target
      ↓
Open DevTools
      ↓
DOM Invader
      ↓
Prototype Pollution
      ↓
Identify Sources
      ↓
Test Canary
      ↓
Search for Gadgets
      ↓
Manually Verify
```

Automation should assist analysis, not replace it.

---

# DOM Invader Canary

DOM Invader can help inject a canary property and detect whether it reaches the prototype.

Conceptually:

```text
URL
 ↓
Prototype Pollution Source
 ↓
Canary
 ↓
Object.prototype
 ↓
DOM Invader Detects Property
```

Once pollution is confirmed, investigate whether the property can reach a useful gadget.

---

# DOM Invader Gadget Detection

A gadget may take a polluted property and use it in a dangerous browser operation.

Conceptually:

```text
Polluted Property
       ↓
JavaScript Gadget
       ↓
DOM Sink
       ↓
Potential XSS
```

DOM Invader can help identify these relationships.

Manual validation remains important.

---

# Burp Scanner

Depending on Burp Suite edition and application behaviour, automated scanning may identify prototype pollution-related issues.

Treat scanner findings as:

```text
Potential vulnerability
```

until manually reproduced.

---

# Browser Console Workflow

After a suspected client-side pollution attempt:

```javascript
({}).amPrototypeTest
```

If undefined:

```text
Pollution not confirmed
```

If the canary appears:

```text
Pollution primitive may exist
```

Then investigate:

```text
Where did it come from?
Which input created it?
Which properties are useful?
Which gadget consumes them?
```

---

# Testing Different Sources

Potential client-side sources:

```text
Query parameters
Fragments
postMessage
Cookies
Local storage
Session storage
JSON responses
```

Potential server-side sources:

```text
JSON request bodies
Form parameters
Nested query parameters
Configuration APIs
Object update endpoints
WebSocket messages
```

---

# postMessage

Client-side applications may accept cross-window messages:

```javascript
window.addEventListener("message", function(event) {
    // process event.data
});
```

If:

```text
event.data
```

is merged into application objects, investigate whether prototype-related properties are handled safely.

Also verify origin validation independently.

---

# WebSockets

WebSocket applications frequently exchange JSON objects.

Example:

```json
{
  "action": "update",
  "options": {
    "theme": "dark"
  }
}
```

If arbitrary nested objects are merged server-side or client-side, prototype pollution may become relevant.

Refer to:

```text
docs/web/websockets.md
```

---

# API Testing

APIs commonly expose:

```text
JSON
Nested structures
Patch operations
Configuration objects
```

Potentially interesting endpoints include:

```text
/profile
/settings
/preferences
/config
/update
/import
```

Focus on endpoints that recursively process user-controlled objects.

Refer to:

[API Security](api-security.md)

---

# GraphQL

GraphQL mutations may accept nested input objects.

Example conceptually:

```graphql
mutation {
    updateSettings(input: {
        theme: "dark"
    }) {
        success
    }
}
```

The GraphQL layer itself is not necessarily vulnerable.

Investigate what happens when nested input reaches JavaScript object-processing logic.

---

# Mass Assignment vs Prototype Pollution

Mass assignment:

```text
Attacker supplies legitimate object properties
        ↓
Application assigns properties it should not
```

Prototype pollution:

```text
Attacker manipulates prototype-related properties
        ↓
Other objects inherit attacker-controlled values
```

These can appear in similar endpoints but are distinct vulnerability classes.

---

# Prototype Pollution vs Object Injection

Prototype pollution specifically involves:

```text
Prototype chain manipulation
```

Generic object injection may involve attacker-controlled object properties without modifying shared prototypes.

Use precise terminology when reporting.

---

# Prototype Pollution vs Insecure Deserialization

Insecure deserialization involves unsafe processing of serialised objects or object graphs.

Prototype pollution involves unsafe manipulation of JavaScript prototype inheritance.

They may occur in related object-processing code, but they are separate issues.

Refer to:

[Insecure Deserialization](deserialization.md)

---

# Prototype Pollution vs Parameter Pollution

HTTP parameter pollution involves duplicate or ambiguous HTTP parameters.

Prototype pollution involves JavaScript object prototypes.

Do not confuse:

```text
Parameter Pollution
```

with:

```text
Prototype Pollution
```

---

# Testing for Gadgets

After confirming pollution, create a list:

```text
Pollutable Property
       ↓
Where Is It Read?
       ↓
What Type Is Expected?
       ↓
What Does It Control?
       ↓
Does It Reach a Sink?
```

For each candidate:

```text
Property:
Expected type:
Read location:
Destination:
Security impact:
```

This makes analysis systematic.

---

# Property Types

A gadget may expect:

```text
String
Boolean
Number
Object
Array
Function
```

The polluted value must normally match the application's expectations.

For example:

```text
isAdmin → Boolean
url → String
timeout → Number
options → Object
```

Understanding expected types reduces unnecessary testing.

---

# Boolean Gadgets

A property may control whether functionality is enabled.

Conceptually:

```javascript
if (options.enabled) {
    performAction();
}
```

If:

```text
enabled
```

can be inherited from the prototype, pollution may alter application behaviour.

---

# String Gadgets

String properties commonly control:

```text
URLs
HTML
File names
Template names
Commands
Paths
```

Example:

```javascript
element.innerHTML = options.html;
```

If:

```text
options.html
```

is inherited and attacker-controlled, investigate the resulting context.

---

# URL Gadgets

Potential properties include:

```text
url
src
href
endpoint
callback
redirect
transport_url
```

Potential sinks include:

```text
script.src
iframe.src
location
fetch()
XMLHttpRequest
```

The resulting vulnerability depends on context.

---

# DOM Sink Review

Important browser sinks include:

```text
innerHTML
outerHTML
insertAdjacentHTML
document.write
eval
Function
script.src
iframe.src
location
```

Some sinks lead to:

```text
HTML injection
```

others to:

```text
JavaScript execution
```

and others to:

```text
Navigation or network requests
```

Classify the actual behaviour.

---

# Prototype Pollution to DOM XSS

A typical chain is:

```text
URL Parameter
     ↓
Prototype Pollution
     ↓
Polluted Property
     ↓
Application Configuration
     ↓
DOM Gadget
     ↓
Unsafe HTML / Script Sink
     ↓
DOM XSS
```

The finding should explain the complete chain.

---

# Prototype Pollution to Access Control

Conceptually:

```text
Attacker Input
     ↓
Prototype
     ↓
isAdmin = true
     ↓
Application Checks user.isAdmin
     ↓
Inherited Value Accepted
     ↓
Authorisation Decision
```

This requires a real vulnerable application flow.

Do not claim privilege escalation simply because you can create an `isAdmin` property on a prototype.

---

# Prototype Pollution to Server-Side Code Execution

Server-side prototype pollution can, in specific application and runtime contexts, become part of a chain leading to code execution.

However:

```text
Prototype Pollution
≠
Automatic RCE
```

A complete exploit requires a suitable server-side gadget.

During assessment:

```text
Confirm pollution
Identify application/runtime gadget
Understand exact behaviour
Use minimum-impact validation
```

Do not attempt speculative destructive gadget chains on production systems.

---

# Detection Without Exploitation

A strong finding can sometimes be demonstrated with:

```text
Controlled Input
      ↓
Prototype Pollution
      ↓
Harmless Property
      ↓
Observable Application Behaviour
```

You do not always need to demonstrate the worst theoretical impact.

Document:

```text
Confirmed primitive
Reachable gadget
Realistic security impact
```

separately.

---

# False Positives

Do not report prototype pollution solely because:

```text
__proto__ appears in source code
A dependency had a historical CVE
A scanner reports a possible issue
A query parameter is accepted
A property appears in an object
```

Confirm actual prototype modification.

---

# Verification Questions

Ask:

```text
Can attacker-controlled input reach object processing?

Can prototype-related property names be supplied?

Does the prototype actually change?

Can a fresh object inherit the property?

Does the pollution persist?

Is there a useful gadget?

Can the gadget cross a security boundary?
```

---

# Client-Side Checklist

## Discovery

```text
[ ] Identify JavaScript bundles
[ ] Check source maps
[ ] Identify query parsers
[ ] Identify fragment processing
[ ] Identify postMessage handlers
[ ] Identify configuration objects
[ ] Identify object merge functions
```

## Pollution

```text
[ ] Test harmless canary
[ ] Check __proto__ handling
[ ] Check constructor.prototype handling
[ ] Verify Object.prototype
[ ] Verify fresh object inheritance
[ ] Refresh and confirm repeatability
```

## Gadgets

```text
[ ] Search innerHTML
[ ] Search outerHTML
[ ] Search document.write
[ ] Search insertAdjacentHTML
[ ] Search script.src
[ ] Search iframe.src
[ ] Search eval
[ ] Search Function
[ ] Search configuration properties
```

## Tools

```text
[ ] Burp Proxy
[ ] Burp Repeater
[ ] Burp Browser
[ ] DOM Invader
[ ] Browser DevTools
[ ] Source search
```

---

# Server-Side Checklist

## Discovery

```text
[ ] Identify Node.js
[ ] Identify JSON endpoints
[ ] Identify nested parameters
[ ] Identify configuration endpoints
[ ] Identify merge functions
[ ] Review package.json where available
[ ] Review dependencies
```

## Pollution

```text
[ ] Establish baseline
[ ] Use harmless canary
[ ] Send pollution attempt
[ ] Send follow-up request
[ ] Observe behaviour
[ ] Check repeatability
[ ] Consider multiple workers
```

## Impact

```text
[ ] Configuration manipulation
[ ] Authentication impact
[ ] Authorisation impact
[ ] Response manipulation
[ ] Network behaviour
[ ] Template behaviour
[ ] Application stability
[ ] Potential gadget chain
```

---

# Source Code Review Checklist

```text
[ ] Search __proto__
[ ] Search prototype
[ ] Search constructor
[ ] Search recursive merge
[ ] Search deep merge
[ ] Search Object.assign
[ ] Search for...in
[ ] Search dynamic property assignment
[ ] Search query parsing
[ ] Search JSON processing
[ ] Search configuration merging
[ ] Search DOM sinks
[ ] Trace attacker-controlled objects
```

---

# Quick Reference

```text
ATTACKER INPUT
      ↓
OBJECT PROCESSING
      ↓
CAN PROTOTYPE BE REACHED?
      ↓
     YES
      ↓
POLLUTE HARMLESS CANARY
      ↓
CREATE FRESH OBJECT
      ↓
CANARY INHERITED?
      ↓
     YES
      ↓
PROTOTYPE POLLUTION CONFIRMED
      ↓
SEARCH FOR GADGET
      ↓
PROPERTY READ?
      ↓
     YES
      ↓
DANGEROUS SINK?
      ↓
     YES
      ↓
VALIDATE SECURITY IMPACT
      ↓
REPORT
```

---

# Practical Testing Notes

Keep a table during testing:

| ID | Source | Property | Canary | Result | Gadget |
|---|---|---|---|---|---|
| PP-001 | Query | `amPrototypeTest` | `AM-PP-001` | Not inherited | None |
| PP-002 | JSON | `amPrototypeTest` | `AM-PP-002` | Inherited | Investigate |
| PP-003 | Fragment | `amPrototypeTest` | `AM-PP-003` | Not inherited | None |

This becomes particularly useful when an application has several JavaScript parsers.

---

# Evidence Collection

For a confirmed prototype pollution vulnerability, record:

```text
Affected URL
Affected parameter
HTTP method
Input format
Prototype path
Canary property
Canary value
Baseline behaviour
Pollution request
Verification method
Prototype verification
Persistence behaviour
Affected JavaScript
Gadget
Sink
Security impact
Browser/runtime information
Relevant screenshots
```

---

# Example Finding: Client-Side Prototype Pollution

```text
Finding:
Client-Side Prototype Pollution via URL Query Parameters

Affected Endpoint:
/application

Observed:
The application processes nested query-string parameters using client-side JavaScript.

A controlled prototype pollution test introduced a unique harmless property into Object.prototype.

After processing the supplied input, a newly created JavaScript object inherited the controlled property even though it was not explicitly defined on that object.

Impact:
An attacker can influence properties inherited by JavaScript objects within the affected page. The security impact depends on whether polluted properties are consumed by security-sensitive application gadgets.

Recommendation:
Prevent prototype-related property names from being processed during object construction and use safe, maintained parsing and merge functionality.
```

---

# Example Finding: Prototype Pollution to DOM XSS

```text
Finding:
Client-Side Prototype Pollution Leads to DOM-Based Cross-Site Scripting

Observed:
Attacker-controlled URL input was able to introduce a property into Object.prototype.

Application JavaScript subsequently read the inherited property from a configuration object and passed the resulting value to a DOM sink without appropriate handling.

Impact:
An attacker may be able to execute JavaScript in the browser of a user who visits a crafted application URL.

Recommendation:
Prevent prototype pollution at the source and remove the unsafe gadget by ensuring untrusted values cannot reach executable DOM sinks.
```

---

# Example Finding: Server-Side Prototype Pollution

```text
Finding:
Server-Side Prototype Pollution via JSON Object Merge

Affected Endpoint:
/api/settings

Observed:
The endpoint recursively merged attacker-controlled JSON properties into a server-side JavaScript object.

A controlled harmless property was introduced through a prototype-related property path and subsequently influenced newly created objects within the application.

Impact:
An attacker can manipulate inherited server-side object properties. Depending on available application gadgets, this may affect application configuration, security decisions or other server-side behaviour.

Recommendation:
Reject prototype-related property names, use safe object merge implementations and ensure security-sensitive configuration does not rely on inherited properties.
```

---

# Example Finding: Authorisation Impact

```text
Finding:
Prototype Pollution Influences Server-Side Authorisation Logic

Observed:
A prototype pollution primitive allowed an inherited security-sensitive property to influence an application authorisation decision.

The affected logic trusted the inherited property without verifying that it was explicitly associated with the authenticated user.

Impact:
An attacker may be able to obtain functionality or permissions not assigned to their account.

Recommendation:
Prevent prototype pollution and derive authorisation decisions exclusively from trusted server-side identity and permission data. Security-sensitive properties should not be inherited from generic object prototypes.
```

---

# Reporting Titles

Prefer precise titles such as:

```text
Client-Side Prototype Pollution via Query Parameter

Prototype Pollution Leads to DOM-Based Cross-Site Scripting

Server-Side Prototype Pollution via Unsafe Recursive Object Merge

Prototype Pollution Influences Authorisation Logic

Prototype Pollution in Configuration Object Allows Application Behaviour Manipulation

Prototype Pollution via Unsafe Nested Parameter Parsing
```

Avoid vague titles such as:

```text
JavaScript Issue

Prototype Issue
```

---

# Severity

Severity depends on the complete chain.

For example:

```text
Prototype Pollution
      ↓
No Useful Gadget
```

may have limited demonstrated impact.

While:

```text
Prototype Pollution
      ↓
DOM Gadget
      ↓
JavaScript Execution
```

may result in XSS.

Or:

```text
Server-Side Prototype Pollution
      ↓
Security-Sensitive Gadget
      ↓
Authorisation Bypass
```

may have significantly greater impact.

Report the demonstrated security impact rather than assigning severity based solely on the pollution primitive.

---

# Remediation

Prototype pollution should be addressed at multiple layers.

A defence-in-depth model is:

```text
Validate Input
     ↓
Reject Dangerous Keys
     ↓
Use Safe Object Operations
     ↓
Avoid Prototype Inheritance Where Unnecessary
     ↓
Use Own-Property Checks
     ↓
Update Dependencies
     ↓
Remove Dangerous Gadgets
```

---

# Reject Prototype-Related Keys

Applications that accept arbitrary object properties should reject dangerous property names where they are not required.

Examples include:

```text
__proto__
prototype
constructor
```

Filtering must account for the complete object-processing logic.

Simply blocking one string is not necessarily sufficient.

---

# Schema Validation

Prefer explicit input schemas.

Instead of:

```text
Accept arbitrary object
```

define:

```text
Allowed property A
Allowed property B
Allowed property C
```

Conceptually:

```text
Incoming JSON
     ↓
Schema Validation
     ↓
Known Property?
   ↓          ↓
 YES         NO
 ↓            ↓
Process      Reject
```

---

# Avoid Arbitrary Recursive Merging

Avoid recursively merging untrusted objects into application objects unless absolutely necessary.

Instead of:

```text
User Object
    ↓
Recursive Merge
    ↓
Application Configuration
```

prefer explicitly copying required properties.

---

# Explicit Property Assignment

For example:

```javascript
const settings = {
    theme: input.theme,
    language: input.language
};
```

This is generally easier to reason about than accepting an arbitrary nested object.

---

# Null-Prototype Objects

Where inheritance is unnecessary, objects can be created without a prototype:

```javascript
const dictionary = Object.create(null);
```

Such objects do not inherit from:

```javascript
Object.prototype
```

This can be useful for dictionary-style data structures.

It is not a universal replacement for normal objects.

---

# Object.freeze

In some environments, defensive use of:

```javascript
Object.freeze()
```

may help protect specific objects from modification.

For example:

```javascript
Object.freeze(Object.prototype);
```

can have significant compatibility implications and should not be introduced blindly.

Fix the vulnerable input processing rather than relying solely on runtime freezing.

---

# Own-Property Checks

Security-sensitive code should distinguish own properties from inherited properties.

Prefer:

```javascript
Object.hasOwn(object, "property")
```

where appropriate.

For example:

```javascript
if (
    Object.hasOwn(user, "isAdmin") &&
    user.isAdmin === true
) {
    // authorised behaviour
}
```

Authorisation should still rely on trusted server-side state.

---

# Dependency Updates

Keep JavaScript dependencies current.

Pay particular attention to packages performing:

```text
Deep merging
Query parsing
Object cloning
Configuration processing
Property path assignment
```

Review:

```text
package.json
package-lock.json
yarn.lock
pnpm-lock.yaml
```

---

# Do Not Rely Only on Dependency Patching

Even when dependencies are current, custom application code may remain vulnerable.

Review:

```text
Custom merge functions
Custom query parsers
Dynamic property assignment
Configuration merging
```

as well.

---

# Remove Gadgets

Defence should not stop at preventing prototype pollution.

Where possible, remove dangerous gadgets.

For example, avoid:

```javascript
element.innerHTML = config.html;
```

when safe DOM APIs can be used.

This creates defence in depth:

```text
Pollution Prevention
       +
Gadget Removal
       =
Reduced Exploitability
```

---

# Use Safe DOM APIs

Prefer:

```javascript
textContent
```

when rendering text.

Example:

```javascript
element.textContent = value;
```

rather than:

```javascript
element.innerHTML = value;
```

when HTML interpretation is not required.

Refer to:

```text
docs/web/xss.md
```

---

# Test After Remediation

After remediation, repeat:

```text
Original source
 ↓
Prototype canary
 ↓
Prototype verification
 ↓
Gadget verification
```

Confirm that:

```text
Dangerous keys rejected
Prototype unchanged
Fresh objects unaffected
Application functionality preserved
```

---

# Prototype Pollution Testing Checklist

```text
[ ] Identify JavaScript environment

[ ] Determine client-side or server-side

[ ] Identify attacker-controlled object input

[ ] Identify query or JSON parsers

[ ] Identify recursive merge functionality

[ ] Test harmless unique canary

[ ] Check __proto__ handling

[ ] Check constructor.prototype handling

[ ] Verify actual prototype modification

[ ] Verify inheritance using fresh object

[ ] Determine persistence

[ ] Identify potential gadgets

[ ] Trace polluted property

[ ] Identify sink

[ ] Validate security impact safely

[ ] Document source-to-sink chain

[ ] Clean up where applicable
```

---

# Tools

Useful tools include:

```text
Burp Suite
Burp Repeater
Burp Proxy
Burp DOM Invader
Browser DevTools
JavaScript source search
grep
ripgrep
npm audit
```

The most important tools are often:

```text
Browser DevTools
+
DOM Invader
+
Manual JavaScript Analysis
```

because prototype pollution exploitation depends heavily on application-specific gadgets.

---

# References

## PortSwigger Web Security Academy: Prototype Pollution

https://portswigger.net/web-security/prototype-pollution

PortSwigger provides detailed coverage of:

```text
JavaScript prototypes
Prototype pollution sources
Client-side prototype pollution
Server-side prototype pollution
Prototype pollution gadgets
DOM XSS
Manual testing
DOM Invader
Remediation
```

---

## PortSwigger Prototype Pollution Labs

https://portswigger.net/web-security/all-labs#prototype-pollution

Practical labs covering client-side and server-side prototype pollution.

---

## PortSwigger: Finding Client-Side Prototype Pollution with DOM Invader

https://portswigger.net/burp/documentation/desktop/tools/dom-invader/prototype-pollution

Documentation for using Burp's DOM Invader during prototype pollution testing.

---

## OWASP Prototype Pollution Prevention Cheat Sheet

https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html

OWASP guidance for preventing prototype pollution in JavaScript applications.

---

## MDN: Inheritance and the Prototype Chain

https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Inheritance_and_the_prototype_chain

Useful background on JavaScript prototype-based inheritance.

---

## MDN: Object.hasOwn()

https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/hasOwn

Reference for checking whether a property exists directly on an object rather than through its prototype chain.

---

## MDN: Object.create()

https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/create

Reference for creating objects with explicitly selected prototypes, including null-prototype objects.

---

# Final Prototype Pollution Testing Model

```text
                       ATTACKER INPUT
                             ↓
               ┌─────────────┼─────────────┐
               ↓             ↓             ↓
             QUERY          JSON        MESSAGE
               ↓             ↓             ↓
               └─────────────┼─────────────┘
                             ↓
                    OBJECT PROCESSING
                             ↓
               ┌─────────────┼─────────────┐
               ↓             ↓             ↓
             MERGE          PARSE          SET
               ↓             ↓             ↓
               └─────────────┼─────────────┘
                             ↓
                PROTOTYPE PATH REACHABLE?
                             ↓
                            YES
                             ↓
                    HARMLESS CANARY
                             ↓
                    PROTOTYPE MODIFIED?
                             ↓
                            YES
                             ↓
                 FRESH OBJECT INHERITS?
                             ↓
                            YES
                             ↓
              PROTOTYPE POLLUTION PRIMITIVE
                             ↓
                       FIND GADGET
                             ↓
               ┌─────────────┼─────────────┐
               ↓             ↓             ↓
              DOM         CONFIG       SECURITY
            PROPERTY      PROPERTY      PROPERTY
               ↓             ↓             ↓
               └─────────────┼─────────────┘
                             ↓
                     DANGEROUS SINK?
                             ↓
                            YES
                             ↓
                  SECURITY BOUNDARY CROSSED
                             ↓
                    VALIDATE MINIMALLY
                             ↓
                         DOCUMENT
                             ↓
                           REPORT
```

The key principle is:

> Prototype pollution is usually the beginning of the vulnerability chain rather than the end. First prove that attacker-controlled input can modify a prototype using a harmless canary. Then determine which application properties inherit that value, identify a suitable gadget, trace the value into a security-sensitive sink, and report the demonstrated impact rather than assuming that prototype pollution automatically means XSS, privilege escalation or remote code execution.
