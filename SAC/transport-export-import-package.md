#### SAP SAC Transport Package Scheduling 
##### DEV → QAS → PROD (End-to-End Explanation)

This document explains **SAP Analytics Cloud (SAC) Transport Package Scheduling** covering **all phases from Development to Production**, written in **real-time project and enterprise delivery language**.

---

##### 1. What is a Transport Package in SAP SAC?

A **Transport Package** in **SAP Analytics Cloud (SAC)** is a **container** used to move SAC content across systems in a controlled and auditable way.

##### Objects Included
- Stories 
- Models 
- Dimensions 
- Data Actions 
- Multi Actions 
- Analytical Applications 
- Files (optional)

**Purpose:** 
Enable **controlled, versioned, and traceable content movement** across system landscapes.

---

##### 2. Typical SAC Landscape

```text
DEV  →  QAS  →  PROD

System Purpose

DEV Development and unit testing
QAS Integration testing / UAT
PROD Live business usage



---

3. High-Level Transport Flow

Create Package in DEV
        ↓
Schedule Export (DEV)
        ↓
Import to QAS
        ↓
Testing & Validation
        ↓
Re-Export
        ↓
Import to PROD


---

4. Phase 1: Create Transport Package in DEV

Step 1: Create Package

Go to SAC → Transport

Create a new package

Provide:

Package Name

Description


Source system = DEV


Step 2: Add Objects

Add all required objects:

Models

Stories

Data Actions

Dimensions


Dependency Handling

SAC automatically detects dependencies.

Example:

Story → Model → Dimensions


---

5. Phase 2: Schedule Export from DEV

Why Scheduling?

Avoids manual errors

Ensures consistency

Suitable for planned or off-hour deployments


Export Types

Immediate Export

Scheduled Export (recommended)


Scheduling Details

Date and Time

One-time or recurring

Target system = QAS


Result:
SAC generates a transport artifact stored internally.


---

6. Phase 3: Import into QAS

Import Steps

Login to QAS

Navigate to Transport Management

Select incoming package

Trigger Import


Import Validation

Object existence

Dependency resolution

Version compatibility


Import Modes

Overwrite existing content

Skip existing objects


Outcome:
Objects become available in QAS for testing.


---

7. Phase 4: Testing & Validation in QAS

What is Tested?

Story rendering

Data accuracy

Data Action execution

Performance

Role and authorization checks


Possible Results

Result Action

Passed Move to PROD
Failed Fix in DEV and re-transport



---

8. Phase 5: Preparing Transport to PROD

Option A: Re-Export from DEV (Recommended)

DEV acts as single source of truth

Same package is scheduled again

Target system = PROD


Option B: Promote from QAS

Less commonly used

Depends on project governance



---

9. Phase 6: Schedule Export to PROD

Best Practices

Deploy during low-usage hours

Freeze DEV changes

Inform business users


Export Scope

Approved objects only

Version-locked content



---

10. Phase 7: Import into PROD

PROD Import

Transport admin triggers import

Resolve conflicts if any

Perform final smoke testing


Outcome:
Content becomes live for business users.


---

11. Versioning & Rollback

Versioning

Each transport creates a version

Used for tracking and audit


Rollback

No automatic rollback in SAC

Requires re-import of a previous stable package



---

12. Real-Time Example

Scenario: Finance Cash Flow Dashboard

DEV

Develop model and story

Package name: FIN_CASHFLOW_V1


QAS

Import and validate with finance users


PROD

Schedule weekend deployment

Import and go live on Monday


---

13. Benefits of SAC Transport Scheduling

Controlled deployments

Audit-friendly process

Reduced production risk

Enterprise-ready change management

Supports CI/CD mindset



---

