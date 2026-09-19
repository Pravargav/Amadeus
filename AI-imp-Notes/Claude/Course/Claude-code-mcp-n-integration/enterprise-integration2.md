## Authentication & Integration Checklist (Claude Developer Certification Notes)

### Quick Exam Summary

When connecting Claude to enterprise systems, focus on four decisions:

1. Authentication method
2. Secret storage location
3. Audit logging
4. Configuration governance

The choice depends on the type of service being integrated.

---

### 1. Remote Service with User Identity

Examples:

- Salesforce
- Google Workspace
- Microsoft 365
- Linear

Authentication:

- OAuth

Secret Storage:

- OAuth provider issues tokens.
- Client securely stores the token.

Logging:

- PostToolUse hook logs every tool call.

Configuration Control:

- Enterprise administrators lock configuration through managed settings.

Remember:

Claude acts **as the user**.

Flow:

```text
User Login
      ↓
OAuth Authorization
      ↓
Access Token Issued
      ↓
Claude Acts As User
      ↓
Audit Log Created
```

---

### 2. Remote Service with Service Identity

Examples:

- Internal APIs
- Backend Services
- Service Accounts

Authentication:

- API Key
- Service Account Credential

Secret Storage:

- Environment variables
- Secret managers

Never:

```text
Hardcode keys into code
```

Always:

```text
Store keys outside code
```

Logging:

- PostToolUse hook

Configuration Control:

- Enterprise-managed settings

Remember:

Claude acts **as a service account**, not as an individual user.

Flow:

```text
Service Account
       ↓
API Key
       ↓
Environment Variable
       ↓
Claude Accesses Service
       ↓
Audit Log Created
```

---

### 3. Local Services

Examples:

- File System
- Local Database
- Local Tools

Authentication:

- No network authentication

Security Boundary:

- Operating system permissions

Secret Storage:

- No credential required

Governance:

- Allow rules
- Deny rules

Logging:

- PostToolUse hook

Configuration Control:

- Enterprise-managed deny rules

Remember:

Security comes from file-system permissions, not OAuth or API keys.

Flow:

```text
Claude
   ↓
Local Tool
   ↓
OS Permissions
   ↓
Allow / Deny Rules
   ↓
Audit Log
```

---

## Enterprise Checklist for Exams

Before production deployment verify:

### Authentication

Ask:

- Is OAuth required?
- Is API key authentication required?
- Is local permission-based access sufficient?

---

### Secret Management

Verify:

- No secrets inside source code.
- No secrets inside repository files.
- Secret stored in environment variable or secret manager.

Correct:

```json
{
  "apiKey": "${API_KEY}"
}
```

Wrong:

```json
{
  "apiKey": "my-secret-key"
}
```

---

### Audit Logging

Verify:

- PostToolUse hooks enabled.
- Every tool call logged.
- Logs available for compliance review.

Captured information typically includes:

- User
- Tool
- Parameters
- Timestamp
- Result

---

### Configuration Governance

Verify:

- Users cannot override security controls.
- Administrators manage settings centrally.
- Authentication configuration is consistent.

---

## Cost, Complexity, and Risk

### Cost

Enterprise security has some operational costs:

#### OAuth

Requires:

- OAuth application setup
- User authorization

Usually a one-time setup per service.

---

#### API Keys

Requires:

- Secret storage
- Secret rotation process

---

#### Audit Logging

Requires:

- PostToolUse hooks
- Log storage

Adds a small overhead to every tool execution.

---

### Complexity

Prototype environment:

```text
Can Claude connect?
```

Enterprise environment:

```text
Can Claude connect securely?
Can it be audited?
Can admins control it?
Can it pass compliance review?
```

The extra requirements increase deployment complexity.

---

### Risk

Highest risk appears when moving:

```text
Prototype → Production
```

Common mistakes:

- Hardcoded credentials
- No audit logs
- No centralized control
- Weak secret management

These issues often fail security reviews.

Key lesson:

Security requirements should be addressed during planning, not during the final review.

---

## When This Approach Works Best

### Ideal For

- Healthcare systems
- Banking platforms
- Insurance applications
- Enterprise SaaS integrations
- Any regulated environment

Benefits:

- Better compliance
- Easier audits
- Consistent governance
- Reduced security risk

---

## What Adds Complexity

Organizations unfamiliar with:

- OAuth
- Secret managers
- Compliance controls
- Enterprise governance

often need help from:

- Security teams
- IT administrators
- Compliance stakeholders

Project timelines should include this coordination effort.

---

## When a Simpler Approach Is Fine

For:

- Proof of Concepts (POCs)
- Internal demos
- Experimental projects

the full enterprise checklist may be unnecessary.

However, one best practice should always be followed:

✅ Keep secrets in environment variables.

Even prototypes benefit from this habit.

---

## Case Study: OAuth Worked in Staging but Failed in Production

### The Situation

A team built an MCP integration.

Everything worked perfectly in:

```text
staging.mycompany.com
```

After deployment:

```text
production.mycompany.com
```

All user sign-ins failed.

Team assumed:

```text
Code bug
```

Actual issue:

```text
OAuth configuration problem
```

---

### What Happened?

OAuth providers verify redirect URIs.

Only registered redirect URIs are allowed.

The team registered:

```text
staging.mycompany.com
```

But forgot to register:

```text
production.mycompany.com
```

When production users attempted login:

1. User clicked Sign In.
2. OAuth provider checked redirect URI.
3. URI was not registered.
4. OAuth rejected request.
5. Login failed.

---

### Security Review Conversation Simplified

Reviewer:

```text
Why are production logins failing?
```

Developer:

```text
OAuth worked in staging.
```

Reviewer:

```text
The production redirect URI was never registered.
```

Developer:

```text
So I must register the 
