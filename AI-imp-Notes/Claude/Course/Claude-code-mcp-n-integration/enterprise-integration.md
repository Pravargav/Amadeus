## Connecting Claude to Enterprise Systems Securely (Claude Developer Certification Notes)

### Why Enterprise Integration Is Different from a Prototype

A prototype only proves that the connection works.

An enterprise deployment must answer additional questions:

- Who is Claude acting as?
- Can that identity be audited?
- What data can Claude access?
- Where does the data go?
- Can administrators control the configuration?
- Can all activities be logged for compliance reviews?

In regulated industries like banking, healthcare, and government, these questions are mandatory before deployment.

Think of it this way:

- Prototype = "Can it connect?"
- Enterprise = "Can it connect securely, compliantly, and audibly?"

---

### Authentication Patterns by Service Type

#### 1. Remote Services with User Identity

Use **OAuth**.

How it works:

1. Claude tries to access the service.
2. MCP server returns **401 Unauthorized**.
3. User is redirected to a browser sign-in page.
4. User grants permission.
5. Access token is issued and stored securely.
6. Claude acts on behalf of that user.

Examples:

- Linear
- Google Workspace
- Microsoft 365
- Salesforce

Benefits:

- No manual secret sharing.
- User identity is preserved.
- Actions are traceable to a specific user.

Use when:

- Authorization depends on the individual user.
- User-specific permissions are required.

---

#### 2. Remote Services with Service Identity

Use **API Keys** or **Service Accounts**.

How it works:

1. A service account is created.
2. API key is stored securely.
3. Key is injected through environment variables or secret stores.
4. Claude authenticates as the service account.

Example:

```bash
API_KEY=${MY_SERVICE_KEY}
```

Benefits:

- Simple automation.
- Suitable for CI/CD pipelines.
- No human user involved.

Use when:

- Background automation is required.
- System-level access is needed.

Important Rule:

❌ Never hardcode API keys in code or configuration files.

✅ Store them in environment variables or secret managers.

---

#### 3. Local Services with File-System Access

Use:

- stdio transport
- File-system permissions

How it works:

- Claude communicates locally.
- No network authentication is needed.
- Security depends on operating system permissions.

Governance is provided using:

- Allow rules
- Deny rules
- Configuration policies

Use when:

- Tool runs entirely on the local machine.
- Communication never leaves the host.

---

### Secret Management Best Practices

Authentication is only half the problem.

The other half is protecting secrets after authentication.

Three principles must always be followed.

---

### Principle 1: Separation

Credential and configuration must be separate.

Bad:

```json
{
  "apiKey": "abc123secret"
}
```

Good:

```json
{
  "apiKey": "${SERVICE_KEY}"
}
```

Why?

Configuration files:

- Are shared
- Are committed to Git
- Are copied frequently

If a secret is inside the file, it spreads everywhere.

Key takeaway:

- Config contains references.
- Secret store contains values.

---

### Principle 2: Store Secrets Properly

#### Environment Variables

Best for:

- Local development
- CI/CD pipelines
- Short-lived usage

Example:

```bash
export SERVICE_KEY=abc123
```

Benefits:

- Not stored in code.
- Easy to inject at runtime.

---

#### Secret Stores

Best for:

- Shared services
- Enterprise deployments
- Compliance requirements

Examples:

- Azure Key Vault
- AWS Secrets Manager
- HashiCorp Vault

Benefits:

- Centralized storage.
- Access control.
- Read auditing.
- Easier rotation.

Rule:

Use environment variables for local secrets.

Use secret stores for shared or audited secrets.

---

### Principle 3: Rotation

Rotation means replacing a credential with a new one.

Rotate:

- On a schedule
- Immediately after suspected exposure

Why?

Once a key leaks, it is no longer secret.

The only solution is:

1. Create a new key.
2. Replace the old key.
3. Disable the compromised key.

Benefits of rotation:

- Limits security impact.
- Reduces exposure duration.
- Improves compliance.

---

### Least-Privilege Access

Always give a credential only the permissions it needs.

Example:

Instead of:

```text
Full database access
```

Use:

```text
Read-only customer reports
```

Benefits:

- Smaller attack surface.
- Reduced damage if compromised.
- Better compliance posture.

Principle:

**Minimum permission required to perform the task.**

---

### What Regulated Industries Require

Industries such as:

- Banking
- Healthcare
- Insurance
- Government

Need more than successful authentication.

They require answers to three major compliance questions.

---

### 1. Can Configuration Be Locked Down?

Enterprise administrators should be able to deploy a managed MCP configuration.

Benefits:

- Users cannot modify authentication settings.
- Consistent security controls.
- Easier audits.

Without this:

- Every developer might have a different configuration.
- Compliance becomes difficult.

---

### 2. Can Every Action Be Audited?

Use audit logging.

Recommended approach:

**PostToolUse Hooks**

How it works:

1. Tool executes.
2. Hook runs automatically.
3. Tool call details are logged.

Information captured:

- User
- Tool used
- Parameters
- Timestamp
- Result

Benefits:

- Compliance evidence.
- Security investigations.
- Change tracking.

Important:

The model cannot skip the hook.

Logging happens deterministically.

---

### 3. Where Does Data Go?

This is called **Data Residency**.

Organizations need clear answers to:

- Where data is processed?
- Which region stores the data?
- Does data leave the country?

Good practice:

- Use region-specific endpoints.
- Deploy infrastructure in approved regions.
- Keep processing within required geographic boundaries.

Example:

```text
EU customer data
        ↓
EU-hosted MCP server
        ↓
EU processing region
```

Benefits:

- Regulatory compliance.
- Better governance.
- Easier audits.

---

## Code Modernization Using Claude

Code modernization is a common enterprise use case.

Challenges:

- Large codebases
- Legacy systems
- Unknown dependencies
- High risk of changes

Claude's workflow helps reduce these risks.

---

### Explore → Plan → Code Loop

#### Step 1: Explore

Claude reads:

- Source code
- Dependencies
- Architecture

No modifications occur.

Goal:

Understand before changing.

---

#### Step 2: Plan

Plan Mode keeps Claude read-only.

Claude generates:

- Proposed changes
- Migration strategy
- Risk analysis

The human reviews before approval.

Goal:

Build confidence before editing.

---

#### Step 3: Code

Only after approval:

- Files are modified
- Refactoring begins
- Updates are applied

Goal:

Controlled execution.

---

### Additional Safety Controls

#### Hooks

Prevent dangerous operations.

Examples:

- Block edits to production configs.
- Prevent modifying sensitive directories.
- Enforce approval workflows.

---

#### CLAUDE.md

Stores project instructions.

Examples:

- Coding standards
- Architecture patterns
- Migration rules
- Team conventions

Benefits:

- Consistent changes across the project.
- Reduced drift toward legacy patterns.

---

## Three Questions Before Any High-Risk Agentic Task

### Question 1: What Is the Blast Radius?

Ask:

- What systems depend on this code?
- What breaks if a change is wrong?
- How large is the impact?

Larger impact = stronger controls.

---

### Question 2: How Will Changes Be Audited?

Ask:

- Are PostToolUse hooks enabled?
- Is every action logged?
- Can reviewers verify what happened?

Every significant action should be traceable.

---

### Question 3: Who Approves Each Stage?

Define:

- Who approves exploration results?
- Who approves plans?
- Who approves execution?

Plan Mode creates the boundary, but humans define the approval process.

-> https://youtu.be/ZDuRmhLSLOY?si=jW7g-jxU-lyTOqfB
