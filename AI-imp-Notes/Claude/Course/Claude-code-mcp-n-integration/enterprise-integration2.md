# Managing Secrets Securely: Storage, Rotation, and Separation from Configuration

Authentication gets you access to a system. Secret management ensures that access remains secure over time.

The key lesson:

> A secret is not secure just because it uses a good authentication method. It must also be stored, managed, and rotated properly.

---

## 1. Separation: Keep Secrets Out of Configuration Files

**Rule:**
Configuration files should contain only references to secrets, not the actual secret values.

✅ Good

```text
API_KEY=${MY_API_KEY}
```

❌ Bad

```text
API_KEY=abcd123456789
```

### Why?

Configuration files are often:

- Shared
- Committed to Git
- Cloned by other developers
- Stored in repository history

If a secret is written directly in the file, it spreads everywhere the file goes.

### Benefit

Keeping secrets separate makes configuration files safe to share and version-control.

---

## 2. Store Secrets in the Right Place

After removing the secret from the configuration file, it needs a secure home.

### Option A: Environment Variables

Best for:

- One machine
- One application
- CI/CD pipeline runs
- Short-lived secrets

Example:

```text
MY_API_KEY=secret_value
```

The application reads the value at runtime without saving it in code.

### Option B: Secret Store

Best for:

- Multiple services
- Shared credentials
- Audited environments
- Enterprise deployments

Examples:

- Azure Key Vault
- AWS Secrets Manager
- HashiCorp Vault

A secret store:

- Securely holds credentials
- Returns them only to authorized users/services
- Records who accessed them
- Centralizes secret management

### Benefit

When the secret changes, all applications automatically use the new value without changing code.

---

## 3. Rotation: Replace Secrets Regularly

**Rotation** means replacing an old credential with a new one.

Rotate secrets:

- On a regular schedule
- Immediately after suspected exposure

### Why?

Once a secret is leaked:

> It can never be considered secret again.

The correct response is to issue a new credential.

### Benefit

If applications reference secrets by name:

```text
DATABASE_PASSWORD
```

instead of hardcoding values, the underlying secret can change without modifying application code.

---

## Additional Best Practices

### Use Least Privilege

Give each credential only the access it needs.

Example:

```text
Reporting Service → Read-only access
```

instead of:

```text
Reporting Service → Full admin access
```

If the credential leaks, the damage is limited.

---

### Track Credential Usage

Maintain a record of:

- Which services use each secret
- Who owns the secret
- Where it is used

This makes rotation easier and prevents outages when credentials change.

---

# Summary

Three practices prevent secret leaks:

1. **Separation**
   - Keep secrets out of configuration files.

2. **Secure Storage**
   - Use environment variables for local/temporary secrets.
   - Use a secret store for shared or auditable secrets.

3. **Rotation**
   - Regularly replace credentials and immediately rotate leaked ones.

## Key Takeaway

```text
Config File → References Secret
Secret Store / Environment Variable → Holds Secret
Rotation → Replaces Secret When Needed
```

A secure system never hardcodes credentials in code or configuration. Instead, it separates, securely stores, and regularly rotates them.

# The passage is talking about the credentials used to access external systems through Claude/MCP integrations, not specifically Claude's own API key.

## Short Answer

It can refer to:

✅ A GitHub Personal Access Token  
✅ A Jira API key  
✅ A Database credential  
✅ An Internal API key  
✅ A Claude API key (if your application is calling Claude)

The concept is generic:

> Any secret used for authentication should be stored securely, separated from configuration, and rotated regularly.

---

# In the MCP Context

Suppose Claude accesses GitHub through an MCP server.

## Bad

```json
{
  "github_token": "ghp_xxxxxxxxx"
}
```

If this file is committed to Git:

- The token leaks
- Everyone cloning the repo gets it
- It remains in Git history

## Good

```json
{
  "github_token": "${GITHUB_TOKEN}"
}
```

And:

```bash
export GITHUB_TOKEN=ghp_xxxxxxxxx
```

Now the configuration file contains only a reference, not the secret itself.

---

# What Key Leak Are They Referring To?

The sentence:

> "The MCP key leak mentioned earlier was not a bad choice of auth method, it was a credential that lived in the wrong place..."

means:

The problem was not OAuth vs API Key.

The problem was:

```text
Secret stored directly inside a file
```

instead of

```text
Secret stored in environment variables or a secret vault
```

---

# Is It Claude API Key or External Application API Key?

## Scenario 1: Claude Accessing GitHub

```text
Claude
  ↓
MCP Server
  ↓
GitHub
```

Secret being discussed:

```text
GitHub PAT (Personal Access Token)
```

---

## Scenario 2: Claude Accessing Jira

```text
Claude
  ↓
MCP Server
  ↓
Jira
```

Secret being discussed:

```text
Jira API Key / OAuth Token
```

---

## Scenario 3: Your App Accessing Claude

```text
Your Application
      ↓
Claude API
```

Secret being discussed:

```text
Claude API Key
```

The same rules apply:

- Don't hardcode it
- Store it in environment variables or a secret store
- Rotate it regularly

---

# What the Module Most Likely Means

Because the section is about:

> Connecting Claude to enterprise systems

the primary focus is usually on the credentials used by Claude/MCP to access enterprise systems such as:

- GitHub
- Linear
- Jira
- Internal APIs
- Databases

rather than Claude's own API key.

Think of it as:

```text
Claude → Enterprise System
```

and the secret belongs to the Enterprise System being accessed.

---

# Key Takeaway

```text
The lesson is not about a specific key.

It applies to ANY authentication secret:
- Claude API keys
- GitHub tokens
- Jira tokens
- Database passwords
- Internal service credentials
```

The module's main message is:

> Never store secrets directly in configuration files or source code. Use environment variables or a secret manager, and rotate credentials when necessary.
