## Accelerator & IP Contribution: Comparing Platforms - The Platform Picked on Familiarity That Failed Residency

### Scenario Overview

This case highlights a common mistake in enterprise AI deployments:

> Choosing a platform because it is familiar to the development team rather than because it satisfies the customer's requirements.

The team optimized for development speed and ease of migration. Although the application worked correctly and passed technical testing, it failed the customer's compliance review and could not be deployed.

For the Claude Developer Certification exam, this example reinforces an important principle:

> Platform selection should be driven by customer requirements, not developer convenience.

---

### What Happened?

A development team needed to build a Claude-based solution for a regulated customer.

The team selected a platform because:

- They had used it before.
- The integration was familiar.
- Existing knowledge reduced development effort.
- The project deadline was approaching.

Benefits achieved:

- Faster implementation
- Quicker development
- Successful functional testing

Initially, everything appeared successful.

---

### Security Review Discovery

During the customer's security and compliance review, an important question was raised:

> "Where is customer data being processed?"

The selected platform failed to satisfy the customer's data residency requirements.

As a result:

- Compliance approval was denied.
- The deployment could not proceed.
- The project could not move into production.

Although the application worked technically, it failed the requirements needed for release.

---

### The Alternative Platform

Another available platform:

- Supported regional deployment.
- Satisfied residency requirements.
- Had already been approved by the customer.
- Met compliance expectations.

However:

- The team was less familiar with it.
- Development would have taken more effort.

Despite this, it was the correct choice because it fulfilled the customer's requirements.

---

### Outcome

The deployment was rejected.

The team had to:

1. Stop the original release.
2. Select the compliant platform.
3. Rebuild integrations.
4. Retest the solution.
5. Repeat review processes.

This resulted in:

- Additional costs
- Project delays
- Increased workload
- Lost development effort

---

## Why Did It Fail?

### The Team Optimized for the Wrong Goal

The team focused on:

```text
Can we build it quickly?
```

Instead of:

```text
Can the customer legally and securely deploy it?
```

Development speed became the decision factor.

Compliance requirements were ignored during platform selection.

As a result, the chosen platform passed:

- Development reviews
- Functional tests

but failed:

- Security reviews
- Compliance reviews
- Residency validation

---

### Functional Success Does Not Guarantee Deployment Approval

The application may have been technically perfect.

It may have achieved:

- Accurate responses
- Low latency
- Successful integrations

However, if residency requirements are violated:

```text
The solution cannot be shipped.
```

For regulated customers, compliance is often more important than technical convenience.

---

## Understanding Data Residency

### What Is Data Residency?

Data residency specifies:

> Where data must be processed, stored, or transmitted.

Examples:

- Data must remain in the European Union.
- Data must remain within a specific country.
- Data must stay within approved cloud regions.

These requirements may come from:

- Government regulations
- Customer contracts
- Industry standards
- Internal security policies

---

### Why Residency Matters

Organizations in sectors such as:

- Banking
- Healthcare
- Government
- Insurance

often cannot process data outside approved regions.

Even if a platform offers:

- Better features
- Faster development
- Lower cost

it may be unusable if residency requirements are not met.

---

## The Real Root Cause

The problem was not:

- Claude
- Code quality
- Testing
- Integrations

The root cause was:

> Compliance requirements were not identified during scoping.

The team began building before validating:

- Residency needs
- Compliance obligations
- Deployment constraints

As a result, the risk appeared later when fixing it became expensive.


## Scoping Is Critical

### What Is Scoping?

Scoping is the early discovery phase where requirements are gathered.

During scoping, teams should identify:

#### Functional Requirements

What must the application do?

Example:

- Summarize documents
- Classify support tickets
- Generate responses

---

#### Infrastructure Requirements

How must the application operate?

Examples:

- Latency targets
- Scale targets
- Uptime expectations

---

#### Compliance Requirements

What regulations must be followed?

Examples:

- Data residency
- Security policies
- Industry regulations

---

#### Identity Requirements

How will users authenticate?

Examples:

- AWS IAM
- Azure AD
- Google IAM

---

### Why Scoping Saves Money

Early Discovery Cost:

```text
One Requirements Conversation
```

Late Discovery Cost:

```text
Entire Rebuild
```

The certification emphasizes that identifying constraints early is significantly cheaper than redesigning later.

---

## Lessons for Accelerator and IP Contributions

When creating reusable accelerators and IP assets:

### Do Not Assume a Platform

Build accelerators that can support multiple deployment environments when possible.




