## Accelerator & IP Contribution: Deployment & Versioning

### What is Deployment & Versioning?

After building a Claude application, accelerator, or IP asset, two important questions must be answered:

1. Where will the Claude workload run?
2. How will the version be controlled?

Deployment determines the platform that executes the Claude workload.

Versioning ensures that model, prompt, and application changes are controlled, traceable, and reversible.

For the Claude Developer Certification exam, remember:

> Deployment decides where the workload runs.
>
> Versioning ensures production behavior remains predictable and auditable.

---

### Why Deployment Matters

The deployment platform is the environment where Claude processes requests.

Although the same Claude model may be available on multiple platforms, the customer's existing cloud environment typically determines the platform choice.

Reasons include:

- Existing cloud investments
- Identity management systems
- Compliance agreements
- Security controls
- Data residency requirements

The best platform is often not the most technically advanced one.

Instead, it is usually the platform that best fits the customer's operational and compliance requirements.

---

### Key Factors That Influence Platform Choice

#### Identity

Identity determines:

- Who can access the system
- Authentication methods
- Authorization controls
- Auditability

Examples:

- AWS IAM
- Google Cloud IAM
- Microsoft Identity
- Anthropic Identity

A platform that aligns with an organization's existing identity infrastructure reduces integration complexity.

---

#### Data Residency

Data residency determines:

- Where data is processed
- Where data is stored
- Regulatory compliance requirements

Examples:

- GDPR
- HIPAA
- Government regulations
- Internal company policies

For regulated customers, residency can be the primary platform selection factor.

---

#### Compliance

Existing compliance approvals are valuable.

If a customer already operates in AWS under approved security controls, choosing AWS-based deployment generally avoids repeating lengthy compliance reviews.

---

### Claude Deployment Options

### 1. First-Party Claude API

Operated directly by Anthropic.

Characteristics:

- Newest features usually arrive first.
- Direct access to Claude capabilities.
- Anthropic identity and terms apply.

Choose When:

- Customer has no strong cloud preference.
- Latest Claude capabilities are required.
- Residency constraints are minimal.

Advantages:

- Fast access to new features.
- Direct model support.
- Highest feature availability.

---

### 2. Claude Platform on AWS

Runs through the customer's AWS account while using Anthropic model identities and lifecycle.

Characteristics:

- AWS integration.
- Anthropic-operated inference.
- Anthropic model lifecycle.

Choose When:

- Customer uses AWS.
- Customer wants Anthropic model IDs.
- Customer wants behavior similar to the first-party Claude API.

Advantages:

- Familiar AWS environment.
- Anthropic feature alignment.

---

### 3. Claude in Amazon Bedrock

Uses the Anthropic Messages API interface through Amazon Bedrock.

Characteristics:

- AWS identity and governance.
- Data remains within customer AWS controls.
- Broad feature parity with Claude API.

Choose When:

- Customer already uses AWS.
- AWS compliance controls are important.
- Centralized AWS governance is required.

Advantages:

- Strong AWS integration.
- Existing AWS compliance posture.
- Enterprise-friendly deployment.

---

### 4. Claude on Amazon Bedrock (Legacy)

Uses:

- InvokeModel API
- Converse API

Characteristics:

- Older implementation model.
- ARN-based model versioning.

Choose When:

- Existing Bedrock implementation already uses these APIs.
- Migration has not yet occurred.

Advantages:

- Supports legacy integrations.
- Compatible with existing architectures.

---

### 5. Google Vertex AI

Claude is deployed through Google Cloud.

Characteristics:

- Google IAM.
- Google billing.
- Regional deployment options.

Choose When:

- Customer primarily operates on Google Cloud.
- Existing GCP compliance controls exist.
- Residency requirements can be met through Google infrastructure.

Advantages:

- Google ecosystem integration.
- Regional deployment flexibility.

---

### 6. Third-Party Platforms

Examples:

- Microsoft Foundry
- Other AI-enabled enterprise platforms

Characteristics:

- Claude is embedded inside another platform.
- Identity and billing follow the platform provider.

Choose When:

- Customer already uses the platform.
- Existing governance and operational processes are established.

Advantages:

- Faster adoption.
- Reduced integration effort.
- Existing security controls.

---

### Microsoft Foundry Hosting Models

Claude in Microsoft Foundry currently supports multiple hosting approaches.

#### Hosted on Azure

Characteristics:

- Inference runs on Azure infrastructure.
- Supports selected Claude models.
- Azure compliance posture applies.

Useful for:

- Strong Azure residency requirements.
- Existing Azure governance processes.

---

#### Hosted on Anthropic

Characteristics:

- Inference runs on Anthropic-operated infrastructure.
- Broader Claude model availability.

Important:

For regulated workloads, always verify:

- Hosting form
- Data residency implications
- Compliance requirements

before deployment.

---

## Versioning

### Why Versioning Matters

Without versioning, production behavior can change unexpectedly.

Example:

Today:

```python
model = "claude-sonnet"
```

Tomorrow:

The alias may point to a newer model version.

Result:

- Different outputs
- Different behavior
- Different performance

without any deployment change from your team.

This creates operational risk.

---

### Alias vs Pinned Version

#### Moving Alias

Alias:

```python
model = "claude-haiku-4-5"
```

Problem:

The underlying model can change over time.

Output behavior may change.

---

#### Pinned Version

Pinned Snapshot:

```python
model = "claude-haiku-4-5-20251001"
```

Benefit:

The exact model version remains constant until intentionally changed.

This creates:

- Stability
- Traceability
- Auditability

---

### Version Everything

A Claude application consists of more than the model.

Version:

#### Model Version

Example:

- Claude Sonnet version
- Claude Opus version

#### Prompt Version

Prompt changes can significantly change output behavior.

Prompt updates should be tracked.

#### Application Version

Includes:

- Agent logic
- Tool integrations
- Business rules

Each deployment should have a defined release version.

---

### Keep Previous Versions

Always retain:

- Previous model versions
- Previous prompts
- Previous releases

Reason:

Rollback capability.

If a deployment causes regression:

- Restore prior version.
- Recover quickly.
- Reduce production impact.

---

## Evaluation-Based Promotion

### What is Promotion?

Promotion means moving a version from testing into production.

Example:

Development
→ Testing
→ Staging
→ Production

---

### Never Promote Without Evaluation

A new version should pass evaluations before production release.

Evaluation measures:

- Accuracy
- Quality
- Safety
- Latency
- Hallucination rates

Only versions meeting requirements should be promoted.

---

### Baseline Comparison

Compare:

Current Production Version

vs

New Candidate Version

If the new version:

- Improves performance
- Maintains safety
- Passes tests

then promote.

Otherwise:

- Reject
- Fix issues
- Retest

---

### Rollback Strategy

If production quality degrades:

1. Identify regression.
2. Revert to prior version.
3. Investigate cause.
4. Deploy corrected release.

A rollback strategy is a critical enterprise requirement.

---

## Deployment Decision Logic

Think of platform selection like this:

#### Choose First-Party Claude API

When:

- Latest features are required.
- No strong cloud constraints exist.

#### Choose AWS-Based Options

When:

- Customer already operates on AWS.
- AWS identity and compliance are important.

#### Choose Vertex AI

When:

- Customer is invested in Google Cloud.
- Google governance must be preserved.

#### Choose Microsoft Foundry or Another Platform

When:

- Customer already operates there.
- Existing controls simplify adoption.

---

## Handles Well

- Aligns deployment with customer cloud strategy.
- Supports compliance requirements.
- Maintains identity controls.
- Enables predictable production behavior.
- Supports rollback and auditing.
- Prevents unexpected model changes.

---

## Adds Cost or Complexity

- Version management effort.
- Storage of previous releases.
- Evaluation maintenance.
- Deployment approvals.
- Release governance.
- Rollback testing.

However, these controls significantly improve reliability and compliance.

---

## Use a Different Approach

For:

- Personal experiments
- Hackathons
- Proof-of-concepts
- Throwaway prototypes

Using a moving alias may be acceptable.

Example:

```python
model = "claude-sonnet"
```

For production workloads:

Always pin versions and maintain rollback capability.

