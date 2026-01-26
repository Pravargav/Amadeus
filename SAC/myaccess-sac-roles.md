# Why Amadeus Uses **MyAccess** Even Though SAC Has Roles

Even though **SAP Analytics Cloud (SAC)** has its own role-based permissions, Amadeus uses **MyAccess** as a **central Identity & Access Management (IAM)** layer. SAC roles control **what you can do inside SAC**, while MyAccess controls **whether you can access SAC at all**—with governance, audit, and compliance.

---

## Key Reasons

### 1) Centralized IAM & Consistency
- One place to request, approve, and revoke access across many apps (SAC, BW, Jira, ServiceNow, etc.).
- Ensures consistent processes, ownership, and visibility.

### 2) Compliance & Audit (SOX, ISO 27001, GDPR)
- MyAccess provides:
  - Approval workflows and audit trails 
  - Segregation of Duties (SoD) checks 
  - Periodic access reviews & recertification 
- SAC roles alone don’t satisfy enterprise governance requirements.

### 3) Two-Layer Security Model
- **Layer 1 – MyAccess:** Grants/blocks entry to the SAC application itself. 
- **Layer 2 – SAC Roles:** Define functional permissions inside SAC (e.g., Viewer vs. Story Designer, data access, modeler/admin).

### 4) Standardization Across Systems
- Same request/approval pattern for SAP systems, SAC, Snowflake, Git, Jira, ServiceNow, etc.
- Reduces operational overhead and process variance.

### 5) Faster Deactivation & HR Sync
- When someone changes role or exits, MyAccess can immediately revoke app access across all systems.
- Prevents orphaned or lingering accounts.

---
