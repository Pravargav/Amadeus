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
