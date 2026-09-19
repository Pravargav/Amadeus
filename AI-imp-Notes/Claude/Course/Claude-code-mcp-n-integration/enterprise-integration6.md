# Authentication and Integration Checklist

This section summarizes the key security decisions needed when connecting Claude/MCP integrations to different types of services.

---

# Service Types and Recommended Authentication

## 1. Remote Service with User Identity

Examples:

- Google Workspace
- Jira
- Linear
- Salesforce

### Authentication

Use:

```text
OAuth
```

### Secret Storage

```text
OAuth token issued by the provider
and stored securely by the client.
```

### Logging

```text
PostToolUse Hook
      ↓
Audit Log
```

Every tool invocation should be logged for auditing purposes.

### Configuration Control

```text
Administrator
      ↓
Enterprise Managed Settings
```

Admins can centrally enforce configuration and prevent users from changing it.

---

## 2. Remote Service with Service Identity

Examples:

- Internal APIs
- Backend Services
- Enterprise Databases
- Service-to-Service Integrations

### Authentication

Use:

```text
API Key
```

### Secret Storage

```text
Environment Variable
```

Example:

```bash
export API_KEY=secret_value
```

Never store secrets directly in source code or committed configuration files.

### Logging

```text
PostToolUse Hook
      ↓
Audit Log
```

### Configuration Control

```text
Administrator
      ↓
Enterprise Managed Settings
```

---

## 3. Local Services

Examples:

- Local Files
- Local Databases
- Local Development Tools

### Authentication

```text
File-System Permissions
```

No network credential is required.

### Secret Storage

```text
No credential needed
```

Access control is enforced through:

- OS permissions
- Allow/Deny rules

### Logging

```text
PostToolUse Hook
      ↓
Audit Log
```

### Configuration Control

```text
Deny Rules
      ↓
Enterprise Managed Settings
```

---

# Cost, Complexity, and Risk

## Cost

Different authentication mechanisms introduce operational overhead.

### OAuth

Requires:

- User sign-in
- Initial setup per service

### API Keys

Require:

- Secret management
- Rotation procedures

### Audit Logging

Requires:

- Logging infrastructure
- Storage for compliance records

---

## Complexity

Enterprise environments introduce additional requirements beyond building a working connection:

- Identity management
- Secret handling
- Auditability
- Compliance controls
- Data governance

A prototype often ignores these concerns.

An enterprise deployment cannot.

---

## Risk

The highest risk appears when a prototype is promoted to production.

A system becomes risky if it has:

```text
Hardcoded Credentials
+
No Audit Logging
+
No Central Administration
```

Such systems typically fail security reviews.

---

# When This Approach Works Well

Use the full enterprise checklist when:

- Working with regulated customers
- Handling sensitive data
- Supporting compliance audits
- Requiring centralized governance

Examples:

- Healthcare systems
- Financial systems
- Government systems
- Enterprise SaaS integrations

### Benefit

Security requirements are addressed early rather than delaying deployment later.

---

# When It Adds Cost or Complexity

Some teams are unfamiliar with:

- OAuth
- Secret stores
- Enterprise security processes

These environments typically require collaboration with:

- Security teams
- IT administrators
- Compliance reviewers

Project schedules should account for this coordination.

---

# When a Simpler Approach Is Acceptable

For:

- Demos
- Proofs of concept
- Internal experiments
- Non-production systems

The full enterprise checklist may be unnecessary.

However, one best practice should always be followed:

```text
Never hardcode secrets.
```

Use environment variables even in prototypes.

---

# Case Study: OAuth Worked in Staging but Failed in Production

## Setup

The team successfully tested OAuth in staging.

```text
staging.mycompany.com
      ↓
OAuth Works
```

They assumed production would also work.

```text
production.mycompany.com
      ↓
OAuth Fails
```

---

# What Happened?

OAuth providers validate a:

```text
Redirect URI
```

during login.

Only registered redirect URIs are allowed.

Example:

Registered:

```text
https://staging.mycompany.com/callback
```

Not Registered:

```text
https://production.mycompany.com/callback
```

When users attempted to sign in:

```text
User Login
      ↓
OAuth Provider
      ↓
Redirect URI Check
      ↓
Mismatch
      ↓
Authentication Failure
```

The login flow failed even though the code was correct.

---

# The Root Cause

The problem was not:

```text
Code Defect
```

The problem was:

```text
Missing OAuth Configuration
```

The production redirect URI was never added to the OAuth application registration.

---

# The Security Review Conversation

### Security Reviewer

> Every production sign-in attempt fails because of a redirect URI mismatch.

### Developer

> It worked in staging.

