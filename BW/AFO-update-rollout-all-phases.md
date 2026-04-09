### SAP Analysis for Office – Change Request & Company Portal Flow 

This document explains the **end-to-end flow of SAP Analysis for Office (AO)** upgrade and deployment in **Cognizant**, using **Win@Approach (ChaRM)** and the **Company Portal (like a Play Store)**.

---

### 1️⃣ Identifying – Version & Support Package (Change Initiation)

- Identify the **supported combination**:
  - Windows OS version
  - MS Office version (32-bit / 64-bit)
  - SAP Analysis for Office (AO) version
  - AO Support Package (SP)
- Reasons for change:
  - Windows / Office upgrade
  - SAP recommended patch
  - Bug fixes or security issues

**Output:**
- Change Request (CR) raised in **Win@Approach**
- Scope defined as *AO upgrade & deployment via Company Portal*

---

### 2️⃣ Deployment Phase – DPS Team (Implementation)

- DPS (Desktop / Platform Support) team:
  - Packages AO installer along with required SP
  - Performs pilot deployment
  - Validates Excel add-in registration
- CR updated with:
  - Implementation steps
  - Risk and impact analysis
  - Rollback plan

**Users involved:**
1. Internal IT team 
2. Technical and Functional users 

This phase maps to **Implementation status in Win@Approach**.

---

### 3️⃣ UAT – User Acceptance Testing

- AO tested on pilot user laptops
- Validation includes:
  - AO tab visibility in Excel
  - BW / HANA connectivity
  - Existing reports and workbooks
- Issues tracked via:
  - ServiceNow tickets
  - Linked to the Win@Approach CR

**Outcome:**
- Business validation
- UAT sign-off captured in Win@Approach

---

### 4️⃣ End User Rollout – Company Portal (Like Play Store)

- After UAT approval:
  - DPS publishes **SAP Analysis for Office** in the **Company Portal**
- End users can:
  - Install or upgrade AO via self-service
  - Access only the **approved and supported version**
- Global rollout completed without manual installations

**Company Portal ensures:**
- Standardization
- Compliance
- Easy upgrades and rollback

---

### 5️⃣ Communication – Throughout the Change Lifecycle

Communication is mandatory at all stages:

- Pre-change notifications
- Installation and usage instructions
- Supported version matrix
- Known issues and FAQs
- Post-deployment confirmation

Communication artifacts are attached to the **Win@Approach Change Request**.

---

### 🔁 Tool & Phase Mapping

| Step | Tool / Platform |
|-----|-----------------|
| Change creation | Win@Approach |
| Issue tracking | ServiceNow |
| Deployment & packaging | DPS Team |
| End-user installation | Company Portal |
| Reporting tool | SAP Analysis for Office |

---

### 🎯Summary

> *SAP Analysis for Office upgrades are managed through a Win@Approach change, validated in UAT, and deployed globally via the Company Portal with controlled self-service access for end users.*

--- 
